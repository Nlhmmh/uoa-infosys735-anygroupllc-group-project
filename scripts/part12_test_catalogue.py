#!/usr/bin/env python3
"""Assert the working pilot, dependency access and basic private-image protection."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

from lab_support import aws_json, http_get, stack_outputs


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def run_checks(wait=False):
    core = stack_outputs(os.getenv("CORE_STACK_NAME", "anygroup-gp2-core"))
    micro = stack_outputs(os.getenv("MICROSERVICE_STACK_NAME", "anygroup-gp2-microservice"))
    require("CatalogueServiceName" in micro, "DeployService is not enabled")
    if wait:
        aws_json("ecs", "wait", "services-stable", "--cluster", micro["CatalogueClusterName"], "--services", micro["CatalogueServiceName"])
        for arn in (core["FrontendTargetGroupArn"], core["BackendTargetGroupArn"], micro["CatalogueTargetGroupArn"]):
            aws_json("elbv2", "wait", "target-in-service", "--target-group-arn", arn)
    base = "http://" + core["AlbDnsName"]
    page = http_get(base + "/", json_response=False).decode()
    require("AnyGroup Market" in page, "Storefront page missing")
    require(re.search(r"Instance:\s*i-[0-9a-f]+", page), "Frontend instance metadata missing")
    require("${!" not in page, "Unresolved launch-template variable in storefront")
    legacy = http_get(base + "/api/health")
    require(re.fullmatch(r"i-[0-9a-f]+", legacy.get("instance_id", "")), "Backend instance metadata missing")
    require(legacy.get("availability_zone", "unknown") != "unknown", "Backend AZ missing")
    db = http_get(base + "/api/db")
    require(db.get("all_reachable") and len(db.get("databases", [])) == 2, "Both dummy DB nodes must be reachable")
    health = http_get(base + "/catalogue/health")
    require(health.get("status") == "healthy", "Catalogue process is not live")
    ready = http_get(base + "/catalogue/ready")
    require(ready.get("dependencies") == {"dynamodb": "accessible", "s3": "accessible"}, "Catalogue dependencies not accessible")
    products = http_get(base + "/catalogue/products")["products"]
    require({"P1001", "P1002", "P1003"} <= {p["product_id"] for p in products}, "Seed products missing")
    for product in ("P1001", "P1002", "P1003"):
        item = http_get(base + "/catalogue/products/" + product)["product"]
        require(item["product_id"] == product, "Product response mismatch")
        image = http_get(base + "/catalogue/products/" + product + "/image-url")
        require(image["expires_in_seconds"] == 300, "Unexpected image URL expiry")
        parsed = urlsplit(image["image_url"])
        require(parsed.scheme == "https", "Images must use HTTPS")
        http_get(image["image_url"], json_response=False, sample_only=True)
        unsigned = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        http_get(unsigned, expect=403, json_response=False, sample_only=True)
    http_get(base + "/catalogue/products/DOES-NOT-EXIST", expect=404)
    http_get(base + "/catalogue/unknown", expect=404)

    require("CatalogueServiceName" in micro, "DeployService is not enabled")
    cluster, service = micro["CatalogueClusterName"], micro["CatalogueServiceName"]
    described = aws_json("ecs", "describe-services", "--cluster", cluster, "--services", service)
    require(not described.get("failures"), "ECS describe-services reported failures")
    state = described["services"][0]
    require(state["status"] == "ACTIVE" and state["desiredCount"] == 2 and state["runningCount"] == 2
            and state["pendingCount"] == 0, "ECS service must have two running tasks and no pending tasks")
    primary = next(d for d in state["deployments"] if d["status"] == "PRIMARY")
    require(primary.get("rolloutState") == "COMPLETED", "ECS rollout has not completed")
    definition = aws_json("ecs", "describe-task-definition", "--task-definition", state["taskDefinition"])["taskDefinition"]
    require("@sha256:" in definition["containerDefinitions"][0]["image"], "Running task definition is not pinned to a digest")
    require(definition["runtimePlatform"]["cpuArchitecture"] == "X86_64", "Unexpected task architecture")
    task_ids = aws_json("ecs", "list-tasks", "--cluster", cluster, "--service-name", service, "--desired-status", "RUNNING")["taskArns"]
    require(len(task_ids) == 2, "Expected two running catalogue tasks")
    tasks = aws_json("ecs", "describe-tasks", "--cluster", cluster, "--tasks", *task_ids)
    require(not tasks.get("failures"), "ECS describe-tasks reported failures")
    zones = sorted({t["availabilityZone"] for t in tasks["tasks"]})
    require(len(zones) == 2, "Catalogue tasks are not currently distributed across two AZs")
    targets = {}
    for name, arn in (("frontend", core["FrontendTargetGroupArn"]), ("backend", core["BackendTargetGroupArn"]),
                      ("catalogue", micro["CatalogueTargetGroupArn"])):
        target_state = aws_json("elbv2", "describe-target-health", "--target-group-arn", arn)["TargetHealthDescriptions"]
        healthy = sum(t["TargetHealth"]["State"] == "healthy" for t in target_state)
        require(healthy >= 2, f"{name} target group must have at least two healthy targets")
        targets[name] = healthy
    return {"status": "PASS", "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "catalogue_version": health["version"], "catalogue_task_azs": zones,
            "healthy_targets": targets, "seed_product_and_image_checks": 3,
            "unsigned_image_access": "HTTP_403", "database_replication": "NOT_IMPLEMENTED_SIMULATION_ONLY"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Save a result without presigned URLs or credentials")
    parser.add_argument("--wait", action="store_true", help="Wait for ECS stability and target health before checking endpoints")
    args = parser.parse_args()
    try:
        result = run_checks(args.wait)
    except (AssertionError, RuntimeError, KeyError, ValueError, OSError, StopIteration) as exc:
        result = {"status": "FAIL", "error": str(exc), "captured_at_utc": datetime.now(timezone.utc).isoformat()}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
