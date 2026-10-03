#!/usr/bin/env bash
set -euo pipefail

# INFOSYS 735 GP2 Part 13 - dependency-aware teardown.
#
# Run from repository root.
#
# Usage:
#   ./scripts/part13_teardown_all.sh
#   ./scripts/part13_teardown_all.sh --yes
#
# Order:
#   microservice -> observability -> empty S3 -> core -> network

REGION="${AWS_REGION:-us-east-1}"
NETWORK_STACK="${NETWORK_STACK_NAME:-anygroup-gp2-network}"
CORE_STACK="${CORE_STACK_NAME:-anygroup-gp2-core}"
OBS_STACK="${OBS_STACK_NAME:-anygroup-gp2-observability}"
MICRO_STACK="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"

if [[ "${1:-}" != "--yes" ]]; then
  echo "This will delete all GP2 Learner Lab stacks and demo data:"
  echo "  $MICRO_STACK"
  echo "  $OBS_STACK"
  echo "  $CORE_STACK"
  echo "  $NETWORK_STACK"
  read -r -p "Type DELETE to continue: " answer
  [[ "$answer" == "DELETE" ]] || { echo "Cancelled."; exit 1; }
fi

stack_exists() {
  aws cloudformation describe-stacks \
    --stack-name "$1" \
    --region "$REGION" >/dev/null 2>&1
}

delete_and_wait() {
  local stack="$1"
  if ! stack_exists "$stack"; then
    echo "$stack: not found; skipping."
    return
  fi
  echo "Deleting $stack ..."
  aws cloudformation delete-stack --stack-name "$stack" --region "$REGION"
  aws cloudformation wait stack-delete-complete --stack-name "$stack" --region "$REGION"
  echo "$stack: deleted."
}

# Best-effort ECR image cleanup before the microservice repository is deleted.
if stack_exists "$MICRO_STACK"; then
  ECR_REPO="$(
    aws cloudformation describe-stacks \
      --stack-name "$MICRO_STACK" \
      --region "$REGION" \
      --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryName'].OutputValue | [0]" \
      --output text 2>/dev/null || true
  )"
  if [[ -n "$ECR_REPO" && "$ECR_REPO" != "None" ]]; then
    TMP_IDS="$(mktemp)"
    aws ecr list-images \
      --repository-name "$ECR_REPO" \
      --region "$REGION" \
      --query 'imageIds[*]' \
      --output json > "$TMP_IDS" || true
    if [[ "$(cat "$TMP_IDS")" != "[]" ]]; then
      echo "Removing ECR images from $ECR_REPO ..."
      aws ecr batch-delete-image \
        --repository-name "$ECR_REPO" \
        --image-ids "file://$TMP_IDS" \
        --region "$REGION" >/dev/null || true
    fi
    rm -f "$TMP_IDS"
  fi
fi

delete_and_wait "$MICRO_STACK"
delete_and_wait "$OBS_STACK"

# Empty the core S3 bucket before deleting its stack.
if stack_exists "$CORE_STACK"; then
  BUCKET="$(
    aws cloudformation describe-stacks \
      --stack-name "$CORE_STACK" \
      --region "$REGION" \
      --query "Stacks[0].Outputs[?OutputKey=='CatalogueImageBucketName'].OutputValue | [0]" \
      --output text 2>/dev/null || true
  )"
  if [[ -n "$BUCKET" && "$BUCKET" != "None" ]]; then
    echo "Emptying S3 bucket $BUCKET ..."
    aws s3 rm "s3://$BUCKET/" --recursive --region "$REGION" || true
  fi
fi

delete_and_wait "$CORE_STACK"
delete_and_wait "$NETWORK_STACK"

echo
echo "Teardown sequence completed."
echo "Check CloudFormation, EC2, ELB, ECS, ECR, DynamoDB, S3, SNS and Tag Editor for orphaned resources."
