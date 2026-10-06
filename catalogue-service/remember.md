# Read-only lab diagnostics

Use these commands only in your authenticated lab session. Infrastructure is
managed by the four CloudFormation stacks; these commands inspect it.

```bash
export AWS_REGION=us-east-1
export AWS_PAGER=""
aws sts get-caller-identity
vpc_id="$(aws cloudformation describe-stacks --stack-name anygroup-gp2-network --query "Stacks[0].Outputs[?OutputKey=='VpcId'].OutputValue | [0]" --output text)"
aws ec2 describe-vpcs --vpc-ids "$vpc_id"
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$vpc_id"
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ReadOnly,AttributeValue=false --query 'Events[].{Username:Username,Time:EventTime,Event:EventName,EventId:EventId}'
```

CloudTrail Event History is a diagnostic source, not proof that this project
deploys an audit trail. Do not put credentials or complete signed URLs in evidence.
See [the main deployment and testing guide](../IaC_Deployment_and_Usage_Instructions.md) for the complete verification sequence.
