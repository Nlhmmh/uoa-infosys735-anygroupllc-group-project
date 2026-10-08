#!/usr/bin/env bash
# One entry point for routine lab setup, tests, image updates and teardown.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PAGER=""
export AWS_REGION="${AWS_REGION:-us-east-1}"
MODE="${1:-}"

verify() {
  local evidence_dir="${EVIDENCE_DIR:-evidence/$(date -u +%Y%m%dT%H%M%SZ)}"
  mkdir -p "$evidence_dir"
  ./scripts/part12_test_catalogue.sh --wait --output "$evidence_dir/smoke.json"
  python3 scripts/part14_collect_evidence.py --output "$evidence_dir/configuration"
  echo "Evidence saved in $evidence_dir. Recovery/failover/load tests are separate experiments."
}

ensure_image() {
  local tag="$1" repo result
  repo="$(aws cloudformation describe-stacks --stack-name "${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}" \
    --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryName'].OutputValue | [0]" --region "$AWS_REGION" --output text)"
  if result="$(aws ecr describe-images --repository-name "$repo" --image-ids "imageTag=$tag" \
    --region "$AWS_REGION" --query 'imageDetails[0].imageDigest' --output text 2>&1)"; then
    echo "Reusing immutable image $tag ($result). For changed code use a new tag."
  elif [[ "$result" == *ImageNotFoundException* ]]; then
    ./scripts/part12_build_push.sh "$tag" catalogue-service
  else
    echo "$result" >&2
    return 1
  fi
}

case "$MODE" in
  setup)
    export EVIDENCE_DIR="${EVIDENCE_DIR:-evidence/$(date -u +%Y%m%dT%H%M%SZ)}"
    for command in aws docker python3; do
      command -v "$command" >/dev/null || { echo "Missing $command. Use AWS CloudShell with Docker available." >&2; exit 1; }
    done
    docker info >/dev/null 2>&1 || { echo "Docker is not running. Start Docker before setup; no infrastructure was created." >&2; exit 1; }
    ./scripts/part13_deploy_all.sh validate
    ./scripts/part13_deploy_all.sh foundation "${2:-${NOTIFICATION_EMAIL:-}}"
    ensure_image "${3:-v1}"
    ./scripts/part12_seed_catalogue.sh
    bucket="$(aws cloudformation describe-stacks --stack-name "${CORE_STACK_NAME:-anygroup-gp2-core}" \
      --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='CatalogueImageBucketName'].OutputValue | [0]" --output text)"
    for product in P1001 P1002 P1003; do
      aws s3 cp "sample-images/$product.jpg" "s3://$bucket/products/$product.jpg" --region "$AWS_REGION"
    done
    python3 scripts/part15_seed_database.py
    rotation_key="$(python3 scripts/part16_package_rotation.py --bucket "$bucket")"
    ./scripts/part13_deploy_all.sh rotation "$rotation_key" "${BACKEND_ROTATION_DAYS:-30}"
    python3 scripts/part16_test_secret_rotation.py --wait-initial \
      --output "${EVIDENCE_DIR:-evidence/$(date -u +%Y%m%dT%H%M%SZ)}/rotation"
    ./scripts/part13_deploy_all.sh feature "${3:-v1}"
    verify
    echo "Setup complete. Confirm the SNS email subscription, then follow the guide for failover/scaling tests."
    ;;
  update)
    [[ -n "${2:-}" ]] || { echo "Usage: $0 update NEW_IMAGE_TAG" >&2; exit 1; }
    ensure_image "$2"
    ./scripts/part13_deploy_all.sh feature "$2"
    verify
    ;;
  test) verify ;;
  rotate)
    export EVIDENCE_DIR="${EVIDENCE_DIR:-evidence/rotation-$(date -u +%Y%m%dT%H%M%SZ)}"
    python3 scripts/part16_test_secret_rotation.py --rotate \
      --output "${EVIDENCE_DIR:-evidence/rotation-$(date -u +%Y%m%dT%H%M%SZ)}"
    verify
    ;;
  load)
    base="$(aws cloudformation describe-stacks --stack-name "${CORE_STACK_NAME:-anygroup-gp2-core}" \
      --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" --output text)"
    evidence_dir="${EVIDENCE_DIR:-evidence/scaling-$(date -u +%Y%m%dT%H%M%SZ)}"
    python3 scripts/part09_load_test.py "http://$base/" --requests 2400 --duration 480 --workers 10 --output "$evidence_dir/load.json"
    python3 scripts/part14_collect_evidence.py --output "$evidence_dir/configuration"
    ;;
  failover)
    python3 scripts/part15_test_rds_failover.py --output "${EVIDENCE_DIR:-evidence/rds-failover-$(date -u +%Y%m%dT%H%M%SZ)}"
    verify
    ;;
  status) ./scripts/part13_deploy_all.sh status ;;
  teardown)
    secret_args=()
    if secret_arn="$(aws cloudformation describe-stacks --stack-name "${CORE_STACK_NAME:-anygroup-gp2-core}" \
      --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='DatabaseMasterSecretArn'].OutputValue | [0]" --output text 2>&1)"; then
      if [[ -n "$secret_arn" && "$secret_arn" != "None" ]]; then
        secret_args=(--managed-secret-arn "$secret_arn")
      fi
    elif [[ "$secret_arn" != *ValidationError* || "$secret_arn" != *"does not exist"* ]]; then
      echo "$secret_arn" >&2; exit 1
    fi
    ./scripts/part13_teardown_all.sh "${2:-}"
    python3 scripts/part14_collect_evidence.py --after-teardown \
      --output "${EVIDENCE_DIR:-evidence/after-teardown-$(date -u +%Y%m%dT%H%M%SZ)}" "${secret_args[@]}"
    ;;
  *)
    echo "Usage: $0 setup [notification-email] [image-tag]"
    echo "       $0 test | status | load | failover | rotate | update NEW_IMAGE_TAG | teardown [--yes]"
    exit 1
    ;;
esac
