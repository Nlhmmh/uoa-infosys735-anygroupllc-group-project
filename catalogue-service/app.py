import logging
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("catalogue")

TABLE_NAME = os.environ["CATALOGUE_TABLE"]
IMAGE_BUCKET = os.environ["IMAGE_BUCKET"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")


def normalise(value):
    """Convert DynamoDB Decimal values into JSON-safe Python types."""
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    if isinstance(value, list):
        return [normalise(item) for item in value]
    if isinstance(value, dict):
        return {key: normalise(item) for key, item in value.items()}
    return value


def get_product(product_id):
    response = table.get_item(Key={"product_id": product_id})
    return response.get("Item")


@app.get("/catalogue")
@app.get("/catalogue/health")
def health():
    return jsonify(
        {
            "service": "catalogue-microservice",
            "status": "healthy",
            "table": TABLE_NAME,
            "image_bucket": IMAGE_BUCKET,
        }
    )


@app.get("/catalogue/products")
def list_products():
    response = table.scan()
    items = sorted(response.get("Items", []), key=lambda item: item["product_id"])

    # The seed dataset is intentionally tiny. A production catalogue would use
    # query/index/pagination patterns rather than an unrestricted table scan.
    logger.info("catalogue_list count=%s", len(items))
    return jsonify({"service": "catalogue-microservice", "products": normalise(items)})


@app.get("/catalogue/products/<product_id>")
def product(product_id):
    item = get_product(product_id)
    if not item:
        return jsonify({"error": "product_not_found", "product_id": product_id}), 404

    logger.info("catalogue_get product_id=%s", product_id)
    return jsonify({"service": "catalogue-microservice", "product": normalise(item)})


@app.get("/catalogue/products/<product_id>/image-url")
def product_image_url(product_id):
    item = get_product(product_id)
    if not item:
        return jsonify({"error": "product_not_found", "product_id": product_id}), 404

    image_key = item.get("image_key")
    if not image_key:
        return jsonify({"error": "image_key_missing", "product_id": product_id}), 404

    try:
        s3.head_object(Bucket=IMAGE_BUCKET, Key=image_key)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        logger.warning(
            "image_lookup_failed product_id=%s key=%s code=%s",
            product_id,
            image_key,
            code,
        )
        return (
            jsonify(
                {
                    "error": "image_not_available",
                    "product_id": product_id,
                    "image_key": image_key,
                }
            ),
            404,
        )

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": IMAGE_BUCKET, "Key": image_key},
        ExpiresIn=300,
    )
    logger.info("image_url_generated product_id=%s key=%s", product_id, image_key)
    return jsonify(
        {
            "product_id": product_id,
            "image_key": image_key,
            "expires_in_seconds": 300,
            "image_url": url,
        }
    )


@app.errorhandler(Exception)
def unhandled_error(exc):
    logger.exception("unhandled_error")
    return jsonify({"error": "internal_server_error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
