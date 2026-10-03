#!/usr/bin/env bash
set -euo pipefail

# INFOSYS 735 GP2 Part 13 - safe deployment orchestration.
#
# Run from repository root.
#
# Modes:
#   validate
#   foundation [notification-email]
#   feature [image-tag]
#   status
#
# Recommended sequence:
#   ./scripts/part13_deploy_all.sh validate
#   ./scripts/part13_deploy_all.sh foundation your-email@example.com
#   ./scripts/part12_build_push.sh v1 catalogue-service
#   ./scripts/part12_seed_catalogue.sh
#   ./scripts/part13_deploy_all.sh feature v1
#   ./scripts/part12_test_catalogue.sh

REGION="${AWS_REGION:-us-east-1}"
MODE="${1:-}"

NETWORK_STACK="${NETWORK_STACK_NAME:-anygroup-gp2-network}"
CORE_STACK="${CORE_STACK_NAME:-anygroup-gp2-core}"
OBS_STACK="${OBS_STACK_NAME:-anygroup-gp2-observability}"
MICRO_STACK="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"

cf_validate() {
  local file="$1"
  echo "Validating $file ..."
  aws cloudformation validate-template \
    --template-body "file://$file" \
    --region "$REGION" >/dev/null
}

deploy_network() {
  aws cloudformation deploy \
    --template-file cloudformation/01-network-stack.yaml \
    --stack-name "$NETWORK_STACK" \
    --parameter-overrides EnvironmentName=anygroup-gp2 \
    --region "$REGION"
}

deploy_core() {
  aws cloudformation deploy \
    --template-file cloudformation/02-core-infrastructure-stack_UPDATED.yaml \
    --stack-name "$CORE_STACK" \
    --parameter-overrides \
      NetworkStackName="$NETWORK_STACK" \
      EnvironmentName=anygroup-gp2 \
      FrontendMinSize=2 \
      FrontendDesiredCapacity=2 \
      FrontendMaxSize=4 \
      FrontendRequestCountTarget=50 \
      BackendMinSize=2 \
      BackendDesiredCapacity=2 \
      BackendMaxSize=2 \
    --region "$REGION"
}

deploy_observability() {
  local email="${1:-}"
  aws cloudformation deploy \
    --template-file cloudformation/03-observability-stack_UPDATED.yaml \
    --stack-name "$OBS_STACK" \
    --parameter-overrides \
      EnvironmentName=anygroup-gp2 \
      CoreStackName="$CORE_STACK" \
      NotificationEmail="$email" \
      MinimumHealthyFrontendTargets=2 \
      Target5xxThreshold=1 \
    --region "$REGION"
}

deploy_micro_phase1() {
  aws cloudformation deploy \
    --template-file cloudformation/04-microservice-stack_UPDATED.yaml \
    --stack-name "$MICRO_STACK" \
    --parameter-overrides \
      EnvironmentName=anygroup-gp2 \
      NetworkStackName="$NETWORK_STACK" \
      CoreStackName="$CORE_STACK" \
      ObservabilityStackName="$OBS_STACK" \
      LabRoleName=LabRole \
      ContainerImageTag=v1 \
      CatalogueDesiredCount=2 \
      DeployService=false \
      EnableCatalogueAlarm=true \
    --region "$REGION"
}

deploy_micro_phase2() {
  local image_tag="${1:-v1}"

  local repo
  repo="$(
    aws cloudformation describe-stacks \
      --stack-name "$MICRO_STACK" \
      --region "$REGION" \
      --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryName'].OutputValue | [0]" \
      --output text
  )"

  if [[ -z "$repo" || "$repo" == "None" ]]; then
    echo "Could not discover ECR repository. Run foundation first."
    exit 1
  fi

  local digest
  digest="$(
    aws ecr describe-images \
      --repository-name "$repo" \
      --image-ids imageTag="$image_tag" \
      --region "$REGION" \
      --query "imageDetails[0].imageDigest" \
      --output text 2>/dev/null || true
  )"

  if [[ -z "$digest" || "$digest" == "None" ]]; then
    echo "ECR image tag '$image_tag' does not exist."
    echo "Run: ./scripts/part12_build_push.sh $image_tag catalogue-service"
    exit 1
  fi

  echo "Found ECR image $repo:$image_tag ($digest)"

  aws cloudformation deploy \
    --template-file cloudformation/04-microservice-stack_UPDATED.yaml \
    --stack-name "$MICRO_STACK" \
    --parameter-overrides \
      EnvironmentName=anygroup-gp2 \
      NetworkStackName="$NETWORK_STACK" \
      CoreStackName="$CORE_STACK" \
      ObservabilityStackName="$OBS_STACK" \
      LabRoleName=LabRole \
      ContainerImageTag="$image_tag" \
      CatalogueDesiredCount=2 \
      DeployService=true \
      EnableCatalogueAlarm=true \
    --region "$REGION"
}

status() {
  for stack in "$NETWORK_STACK" "$CORE_STACK" "$OBS_STACK" "$MICRO_STACK"; do
    echo -n "$stack: "
    aws cloudformation describe-stacks \
      --stack-name "$stack" \
      --region "$REGION" \
      --query "Stacks[0].StackStatus" \
      --output text 2>/dev/null || echo "NOT_FOUND"
  done
}

case "$MODE" in
  validate)
    cf_validate cloudformation/01-network-stack.yaml
    cf_validate cloudformation/02-core-infrastructure-stack_UPDATED.yaml
    cf_validate cloudformation/03-observability-stack_UPDATED.yaml
    cf_validate cloudformation/04-microservice-stack_UPDATED.yaml
    echo "AWS validate-template completed for all four templates."
    ;;

  foundation)
    EMAIL="${2:-}"
    echo "Deploying network..."
    deploy_network
    echo "Deploying core..."
    deploy_core
    echo "Deploying observability..."
    deploy_observability "$EMAIL"
    echo "Deploying microservice phase 1..."
    deploy_micro_phase1
    echo
    echo "Foundation deployment complete."
    echo "Next:"
    echo "  ./scripts/part12_build_push.sh v1 catalogue-service"
    echo "  ./scripts/part12_seed_catalogue.sh"
    echo "  ./scripts/part13_deploy_all.sh feature v1"
    ;;

  feature)
    IMAGE_TAG="${2:-v1}"
    deploy_micro_phase2 "$IMAGE_TAG"
    ;;

  status)
    status
    ;;

  *)
    echo "Usage:"
    echo "  $0 validate"
    echo "  $0 foundation [notification-email]"
    echo "  $0 feature [image-tag]"
    echo "  $0 status"
    exit 1
    ;;
esac
