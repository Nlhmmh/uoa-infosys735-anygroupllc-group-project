#!/usr/bin/env bash
set -euo pipefail

# INFOSYS 735 GP2 Part 10 - CloudWatch/SNS validation helper.
#
# Usage:
#   ./part10_test_observability.sh sns <topic-arn>
#   ./part10_test_observability.sh alarm <alarm-name>
#
# "sns" verifies direct SNS delivery.
# "alarm" temporarily sets a CloudWatch alarm state to ALARM so the alarm action
# can be tested without deliberately damaging infrastructure. A real controlled
# frontend-failure test should still be performed in Part 14.

MODE="${1:-}"
TARGET="${2:-}"

if [[ -z "$MODE" || -z "$TARGET" ]]; then
  echo "Usage:"
  echo "  $0 sns <topic-arn>"
  echo "  $0 alarm <alarm-name>"
  exit 1
fi

case "$MODE" in
  sns)
    aws sns publish \
      --topic-arn "$TARGET" \
      --subject "INFOSYS735 GP2 SNS test" \
      --message "Test notification from the AnyGroupLLC Group Project 2 observability validation."
    echo "SNS publish request sent. Check the confirmed subscription destination."
    ;;

  alarm)
    aws cloudwatch set-alarm-state \
      --alarm-name "$TARGET" \
      --state-value ALARM \
      --state-reason "INFOSYS735 GP2 controlled notification test"
    echo "Alarm state set to ALARM for test purposes."
    echo "CloudWatch will return to metric-driven state on a later evaluation."
    ;;

  *)
    echo "Unknown mode: $MODE"
    exit 1
    ;;
esac
