"""Single-user Oracle password rotation for the configured application secret only."""
import json
import os
import re

import boto3
from botocore.config import Config
import oracledb


def credentials(client, arn, stage, token=None):
    request = {"SecretId": arn, "VersionStage": stage}
    if token:
        request["VersionId"] = token
    value = json.loads(client.get_secret_value(**request)["SecretString"])
    if (value.get("username", "").lower() != "anygroupapp"
            or not re.fullmatch(r"[A-Za-z0-9]{20,30}", value.get("password", ""))):
        raise ValueError("Unexpected application credential format")
    return value


def connect(value):
    # Connection targets come from CloudFormation, never from an incoming event/secret.
    connection = oracledb.connect(
        user=value["username"], password=value["password"],
        host=os.environ["DB_HOST"], port=int(os.environ["DB_PORT"]),
        sid=os.environ["DB_NAME"], tcp_connect_timeout=5, retry_count=0)
    connection.call_timeout = 5000
    return connection


def try_connect(value):
    try:
        return connect(value)
    except oracledb.DatabaseError as exc:
        # A network outage must not be treated as an invalid password.
        if getattr(exc.args[0], "code", None) != 1017:
            raise
        return None


def test_pending(client, arn, token):
    owner = os.environ["DB_OWNER"].upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,29}", owner):
        raise ValueError("Unexpected database owner")
    with connect(credentials(client, arn, "AWSPENDING", token)) as connection:
        with connection.cursor() as cursor:
            for table in ("DEMO_ORDERS", "DEMO_CUSTOMERS"):
                cursor.execute(f"SELECT COUNT(*) FROM {owner}.{table}")
                if cursor.fetchone()[0] < 1:
                    raise ValueError("Seeded application data is missing")


def lambda_handler(event, context):
    arn, token, step = (event.get(name) for name in ("SecretId", "ClientRequestToken", "Step"))
    if arn != os.environ["APP_SECRET_ARN"]:
        raise ValueError("Rotation is restricted to the configured application secret")
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9-]{32,64}", token):
        raise ValueError("Invalid rotation token")
    if step not in {"createSecret", "setSecret", "testSecret", "finishSecret"}:
        raise ValueError("Invalid rotation step")
    client = boto3.client("secretsmanager", config=Config(
        connect_timeout=5, read_timeout=10, retries={"max_attempts": 2}))
    metadata = client.describe_secret(SecretId=arn)
    if not metadata.get("RotationEnabled"):
        raise ValueError("Rotation is not enabled")
    stages = metadata.get("VersionIdsToStages", {})
    if token not in stages:
        raise ValueError("Unknown rotation version")
    if "AWSCURRENT" in stages[token]:
        return
    if "AWSPENDING" not in stages[token]:
        raise ValueError("Rotation version is not pending")

    if step == "createSecret":
        current = credentials(client, arn, "AWSCURRENT")
        try:
            credentials(client, arn, "AWSPENDING", token)
        except client.exceptions.ResourceNotFoundException:
            current["password"] = client.get_random_password(
                PasswordLength=24, ExcludePunctuation=True,
                RequireEachIncludedType=True)["RandomPassword"]
            if not re.fullmatch(r"[A-Za-z0-9]{24}", current["password"]):
                raise ValueError("Unexpected generated password format")
            client.put_secret_value(SecretId=arn, ClientRequestToken=token,
                                    SecretString=json.dumps(current), VersionStages=["AWSPENDING"])
    elif step == "setSecret":
        pending = credentials(client, arn, "AWSPENDING", token)
        connection = try_connect(pending)
        if connection is not None:
            connection.close()  # A retried step must not change the password twice.
            return
        current = credentials(client, arn, "AWSCURRENT")
        connection = try_connect(current)
        if connection is None:
            try:
                current = credentials(client, arn, "AWSPREVIOUS")
            except client.exceptions.ResourceNotFoundException:
                raise ValueError("No working application credentials") from None
            connection = try_connect(current)
        if connection is None:
            raise ValueError("No working application credentials")
        with connection:
            # Thin-mode password change affects this user's own password; no admin secret.
            connection.changepassword(current["password"], pending["password"])
    elif step == "testSecret":
        test_pending(client, arn, token)
    else:
        # Recheck actual SELECT access before promoting the pending version.
        test_pending(client, arn, token)
        current_version = next((v for v, labels in stages.items() if "AWSCURRENT" in labels), None)
        if current_version is None:
            raise ValueError("Current credential version is missing")
        client.update_secret_version_stage(SecretId=arn, VersionStage="AWSCURRENT",
                                          MoveToVersionId=token, RemoveFromVersionId=current_version)
