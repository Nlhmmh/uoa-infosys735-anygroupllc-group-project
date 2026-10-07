"""Synthetic legacy API backed by private RDS Oracle, using a read-only DB user."""
import argparse
import json
import os
import re
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import boto3
from botocore.config import Config
import oracledb

REGION = os.getenv("AWS_REGION", "us-east-1")
OWNER = os.getenv("DB_OWNER", "anygroupadmin").upper()
_secret_cache = {}
_lock = threading.Lock()


def secret(arn, refresh=False):
    with _lock:
        cached = _secret_cache.get(arn)
        if not refresh and cached and time.monotonic() - cached[0] < 60:
            return cached[1]
        client = boto3.client("secretsmanager", region_name=REGION,
                              config=Config(connect_timeout=3, read_timeout=3,
                                            retries={"max_attempts": 1}))
        value = json.loads(client.get_secret_value(SecretId=arn)["SecretString"])
        _secret_cache[arn] = (time.monotonic(), value)
        return value


def connect(admin=False):
    arn = os.environ["DB_MASTER_SECRET_ARN" if admin else "DB_APP_SECRET_ARN"]
    for attempt in range(2):
        credentials = secret(arn, refresh=bool(attempt))
        try:
            connection = oracledb.connect(
                user=credentials["username"], password=credentials["password"],
                host=os.environ["DB_HOST"], port=int(os.getenv("DB_PORT", "1521")),
                sid=os.getenv("DB_NAME", "ANYGROUP"), tcp_connect_timeout=3,
                retry_count=0)
            connection.call_timeout = 5000
            return connection
        except oracledb.DatabaseError as exc:
            if attempt or getattr(exc.args[0], "code", None) != 1017:
                raise


def seed_database():
    """Run explicitly through SSM; application requests never write or use admin credentials."""
    app = secret(os.environ["DB_APP_SECRET_ARN"], refresh=True)
    username, password = app["username"].upper(), app["password"]
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,29}", username) or not re.fullmatch(r"[a-zA-Z0-9]{20,30}", password):
        raise ValueError("Unexpected generated application credential format")
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,29}", OWNER):
        raise ValueError("Invalid database owner")
    with connect(admin=True) as connection:
        with connection.cursor() as cursor:
            for ddl in (
                "CREATE TABLE demo_orders (order_id VARCHAR2(30) PRIMARY KEY, status VARCHAR2(30) NOT NULL)",
                "CREATE TABLE demo_customers (customer_id VARCHAR2(30) PRIMARY KEY, name VARCHAR2(80), status VARCHAR2(30))",
            ):
                try:
                    cursor.execute(ddl)
                except oracledb.DatabaseError as exc:
                    if getattr(exc.args[0], "code", None) != 955:
                        raise
            for order_id, status in (("ORD-1001", "Processing"), ("ORD-1002", "Ready")):
                cursor.execute("MERGE INTO demo_orders d USING (SELECT :id order_id, :status status FROM dual) s "
                               "ON (d.order_id=s.order_id) WHEN MATCHED THEN UPDATE SET d.status=s.status "
                               "WHEN NOT MATCHED THEN INSERT (order_id,status) VALUES (s.order_id,s.status)",
                               id=order_id, status=status)
            cursor.execute("MERGE INTO demo_customers d USING (SELECT 'CUST-1001' customer_id FROM dual) s "
                           "ON (d.customer_id=s.customer_id) WHEN NOT MATCHED THEN "
                           "INSERT (customer_id,name,status) VALUES ('CUST-1001','Demo Customer','Active')")
            connection.commit()
            try:
                cursor.execute(f'CREATE USER {username} IDENTIFIED BY "{password}"')
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0], "code", None) != 1920:
                    raise
                cursor.execute(f'ALTER USER {username} IDENTIFIED BY "{password}"')
            cursor.execute(f"GRANT CREATE SESSION TO {username}")
            for table in ("DEMO_ORDERS", "DEMO_CUSTOMERS"):
                cursor.execute(f"GRANT SELECT ON {OWNER}.{table} TO {username}")
    print(json.dumps({"status": "SEEDED", "engine": "oracle", "orders": 2, "customers": 1,
                      "application_access": "SELECT_ONLY"}))


def query(path):
    with connect() as connection:
        with connection.cursor() as cursor:
            if path == "/api/orders":
                cursor.execute(f"SELECT order_id, status FROM {OWNER}.demo_orders ORDER BY order_id")
                return {"orders": [{"order_id": row[0], "status": row[1]} for row in cursor.fetchall()]}
            if path == "/api/account":
                cursor.execute(f"SELECT name, status FROM {OWNER}.demo_customers WHERE customer_id=:id", id="CUST-1001")
                row = cursor.fetchone()
                if row is None:
                    raise ValueError("Seed customer missing")
                return {"customer": {"name": row[0], "status": row[1]}}
            cursor.execute("SELECT 1 FROM dual")
            accessible = cursor.fetchone()[0] == 1
            cursor.execute(f"SELECT COUNT(*) FROM {OWNER}.demo_orders")
            return {"database_tier": "RDS_ORACLE_MULTI_AZ", "database_accessible": accessible,
                    "seed_order_count": cursor.fetchone()[0], "application_access": "SELECT_ONLY"}


def metadata(path):
    try:
        root = "http://169.254.169.254/latest/"
        request = urllib.request.Request(root + "api/token", method="PUT",
                                         headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"})
        token = urllib.request.urlopen(request, timeout=1).read().decode()
        request = urllib.request.Request(root + "meta-data/" + path, headers={"X-aws-ec2-metadata-token": token})
        return urllib.request.urlopen(request, timeout=1).read().decode()
    except Exception:
        return "unknown"


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        base = {"service": "legacy-backend", **self.server.identity}
        if self.path == "/api/health":
            self.send_json({**base, "status": "healthy"})
        elif self.path in {"/api/db", "/api/orders", "/api/account"}:
            try:
                self.send_json({**base, **query(self.path)})
            except Exception:
                # Never send/log driver exception text: it can contain sensitive connection details.
                self.send_json({**base, "error": "database_unavailable"}, 503)
        else:
            self.send_json({"error": "not_found"}, 404)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-db", action="store_true")
    args = parser.parse_args()
    if args.seed_db:
        try:
            seed_database()
        except Exception:
            print(json.dumps({"status": "FAIL", "error": "Database seed failed; check RDS, secrets permissions and connectivity"}))
            return 1
        return 0
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,29}", OWNER):
        raise ValueError("Invalid database owner")
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    server.identity = {"instance_id": metadata("instance-id"), "availability_zone": metadata("placement/availability-zone")}
    server.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
