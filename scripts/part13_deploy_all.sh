#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PAGER=""

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
# For routine setup use ./scripts/lab.sh setup your-email@example.com.
# These phase commands remain available for diagnostics and targeted updates.

REGION="${AWS_REGION:-us-east-1}"
MODE="${1:-}"

NETWORK_STACK="${NETWORK_STACK_NAME:-anygroup-gp2-network}"
CORE_STACK="${CORE_STACK_NAME:-anygroup-gp2-core}"
OBS_STACK="${OBS_STACK_NAME:-anygroup-gp2-observability}"
MICRO_STACK="${MICROSERVICE_STACK_NAME:-anygroup-gp2-microservice}"

preflight() {
  aws sts get-caller-identity --region "$REGION" --query '{Account:Account,Arn:Arn}' --output json
  local total other
  total="$(aws ec2 describe-instances --region "$REGION" \
    --filters 'Name=instance-state-name,Values=pending,running' \
    --query 'length(Reservations[].Instances[])' --output text)"
  other="$(aws ec2 describe-instances --region "$REGION" \
    --filters 'Name=instance-state-name,Values=pending,running' \
    --query 'length(Reservations[].Instances[] | [?Tags == null || !contains(Tags[?Key==`Project`].Value, `INFOSYS735-GP2`)])' --output text)"
  if (( total > 4 || other > 0 )); then
    echo "Deployment requires the four-instance project baseline with no unrelated running EC2." >&2
    echo "Found $total running/pending EC2, including $other unrelated instances. Wait for scale-in or clear your unrelated lab resources first." >&2
    exit 1
  fi
}

rds_preflight() {
  local options
  options="$(aws rds describe-orderable-db-instance-options --engine oracle-se2 \
    --db-instance-class "${DB_INSTANCE_CLASS:-db.t3.small}" --license-model license-included \
    --region "$REGION" --output json)"
  DB_ENGINE_VERSION="$(printf '%s' "$options" | python3 -c '
import json,sys
rows=[r for r in json.load(sys.stdin).get("OrderableDBInstanceOptions",[]) if r.get("MultiAZCapable") and r.get("Vpc") and r.get("StorageType")=="gp2" and r.get("EngineVersion","").startswith("19.") and r.get("MinStorageSize",999)<=20]
if not rows: raise SystemExit("No orderable Oracle 19 SE2 License Included Multi-AZ/gp2 option for this class. Check lab permissions or set DB_INSTANCE_CLASS=db.t3.medium; no resources created by this check.")
print(sorted({r["EngineVersion"] for r in rows})[-1])')"
  export DB_ENGINE_VERSION
  echo "Oracle preflight: ${DB_INSTANCE_CLASS:-db.t3.small}, $DB_ENGINE_VERSION, License Included, Multi-AZ, 20 GiB gp2."
}

cf_validate() {
  local file="$1"
  echo "Validating $file ..."
  aws cloudformation validate-template \
    --template-body "file://$file" \
    --region "$REGION" >/dev/null
}

deploy_network() {
  aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --template-file cloudformation/01-network-stack.yaml \
    --stack-name "$NETWORK_STACK" \
    --parameter-overrides EnvironmentName=anygroup-gp2 \
    --region "$REGION"
}

deploy_core() {
  aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --template-file cloudformation/02-core-infrastructure-stack.template.json \
    --stack-name "$CORE_STACK" \
    --parameter-overrides \
      NetworkStackName="$NETWORK_STACK" \
      EnvironmentName=anygroup-gp2 \
      DbInstanceClass="${DB_INSTANCE_CLASS:-db.t3.small}" \
      DbEngineVersion="$DB_ENGINE_VERSION" \
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
    --no-fail-on-empty-changeset \
    --template-file cloudformation/03-observability-stack.yaml \
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
  local previous
  if previous="$(aws cloudformation describe-stacks --stack-name "$MICRO_STACK" --region "$REGION" \
    --query 'Stacks[0].Parameters' --output json 2>&1)"; then
    local service_enabled pinned tag
    service_enabled="$(printf '%s' "$previous" | python3 -c 'import json,sys; p={i["ParameterKey"]:i["ParameterValue"] for i in json.load(sys.stdin)}; print(p.get("DeployService","false"))')"
    pinned="$(printf '%s' "$previous" | python3 -c 'import json,sys; p={i["ParameterKey"]:i["ParameterValue"] for i in json.load(sys.stdin)}; print(p.get("ContainerImageDigest",""))')"
    if [[ "$service_enabled" == "true" && -z "$pinned" ]]; then
      tag="$(printf '%s' "$previous" | python3 -c 'import json,sys; p={i["ParameterKey"]:i["ParameterValue"] for i in json.load(sys.stdin)}; print(p["ContainerImageTag"])')"
      echo "Upgrading the existing active catalogue to a pinned image without disabling it."
      deploy_micro_phase2 "$tag"
      return
    fi
  elif [[ "$previous" != *ValidationError* || "$previous" != *"does not exist"* ]]; then
    echo "$previous" >&2
    exit 1
  fi
  aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --template-file cloudformation/04-microservice-stack.yaml \
    --stack-name "$MICRO_STACK" \
    --parameter-overrides \
      EnvironmentName=anygroup-gp2 \
      NetworkStackName="$NETWORK_STACK" \
      CoreStackName="$CORE_STACK" \
      ObservabilityStackName="$OBS_STACK" \
      LabRoleName=LabRole \
      CatalogueDesiredCount=2 \
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
      --output text
  )"

  if [[ -z "$digest" || "$digest" == "None" ]]; then
    echo "ECR image tag '$image_tag' does not exist."
    echo "Run: ./scripts/part12_build_push.sh $image_tag catalogue-service"
    exit 1
  fi

  echo "Found ECR image $repo:$image_tag ($digest)"

  local table bucket product
  table="$(aws cloudformation describe-stacks --stack-name "$MICRO_STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTableName'].OutputValue | [0]" --output text)"
  bucket="$(aws cloudformation describe-stacks --stack-name "$CORE_STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueImageBucketName'].OutputValue | [0]" --output text)"
  for product in P1001 P1002 P1003; do
    local key value
    key="{\"product_id\":{\"S\":\"$product\"}}"
    value="$(aws dynamodb get-item --table-name "$table" --key "$key" --consistent-read \
      --region "$REGION" --query 'Item.product_id.S' --output text)"
    [[ "$value" == "$product" ]] || { echo "Seed $product before activation." >&2; exit 1; }
    aws s3api head-object --bucket "$bucket" --key "products/$product.jpg" --region "$REGION" >/dev/null
  done

  aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --template-file cloudformation/04-microservice-stack.yaml \
    --stack-name "$MICRO_STACK" \
    --parameter-overrides \
      EnvironmentName=anygroup-gp2 \
      NetworkStackName="$NETWORK_STACK" \
      CoreStackName="$CORE_STACK" \
      ObservabilityStackName="$OBS_STACK" \
      LabRoleName=LabRole \
      ContainerImageTag="$image_tag" \
      ContainerImageDigest="$digest" \
      CatalogueDesiredCount=2 \
      DeployService=true \
      EnableCatalogueAlarm=true \
    --region "$REGION"
}

status() {
  for stack in "$NETWORK_STACK" "$CORE_STACK" "$OBS_STACK" "$MICRO_STACK"; do
    echo -n "$stack: "
    local result
    if result="$(aws cloudformation describe-stacks \
      --stack-name "$stack" \
      --region "$REGION" \
      --query "Stacks[0].StackStatus" \
      --output text 2>&1)"; then
      echo "$result"
    elif [[ "$result" == *ValidationError* && "$result" == *"does not exist"* ]]; then
      echo "NOT_FOUND"
    else
      echo "$result" >&2
      return 1
    fi
  done
}

case "$MODE" in
  validate)
    cf_validate cloudformation/01-network-stack.yaml
    cf_validate cloudformation/02-core-infrastructure-stack.template.json
    cf_validate cloudformation/03-observability-stack.yaml
    cf_validate cloudformation/04-microservice-stack.yaml
    echo "AWS validate-template completed for all four templates."
    ;;

  foundation)
    preflight
    rds_preflight
    EMAIL="${2:-}"
    echo "Deploying network..."
    deploy_network
    echo "Deploying core..."
    deploy_core
    echo "Deploying observability..."
    deploy_observability "$EMAIL"
    echo "Deploying microservice foundation (preserving existing activation/image parameters)..."
    deploy_micro_phase1
    echo
    echo "Foundation deployment complete."
    echo "Routine setup continues automatically when invoked through scripts/lab.sh."
    echo "For individual phase work:"
    echo "  ./scripts/part12_build_push.sh v1 catalogue-service"
    echo "  ./scripts/part12_seed_catalogue.sh"
    echo "  ./scripts/part11_s3_test.sh upload sample-images/P1001.jpg products/P1001.jpg"
    echo "  ./scripts/part11_s3_test.sh upload sample-images/P1002.jpg products/P1002.jpg"
    echo "  ./scripts/part11_s3_test.sh upload sample-images/P1003.jpg products/P1003.jpg"
    echo "  ./scripts/part13_deploy_all.sh feature v1"
    ;;

  feature)
    preflight
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
