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
import time
import urllib.request
import urllib.error


def hit(url: str, timeout: float) -> int:
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
            return response.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate a small amount of HTTP load for the Part 9 Auto Scaling demo."
    )
    parser.add_argument("url", help="ALB URL, for example http://my-alb.us-east-1.elb.amazonaws.com/")
    parser.add_argument("--requests", type=int, default=400, help="Total requests (default: 400)")
    parser.add_argument("--workers", type=int, default=20, help="Concurrent workers (default: 20)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout seconds (default: 5)")
    args = parser.parse_args()

    if args.requests < 1 or args.workers < 1:
        raise SystemExit("--requests and --workers must be positive")

    print(f"Target:   {args.url}")
    print(f"Requests: {args.requests}")
    print(f"Workers:  {args.workers}")
    print("Starting...")

    started = time.perf_counter()
    counts = collections.Counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(hit, args.url, args.timeout) for _ in range(args.requests)]
        for future in concurrent.futures.as_completed(futures):
            counts[future.result()] += 1

    elapsed = time.perf_counter() - started
    rps = args.requests / elapsed if elapsed else 0.0

    print("\nResult")
    print("------")
    for status, count in sorted(counts.items()):
        label = "connection/error" if status == 0 else f"HTTP {status}"
        print(f"{label:18} {count}")
    print(f"\nElapsed: {elapsed:.2f}s")
    print(f"Rate:    {rps:.2f} requests/s")
    print("\nAuto Scaling is not instantaneous.")
    print("Watch EC2 Auto Scaling Activity and the frontend target group for several minutes.")


if __name__ == "__main__":
    main()
