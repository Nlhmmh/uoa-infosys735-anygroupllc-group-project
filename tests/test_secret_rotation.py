import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("application_rotation", ROOT / "rotation-service/app.py")
rotation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rotation)
sys.path.insert(0, str(ROOT / "scripts"))
import part16_test_secret_rotation as tool
import part15_seed_database as seed_tool

TOKEN, CURRENT, ARN = "a" * 64, "b" * 64, "arn:aws:secretsmanager:us-east-1:123456789012:secret:app"
CURRENT_VALUE = {"username": "anygroupapp", "password": "A" * 24}
PENDING_VALUE = {"username": "anygroupapp", "password": "B" * 24}


class MissingSecret(Exception):
    pass


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"APP_SECRET_ARN": ARN, "DB_HOST": "private-db",
            "DB_PORT": "1521", "DB_NAME": "ANYGROUP", "DB_OWNER": "anygroupadmin"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client = MagicMock()
        self.client.exceptions.ResourceNotFoundException = MissingSecret
        self.client.describe_secret.return_value = {"RotationEnabled": True,
            "VersionIdsToStages": {CURRENT: ["AWSCURRENT"], TOKEN: ["AWSPENDING"]}}
        self.client.get_secret_value.side_effect = lambda **kw: {"SecretString": json.dumps(
            PENDING_VALUE if kw["VersionStage"] == "AWSPENDING" else CURRENT_VALUE)}
        self.factory = patch.object(rotation.boto3, "client", return_value=self.client)
        self.factory.start()
        self.addCleanup(self.factory.stop)

    def invoke(self, step, **override):
        return rotation.lambda_handler({"SecretId": ARN, "ClientRequestToken": TOKEN,
                                        "Step": step, **override}, None)

    def test_rejects_another_secret_before_any_aws_access(self):
        with self.assertRaises(ValueError):
            self.invoke("setSecret", SecretId="other-secret")
        self.client.describe_secret.assert_not_called()

    def test_requires_pending_version_and_enabled_rotation(self):
        for metadata in ({"RotationEnabled": False}, {"RotationEnabled": True,
                "VersionIdsToStages": {TOKEN: ["AWSPREVIOUS"]}}):
            self.client.describe_secret.return_value = metadata
            with self.assertRaises(ValueError):
                self.invoke("setSecret")
        self.client.get_secret_value.assert_not_called()

    def test_completed_step_is_idempotent(self):
        self.client.describe_secret.return_value["VersionIdsToStages"][TOKEN] = ["AWSCURRENT"]
        self.invoke("setSecret")
        self.client.get_secret_value.assert_not_called()

    def test_create_does_not_replace_an_existing_pending_password(self):
        self.invoke("createSecret")
        self.client.put_secret_value.assert_not_called()
        self.client.get_random_password.assert_not_called()

    def test_create_generates_and_stages_a_new_version(self):
        self.client.get_secret_value.side_effect = [{"SecretString": json.dumps(CURRENT_VALUE)}, MissingSecret()]
        self.client.get_random_password.return_value = {"RandomPassword": "C" * 24}
        self.invoke("createSecret")
        call = self.client.put_secret_value.call_args.kwargs
        self.assertEqual(call["VersionStages"], ["AWSPENDING"])
        self.assertEqual(call["ClientRequestToken"], TOKEN)
        self.assertEqual(json.loads(call["SecretString"])["username"], "anygroupapp")
        self.client.update_secret_version_stage.assert_not_called()

    def test_set_changes_only_the_application_users_password(self):
        connection = MagicMock()
        connection.__enter__.return_value = connection
        with patch.object(rotation, "try_connect", side_effect=[None, connection]) as login:
            self.invoke("setSecret")
        connection.changepassword.assert_called_once_with("A" * 24, "B" * 24)
        self.assertEqual([c.args[0] for c in login.call_args_list], [PENDING_VALUE, CURRENT_VALUE])
        self.assertTrue(all(c.kwargs["VersionStage"] != "AWSPREVIOUS"
                            for c in self.client.get_secret_value.call_args_list))

    def test_retried_set_does_not_change_a_working_pending_password(self):
        connection = MagicMock()
        with patch.object(rotation, "try_connect", return_value=connection):
            self.invoke("setSecret")
        connection.close.assert_called_once()
        connection.changepassword.assert_not_called()

    def test_set_can_recover_using_the_previous_password(self):
        connection = MagicMock()
        connection.__enter__.return_value = connection
        with patch.object(rotation, "try_connect", side_effect=[None, None, connection]):
            self.invoke("setSecret")
        self.assertEqual(self.client.get_secret_value.call_args.kwargs["VersionStage"], "AWSPREVIOUS")
        connection.changepassword.assert_called_once()

    def test_network_errors_are_not_treated_as_invalid_passwords(self):
        error = rotation.oracledb.DatabaseError(SimpleNamespace(code=12541))
        with patch.object(rotation, "connect", side_effect=error):
            with self.assertRaises(rotation.oracledb.DatabaseError):
                rotation.try_connect(CURRENT_VALUE)

    def test_finish_requires_read_access_and_promotes_only_after_testing(self):
        connection = MagicMock()
        connection.__enter__.return_value = connection
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (2,)
        with patch.object(rotation, "connect", return_value=connection):
            self.invoke("finishSecret")
        self.assertEqual(cursor.execute.call_count, 2)
        self.client.update_secret_version_stage.assert_called_once_with(
            SecretId=ARN, VersionStage="AWSCURRENT", MoveToVersionId=TOKEN, RemoveFromVersionId=CURRENT)

    def test_failed_data_check_never_promotes_password(self):
        connection = MagicMock()
        connection.__enter__.return_value = connection
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = (0,)
        with patch.object(rotation, "connect", return_value=connection):
            with self.assertRaises(ValueError):
                self.invoke("finishSecret")
        self.client.update_secret_version_stage.assert_not_called()

    def test_unexpected_identity_never_reaches_oracle(self):
        self.client.get_secret_value.side_effect = None
        self.client.get_secret_value.return_value = {"SecretString": json.dumps(
            {"username": "admin", "password": "A" * 24})}
        with patch.object(rotation, "connect") as connect:
            with self.assertRaises(ValueError):
                self.invoke("setSecret")
        connect.assert_not_called()


class RotationEvidenceTests(unittest.TestCase):
    def test_seed_refuses_pending_rotation_before_database_access(self):
        with patch.object(seed_tool, "stack_outputs", return_value={"DatabaseApplicationSecretArn": ARN}), \
             patch.object(seed_tool, "aws_json", return_value={"VersionIdsToStages": {TOKEN: ["AWSPENDING"]}}) as aws:
            with self.assertRaisesRegex(RuntimeError, "pending"):
                seed_tool.seed()
        self.assertEqual(aws.call_count, 1)

    def test_changed_rows_cannot_produce_a_rotation_pass(self):
        before = {"RotationEnabled": True, "VersionIdsToStages": {CURRENT: ["AWSCURRENT"]}}
        after = {"RotationEnabled": True, "VersionIdsToStages": {TOKEN: ["AWSCURRENT"]}}
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(tool, "stack_outputs", return_value={"DatabaseApplicationSecretArn": ARN, "AlbDnsName": "alb"}), \
             patch.object(tool, "aws_json", side_effect=[before, {"VersionId": TOKEN}, after]), \
             patch.object(tool, "http_get", side_effect=[{"order": "old"}, {}, {"order": "changed"}, {}]):
            with self.assertRaisesRegex(RuntimeError, "changed"):
                tool.run(Path(directory), True, 1)
            self.assertFalse((Path(directory)/"summary.json").exists())

    def test_metadata_requires_requested_version_and_no_unfinished_pending(self):
        done = {"RotationEnabled": True, "LastRotatedDate": "date",
                "VersionIdsToStages": {TOKEN: ["AWSCURRENT"]}}
        self.assertTrue(tool.rotation_complete(done, TOKEN))
        self.assertFalse(tool.rotation_complete(done, CURRENT))
        self.assertFalse(tool.rotation_complete({**done, "RotationEnabled": False}, TOKEN))
        self.assertFalse(tool.rotation_complete({**done, "VersionIdsToStages": {
            TOKEN: ["AWSCURRENT"], CURRENT: ["AWSPENDING"]}}, TOKEN))

    def test_rotate_preserves_data_without_retrieving_secrets(self):
        before = {"RotationEnabled": True, "VersionIdsToStages": {CURRENT: ["AWSCURRENT"]}}
        after = {"RotationEnabled": True, "LastRotatedDate": "date",
                 "VersionIdsToStages": {TOKEN: ["AWSCURRENT"], CURRENT: ["AWSPREVIOUS"]}}
        responses = [before, {"VersionId": TOKEN}, after]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(tool, "stack_outputs", return_value={"DatabaseApplicationSecretArn": ARN, "AlbDnsName": "alb"}), \
             patch.object(tool, "aws_json", side_effect=responses) as aws, \
             patch.object(tool, "http_get", return_value={"record": "preserved"}):
            result = tool.run(Path(directory), True, 1)
            self.assertTrue(result["data_preserved"])
            self.assertEqual(result["promoted_version"], TOKEN)
        self.assertFalse(any("get-secret-value" in c.args for c in aws.call_args_list))

    def test_rotate_rejects_an_unfinished_rotation_before_mutation(self):
        pending = {"RotationEnabled": True, "VersionIdsToStages": {TOKEN: ["AWSPENDING"]}}
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(tool, "stack_outputs", return_value={"DatabaseApplicationSecretArn": ARN, "AlbDnsName": "alb"}), \
             patch.object(tool, "aws_json", return_value=pending) as aws:
            with self.assertRaises(RuntimeError):
                tool.run(Path(directory), True, 1)
        self.assertEqual(aws.call_count, 1)
