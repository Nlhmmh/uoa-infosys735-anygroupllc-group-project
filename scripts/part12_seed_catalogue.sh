#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"
REGION="${AWS_REGION:-us-east-1}"

TABLE="$(
  aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTableName'].OutputValue | [0]" \
    --output text
)"

if [[ -z "$TABLE" || "$TABLE" == "None" ]]; then
  echo "Could not discover CatalogueTableName from stack $STACK_NAME."
  exit 1
fi

echo "Seeding DynamoDB table: $TABLE"

aws dynamodb put-item --region "$REGION" --table-name "$TABLE" --item '{
  "product_id":{"S":"P1001"},
  "name":{"S":"New Zealand Honey"},
  "category":{"S":"Grocery"},
  "price":{"N":"14.99"},
  "availability":{"BOOL":true},
  "image_key":{"S":"products/P1001.jpg"}
}'

aws dynamodb put-item --region "$REGION" --table-name "$TABLE" --item '{
  "product_id":{"S":"P1002"},
  "name":{"S":"Fresh Apples"},
  "category":{"S":"Fresh Produce"},
  "price":{"N":"5.49"},
  "availability":{"BOOL":true},
  "image_key":{"S":"products/P1002.jpg"}
}'

aws dynamodb put-item --region "$REGION" --table-name "$TABLE" --item '{
  "product_id":{"S":"P1003"},
  "name":{"S":"Whole Milk"},
  "category":{"S":"Dairy"},
  "price":{"N":"4.79"},
  "availability":{"BOOL":true},
  "image_key":{"S":"products/P1003.jpg"}
}'

echo
echo "Seed complete."
aws dynamodb scan \
  --region "$REGION" \
  --table-name "$TABLE" \
  --projection-expression "product_id,#n,category,price,availability,image_key" \
  --expression-attribute-names '{"#n":"name"}'
