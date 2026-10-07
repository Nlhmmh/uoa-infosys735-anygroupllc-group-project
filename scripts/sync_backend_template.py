#!/usr/bin/env python3
"""Embed application sources in EC2 user data; never embed database passwords."""
import argparse
import base64
import gzip
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


class Dumper(yaml.SafeDumper):
    pass


def string(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|" if "\n" in value else None)


Dumper.add_representer(str, string)


def generate(check=False):
    path = ROOT / "cloudformation" / "02-core-infrastructure-stack.yaml"
    template = yaml.safe_load(path.read_text())
    source = (ROOT / "backend-service" / "app.py").read_text()
    requirements = (ROOT / "backend-service" / "requirements.txt").read_text()
    script = """#!/bin/bash
set -euo pipefail
dnf install -y aws-cfn-bootstrap python3-pip
trap '/opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource BackendAutoScalingGroup --region ${AWS::Region}' EXIT
python3 -m venv /opt/anygroup-backend-venv
cat > /opt/anygroup-backend-requirements.txt <<'REQ'
""" + requirements + """REQ
/opt/anygroup-backend-venv/bin/pip install -r /opt/anygroup-backend-requirements.txt
cat > /opt/anygroup_backend.py <<'PY'
""" + source + """PY
cat > /etc/anygroup-backend.env <<'ENV'
AWS_REGION=${AWS::Region}
DB_HOST=${OracleDatabase.Endpoint.Address}
DB_PORT=${OracleDatabase.Endpoint.Port}
DB_NAME=${DbName}
DB_OWNER=${DbMasterUsername}
DB_MASTER_SECRET_ARN=${OracleDatabase.MasterUserSecret.SecretArn}
DB_APP_SECRET_ARN=${BackendDbCredentials}
ENV
chmod 600 /etc/anygroup-backend.env
cat > /etc/systemd/system/anygroup-backend.service <<'UNIT'
[Unit]
Description=AnyGroupLLC RDS-backed Legacy Demo API
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
EnvironmentFile=/etc/anygroup-backend.env
ExecStart=/opt/anygroup-backend-venv/bin/python /opt/anygroup_backend.py
Restart=always
RestartSec=2
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now anygroup-backend.service
curl -fsS --retry 20 --retry-delay 2 --retry-connrefused http://127.0.0.1:8080/api/health
"""
    data = {"Fn::Base64": {"Fn::Sub": script}}
    target = template["Resources"]["BackendLaunchTemplate"]["Properties"]["LaunchTemplateData"]
    if check:
        if target["UserData"] != data:
            raise ValueError("Backend source and template differ; run scripts/sync_backend_template.py")
    else:
        target["UserData"] = data
    # Compress storefront HTML to keep the direct-deployment template below 51,200 bytes.
    # Runtime identity placeholders are replaced on the frontend, not in the source HTML.
    html = (ROOT / "frontend" / "index.html").read_bytes()
    encoded = base64.b64encode(gzip.compress(html, mtime=0)).decode()
    frontend = template["Resources"]["FrontendLaunchTemplate"]["Properties"]["LaunchTemplateData"]["UserData"]["Fn::Base64"]["Fn::Sub"]
    fragment = "# FRONTEND_HTML_START\nbase64 -d <<'HTML_GZIP' | gzip -dc > /var/www/html/index.html\n" + encoded + "\nHTML_GZIP\nsed \"s/__INSTANCE_ID__/$INSTANCE_ID/g; s/__AZ__/$AZ/g\" /var/www/html/index.html > /var/www/html/index.tmp\nmv /var/www/html/index.tmp /var/www/html/index.html\n# FRONTEND_HTML_END"
    rendered, count = re.subn(r"# FRONTEND_HTML_START\n.*?# FRONTEND_HTML_END", lambda match: fragment, frontend[0], flags=re.S)
    if count != 1:
        raise ValueError("Expected one frontend HTML marker pair in user data")
    if check:
        if rendered != frontend[0]:
            raise ValueError("Frontend source and template differ; run scripts/sync_backend_template.py")
    else:
        frontend[0] = rendered
        path.write_text(yaml.dump(template, Dumper=Dumper, sort_keys=False, width=120))
    # The readable YAML exceeds the inline AWS limit; the equivalent JSON fits without a staging bucket.
    compact = json.dumps(template, separators=(",", ":")) + "\n"
    if len(compact.encode()) > 51200:
        raise ValueError("Compact core template exceeds AWS's 51,200-byte direct template limit")
    deployment = path.with_suffix(".template.json")
    if check:
        if not deployment.exists() or deployment.read_text() != compact:
            raise ValueError("Compact deployment template is stale; run scripts/sync_backend_template.py")
    else:
        deployment.write_text(compact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(parser.parse_args().check)
