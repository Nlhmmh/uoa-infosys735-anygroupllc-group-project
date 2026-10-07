#!/usr/bin/env python3
"""Sample an endpoint during a manual lab failure test; never terminates resources."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def sample(url, timeout, expected_key=None, expected_value=None):
    start = time.monotonic()
    status, valid = 0, False
    try:
        with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=timeout) as response:
            status = response.getcode()
            body = response.read()
            valid = status == 200
            if expected_key:
                value = json.loads(body)
                for key in expected_key.split("."):
                    value = value[int(key)] if isinstance(value, list) else value[key]
                valid = valid and str(value) == expected_value
    except HTTPError as exc:
        status = exc.code
        exc.close()
    except (URLError, OSError, ValueError, KeyError, TypeError, IndexError):
        valid = False
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "http_status": status,
            "functional_success": valid, "latency_ms": round((time.monotonic() - start) * 1000, 2)}


def summary(samples):
    latencies = sorted(s["latency_ms"] for s in samples if s["functional_success"])
    percentile = lambda p: latencies[max(0, math.ceil(len(latencies) * p) - 1)] if latencies else None
    return {"samples": len(samples), "successes": len(latencies),
            "observed_success_percent": round(100 * len(latencies) / len(samples), 2) if samples else None,
            "http_status_counts": dict(Counter(str(s["http_status"]) for s in samples)),
            "successful_latency_p50_ms": percentile(.5), "successful_latency_p95_ms": percentile(.95),
            "failure_observed": any(not s["functional_success"] for s in samples),
            "final_sample_success": samples[-1]["functional_success"] if samples else None,
            "interpretation": "Sampled endpoint behaviour; not an SLA, AZ-outage test, or full-capacity recovery measurement"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--duration", type=float, default=300)
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--expect-json-key")
    parser.add_argument("--expect-json-value")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.duration, args.interval, args.timeout) <= 0:
        parser.error("duration, interval and timeout must be positive")
    url = urlsplit(args.url)
    if url.scheme not in {"http", "https"} or not url.netloc or url.query or url.username:
        parser.error("Use a plain HTTP(S) lab endpoint without credentials or query parameters")
    if bool(args.expect_json_key) != (args.expect_json_value is not None):
        parser.error("Supply both --expect-json-key and --expect-json-value")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    samples = []
    deadline = time.monotonic() + args.duration
    with args.output.open("w") as output:
        while time.monotonic() < deadline:
            started = time.monotonic()
            result = sample(args.url, args.timeout, args.expect_json_key, args.expect_json_value)
            samples.append(result)
            output.write(json.dumps(result) + "\n")
            output.flush()
            time.sleep(max(0, min(args.interval - (time.monotonic() - started), deadline - time.monotonic())))
    report = summary(samples)
    args.output.with_suffix(".summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    # Observing a controlled failure is evidence, not a failed test harness.
    return 0 if samples else 1


if __name__ == "__main__":
    raise SystemExit(main())
