"""Read-only AWS CLI and HTTP helpers; no credentials are written to evidence."""
import json
import os
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def aws_json(*args):
    command = ["aws", *args, "--region", os.getenv("AWS_REGION", "us-east-1"), "--output", "json"]
    result = subprocess.run(command, capture_output=True, text=True, env={**os.environ, "AWS_PAGER": ""})
    if result.returncode:
        raise RuntimeError(f"AWS {args[0]} {args[1]} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def stack_outputs(name):
    result = aws_json("cloudformation", "describe-stacks", "--stack-name", name)
    return {item["OutputKey"]: item["OutputValue"] for item in result["Stacks"][0].get("Outputs", [])}


def http_get(url, *, expect=200, json_response=True, sample_only=False):
    request = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "AnyGroup-GP2-validation/1.0"})
    try:
        response = urlopen(request, timeout=30)
    except HTTPError as exc:
        response = exc
    with response:
        status = response.getcode()
        body = response.read(1 if sample_only else -1)
    if status != expect:
        # Do not print URLs: an image URL can contain temporary signing credentials.
        raise AssertionError(f"Expected HTTP {expect}; received HTTP {status}")
    return json.loads(body) if json_response else body
