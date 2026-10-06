import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from decimal import Decimal

from botocore.exceptions import ClientError

APP_PATH = Path(__file__).resolve().parents[1]/"catalogue-service"/"app.py"


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.table, self.s3 = Mock(), Mock()
        database = Mock()
        database.Table.return_value = self.table
        spec = importlib.util.spec_from_file_location("catalogue_under_test", APP_PATH)
        self.app = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, {"CATALOGUE_TABLE": "test-table", "IMAGE_BUCKET": "test-images", "APP_VERSION": "v2"}), \
             patch("boto3.resource", return_value=database), patch("boto3.client", return_value=self.s3):
            spec.loader.exec_module(self.app)
        self.app.logger.disabled = True
        self.client = self.app.app.test_client()

    def test_health_is_liveness_without_dependency_calls(self):
        response = self.client.get("/catalogue/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["version"], "v2")
        self.assertEqual(response.json["check"], "process_liveness_only")
        self.table.scan.assert_not_called()
        self.s3.list_objects_v2.assert_not_called()

    def test_readiness_checks_both_dependencies(self):
        response = self.client.get("/catalogue/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["dependencies"], {"dynamodb": "accessible", "s3": "accessible"})
        self.table.scan.assert_called_once_with(Limit=1, ProjectionExpression="product_id")
        self.s3.list_objects_v2.assert_called_once()

    def test_readiness_reports_database_failure(self):
        self.table.scan.side_effect = ClientError({"Error": {"Code": "AccessDeniedException"}}, "Scan")
        response = self.client.get("/catalogue/ready")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["dependencies"]["dynamodb"], "unavailable")
        self.assertEqual(response.json["dependencies"]["s3"], "accessible")

    def test_readiness_reports_storage_failure(self):
        self.s3.list_objects_v2.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "ListObjectsV2")
        self.assertEqual(self.client.get("/catalogue/ready").status_code, 503)

    def test_paginated_catalogue_is_complete_and_sorted(self):
        self.table.scan.side_effect = [
            {"Items": [{"product_id": "P2", "price": Decimal("14.99")}], "LastEvaluatedKey": {"product_id": "P2"}},
            {"Items": [{"product_id": "P1", "stock": Decimal("3"), "nested": [Decimal("1.5")]}]},
        ]
        response = self.client.get("/catalogue/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["product_id"] for p in response.json["products"]], ["P1", "P2"])
        self.assertEqual(response.json["products"][0]["nested"], [1.5])
        self.assertEqual(response.json["products"][1]["price"], 14.99)
        self.table.scan.assert_any_call(ExclusiveStartKey={"product_id": "P2"})

    def test_missing_product_is_404(self):
        self.table.get_item.return_value = {}
        self.assertEqual(self.client.get("/catalogue/products/missing").status_code, 404)

    def test_unknown_route_keeps_404(self):
        self.assertEqual(self.client.get("/catalogue/unknown").status_code, 404)

    def test_unsupported_method_keeps_405(self):
        self.assertEqual(self.client.post("/catalogue/products").status_code, 405)

    def test_valid_image_is_checked_and_signed_for_five_minutes(self):
        self.table.get_item.return_value = {"Item": {"image_key": "products/P1001.jpg"}}
        self.s3.generate_presigned_url.return_value = "https://example.invalid/signed"
        response = self.client.get("/catalogue/products/P1001/image-url")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["expires_in_seconds"], 300)
        self.s3.head_object.assert_called_once_with(Bucket="test-images", Key="products/P1001.jpg")
        self.s3.generate_presigned_url.assert_called_once_with("get_object",
            Params={"Bucket": "test-images", "Key": "products/P1001.jpg"}, ExpiresIn=300)

    def test_missing_image_key_is_404(self):
        self.table.get_item.return_value = {"Item": {"product_id": "P1001"}}
        self.assertEqual(self.client.get("/catalogue/products/P1001/image-url").status_code, 404)
        self.s3.generate_presigned_url.assert_not_called()

    def test_missing_image_object_is_404(self):
        self.table.get_item.return_value = {"Item": {"image_key": "missing"}}
        self.s3.head_object.side_effect = ClientError({"Error": {"Code": "404"}}, "HeadObject")
        self.assertEqual(self.client.get("/catalogue/products/P1001/image-url").status_code, 404)

    def test_storage_access_denial_is_503_not_missing_product(self):
        self.table.get_item.return_value = {"Item": {"image_key": "exists"}}
        self.s3.head_object.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "HeadObject")
        response = self.client.get("/catalogue/products/P1001/image-url")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["error"], "image_storage_unavailable")

    def test_unhandled_aws_failure_is_503(self):
        self.table.get_item.side_effect = ClientError({"Error": {"Code": "ProvisionedThroughputExceededException"}}, "GetItem")
        self.assertEqual(self.client.get("/catalogue/products/P1001").status_code, 503)

    def test_unexpected_failure_does_not_disclose_details(self):
        self.table.get_item.side_effect = RuntimeError("private diagnostic content")
        response = self.client.get("/catalogue/products/P1001")
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("private diagnostic", response.get_data(as_text=True))
