#!/usr/bin/env python3
"""Explicitly force a lab RDS failover and measure the real SQL-backed API throughout."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from lab_support import aws_json, http_get, stack_outputs
from part14_probe_availability import sample, summary


def restored(before, after, orders_before, orders_after):
    return (after.get("DBInstanceStatus") == "available" and after.get("MultiAZ")
            and bool(after.get("AvailabilityZone")) and bool(before.get("AvailabilityZone"))
            and after.get("AvailabilityZone") != before.get("AvailabilityZone")
            and after.get("Endpoint", {}).get("Address") == before.get("Endpoint", {}).get("Address")
            and bool(orders_before) and orders_before == orders_after)


def run(output, duration):
    output.mkdir(parents=True, exist_ok=True)
    core = stack_outputs(os.getenv("CORE_STACK_NAME", "anygroup-gp2-core"))
    identifier = core["DatabaseInstanceIdentifier"]
    url = "http://" + core["AlbDnsName"] + "/api/orders"
    before = aws_json("rds", "describe-db-instances", "--db-instance-identifier", identifier)["DBInstances"][0]
    if not before.get("MultiAZ") or before["DBInstanceStatus"] != "available":
        raise RuntimeError("RDS must be available and Multi-AZ before forcing a failover")
    orders_before = http_get(url).get("orders", [])
    if not orders_before:
        raise RuntimeError("SQL-backed order data is missing; run setup/test first")
    (output / "before.json").write_text(json.dumps(before, indent=2) + "\n")
    samples = [sample(url, 5, "orders.0.order_id", orders_before[0]["order_id"])]
    if not samples[0]["functional_success"]:
        raise RuntimeError("Baseline functional probe failed; no failover requested")
    trigger = datetime.now(timezone.utc).isoformat()
    (output / "trigger.json").write_text(json.dumps({"requested_at_utc": trigger,
                                                    "database_instance_id": identifier,
                                                    "operation": "reboot-db-instance --force-failover"}, indent=2) + "\n")
    aws_json("rds", "reboot-db-instance", "--db-instance-identifier", identifier, "--force-failover")
    after, orders_after, verified = {}, [], False
    started = time.monotonic()
    next_state_read = 0
    with (output / "requests.jsonl").open("w") as stream:
        stream.write(json.dumps(samples[0]) + "\n")
        while time.monotonic() - started < duration:
            result = sample(url, 5, "orders.0.order_id", orders_before[0]["order_id"])
            samples.append(result)
            stream.write(json.dumps(result) + "\n")
            stream.flush()
            if time.monotonic() >= next_state_read:
                after = aws_json("rds", "describe-db-instances", "--db-instance-identifier", identifier)["DBInstances"][0]
                next_state_read = time.monotonic() + 15
                if result["functional_success"]:
                    try:
                        orders_after = http_get(url).get("orders", [])
                    except (AssertionError, RuntimeError, ValueError, OSError):
                        orders_after = []
                    verified = restored(before, after, orders_before, orders_after)
                    if verified and time.monotonic() - started >= 30:
                        break
            time.sleep(1)
    (output / "after.json").write_text(json.dumps(after, indent=2) + "\n")
    result = {"status": "PASS" if verified else "FAIL", "trigger_time_utc": trigger,
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "database_instance_id": identifier, "primary_az_before": before["AvailabilityZone"],
              "primary_az_after": after.get("AvailabilityZone"), "endpoint_unchanged":
              after.get("Endpoint", {}).get("Address") == before["Endpoint"]["Address"],
              "orders_preserved": bool(orders_before) and orders_before == orders_after,
              "probe": summary(samples), "scope": "One deliberate RDS failover; not an AZ outage or production SLA"}
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=600)
    args = parser.parse_args()
    if args.duration < 60:
        parser.error("Allow at least 60 seconds for failover observation")
    try:
        result = run(args.output, args.duration)
    except (RuntimeError, AssertionError, KeyError, ValueError, OSError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
