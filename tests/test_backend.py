import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("legacy_backend", ROOT / "backend-service" / "app.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class BackendTests(unittest.TestCase):
    def test_database_errors_return_503_without_credentials(self):
        handler = object.__new__(backend.Handler)
        handler.server = SimpleNamespace(identity={"instance_id": "i-test"})
        handler.path = "/api/orders"
        handler.send_json = MagicMock()
        with patch.object(backend, "query", side_effect=RuntimeError("secret_password_should_not_escape")):
            handler.do_GET()
        body, status = handler.send_json.call_args.args
        self.assertEqual(status, 503)
        self.assertEqual(body["error"], "database_unavailable")
        self.assertNotIn("secret_password", str(body))

    def test_orders_are_fetched_from_read_only_database_connection(self):
        connection = MagicMock()
        cursor = connection.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [("ORD-FROM-DB", "Ready")]
        with patch.object(backend, "connect", return_value=connection) as connect:
            result = backend.query("/api/orders")
        connect.assert_called_once_with()
        self.assertEqual(result["orders"], [{"order_id": "ORD-FROM-DB", "status": "Ready"}])

    def test_rotation_refreshes_credentials_once_on_invalid_password(self):
        invalid = backend.oracledb.DatabaseError(SimpleNamespace(code=1017))
        connection = MagicMock()
        with patch.dict(backend.os.environ, {"DB_APP_SECRET_ARN": "app-arn", "DB_HOST": "private-rds"}), \
             patch.object(backend, "secret", return_value={"username": "app", "password": "notprinted"}) as secret, \
             patch.object(backend.oracledb, "connect", side_effect=[invalid, connection]) as connect:
            self.assertIs(backend.connect(), connection)
        self.assertEqual([c.kwargs["refresh"] for c in secret.call_args_list], [False, True])
        self.assertTrue(all(c.kwargs["user"] == "app" for c in connect.call_args_list))

    def test_seed_rejects_unexpected_credentials_before_database_mutation(self):
        with patch.dict(backend.os.environ, {"DB_APP_SECRET_ARN": "app-arn"}), \
             patch.object(backend, "secret", return_value={"username": "app;DROP", "password": "A" * 24}), \
             patch.object(backend, "connect") as connect:
            with self.assertRaises(ValueError):
                backend.seed_database()
            connect.assert_not_called()
