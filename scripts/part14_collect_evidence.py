#!/usr/bin/env python3
"""Capture read-only lab configuration, or check project resources after teardown."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from lab_support import aws_json, stack_outputs

PROJECT = "INFOSYS735-GP2"
PREFIX = "anygroup-gp2"


def collect(output, after_teardown=False, managed_secret_arn=None):
    output.mkdir(parents=True, exist_ok=True)
    errors, captured = {}, {}

    def capture(name, *command):
        try:
            value = aws_json(*command)
            captured[name] = value
        except (RuntimeError, ValueError, OSError) as exc:
            errors[name] = str(exc)
            value = {"collection_error": str(exc)}
        (output / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
        return value

    capture("identity", "sts", "get-caller-identity")
    instances = capture("ec2", "ec2", "describe-instances", "--filters",
                        f"Name=tag:Project,Values={PROJECT}",
                        "Name=instance-state-name,Values=pending,running,stopping,stopped")
    asgs = capture("autoscaling", "autoscaling", "describe-auto-scaling-groups")
    alarms = capture("alarms", "cloudwatch", "describe-alarms", "--alarm-name-prefix", PREFIX)
    vpcs = capture("vpcs", "ec2", "describe-vpcs", "--filters", f"Name=tag:Project,Values={PROJECT}")
    nats = capture("nat_gateways", "ec2", "describe-nat-gateways", "--filter", f"Name=tag:Project,Values={PROJECT}")
    live_nats = [n for n in nats.get("NatGateways", []) if n["State"] != "deleted"]
    eips = capture("elastic_ips", "ec2", "describe-addresses", "--filters", f"Name=tag:Project,Values={PROJECT}")
    databases = capture("rds", "rds", "describe-db-instances")
    project_databases = [d for d in databases.get("DBInstances", []) if d["DBInstanceIdentifier"].startswith(PREFIX)]
    stack_names = [os.getenv(key, f"{PREFIX}-{suffix}") for key, suffix in (
        ("NETWORK_STACK_NAME", "network"), ("CORE_STACK_NAME", "core"),
        ("OBS_STACK_NAME", "observability"), ("MICROSERVICE_STACK_NAME", "microservice"))]
    summaries = capture("stack_inventory", "cloudformation", "list-stacks")
    live_stacks = [s for s in summaries.get("StackSummaries", [])
                   if s["StackName"] in stack_names and s["StackStatus"] != "DELETE_COMPLETE"]
    counts = {
        "ec2": sum(len(r["Instances"]) for r in instances.get("Reservations", [])),
        "autoscaling_groups": sum(g["AutoScalingGroupName"].startswith(PREFIX)
                                  for g in asgs.get("AutoScalingGroups", [])),
        "vpcs": len(vpcs.get("Vpcs", [])), "stacks": len(live_stacks),
        "project_alarms": len(alarms.get("MetricAlarms", [])),
        "nat_gateways": len(live_nats),
        "elastic_ips": len(eips.get("Addresses", [])), "rds_instances": len(project_databases),
    }

    if after_teardown:
        for name, command, collection, field in (
            ("load_balancers", ("elbv2", "describe-load-balancers"), "LoadBalancers", "LoadBalancerName"),
            ("target_groups", ("elbv2", "describe-target-groups"), "TargetGroups", "TargetGroupName"),
            ("ecr", ("ecr", "describe-repositories"), "repositories", "repositoryName"),
            ("dynamodb", ("dynamodb", "list-tables"), "TableNames", None),
            ("ecs", ("ecs", "list-clusters"), "clusterArns", None),
            ("sns", ("sns", "list-topics"), "Topics", "TopicArn"),
            ("s3", ("s3api", "list-buckets"), "Buckets", "Name"),
        ):
            data = capture(name, *command)
            counts[name] = sum((row[field] if field else row).split("/")[-1].split(":")[-1].startswith(PREFIX)
                               for row in data.get(collection, []))
        logs = capture("logs", "logs", "describe-log-groups", "--log-group-name-prefix", f"/{PREFIX}/")
        counts["log_groups"] = len(logs.get("logGroups", []))
        for name, operation, collection, field in (
            ("rds_snapshots", "describe-db-snapshots", "DBSnapshots", "DBInstanceIdentifier"),
            ("rds_backups", "describe-db-instance-automated-backups", "DBInstanceAutomatedBackups", "DBInstanceIdentifier"),
            ("rds_subnet_groups", "describe-db-subnet-groups", "DBSubnetGroups", "DBSubnetGroupName"),
        ):
            data = capture(name, "rds", operation)
            counts[name] = sum(row[field].startswith(PREFIX) for row in data.get(collection, []))
        secrets = capture("secret_metadata", "secretsmanager", "list-secrets")
        counts["secrets"] = sum(secret["Name"].startswith(PREFIX) or any(
            PREFIX in tag["Value"] and "rds" in tag["Key"].lower() for tag in secret.get("Tags", []))
            for secret in secrets.get("SecretList", []))
        if managed_secret_arn:
            try:
                value = aws_json("secretsmanager", "describe-secret", "--secret-id", managed_secret_arn)
                counts["known_rds_managed_secret"] = 1
                (output / "managed_secret_metadata.json").write_text(json.dumps(value, indent=2) + "\n")
            except RuntimeError as exc:
                if "ResourceNotFoundException" in str(exc):
                    counts["known_rds_managed_secret"] = 0
                else:
                    errors["managed_secret_metadata"] = str(exc)
        status = "PARTIAL" if errors else ("PASS" if not any(counts.values()) else "FAIL")
        result = {"status": status, "scope": "project tags, stack names and anygroup-gp2 resource-name prefixes",
                  "remaining_resource_counts": counts}
    else:
        for name in stack_names:
            capture("stack_" + name, "cloudformation", "describe-stacks", "--stack-name", name)
        try:
            network, core, micro = (stack_outputs(stack_names[i]) for i in (0, 1, 3))
            vpc, bucket = network["VpcId"], core["CatalogueImageBucketName"]
            capture("rds_events", "rds", "describe-events", "--source-type", "db-instance",
                    "--source-identifier", core["DatabaseInstanceIdentifier"], "--duration", "1440")
            # Metadata only; never call GetSecretValue or write passwords to evidence.
            capture("database_application_secret_metadata", "secretsmanager", "describe-secret",
                    "--secret-id", core["DatabaseApplicationSecretArn"])
            for name, operation in (("subnets", "describe-subnets"), ("routes", "describe-route-tables"),
                                    ("nacls", "describe-network-acls")):
                capture(name, "ec2", operation, "--filters", f"Name=vpc-id,Values={vpc}")
            groups = capture("security_groups", "ec2", "describe-security-groups", "--filters",
                             f"Name=vpc-id,Values={vpc}", f"Name=tag:Project,Values={PROJECT}")
            for name, operation in (("s3_public_access", "get-public-access-block"),
                                    ("s3_encryption", "get-bucket-encryption"), ("s3_policy", "get-bucket-policy")):
                capture(name, "s3api", operation, "--bucket", bucket)
            capture("s3_objects", "s3api", "list-objects-v2", "--bucket", bucket, "--prefix", "products/")
            capture("dynamodb", "dynamodb", "describe-table", "--table-name", micro["CatalogueTableName"])
            capture("ecr", "ecr", "describe-images", "--repository-name", micro["EcrRepositoryName"])
            capture("ecs_service", "ecs", "describe-services", "--cluster", micro["CatalogueClusterName"],
                    "--services", micro["CatalogueServiceName"])
            task_ids = capture("ecs_task_ids", "ecs", "list-tasks", "--cluster", micro["CatalogueClusterName"],
                               "--service-name", micro["CatalogueServiceName"], "--desired-status", "RUNNING").get("taskArns", [])
            tasks = capture("ecs_tasks", "ecs", "describe-tasks", "--cluster", micro["CatalogueClusterName"],
                            "--tasks", *task_ids) if task_ids else {}
            eni_ids = [d["value"] for task in tasks.get("tasks", []) for attachment in task.get("attachments", [])
                       for d in attachment.get("details", []) if d["name"] == "networkInterfaceId"]
            enis = capture("fargate_network_interfaces", "ec2", "describe-network-interfaces", "--network-interface-ids", *eni_ids) if eni_ids else {}
            for name in ("frontend", "backend"):
                capture(name + "_activity", "autoscaling", "describe-scaling-activities",
                        "--auto-scaling-group-name", core[name.capitalize() + "AutoScalingGroupName"])
            for name, arn in (("frontend", core["FrontendTargetGroupArn"]), ("backend", core["BackendTargetGroupArn"]),
                              ("catalogue", micro["CatalogueTargetGroupArn"])):
                capture(name + "_targets", "elbv2", "describe-target-health", "--target-group-arn", arn)
            capture("listener_rules", "elbv2", "describe-rules", "--listener-arn", core["InternalHttpListenerArn"])
            observability = stack_outputs(stack_names[2])
            capture("sns_subscriptions", "sns", "list-subscriptions-by-topic",
                    "--topic-arn", observability["OperationsTopicArn"])
            security = {
                "all_ec2_have_no_public_ip": all("PublicIpAddress" not in instance
                    for reservation in instances.get("Reservations", []) for instance in reservation["Instances"]
                    if not any(t["Key"] == "Component" and t["Value"] == "Network" for t in instance.get("Tags", []))),
                "no_allow_all_ipv4_egress": all(not (p["IpProtocol"] == "-1"
                    and any(r["CidrIp"] == "0.0.0.0/0" for r in p.get("IpRanges", [])))
                    for g in groups.get("SecurityGroups", []) for p in g.get("IpPermissionsEgress", [])),
                "fargate_has_two_private_enis": len(enis.get("NetworkInterfaces", [])) == 2 and
                    all("PublicIp" not in eni.get("Association", {}) for eni in enis.get("NetworkInterfaces", [])),
                "private_encrypted_multi_az_rds": len(project_databases) == 1 and all(
                    not d["PubliclyAccessible"] and d["StorageEncrypted"] and d["MultiAZ"]
                    and d["BackupRetentionPeriod"] >= 1 for d in project_databases),
                "two_available_nat_gateways_in_two_subnets": len(live_nats) == 2 and
                    all(n["State"] == "available" for n in live_nats) and
                    len({n["SubnetId"] for n in live_nats}) == 2,
            }
            # Missing reads must never become a vacuous security PASS.
            security["configuration_complete"] = len(groups.get("SecurityGroups", [])) == 6 and counts["ec2"] >= 4
        except (RuntimeError, KeyError, ValueError, OSError) as exc:
            errors["dependent_reads"] = str(exc)
            security = {"configuration_complete": False}
        result = {"status": "PARTIAL" if errors else ("CAPTURED" if all(security.values()) else "FAIL"), "resource_counts": counts,
                  "security_configuration_checks": security,
                  "functional_tests": "RUN part12_test_catalogue.sh separately",
                  "failure_recovery_tests": "NOT_RUN_BY_COLLECTOR",
                  "budget_balance": None, "actual_cost": None, "cost_currency": "USD",
                  "cost_owner": None, "cost_efficiency": None}
    result["captured_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["region"] = os.getenv("AWS_REGION", "us-east-1")
    result["collection_errors"] = errors
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("evidence") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--after-teardown", action="store_true", help="Read-only check for remaining project resources")
    parser.add_argument("--managed-secret-arn", help="Known RDS-managed secret ARN saved before teardown; metadata check only")
    args = parser.parse_args()
    result = collect(args.output, args.after_teardown, args.managed_secret_arn)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"CAPTURED", "PASS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
