#!/usr/bin/env python3
"""
INFOSYS 735 GP2 Part 13 - local/static CloudFormation validation.

This validator does NOT claim AWS deployment validation.
It checks:
  - all four expected YAML templates parse;
  - declared resource counts/types;
  - cross-stack Export/ImportValue name compatibility using the project defaults;
  - dependency graph acyclicity;
  - key supporting artefacts;
  - optional Python/shell syntax.

Run from the project repository root:
    python scripts/part13_validate_iac.py

Optional AWS-side template validation (requires AWS CLI credentials):
    python scripts/part13_validate_iac.py --aws --region us-east-1
"""

from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path.cwd()

STACK_FILES = {
    "network": ROOT / "cloudformation" / "01-network-stack.yaml",
    "core": ROOT / "cloudformation" / "02-core-infrastructure-stack.yaml",
    "observability": ROOT / "cloudformation" / "03-observability-stack.yaml",
    "microservice": ROOT / "cloudformation" / "04-microservice-stack.yaml",
}

STACK_NAMES = {
    "network": "anygroup-gp2-network",
    "core": "anygroup-gp2-core",
    "observability": "anygroup-gp2-observability",
    "microservice": "anygroup-gp2-microservice",
}


def walk(obj, fn, path="$"):
    fn(obj, path)
    if isinstance(obj, dict):
        for key, value in obj.items():
            walk(value, fn, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            walk(value, fn, f"{path}[{i}]")


def default_param(template, name):
    return (template.get("Parameters", {}).get(name, {}) or {}).get("Default")


def render_sub(text, stack_key, template):
    replacements = {
        "AWS::StackName": STACK_NAMES[stack_key],
        "NetworkStackName": default_param(template, "NetworkStackName") or STACK_NAMES["network"],
        "CoreStackName": default_param(template, "CoreStackName") or STACK_NAMES["core"],
        "ObservabilityStackName": default_param(template, "ObservabilityStackName") or STACK_NAMES["observability"],
        "EnvironmentName": default_param(template, "EnvironmentName") or "anygroup-gp2",
    }
    out = text
    for key, value in replacements.items():
        out = out.replace("${" + key + "}", str(value))
    return out


def resolve_sub(expr, stack_key, template):
    if isinstance(expr, str):
        return render_sub(expr, stack_key, template)
    if isinstance(expr, dict) and "Fn::Sub" in expr:
        val = expr["Fn::Sub"]
        if isinstance(val, str):
            return render_sub(val, stack_key, template)
        if isinstance(val, list) and val and isinstance(val[0], str):
            return render_sub(val[0], stack_key, template)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", action="store_true", help="Also call aws cloudformation validate-template")
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    failed = False
    templates = {}

    print("Part 13 local IaC validation")
    print("=" * 30)

    for key, path in STACK_FILES.items():
        if not path.exists():
            print(f"FAIL {key}: missing {path}")
            failed = True
            continue
        try:
            template = yaml.safe_load(path.read_text(encoding="utf-8"))
            templates[key] = template
            count = len(template.get("Resources") or {})
            print(f"PASS {key}: YAML parsed; {count} declared resources")
        except Exception as exc:
            print(f"FAIL {key}: {exc}")
            failed = True

    if failed:
        raise SystemExit(1)

    exports = {}
    for key, template in templates.items():
        for output_key, output in (template.get("Outputs") or {}).items():
            exp = output.get("Export") if isinstance(output, dict) else None
            if not exp:
                continue
            resolved = resolve_sub(exp.get("Name"), key, template)
            if resolved:
                exports[resolved] = (key, output_key)

    imports = []
    for key, template in templates.items():
        def finder(obj, path):
            if isinstance(obj, dict) and "Fn::ImportValue" in obj:
                resolved = resolve_sub(obj["Fn::ImportValue"], key, template)
                imports.append((key, path, resolved))
        walk(template, finder)

    unmatched = []
    edges = set()
    for consumer, path, name in imports:
        if name in exports:
            provider, output_key = exports[name]
            if provider != consumer:
                edges.add((provider, consumer))
            print(f"PASS import: {consumer} <- {name} ({provider}.{output_key})")
        else:
            unmatched.append((consumer, path, name))
            print(f"FAIL import: {consumer} <- {name} at {path}")

    if unmatched:
        failed = True

    incoming = {k: set() for k in templates}
    outgoing = {k: set() for k in templates}
    for provider, consumer in edges:
        incoming[consumer].add(provider)
        outgoing[provider].add(consumer)

    queue = sorted(k for k in templates if not incoming[k])
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for nxt in sorted(outgoing[node]):
            incoming[nxt].discard(node)
            if not incoming[nxt] and nxt not in queue and nxt not in order:
                queue.append(nxt)
        queue.sort()

    if len(order) != len(templates):
        print("FAIL dependency graph: cycle detected")
        failed = True
    else:
        print("PASS dependency graph:", " -> ".join(order))

    support = [
        ROOT / "catalogue-service" / "app.py",
        ROOT / "catalogue-service" / "Dockerfile",
        ROOT / "catalogue-service" / "requirements.txt",
        ROOT / "scripts" / "part12_build_push.sh",
        ROOT / "scripts" / "part12_seed_catalogue.sh",
        ROOT / "scripts" / "part12_test_catalogue.sh",
    ]
    for path in support:
        if path.exists():
            print(f"PASS artefact: {path.relative_to(ROOT)}")
        else:
            print(f"FAIL artefact: {path.relative_to(ROOT)} missing")
            failed = True

    for path in [ROOT/"catalogue-service"/"app.py"]:
        if path.exists():
            result = subprocess.run([sys.executable, "-m", "py_compile", str(path)])
            if result.returncode == 0:
                print(f"PASS Python syntax: {path.relative_to(ROOT)}")
            else:
                failed = True

    for path in [
        ROOT/"scripts"/"part12_build_push.sh",
        ROOT/"scripts"/"part12_seed_catalogue.sh",
        ROOT/"scripts"/"part12_test_catalogue.sh",
    ]:
        if path.exists():
            result = subprocess.run(["bash", "-n", str(path)])
            if result.returncode == 0:
                print(f"PASS shell syntax: {path.relative_to(ROOT)}")
            else:
                failed = True

    if args.aws:
        for key, path in STACK_FILES.items():
            result = subprocess.run(
                [
                    "aws", "cloudformation", "validate-template",
                    "--template-body", f"file://{path}",
                    "--region", args.region,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"PASS AWS validate-template: {key}")
            else:
                print(f"FAIL AWS validate-template: {key}")
                print(result.stderr.strip())
                failed = True

    if failed:
        print("\nRESULT: FAIL")
        raise SystemExit(1)

    print("\nRESULT: PASS (static/local checks only unless --aws was used)")


if __name__ == "__main__":
    main()
