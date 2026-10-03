aws sts get-caller-identity
 
aws ec2 describe-vpcs
 
aws ec2 describe-vpcs --output text
 
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=735*  --query   'Vpcs[].VpcId' --output text)
 
aws ec2 describe-internet-gateways --filters Name=attachmen.vpc-id,Values=$vpc_id --output text
 
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ReadOnly,AttributeValue=false --query 'Events[].username:Username,time:EventTime,event:EventName,eventid:EventId,accesskey:AccessKeyId,resource:(Resources[0].ResourceName)}'  --region us-east-1 --output text  --no-cli-pager