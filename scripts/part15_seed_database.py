#!/usr/bin/env python3
"""Seed synthetic Oracle data from one private backend through SSM; no secrets leave EC2."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from lab_support import aws_json, stack_outputs


def seed():
    core = stack_outputs(os.getenv("CORE_STACK_NAME", "anygroup-gp2-core"))
    group = aws_json("autoscaling", "describe-auto-scaling-groups", "--auto-scaling-group-names",
                     core["BackendAutoScalingGroupName"])["AutoScalingGroups"][0]
    instances = [i["InstanceId"] for i in group["Instances"] if i["LifecycleState"] == "InService"]
    if not instances:
        raise RuntimeError("No in-service backend available for database seeding")
    instance = instances[0]
    for _ in range(60):
        state = aws_json("ssm", "describe-instance-information", "--filters",
                         json.dumps([{"Key": "InstanceIds", "Values": [instance]}]))
        if any(i.get("PingStatus") == "Online" for i in state.get("InstanceInformationList", [])):
            break
        time.sleep(5)
    else:
        raise RuntimeError("Backend is not online in SSM; check LabInstanceProfile, SSM agent and NAT routes")
    commands = ["set -eu", "set -a", ". /etc/anygroup-backend.env", "set +a",
                "/opt/anygroup-backend-venv/bin/python /opt/anygroup_backend.py --seed-db"]
    submitted = aws_json("ssm", "send-command", "--document-name", "AWS-RunShellScript",
                         "--instance-ids", instance, "--timeout-seconds", "120",
                         "--parameters", json.dumps({"commands": commands, "executionTimeout": ["120"]}))
    command = submitted["Command"]["CommandId"]
    for _ in range(60):
        invocations = aws_json("ssm", "list-command-invocations", "--command-id", command, "--details").get("CommandInvocations", [])
        invocation = next((i for i in invocations if i["InstanceId"] == instance), None)
        if invocation:
            status = invocation["Status"]
            if status == "Success":
                # Do not store raw Run Command output or credentials in evidence.
                return {"status": "PASS", "command_id": command, "backend_instance_id": instance,
                        "database_instance_id": core["DatabaseInstanceIdentifier"],
                        "captured_at_utc": datetime.now(timezone.utc).isoformat()}
            if status not in {"Pending", "InProgress", "Delayed"}:
                raise RuntimeError(f"Database seed command {command} ended with {status}; inspect this command in SSM")
        time.sleep(5)
    raise RuntimeError(f"Database seed command {command} did not complete within five minutes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = seed()
    except (RuntimeError, KeyError, ValueError, OSError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
