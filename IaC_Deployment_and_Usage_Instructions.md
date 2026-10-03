# INFOSYS 735 Group Project 2 — IaC Deployment and Usage Instructions

**Case:** AnyGroupLLC  
**Prototype Region:** `us-east-1`  
**Infrastructure as Code:** AWS CloudFormation  
**Deployment Environment:** AWS Academy Learner Lab / AWS CloudShell  
**Updated Lab Baseline:** 7 EC2 instances at steady state  
**Purpose:** One complete guide for preparing, deploying, testing, and tearing down the Group Project 2 prototype.

> **Important:** This guide assumes the latest updated artefacts have replaced the older versions and are stored using the **canonical filenames shown in the folder structure below**. For example, the latest updated core template should be saved as `cloudformation/02-core-infrastructure-stack.yaml`, not as a second `.yaml` file.

---

# Section 1 — Background Explanation

## 1.1 What This Repository Deploys

The repository deploys the AnyGroupLLC Learner Lab prototype using four CloudFormation stacks:

```text
01-network-stack.yaml
        ↓
02-core-infrastructure-stack.yaml
        ↓
03-observability-stack.yaml
        ↓
04-microservice-stack.yaml
```

The stacks are deployed in dependency order because later stacks import outputs from earlier stacks.

The deployed stack names are:

```text
anygroup-gp2-network
anygroup-gp2-core
anygroup-gp2-observability
anygroup-gp2-microservice
```

The prototype is designed for:

```text
AWS Region
→ us-east-1
```

The production recommendation remains:

```text
AWS Region
→ ap-southeast-6
```

The Learner Lab is a functional prototype, not production sizing.

---

## 1.2 Final Repository Folder Layout

Keep the project in this structure:

```text
├── catalogue-service
│   ├── Dockerfile
│   ├── README.md
│   ├── app.py
│   ├── remember.md
│   └── requirements.txt
│
├── cloudformation
│   ├── 01-network-stack-parameters.json
│   ├── 01-network-stack.yaml
│   ├── 02-core-infrastructure-stack-parameters.json
│   ├── 02-core-infrastructure-stack.yaml
│   ├── 02-core-security-resources.fragment.yaml
│   ├── 03-observability-stack-parameters.json
│   ├── 03-observability-stack.yaml
│   ├── 04-microservice-security-resources.fragment.yaml
│   ├── 04-microservice-stack-parameters.json
│   └── 04-microservice-stack.yaml
│
├── data
│   ├── part11_sample_catalogue_keys.json
│   ├── part12_catalogue_seed.json
│   ├── part13_stack_manifest.json
│   └── part13_static_validation_report.json
│
├── part13_iac_evidence_checklist.csv
│
├── sample-images
│   ├── P1001.jpg
│   ├── P1002.jpg
│   └── P1003.jpg
│
└── scripts
    ├── part09_load_test.py
    ├── part10_test_observability.sh
    ├── part11_s3_test.sh
    ├── part12_build_push.sh
    ├── part12_seed_catalogue.sh
    ├── part12_test_catalogue.sh
    ├── part13_deploy_all.sh
    ├── part13_teardown_all.sh
    └── part13_validate_iac.py
```

### Files Used Directly During Deployment

| File / Folder | Purpose |
|---|---|
| `cloudformation/01-network-stack.yaml` | VPC, six subnets, Internet Gateway, NAT EC2, route tables, NACLs, S3/DynamoDB gateway endpoints |
| `cloudformation/02-core-infrastructure-stack.yaml` | Public ALB, internal ALB, frontend ASG, backend ASG, dummy DB primary/standby, Security Groups, S3 |
| `cloudformation/03-observability-stack.yaml` | SNS topic and CloudWatch alarms |
| `cloudformation/04-microservice-stack.yaml` | ECR, ECS/Fargate, DynamoDB, catalogue target group, catalogue routing, logs |
| `catalogue-service/` | Catalogue application and Docker image definition |
| `sample-images/` | Product images uploaded to private S3 |
| `scripts/part13_deploy_all.sh` | Main deployment orchestration |
| `scripts/part12_build_push.sh` | Build and push catalogue container to ECR |
| `scripts/part12_seed_catalogue.sh` | Seed DynamoDB catalogue records |
| `scripts/part11_s3_test.sh` | Upload, inspect, list, download, and clean S3 objects |
| `scripts/part12_test_catalogue.sh` | Test website, legacy API, catalogue routes, ECS, and target health |
| `scripts/part10_test_observability.sh` | Test SNS and CloudWatch alarm notifications |
| `scripts/part09_load_test.py` | Generate small HTTP load for frontend Auto Scaling demonstration |
| `scripts/part13_teardown_all.sh` | Delete resources in dependency-safe order |
| `scripts/part13_validate_iac.py` | Local static validation of IaC and supporting files |

The two `*.fragment.yaml` files are reference/security fragments. The main deployment script deploys the four full stack templates, not the fragment files directly.

---

## 1.3 Final Learner Lab Service List

| Layer | AWS Service / Resource | Prototype Use |
|---|---|---|
| Networking | Amazon VPC | Main network `10.0.0.0/16` |
| Networking | Public Subnets ×2 | Public ALB and NAT placement |
| Networking | Private App Subnets ×2 | Frontend, backend, and Fargate placement |
| Networking | Private DB Subnets ×2 | Dummy DB primary and standby |
| Networking | Internet Gateway | Public VPC connectivity |
| Networking | NAT EC2 | Outbound internet for private application subnets |
| Networking | Route Tables | Public, app, and DB routing |
| Networking | Network ACLs | Subnet-level network controls |
| Networking | Security Groups | Tier-to-tier access control |
| Networking | S3 Gateway Endpoint | Private VPC access path to S3 |
| Networking | DynamoDB Gateway Endpoint | Private VPC access path to DynamoDB |
| Entry | Public Application Load Balancer | Customer entry point |
| Web Tier | EC2 Auto Scaling Group | Two Apache frontend EC2 instances across two AZs |
| Application Routing | Internal Application Load Balancer | Private routing from frontend to backend/catalogue |
| Legacy App Tier | EC2 Auto Scaling Group | Two legacy backend demo EC2 instances across two AZs |
| DB Tier | EC2 | Dummy DB Primary in AZ A |
| DB Tier | EC2 | Dummy DB Standby in AZ B |
| Object Storage | Amazon S3 | Private product images |
| Container Registry | Amazon ECR | Catalogue Docker image |
| Modern App Tier | Amazon ECS / Fargate | Two catalogue tasks |
| Catalogue Data | Amazon DynamoDB | Product catalogue metadata |
| Monitoring | Amazon CloudWatch | Metrics, alarms, ECS logs |
| Notification | Amazon SNS | Alarm email notifications |
| IaC | AWS CloudFormation | Source of truth for infrastructure |

The Learner Lab prototype does **not** depend on Route 53, CloudFront, or AWS WAF. Those remain part of the production architecture recommendation.

---

## 1.4 Final Text Architecture Diagram

```text
                                  Internet
                                     │
                                     ▼
                           ┌───────────────────┐
                           │    Public ALB     │
                           │      HTTP :80     │
                           └─────────┬─────────┘
                                     │
                         default /*  │
                                     ▼
                    ┌─────────────────────────┐
                    │   Frontend Target Group │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
      ┌──────────────────┐              ┌──────────────────┐
      │ Frontend EC2     │              │ Frontend EC2     │
      │ AZ A / Apache    │              │ AZ B / Apache    │
      └────────┬─────────┘              └────────┬─────────┘
               │                                 │
               └──────────────┬──────────────────┘
                              │
                              │ Apache reverse proxy
                              │ /api/*
                              │ /catalogue/*
                              ▼
                    ┌──────────────────────┐
                    │    Internal ALB      │
                    │      HTTP :80        │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴──────────────┐
                 │                            │
          priority 100                  priority 50
             /api/*                    /catalogue/*
                 │                            │
                 ▼                            ▼
       ┌────────────────────┐       ┌────────────────────┐
       │ Backend Target     │       │ Catalogue Target   │
       │ Group              │       │ Group              │
       └─────────┬──────────┘       └─────────┬──────────┘
                 │                            │
       ┌─────────┴─────────┐        ┌─────────┴─────────┐
       ▼                   ▼        ▼                   ▼
┌──────────────┐    ┌──────────────┐  Fargate Task A   Fargate Task B
│ Backend EC2  │    │ Backend EC2  │         │                  │
│ AZ A         │    │ AZ B         │         └────────┬─────────┘
└──────┬───────┘    └──────┬───────┘                  │
       │                   │                          ├──► DynamoDB
       └─────────┬─────────┘                          │
                 │                                    └──► Private S3
                 │ TCP 1521                                  Images
         ┌───────┴────────┐
         ▼                ▼
┌────────────────┐  ┌────────────────┐
│ Dummy DB       │  │ Dummy DB       │
│ Primary        │  │ Standby        │
│ DB Subnet A    │  │ DB Subnet B    │
└────────────────┘  └────────────────┘
```

---

## 1.5 What the Website Demonstrates

The frontend is no longer only a technical test page.

It is a customer-facing **AnyGroup Market** storefront containing:

```text
hero section
product search
product cards
product images
product name
category
price
availability
simple cart counter
Live Platform Status
```

The product-card path demonstrates the new service:

```text
Browser
→ Public ALB
→ Frontend EC2
→ Internal ALB
→ ECS/Fargate Catalogue
→ DynamoDB
→ S3 product image
```

The Live Platform Status demonstrates the legacy path:

```text
Browser
→ Public ALB
→ Frontend EC2
→ Internal ALB
→ Backend EC2
→ Dummy DB Primary + Standby
```

The second dummy DB is a **standby architecture simulation**. It does not implement Oracle/RDS replication.

---

## 1.6 EC2 Count and Learner Lab Safety

Normal steady-state EC2 count:

```text
NAT EC2            1
Frontend EC2       2
Backend EC2        2
Dummy DB EC2       2
--------------------
Total              7
```

Frontend ASG:

```text
Min       2
Desired   2
Max       4
```

If the frontend scales to four:

```text
7 baseline
+ 2 additional frontend EC2
= 9 EC2
```

`9` is the planned Learner Lab maximum.

Do not deliberately create extra EC2 instances while the frontend is already scaled to four.

---

# Section 2 — Preparation


## 2.1 Start AWS Academy Learner Lab

Start the Learner Lab first and wait until AWS access is active.

Use:

```text
Region: us-east-1
```

Do not deploy the Learner Lab prototype into the production recommendation Region.

---

## 2.2 Open AWS CloudShell

From the AWS Console, open **CloudShell**.

Set the working Region:

```bash
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""
```

Check the identity:

```bash
aws sts get-caller-identity
```

Expected result:

```text
Account
Arn
UserId
```

If you receive an expired-token or credentials error, restart/refresh the Learner Lab session before continuing.

Check the AWS CLI:

```bash
aws --version
```

Check Python:

```bash
python3 --version
```

Check Docker because the catalogue image build requires it:

```bash
docker --version
```

If Docker is unavailable in the terminal you are using, perform the ECR build/push step from another environment that has Docker and valid current Learner Lab AWS credentials. The CloudFormation, validation, seeding, testing, and teardown steps can still be run from CloudShell.

---

## 2.3 Check Existing Stack State Before Deployment

After uploading the project later, the normal status command is:

```bash
./scripts/part13_deploy_all.sh status
```

However, if you already know you have previous stacks, you can check them immediately with:

```bash
for stack in \
  anygroup-gp2-network \
  anygroup-gp2-core \
  anygroup-gp2-observability \
  anygroup-gp2-microservice
do
  echo -n "$stack: "
  aws cloudformation describe-stacks \
    --stack-name "$stack" \
    --region us-east-1 \
    --query "Stacks[0].StackStatus" \
    --output text 2>/dev/null || echo "NOT_FOUND"
done
```

### Important Case: Network Healthy, Core Failed

If you see:

```text
anygroup-gp2-network: CREATE_COMPLETE
anygroup-gp2-core: ROLLBACK_COMPLETE
anygroup-gp2-observability: NOT_FOUND
anygroup-gp2-microservice: NOT_FOUND
```

keep the network stack and delete only the failed core stack:

```bash
aws cloudformation delete-stack \
  --stack-name anygroup-gp2-core \
  --region us-east-1

aws cloudformation wait stack-delete-complete \
  --stack-name anygroup-gp2-core \
  --region us-east-1
```

Do **not** delete the healthy network stack in this case.

### If an Older Full Architecture Is Already Deployed

If old core, observability, and microservice stacks are already deployed using the previous architecture, the cleanest Learner Lab approach is to tear them down and recreate them using the final artefacts. This avoids stale listener rules, exports, and old single-instance resources.

---

## 2.4 Create the Deployment ZIP Locally

Do not put AWS credentials, access keys, secret keys, session tokens, or downloaded Learner Lab credential files inside the ZIP.

### Windows PowerShell

Run from the project root:

```powershell
Compress-Archive `
  -Path catalogue-service,cloudformation,data,sample-images,scripts,part13_iac_evidence_checklist.csv `
  -DestinationPath anygroup-gp2-deployment.zip `
  -Force
```

### macOS / Linux

Run from the project root:

```bash
zip -r anygroup-gp2-deployment.zip \
  catalogue-service \
  cloudformation \
  data \
  sample-images \
  scripts \
  part13_iac_evidence_checklist.csv
```

The ZIP should contain the folders themselves, not only loose files.

---

## 2.5 Upload the ZIP to AWS CloudShell

In CloudShell:

```text
Actions
→ Upload file
→ select anygroup-gp2-deployment.zip
```

After upload, check:

```bash
ls -lh
```

You should see:

```text
anygroup-gp2-deployment.zip
```

Extract it:

```bash
mkdir -p ~/anygroup-gp2
unzip -o anygroup-gp2-deployment.zip -d ~/anygroup-gp2
cd ~/anygroup-gp2
```

Verify:

```bash
find . -maxdepth 2 -type f | sort
```

Make scripts executable:

```bash
chmod +x scripts/*.sh
```

---

## 2.6 Run Local Static Validation

From the repository root:

```bash
python3 scripts/part13_validate_iac.py
```

Expected high-level result:

```text
YAML templates parse
cross-stack imports resolve
dependency graph is acyclic
catalogue-service files exist
Python syntax passes
shell syntax passes
```

If the validator fails, fix the local artefacts before deploying AWS resources.

---

## 2.7 Run AWS CloudFormation Template Validation

Run:

```bash
./scripts/part13_deploy_all.sh validate
```

Expected:

```text
Validating cloudformation/01-network-stack.yaml ...
Validating cloudformation/02-core-infrastructure-stack.yaml ...
Validating cloudformation/03-observability-stack.yaml ...
Validating cloudformation/04-microservice-stack.yaml ...

AWS validate-template completed for all four templates.
```

This checks CloudFormation template structure.

It does **not** prove that every resource will successfully deploy under Learner Lab quotas and permissions. Runtime validation happens during deployment.

---

# Section 3 — Deployment

## 3.1 How the Deployment Works

The deployment is intentionally split into two stages.

### Stage A — Foundation

```text
Network stack
→ Core stack
→ Observability stack
→ Microservice Phase 1
```

Microservice Phase 1 uses:

```text
DeployService=false
```

It creates the supporting catalogue infrastructure, including:

```text
ECR repository
DynamoDB table
ECS cluster
task definition
catalogue target group
catalogue Security Group
CloudWatch log group
```

The ECS service is not started yet because its container image has not been pushed to ECR.

### Stage B — Feature Activation

After Phase 1:

```text
build Docker image
→ push to ECR
→ seed DynamoDB
→ upload product images to S3
→ update microservice stack with DeployService=true
```

Phase 2 then creates/activates:

```text
/catalogue/* internal ALB rule
ECS/Fargate service
2 Fargate tasks
catalogue health alarm
```

---

## 3.2 Deploy Foundation

Run:

```bash
./scripts/part13_deploy_all.sh \
  foundation \
  nhte538@aucklanduni.ac.nz
```

Expected sequence:

```text
Deploying network...
Deploying core...
Deploying observability...
Deploying microservice phase 1...
Foundation deployment complete.
```

If the network was already successfully deployed:

```text
No changes to deploy. Stack anygroup-gp2-network is up to date
```

is normal.

---

## 3.3 Check Stack Status

Run:

```bash
./scripts/part13_deploy_all.sh status
```

Expected after a successful foundation deployment:

```text
anygroup-gp2-network: CREATE_COMPLETE
anygroup-gp2-core: CREATE_COMPLETE
anygroup-gp2-observability: CREATE_COMPLETE
anygroup-gp2-microservice: CREATE_COMPLETE
```

If a stack fails, inspect the actual failed event before changing the templates:

```bash
aws cloudformation describe-stack-events \
  --stack-name <FAILED-STACK-NAME> \
  --region us-east-1 \
  --query "StackEvents[?ResourceStatus=='CREATE_FAILED'].[Timestamp,LogicalResourceId,ResourceType,ResourceStatusReason]" \
  --output table
```

---

## 3.4 Confirm the SNS Email Subscription

The observability stack creates the SNS topic and email subscription.

Check:

```text
nhte538@aucklanduni.ac.nz
```

Look for an AWS email similar to:

```text
AWS Notification - Subscription Confirmation
```

Click:

```text
Confirm subscription
```

Then verify in:

```text
AWS Console
→ Simple Notification Service
→ Subscriptions
→ Status = Confirmed
```

Do this before testing notifications.

---

## 3.5 Verify Core Infrastructure Before Activating the Catalogue

At this point the expected EC2 baseline is:

```text
NAT                    1
Frontend                2
Backend                 2
Dummy DB                2
--------------------------
Total                   7
```

The catalogue ECS service is not yet active, so the two Fargate tasks are not running yet.

You should also have:

```text
Public ALB
Internal ALB
Frontend ASG
Backend ASG
Private S3 image bucket
```

---

## 3.6 Build and Push the Catalogue Container

Run:

```bash
./scripts/part12_build_push.sh \
  v1 \
  catalogue-service
```

The script:

```text
discovers the ECR repository from CloudFormation
logs Docker into ECR
builds the image
tags the image
pushes tag v1
```

Expected final message:

```text
Pushed: <ECR-REPOSITORY-URI>:v1
```

Verify:

```bash
aws ecr describe-images \
  --repository-name anygroup-gp2-catalogue \
  --region us-east-1 \
  --output table
```

If the physical repository name differs, get it from CloudFormation:

```bash
aws cloudformation describe-stacks \
  --stack-name anygroup-gp2-microservice \
  --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryName'].OutputValue | [0]" \
  --output text
```

---

## 3.7 Seed DynamoDB

Run:

```bash
./scripts/part12_seed_catalogue.sh
```

The script adds:

```text
P1001 — New Zealand Honey
P1002 — Fresh Apples
P1003 — Whole Milk
```

Fields include:

```text
product_id
name
category
price
availability
image_key
```

Verify:

```bash
TABLE="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-microservice \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTableName'].OutputValue | [0]" \
    --output text
)"

aws dynamodb scan \
  --table-name "$TABLE" \
  --region us-east-1 \
  --output table
```

---

## 3.8 Upload Product Images to S3

Upload the three sample images:

```bash
./scripts/part11_s3_test.sh \
  upload \
  sample-images/P1001.jpg \
  products/P1001.jpg
```

```bash
./scripts/part11_s3_test.sh \
  upload \
  sample-images/P1002.jpg \
  products/P1002.jpg
```

```bash
./scripts/part11_s3_test.sh \
  upload \
  sample-images/P1003.jpg \
  products/P1003.jpg
```

Check:

```bash
./scripts/part11_s3_test.sh list
```

Expected keys:

```text
products/P1001.jpg
products/P1002.jpg
products/P1003.jpg
```

Inspect S3 security:

```bash
./scripts/part11_s3_test.sh info
```

The bucket should remain private.

---

## 3.9 Activate the Catalogue Feature

Run:

```bash
./scripts/part13_deploy_all.sh \
  feature \
  v1
```

The script first verifies that ECR tag `v1` exists.

It then updates the microservice stack with:

```text
DeployService=true
CatalogueDesiredCount=2
ContainerImageTag=v1
```

Expected:

```text
Successfully created/updated stack - anygroup-gp2-microservice
```

---

## 3.10 What Phase 2 Adds

After successful activation:

```text
Internal ALB
├── priority 50  /catalogue/* → Catalogue Fargate Target Group
├── priority 100 /api/*       → Backend Target Group
└── default                    → 404
```

ECS should run:

```text
Desired tasks = 2
Running tasks = 2
```

At this point the full storefront can show both product cards and the legacy platform status.

---

# Section 4 — Testing

## 4.1 Test CloudFormation Stacks

Run:

```bash
./scripts/part13_deploy_all.sh status
```

Expected:

```text
network        CREATE_COMPLETE or UPDATE_COMPLETE
core           CREATE_COMPLETE or UPDATE_COMPLETE
observability  CREATE_COMPLETE or UPDATE_COMPLETE
microservice   CREATE_COMPLETE or UPDATE_COMPLETE
```

Also check:

```text
AWS Console
→ CloudFormation
→ Stacks
```

Capture the stack list as IaC evidence.

---

## 4.2 Test the VPC and Subnets

In:

```text
AWS Console
→ VPC
```

Verify:

```text
VPC
10.0.0.0/16

Public A
10.0.0.0/24

Public B
10.0.1.0/24

Private App A
10.0.10.0/24

Private App B
10.0.11.0/24

Private DB A
10.0.20.0/24

Private DB B
10.0.21.0/24
```

Check route tables:

```text
Public
→ Internet Gateway

Private App A/B
→ NAT EC2 for internet-bound traffic

Private DB
→ no default internet route
```

Check VPC endpoints:

```text
S3 Gateway Endpoint
DynamoDB Gateway Endpoint
```

---

## 4.3 Test EC2 Count and AZ Placement

Run:

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters \
    "Name=instance-state-name,Values=running" \
    "Name=tag:Project,Values=INFOSYS735-GP2" \
  --query "Reservations[].Instances[].{Name:Tags[?Key=='Name']|[0].Value,Id:InstanceId,AZ:Placement.AvailabilityZone,PrivateIP:PrivateIpAddress,PublicIP:PublicIpAddress}" \
  --output table
```

Expected steady state:

```text
1 NAT
2 frontend
2 backend
2 dummy DB
```

The application and DB nodes should not have public IP addresses.

Expected placement:

```text
Frontend
→ both AZs

Backend
→ both AZs

Dummy DB Primary
→ DB subnet A

Dummy DB Standby
→ DB subnet B
```

---

## 4.4 Test Public ALB

Get the public ALB DNS name:

```bash
ALB_DNS="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-core \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" \
    --output text
)"

echo "$ALB_DNS"
```

Test:

```bash
curl -I "http://$ALB_DNS/"
```

Expected:

```text
HTTP/1.1 200
```

Open in a browser:

```text
http://<ALB-DNS>/
```

The public ALB should send the request to the frontend target group.

---

## 4.5 Test Frontend Target Group

Get the target group ARN:

```bash
FRONTEND_TG="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-core \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendTargetGroupArn'].OutputValue | [0]" \
    --output text
)"
```

Check health:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$FRONTEND_TG" \
  --region us-east-1 \
  --query "TargetHealthDescriptions[*].{Target:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}" \
  --output table
```

Expected:

```text
2 healthy frontend targets
```

---

## 4.6 Test the Improved Website

Open:

```text
http://<ALB-DNS>/
```

Verify the page contains:

```text
AnyGroup Market branding
hero section
Featured Products
search box
product cards
product images
price
availability
cart counter
Live Platform Status
```

The customer-facing page should not contain assignment wording such as:

```text
Part 12
Strangler Fig Pilot
CloudFormation Demo
```

---

## 4.7 Test Frontend → Legacy Backend

Run:

```bash
curl "http://$ALB_DNS/api/health"
```

Expected JSON includes:

```text
service = legacy-backend
status = healthy
instance_id
availability_zone
```

Actual path:

```text
CloudShell / Browser
→ Public ALB
→ Frontend EC2
→ Apache reverse proxy
→ Internal ALB
→ Backend EC2
```

Run the request repeatedly:

```bash
for i in {1..10}; do
  curl -s "http://$ALB_DNS/api/health"
  echo
done
```

Because two backend targets exist, responses may show different backend instance IDs/AZs.

---

## 4.8 Test Internal ALB Rules

Get the internal listener ARN:

```bash
INTERNAL_LISTENER="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-core \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='InternalHttpListenerArn'].OutputValue | [0]" \
    --output text
)"
```

Inspect rules:

```bash
aws elbv2 describe-rules \
  --listener-arn "$INTERNAL_LISTENER" \
  --region us-east-1 \
  --output table
```

Expected final rule priorities:

```text
50
→ /catalogue
→ /catalogue/*

100
→ /api
→ /api/*

default
→ 404
```

The internal ALB is private. Do not expect to open its DNS name directly from the public internet.

---

## 4.9 Test Backend Target Group

Get the backend target group:

```bash
BACKEND_TG="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-core \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='BackendTargetGroupArn'].OutputValue | [0]" \
    --output text
)"
```

Check:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$BACKEND_TG" \
  --region us-east-1 \
  --query "TargetHealthDescriptions[*].{Target:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}" \
  --output table
```

Expected:

```text
2 healthy backend targets
```

---

## 4.10 Test Backend Auto Scaling Group

Get the name:

```bash
BACKEND_ASG="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-core \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='BackendAutoScalingGroupName'].OutputValue | [0]" \
    --output text
)"
```

Inspect:

```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$BACKEND_ASG" \
  --region us-east-1 \
  --query "AutoScalingGroups[0].{Min:MinSize,Desired:DesiredCapacity,Max:MaxSize,Instances:Instances[*].{Id:InstanceId,AZ:AvailabilityZone,Health:HealthStatus,State:LifecycleState}}" \
  --output json
```

Expected:

```text
Min = 2
Desired = 2
Max = 2
2 InService instances
```

---

## 4.11 Test Backend → Dummy DB Primary and Standby

Run:

```bash
curl "http://$ALB_DNS/api/db"
```

Expected result:

```text
database_tier
→ dummy primary/standby multi-AZ representation

primary
→ reachable

standby
→ reachable

all_reachable
→ true
```

This proves:

```text
Frontend
→ Internal ALB
→ Backend
→ DB Primary
→ DB Standby
```

It does **not** prove Oracle/RDS replication.

---

## 4.12 Test the S3 Image Bucket

Inspect security:

```bash
./scripts/part11_s3_test.sh info
```

Expected controls include:

```text
Block Public Access
server-side encryption
ownership controls
```

List objects:

```bash
./scripts/part11_s3_test.sh list
```

Expected:

```text
products/P1001.jpg
products/P1002.jpg
products/P1003.jpg
```

Optional download test:

```bash
./scripts/part11_s3_test.sh \
  download \
  products/P1001.jpg \
  /tmp/P1001-test.jpg
```

---

## 4.13 Test DynamoDB

Get table name:

```bash
TABLE="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-microservice \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTableName'].OutputValue | [0]" \
    --output text
)"
```

Scan:

```bash
aws dynamodb scan \
  --table-name "$TABLE" \
  --region us-east-1 \
  --projection-expression "product_id,#n,category,price,availability,image_key" \
  --expression-attribute-names '{"#n":"name"}' \
  --output table
```

Expected:

```text
P1001
P1002
P1003
```

---

## 4.14 Test ECR

Get repository:

```bash
ECR_REPO="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-microservice \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='EcrRepositoryName'].OutputValue | [0]" \
    --output text
)"
```

Check images:

```bash
aws ecr describe-images \
  --repository-name "$ECR_REPO" \
  --region us-east-1 \
  --query "imageDetails[*].{Tags:imageTags,Digest:imageDigest,Pushed:imagePushedAt}" \
  --output table
```

Expected:

```text
tag v1 exists
```

---

## 4.15 Test ECS / Fargate

Run the supplied test script:

```bash
./scripts/part12_test_catalogue.sh
```

It checks:

```text
frontend /
legacy backend /api/health
catalogue /catalogue/health
catalogue /catalogue/products
catalogue /catalogue/products/P1001
ECS service desired/running/pending counts
catalogue target health
```

Expected ECS state:

```text
status = ACTIVE
desired = 2
running = 2
pending = 0
```

---

## 4.16 Test Catalogue Target Group

The supplied test script already checks it.

Manual check:

```bash
CATALOGUE_TG="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-microservice \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='CatalogueTargetGroupArn'].OutputValue | [0]" \
    --output text
)"

aws elbv2 describe-target-health \
  --target-group-arn "$CATALOGUE_TG" \
  --region us-east-1 \
  --query "TargetHealthDescriptions[*].{Target:Target.Id,Port:Target.Port,State:TargetHealth.State,Reason:TargetHealth.Reason}" \
  --output table
```

Expected:

```text
2 healthy Fargate IP targets
```

---

## 4.17 Test Catalogue Endpoints

Health:

```bash
curl "http://$ALB_DNS/catalogue/health"
```

Products:

```bash
curl "http://$ALB_DNS/catalogue/products"
```

Single product:

```bash
curl "http://$ALB_DNS/catalogue/products/P1001"
```

Image URL:

```bash
curl "http://$ALB_DNS/catalogue/products/P1001/image-url"
```

The final request should return a short-lived S3 URL.

---

## 4.18 Test Product Cards and Images in the Website

Refresh:

```text
http://<ALB-DNS>/
```

Expected:

```text
P1001 product card
P1002 product card
P1003 product card
```

Each should show:

```text
image
name
category
price
availability
Add to cart
```

If metadata appears but an image does not, test:

```bash
./scripts/part11_s3_test.sh list
```

and:

```bash
curl "http://$ALB_DNS/catalogue/products/P1001/image-url"
```

---

## 4.19 Test Live Platform Status

On the storefront, check:

```text
Web Tier
→ HEALTHY
→ frontend instance ID
→ frontend AZ

Legacy API
→ CONNECTED
→ backend instance ID
→ backend AZ

Database Tier
→ CONNECTED
→ primary reachable
→ standby reachable
```

Press:

```text
Refresh
```

or:

```text
Refresh platform status
```

This is useful live-demo evidence.

---

## 4.20 Test SNS

Get the operations topic:

```bash
TOPIC_ARN="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-observability \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='OperationsTopicArn'].OutputValue | [0]" \
    --output text
)"
```

Send a test:

```bash
./scripts/part10_test_observability.sh \
  sns \
  "$TOPIC_ARN"
```

Expected:

```text
SNS publish request sent
```

Check the confirmed email inbox.

---

## 4.21 Test CloudWatch Alarms

List project alarms:

```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix anygroup-gp2 \
  --region us-east-1 \
  --query "MetricAlarms[*].{Name:AlarmName,State:StateValue,Metric:MetricName}" \
  --output table
```

Expected categories:

```text
frontend unhealthy target
frontend in-service capacity
public ALB target 5XX
backend unhealthy target
backend capacity below two
catalogue unhealthy target
```

Optional notification-path test:

```bash
ALARM_NAME="$(
  aws cloudformation describe-stacks \
    --stack-name anygroup-gp2-observability \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='BackendUnhealthyHostAlarmName'].OutputValue | [0]" \
    --output text
)"

./scripts/part10_test_observability.sh \
  alarm \
  "$ALARM_NAME"
```

This manually sets an alarm state for notification testing. It is not a substitute for the controlled failure test.

---

## 4.22 Test Frontend Auto Scaling

First obtain the public URL:

```bash
ALB_URL="http://$ALB_DNS/"
```

Generate a small load:

```bash
python3 scripts/part09_load_test.py \
  "$ALB_URL" \
  --requests 400 \
  --workers 20
```

Then monitor:

```text
AWS Console
→ EC2
→ Auto Scaling Groups
→ anygroup-gp2-frontend-asg
```

and:

```text
AWS Console
→ EC2
→ Target Groups
→ frontend target group
```

Auto Scaling is not instantaneous.

### Safety

The normal total is `7` EC2.

If the frontend scales from `2` to `4`:

```text
total = 9
```

Do not deliberately run an additional EC2 replacement/failure test while already at 9.

---

## 4.23 Test Frontend Failure and Replacement

Precondition:

```text
2 healthy frontend targets
frontend is not already scaled to 4
```

In the EC2 console, identify one frontend instance that belongs to the frontend ASG.

Terminate **one frontend instance**.

Expected:

```text
public ALB continues through surviving frontend
terminated target becomes unhealthy/deregistered
frontend ASG launches replacement
replacement joins target group
target group returns to 2 healthy targets
website remains available
```

Capture:

```text
ASG Activity
target health transition
replacement EC2
website still responding
```

Do not terminate the NAT instance.

---

## 4.24 Test Backend Failure and Replacement

Precondition:

```text
2 healthy backend targets
frontend is not at the 9-EC2 peak
```

Terminate **one backend ASG instance**.

Expected:

```text
internal ALB routes /api/* to surviving backend
/api/health remains available
Live Platform Status remains connected
backend ASG launches replacement
backend target group returns to 2 healthy targets
```

Capture:

```text
backend target group
backend ASG Activity
replacement instance
/api/health response
```

This is strong Reliability evidence.

---

## 4.25 Test Security Isolation

Verify:

```text
Frontend EC2
→ no public IP

Backend EC2
→ no public IP

Dummy DB Primary
→ no public IP

Dummy DB Standby
→ no public IP
```

Expected allowed flows:

```text
Internet → Public ALB :80
Public ALB → Frontend :80
Frontend → Internal ALB :80
Internal ALB → Backend :8080
Internal ALB → Catalogue :8080
Backend → DB :1521
```

Expected blocked/not exposed:

```text
Internet → Frontend directly
Internet → Backend directly
Internet → DB directly
Frontend → DB directly
Catalogue → DB directly
```

Do not add temporary public SSH/RDP rules just for the demo.

---

## 4.26 Suggested Evidence Capture Order

Capture evidence in this order so the final presentation is easy to follow:

1. CloudFormation — four stacks.
2. VPC and six subnets.
3. EC2 — seven baseline instances and AZ placement.
4. Public ALB and two healthy frontend targets.
5. Internal ALB `/api/*` rule and two healthy backend targets.
6. Dummy DB primary and standby in different DB subnets.
7. Modern AnyGroup Market storefront.
8. `/api/health` response showing backend instance/AZ.
9. `/api/db` showing primary and standby reachable.
10. ECS service with two running Fargate tasks.
11. `/catalogue/*` internal listener rule.
12. Catalogue target group with two healthy targets.
13. DynamoDB product records.
14. S3 product images and bucket security.
15. Product cards/images in the storefront.
16. CloudWatch alarms.
17. SNS confirmed subscription/test message.
18. Frontend or backend controlled failure/replacement evidence.

---

# Section 5 — Tear Down

## 5.1 Why Tear Down Is Important

The Learner Lab has a limited budget.

Do not leave the complete prototype running after you have finished deployment/testing/evidence capture.

The teardown script removes resources in dependency-aware order.

---

## 5.2 Run the Teardown Script

From the repository root:

```bash
./scripts/part13_teardown_all.sh
```

You will see a warning and be asked:

```text
Type DELETE to continue:
```

Enter:

```text
DELETE
```

For a non-interactive teardown:

```bash
./scripts/part13_teardown_all.sh --yes
```

---

## 5.3 Teardown Order

The script performs:

```text
1. ECR image cleanup
2. Delete microservice stack
3. Delete observability stack
4. Empty S3 bucket
5. Delete core stack
6. Delete network stack
```

Dependency order:

```text
Microservice
→ Observability
→ Core
→ Network
```

The S3 bucket must be empty before the core stack can delete it.

---

## 5.4 Verify CloudFormation Deletion

Run:

```bash
for stack in \
  anygroup-gp2-network \
  anygroup-gp2-core \
  anygroup-gp2-observability \
  anygroup-gp2-microservice
do
  echo -n "$stack: "
  aws cloudformation describe-stacks \
    --stack-name "$stack" \
    --region us-east-1 \
    --query "Stacks[0].StackStatus" \
    --output text 2>/dev/null || echo "NOT_FOUND"
done
```

Expected:

```text
anygroup-gp2-network: NOT_FOUND
anygroup-gp2-core: NOT_FOUND
anygroup-gp2-observability: NOT_FOUND
anygroup-gp2-microservice: NOT_FOUND
```

---

## 5.5 Verify No Project EC2 Instances Remain

Run:

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters \
    "Name=tag:Project,Values=INFOSYS735-GP2" \
    "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query "Reservations[].Instances[].{Id:InstanceId,State:State.Name,Name:Tags[?Key=='Name']|[0].Value}" \
  --output table
```

Expected after complete teardown:

```text
no remaining project instances
```

---

## 5.6 Final Console Check

Check these AWS Console areas for orphaned project resources:

```text
CloudFormation
EC2 Instances
Auto Scaling Groups
Load Balancers
Target Groups
ECS
ECR
DynamoDB
S3
CloudWatch
SNS
VPC
```

If the teardown script reports a deletion failure, inspect that stack's CloudFormation events rather than manually deleting random dependent resources.

---

# Quick End-to-End Command Sequence

For a normal clean deployment, the full sequence is:

```bash
# Enter project
cd ~/anygroup-gp2

# Region
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

# Check access
aws sts get-caller-identity

# Local/static validation
python3 scripts/part13_validate_iac.py

# AWS template validation
./scripts/part13_deploy_all.sh validate

# Foundation
./scripts/part13_deploy_all.sh \
  foundation \
  nhte538@aucklanduni.ac.nz

# Confirm SNS subscription in email

# Build/push image
./scripts/part12_build_push.sh \
  v1 \
  catalogue-service

# Seed catalogue
./scripts/part12_seed_catalogue.sh

# Upload images
./scripts/part11_s3_test.sh upload sample-images/P1001.jpg products/P1001.jpg
./scripts/part11_s3_test.sh upload sample-images/P1002.jpg products/P1002.jpg
./scripts/part11_s3_test.sh upload sample-images/P1003.jpg products/P1003.jpg

# Activate catalogue feature
./scripts/part13_deploy_all.sh \
  feature \
  v1

# Check all stacks
./scripts/part13_deploy_all.sh status

# Test catalogue and route coexistence
./scripts/part12_test_catalogue.sh

# Open storefront using the public ALB DNS

# When completely finished
./scripts/part13_teardown_all.sh
```

---

# Final Expected Working Prototype

```text
Customer
   │
   ▼
Public ALB
   │
   ▼
Frontend ASG
├── Frontend AZ A
└── Frontend AZ B
   │
   ▼
Internal ALB
├── /api/*
│     └── Backend ASG
│          ├── Backend AZ A
│          └── Backend AZ B
│                │
│                ├── Dummy DB Primary — AZ A
│                └── Dummy DB Standby — AZ B
│
└── /catalogue/*
      └── ECS/Fargate ×2
            ├── DynamoDB
            └── Private S3 product images

CloudWatch
→ SNS
→ confirmed operations email

CloudFormation
→ source of truth for infrastructure
```

The final website provides one visible demonstration of both architectural paths:

```text
Product cards
→ modern catalogue service

Live Platform Status
→ legacy backend + dummy DB path
```
