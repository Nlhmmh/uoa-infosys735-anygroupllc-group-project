#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PAGER=""

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
  local result
  if result="$(aws cloudformation describe-stacks \
    --stack-name "$1" \
    --region "$REGION" 2>&1)"; then
    return 0
  elif [[ "$result" == *ValidationError* && "$result" == *"does not exist"* ]]; then
    return 1
  fi
  echo "$result" >&2
  exit 1
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

# ECR EmptyOnDelete removes images only when CloudFormation deletes the repository.
# Do not delete images while ECS tasks may still need them.
delete_and_wait "$MICRO_STACK"
delete_and_wait "$OBS_STACK"

# Empty the core S3 bucket before deleting its stack.
if stack_exists "$CORE_STACK"; then
  BUCKET="$(
    aws cloudformation describe-stacks \
      --stack-name "$CORE_STACK" \
      --region "$REGION" \
      --query "Stacks[0].Outputs[?OutputKey=='CatalogueImageBucketName'].OutputValue | [0]" \
      --output text
  )"
  if [[ -n "$BUCKET" && "$BUCKET" != "None" ]]; then
    echo "Emptying S3 bucket $BUCKET ..."
    aws s3 rm "s3://$BUCKET/" --recursive --region "$REGION"
  fi
fi

delete_and_wait "$CORE_STACK"
delete_and_wait "$NETWORK_STACK"

echo
echo "Teardown sequence completed."
echo "Synthetic RDS data and automated backups were deleted; this lab stack does not retain a final DB snapshot."
echo "Check RDS/snapshots, Secrets Manager, NAT gateways/EIPs and the remaining project resources for orphans."
echo "Read-only verification: python3 scripts/part14_collect_evidence.py --after-teardown --output evidence/after-teardown"
