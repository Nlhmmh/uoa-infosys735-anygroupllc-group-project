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
import ast
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import gzip
import json
import re
import shutil
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path.cwd()

STACK_FILES = {
    "network": ROOT / "cloudformation" / "01-network-stack.yaml",
    "core": ROOT / "cloudformation" / "02-core-infrastructure-stack.template.json",
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
    parser.add_argument("--require-lint", action="store_true", help="Fail if cfn-lint is unavailable")
    parser.add_argument("--tests", action="store_true", help="Run local regression tests with mocked AWS")
    parser.add_argument("--write-report", action="store_true", help="Refresh the static report with current source hashes")
    args = parser.parse_args()

    failed = False
    templates = {}
    aws_validation_results = {}

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
            if path.stat().st_size > 51200:
                raise ValueError("Template exceeds the 51,200-byte direct AWS template-body limit")
            count = len(template.get("Resources") or {})
            print(f"PASS {key}: YAML parsed; {count} declared resources")
        except Exception as exc:
            print(f"FAIL {key}: {exc}")
            failed = True

    if failed:
        if args.write_report:
            (ROOT/"data"/"part13_static_validation_report.json").write_text(json.dumps({"status": "FAIL", "aws_runtime_validation": "NOT_PERFORMED"}, indent=2) + "\n")
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
        ROOT / "backend-service" / "app.py",
        ROOT / "backend-service" / "requirements.txt",
        ROOT / "frontend" / "index.html",
        ROOT / "cloudformation" / "02-core-infrastructure-stack.yaml",
        ROOT / "scripts" / "lab.sh",
        ROOT / "scripts" / "part15_seed_database.py",
        ROOT / "scripts" / "part12_build_push.sh",
        ROOT / "scripts" / "part12_seed_catalogue.sh",
        ROOT / "scripts" / "part12_test_catalogue.sh",
        ROOT / "scripts" / "part12_test_catalogue.py",
        ROOT / "scripts" / "lab_support.py",
        ROOT / "scripts" / "part14_collect_evidence.py",
        ROOT / "scripts" / "part14_probe_availability.py",
        ROOT / "IaC_Deployment_and_Usage_Instructions.md",
        ROOT / "Presentation_and_Slide_Content.md",
        ROOT / "Rubric_and_Assessment_Checklist.md",
        ROOT / "data" / "cost_model_inputs.json",
    ]
    for path in support:
        if path.exists():
            print(f"PASS artefact: {path.relative_to(ROOT)}")
        else:
            print(f"FAIL artefact: {path.relative_to(ROOT)} missing")
            failed = True

    for path in sorted((ROOT/"scripts").glob("*.py")) + [ROOT/"catalogue-service"/"app.py", ROOT/"backend-service"/"app.py"] + sorted((ROOT/"tests").glob("*.py")):
        try:
            ast.parse(path.read_text())
            print(f"PASS Python syntax: {path.relative_to(ROOT)}")
        except SyntaxError as exc:
            print(f"FAIL Python syntax: {path.relative_to(ROOT)}: {exc}")
            failed = True
    for path in sorted((ROOT/"scripts").glob("*.sh")):
        result = subprocess.run(["bash", "-n", str(path)])
        print(f"{'PASS' if result.returncode == 0 else 'FAIL'} shell syntax: {path.relative_to(ROOT)}")
        failed |= result.returncode != 0

    javascript_checked = False
    for stack, template in templates.items():
        for name, resource in template["Resources"].items():
            props = resource.get("Properties", {})
            data = props.get("UserData", props.get("LaunchTemplateData", {}).get("UserData", {})).get("Fn::Base64")
            if isinstance(data, dict):
                data = data["Fn::Sub"]
                data = data[0] if isinstance(data, list) else data
            if not isinstance(data, str):
                continue
            if resource["Type"] == "AWS::EC2::LaunchTemplate" and re.search(r"(?<!\\)\$\{![^}]+\}", data):
                print(f"FAIL launch-template literal escaping: {name}")
                failed = True
            data = data.replace("${AWS::StackName}", STACK_NAMES[stack]).replace("${AWS::Region}", args.region)
            for variable, value in (("PrimaryDbIp", "10.0.20.10"), ("StandbyDbIp", "10.0.21.10"), ("InternalAlbDns", "internal-alb.example.invalid"), ("VpcCidr", "10.0.0.0/16")):
                data = data.replace("${" + variable + "}", value)
            if len(data.encode()) > 16384:
                print(f"FAIL UserData raw size exceeds 16 KiB: {name}")
                failed = True
            result = subprocess.run(["bash", "-n"], input=data, text=True)
            failed |= result.returncode != 0
            print(f"{'PASS' if result.returncode == 0 else 'FAIL'} UserData shell syntax: {name}")
            for match in re.finditer(r"cat > [^\n]+ <<'PY'\n(.*?)\nPY", data, re.S):
                try:
                    ast.parse(match.group(1))
                    print(f"PASS embedded Python: {name}")
                except SyntaxError as exc:
                    print(f"FAIL embedded Python: {name}: {exc}")
                    failed = True
            compressed = re.search(r"base64 -d <<'HTML_GZIP'[^\n]*\n([A-Za-z0-9+/=\n]+)\nHTML_GZIP", data)
            if compressed or "<script>" in data:
                if compressed:
                    html = gzip.decompress(base64.b64decode(compressed.group(1))).decode()
                    rendered = html.replace("__INSTANCE_ID__", "i-local").replace("__AZ__", "us-east-1a")
                else:
                    html = re.search(r"cat > /var/www/html/index.html <<EOF\n(.*?)\nEOF", data, re.S).group(1)
                    rendered = subprocess.run(["bash", "-c", "INSTANCE_ID=i-local; AZ=us-east-1a; cat <<EOF\n" + html + "\nEOF"], capture_output=True, text=True, check=True).stdout
                if "$(" in html or "`" in html:
                    print("FAIL HTML heredoc contains command substitution; cannot safely render locally")
                    failed = True
                    continue
                js = rendered.split("<script>", 1)[1].split("</script>", 1)[0]
                node = shutil.which("node")
                if node:
                    with tempfile.TemporaryDirectory() as tmp:
                        source = Path(tmp)/"storefront.js"
                        source.write_text(js)
                        result = subprocess.run([node, "--check", str(source)])
                        failed |= result.returncode != 0
                        javascript_checked = result.returncode == 0
                        print(f"{'PASS' if javascript_checked else 'FAIL'} rendered storefront JavaScript")
                else:
                    print("SKIP rendered JavaScript syntax: Node.js unavailable")

    lint = shutil.which("cfn-lint") or str(Path(sys.executable).parent / "cfn-lint")
    lint_status = "NOT_AVAILABLE"
    if Path(lint).exists():
        result = subprocess.run([lint, "--region", args.region, "--template", *map(str, STACK_FILES.values())])
        lint_status = "PASS" if result.returncode == 0 else "FAIL"
        failed |= result.returncode != 0
        print(f"{lint_status} CloudFormation schema/lint checks")
    elif args.require_lint:
        print("FAIL cfn-lint unavailable; install requirements-validation.txt")
        failed = True
    else:
        print("SKIP CloudFormation schema/lint checks: install requirements-validation.txt")

    regression_status, regression_count = "NOT_RUN", None
    result = subprocess.run([sys.executable, str(ROOT/"scripts"/"sync_security_reference.py"), "--check"])
    failed |= result.returncode != 0
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'} current security reference consistency")
    result = subprocess.run([sys.executable, str(ROOT/"scripts"/"sync_backend_template.py"), "--check"])
    failed |= result.returncode != 0
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'} application sources/embedded user data/compact template consistency")
    if args.tests:
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT/"tests"), "-v"], capture_output=True, text=True)
        print(result.stdout + result.stderr)
        regression_status = "PASS" if result.returncode == 0 else "FAIL"
        failed |= result.returncode != 0
        match = re.search(r"Ran (\d+) tests", result.stderr)
        regression_count = int(match.group(1)) if match else None

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
                aws_validation_results[key] = "PASS"
                print(f"PASS AWS validate-template: {key}")
            else:
                aws_validation_results[key] = "FAIL"
                print(f"FAIL AWS validate-template: {key}")
                print(result.stderr.strip())
                failed = True

    if args.write_report:
        source_paths = sorted(set(list(STACK_FILES.values()) + sorted((ROOT/"scripts").glob("*.py")) + sorted((ROOT/"scripts").glob("*.sh")) + sorted((ROOT/"tests").glob("*.py")) + support + [ROOT/"requirements-validation.txt", ROOT/"catalogue-service"/".dockerignore"]))
        report = {
            "status": "FAIL" if failed else "LOCAL_STATIC_VALIDATION_COMPLETE",
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            "aws_runtime_validation": "NOT_PERFORMED",
            "aws_template_validation": aws_validation_results or "NOT_PERFORMED",
            "baseline_ec2_count": 4, "frontend_peak_ec2_count": 6,
            "nat_gateway_count": 2, "rds": "Oracle SE2 License Included Multi-AZ, 20 GiB gp2",
            "resource_counts": {STACK_FILES[k].name: len(t["Resources"]) for k,t in templates.items()},
            "total_declared_resources": sum(len(t["Resources"]) for t in templates.values()),
            "matched_imports": len(imports) - len(unmatched), "unmatched_imports": unmatched,
            "cloudformation_lint": lint_status, "rendered_javascript": "PASS" if javascript_checked else "NOT_VERIFIED",
            "regression_tests": regression_status, "regression_test_count": regression_count,
            "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        }
        (ROOT/"data"/"part13_static_validation_report.json").write_text(json.dumps(report, indent=2) + "\n")

    if failed:
        print("\nRESULT: FAIL")
        raise SystemExit(1)

    print("\nRESULT: PASS (static/local checks only unless --aws was used)")


if __name__ == "__main__":
    main()
