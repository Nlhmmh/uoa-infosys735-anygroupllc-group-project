#!/usr/bin/env python3
"""Wait for initial rotation, or deliberately rotate and verify persisted API data."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from lab_support import aws_json, http_get, stack_outputs


def rotation_complete(metadata, version=None):
    versions = metadata.get("VersionIdsToStages", {})
    pending = any("AWSPENDING" in stages and "AWSCURRENT" not in stages for stages in versions.values())
    if not metadata.get("RotationEnabled") or pending:
        return False
    return ("AWSCURRENT" in versions.get(version, []) if version
            else bool(metadata.get("LastRotatedDate")))


def run(output, rotate=False, timeout=600):
    output.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        (output / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
    core = stack_outputs(os.getenv("CORE_STACK_NAME", "anygroup-gp2-core"))
    arn = core["DatabaseApplicationSecretArn"]
    base = "http://" + core["AlbDnsName"]
    before = aws_json("secretsmanager", "describe-secret", "--secret-id", arn)
    save("before_metadata", before)
    version = None
    rows = None
    if rotate:
        if not before.get("RotationEnabled"):
            raise RuntimeError("Rotation is not configured; run lab.sh setup first")
        if any("AWSPENDING" in stages and "AWSCURRENT" not in stages
               for stages in before.get("VersionIdsToStages", {}).values()):
            raise RuntimeError("A pending rotation exists; resolve or wait for it before another test")
        rows = {path: http_get(base + path) for path in ("/api/orders", "/api/account")}
        trigger = aws_json("secretsmanager", "rotate-secret", "--secret-id", arn)
        save("trigger", trigger)
        version = trigger["VersionId"]
    deadline = time.monotonic() + timeout
    while True:
        metadata = aws_json("secretsmanager", "describe-secret", "--secret-id", arn)
        if rotation_complete(metadata, version):
            break
        if time.monotonic() >= deadline:
            save("after_metadata", metadata)
            raise RuntimeError("Rotation did not complete; inspect its Lambda logs and secret metadata")
        time.sleep(5)
    save("after_metadata", metadata)
    # Pending credentials were tested inside Lambda; check the actual frontend/API path too.
    after = {path: http_get(base + path) for path in ("/api/orders", "/api/account")}
    if rows is not None and rows != after:
        raise RuntimeError("Orders/account data changed during rotation")
    result = {"status": "PASS", "mode": "ROTATE_AND_VERIFY" if rotate else "WAIT_FOR_INITIAL_ROTATION",
              "secret_arn": arn, "promoted_version": version,
              "rotation_enabled": True, "last_rotated_date": metadata.get("LastRotatedDate"),
              "rotation_rules": metadata.get("RotationRules"), "sql_backed_apis": "PASS",
              "data_preserved": True if rotate else "NOT_COMPARED", "api_data": after,
              "captured_at_utc": datetime.now(timezone.utc).isoformat()}
    save("summary", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--wait-initial", action="store_true")
    mode.add_argument("--rotate", action="store_true", help="Deliberately rotate the application password now")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.output, args.rotate, args.timeout)
    except (RuntimeError, ValueError, KeyError, OSError, AssertionError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
