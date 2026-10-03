#!/usr/bin/env bash
set -euo pipefail

CORE_STACK="${CORE_STACK_NAME:-anygroup-gp2-core}"
MICRO_STACK="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"
REGION="${AWS_REGION:-us-east-1}"

ALB_DNS="$(
  aws cloudformation describe-stacks \
    --stack-name "$CORE_STACK" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" \
    --output text
)"

CLUSTER="$(
  aws cloudformation describe-stacks \
    --stack-name "$MICRO_STACK" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueClusterName'].OutputValue | [0]" \
    --output text
)"

SERVICE="$(
  aws cloudformation describe-stacks \
    --stack-name "$MICRO_STACK" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueServiceName'].OutputValue | [0]" \
    --output text
)"

TG_ARN="$(
  aws cloudformation describe-stacks \
    --stack-name "$MICRO_STACK" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTargetGroupArn'].OutputValue | [0]" \
    --output text
)"

if [[ -z "$ALB_DNS" || "$ALB_DNS" == "None" ]]; then
  echo "Could not discover ALB DNS name."
  exit 1
fi

BASE="http://$ALB_DNS"

echo "=== Route coexistence ==="
echo
echo "Frontend /"
curl -fsS "$BASE/" | head -c 200
echo -e "\n"

echo "Legacy backend /api/health"
curl -fsS "$BASE/api/health"
echo -e "\n"

echo "Catalogue /catalogue/health"
curl -fsS "$BASE/catalogue/health"
echo -e "\n"

echo "Catalogue /catalogue/products"
curl -fsS "$BASE/catalogue/products"
echo -e "\n"

echo "Catalogue /catalogue/products/P1001"
curl -fsS "$BASE/catalogue/products/P1001"
echo -e "\n"

echo "=== ECS service ==="
if [[ -n "$SERVICE" && "$SERVICE" != "None" ]]; then
  aws ecs describe-services \
    --cluster "$CLUSTER" \
    --services "$SERVICE" \
    --region "$REGION" \
    --query "services[0].{status:status,desired:desiredCount,running:runningCount,pending:pendingCount,deployments:deployments[*].{status:status,running:runningCount,desired:desiredCount}}" \
    --output json
else
  echo "CatalogueServiceName is not present. DeployService may still be false."
fi

echo
echo "=== Catalogue target health ==="
aws elbv2 describe-target-health \
  --target-group-arn "$TG_ARN" \
  --region "$REGION" \
  --query "TargetHealthDescriptions[*].{target:Target.Id,port:Target.Port,state:TargetHealth.State,reason:TargetHealth.Reason}" \
  --output table
