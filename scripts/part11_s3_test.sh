#!/usr/bin/env bash
set -euo pipefail

# INFOSYS 735 GP2 Part 11 - S3 catalogue bucket validation helper.
#
# Requirements:
#   - AWS CLI authenticated to the Learner Lab account
#   - anygroup-gp2-core stack deployed
#
# Usage:
#   ./part11_s3_test.sh info
#   ./part11_s3_test.sh upload <local-file> <object-key>
#   ./part11_s3_test.sh list
#   ./part11_s3_test.sh download <object-key> <local-output>
#   ./part11_s3_test.sh cleanup
#
# Examples:
#   ./part11_s3_test.sh upload ./sample.jpg products/P1001.jpg
#   ./part11_s3_test.sh list
#   ./part11_s3_test.sh download products/P1001.jpg ./downloaded.jpg
#
# The cleanup command is intended for Learner Lab teardown before deleting the
# CloudFormation core stack. The prototype bucket intentionally does not enable
# versioning so recursive cleanup remains simple.

STACK_NAME="${CORE_STACK_NAME:-anygroup-gp2-core}"
REGION="${AWS_REGION:-us-east-1}"

BUCKET="$(
  aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueImageBucketName'].OutputValue | [0]" \
    --output text
)"

if [[ -z "$BUCKET" || "$BUCKET" == "None" ]]; then
  echo "Could not discover CatalogueImageBucketName from stack $STACK_NAME."
  exit 1
fi

MODE="${1:-}"

case "$MODE" in
  info)
    echo "Stack:  $STACK_NAME"
    echo "Region: $REGION"
    echo "Bucket: $BUCKET"
    echo
    echo "Public access block:"
    aws s3api get-public-access-block \
      --bucket "$BUCKET" \
      --region "$REGION"
    echo
    echo "Encryption:"
    aws s3api get-bucket-encryption \
      --bucket "$BUCKET" \
      --region "$REGION"
    echo
    echo "Ownership controls:"
    aws s3api get-bucket-ownership-controls \
      --bucket "$BUCKET" \
      --region "$REGION"
    ;;

  upload)
    LOCAL_FILE="${2:-}"
    OBJECT_KEY="${3:-}"
    if [[ -z "$LOCAL_FILE" || -z "$OBJECT_KEY" ]]; then
      echo "Usage: $0 upload <local-file> <object-key>"
      exit 1
    fi
    aws s3 cp "$LOCAL_FILE" "s3://$BUCKET/$OBJECT_KEY" \
      --region "$REGION"
    echo
    aws s3api head-object \
      --bucket "$BUCKET" \
      --key "$OBJECT_KEY" \
      --region "$REGION"
    ;;

  list)
    aws s3 ls "s3://$BUCKET/" --recursive --region "$REGION"
    ;;

  download)
    OBJECT_KEY="${2:-}"
    LOCAL_OUTPUT="${3:-}"
    if [[ -z "$OBJECT_KEY" || -z "$LOCAL_OUTPUT" ]]; then
      echo "Usage: $0 download <object-key> <local-output>"
      exit 1
    fi
    aws s3 cp "s3://$BUCKET/$OBJECT_KEY" "$LOCAL_OUTPUT" \
      --region "$REGION"
    echo "Downloaded to $LOCAL_OUTPUT"
    ;;

  cleanup)
    echo "Removing all objects from s3://$BUCKET/ ..."
    aws s3 rm "s3://$BUCKET/" --recursive --region "$REGION"
    echo "Bucket emptied. It can now be deleted by CloudFormation."
    ;;

  *)
    echo "Usage:"
    echo "  $0 info"
    echo "  $0 upload <local-file> <object-key>"
    echo "  $0 list"
    echo "  $0 download <object-key> <local-output>"
    echo "  $0 cleanup"
    exit 1
    ;;
esac
