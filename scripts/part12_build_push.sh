#!/usr/bin/env bash
set -euo pipefail

# Build and push the catalogue image to the ECR repository created by
# 04-microservice-stack.yaml phase 1.

STACK_NAME="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"
REGION="${AWS_REGION:-us-east-1}"
IMAGE_TAG="${1:-v1}"
SERVICE_DIR="${2:-catalogue-service}"

REPOSITORY_URI="$(
  aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryUri'].OutputValue | [0]" \
    --output text
)"

if [[ -z "$REPOSITORY_URI" || "$REPOSITORY_URI" == "None" ]]; then
  echo "Could not discover EcrRepositoryUri from stack $STACK_NAME."
  exit 1
fi

REGISTRY="${REPOSITORY_URI%%/*}"

echo "Repository: $REPOSITORY_URI"
echo "Image tag:   $IMAGE_TAG"
echo "Source:      $SERVICE_DIR"

aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

docker build --platform linux/amd64 -t "anygroup-catalogue:$IMAGE_TAG" "$SERVICE_DIR"
ARCH="$(docker image inspect "anygroup-catalogue:$IMAGE_TAG" --format '{{.Architecture}}')"
if [[ "$ARCH" != "amd64" ]]; then
  echo "Expected amd64 for the X86_64 Fargate task; found $ARCH." >&2
  exit 1
fi
docker tag "anygroup-catalogue:$IMAGE_TAG" "$REPOSITORY_URI:$IMAGE_TAG"
docker push "$REPOSITORY_URI:$IMAGE_TAG"

echo
echo "Pushed: $REPOSITORY_URI:$IMAGE_TAG"
echo "Activate with: ./scripts/part13_deploy_all.sh feature $IMAGE_TAG"
echo "Tags are immutable. For a changed build use a new tag, such as v2; keep the last working image for rollback."
