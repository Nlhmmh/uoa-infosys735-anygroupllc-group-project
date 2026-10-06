#!/usr/bin/env python3
"""
INFOSYS 735 GP2 Part 9 - small ALB request load generator.

Example:
    python part09_load_test.py http://YOUR-ALB-DNS/ --requests 400 --workers 20

Use only against your own Learner Lab endpoint.
The script uses the Python standard library only.
"""

import argparse
import concurrent.futures
import collections
import json
import math
from pathlib import Path
import time
import urllib.request
import urllib.error


def hit(url: str, timeout: float) -> tuple[int, float]:
    started = time.perf_counter()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "INFOSYS735-GP2-Part9-LoadTest/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response.read(256)
            status = response.getcode()
    except urllib.error.HTTPError as exc:
        status = exc.code
    except Exception:
        status = 0
    return status, (time.perf_counter() - started) * 1000


def main():
    parser = argparse.ArgumentParser(
        description="Generate a small amount of HTTP load for the Part 9 Auto Scaling demo."
    )
    parser.add_argument("url", help="ALB URL, for example http://my-alb.us-east-1.elb.amazonaws.com/")
    parser.add_argument("--requests", type=int, default=400, help="Total requests (default: 400)")
    parser.add_argument("--workers", type=int, default=20, help="Concurrent workers (default: 20)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout seconds (default: 5)")
    parser.add_argument("--duration", type=float, default=0, help="Spread the fixed request count across this many seconds; zero sends a burst")
    parser.add_argument("--output", type=Path, help="Save measured request counts and latency")
    args = parser.parse_args()

    if args.requests < 1 or args.workers < 1:
        raise SystemExit("--requests and --workers must be positive")
    if args.timeout <= 0 or args.duration < 0:
        raise SystemExit("timeout must be positive; duration cannot be negative")

    print(f"Target:   {args.url}")
    print(f"Requests: {args.requests}")
    print(f"Workers:  {args.workers}")
    print("Starting...")

    started = time.perf_counter()
    counts = collections.Counter()
    latencies = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = []
        for index in range(args.requests):
            scheduled = started + index * args.duration / args.requests
            time.sleep(max(0, scheduled - time.perf_counter()))
            futures.append(pool.submit(hit, args.url, args.timeout))
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            counts[status] += 1
            if status == 200:
                latencies.append(latency)

    elapsed = time.perf_counter() - started
    rps = args.requests / elapsed if elapsed else 0.0

    print("\nResult")
    print("------")
    for status, count in sorted(counts.items()):
        label = "connection/error" if status == 0 else f"HTTP {status}"
        print(f"{label:18} {count}")
    print(f"\nElapsed: {elapsed:.2f}s")
    print(f"Rate:    {rps:.2f} requests/s")
    latencies.sort()
    percentile = lambda p: round(latencies[max(0, math.ceil(len(latencies)*p)-1)], 2) if latencies else None
    result = {"requests": args.requests, "status_counts": dict(counts), "elapsed_seconds": round(elapsed, 2),
              "requests_per_second": round(rps, 2), "successful_latency_p50_ms": percentile(.5),
              "successful_latency_p95_ms": percentile(.95), "scope": "Learner Lab HTTP response test; not production capacity validation"}
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("\nAuto Scaling is not instantaneous.")
    print("Watch EC2 Auto Scaling Activity and the frontend target group for several minutes.")


if __name__ == "__main__":
    main()
