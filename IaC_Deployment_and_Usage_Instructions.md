# IaC Deployment and Usage Instructions

This is the main guide for deploying, using, testing and removing the AnyGroupLLC website prototype. Use [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md) to prepare the client pitch and [Rubric_and_Assessment_Checklist.md](Rubric_and_Assessment_Checklist.md) to check the submission.

The current implementation replaces the NAT EC2 instance with **two AZ-local NAT gateways** and the dummy database EC2 nodes with **private RDS Oracle SE2 Multi-AZ**. The backend performs real SQL queries. The previous 6 October 2026 evidence describes the older implementation; it does not verify these new resources. Local checks and lab results are separate.

## 1. Architecture and prerequisites

| Component | Current implementation |
|---|---|
| Region | `us-east-1` by default; `AWS_REGION` overrides it |
| Network | One VPC, six subnets in two AZs, IGW, two public NAT gateways with EIPs, custom NACLs |
| Private outbound | Application subnet A → NAT A; application subnet B → NAT B; S3/DynamoDB gateway endpoints |
| Website | Public ALB → private Apache frontend ASG → internal ALB |
| Retained application | `/api/*` → private Python demo backend ASG → real Oracle SQL queries |
| Database | Oracle SE2 License Included, `db.t3.small` default, 20 GiB gp2, encrypted, Multi-AZ primary/standby, private DB subnet group |
| Catalogue | `/catalogue/*` → two private Fargate tasks → DynamoDB metadata and private S3 images |
| Credentials | RDS-managed master secret; separate generated SELECT-only application credentials |
| Operations | Four CloudFormation stacks, bootstrap signals, rolling updates, CloudWatch/SNS, ECR immutable tags and pinned digests |
| EC2 capacity | Four baseline instances: two frontend + two backend. Frontend maximum 4 gives six total; rolling updates can temporarily add a replacement |

RDS is one CloudFormation DB resource with a managed standby, not two EC2 instances. The standby cannot serve application reads. `/api/orders` and `/api/account` read synthetic records from the primary through the stable RDS endpoint. DynamoDB remains the catalogue datastore; RDS supports the retained backend.

The prototype still uses HTTP on the application path, synthetic records and the shared LabRole/LabInstanceProfile. Oracle SQL traffic uses private TCP 1521 without an added TLS option group. Production needs validated TLS/Oracle transport protection, scoped IAM roles, edge-origin protection, auditing, migration and capacity validation. This is not a payment system or proof of PCI compliance.

### Required environment

Use AWS Academy Learners Lab and **AWS CloudShell** for the routine commands. Start the lab and open CloudShell from its AWS Console. CloudShell supplies AWS CLI credentials; do not paste credentials into files or recordings. AWS CLI, Python 3 and a working Docker daemon are required. Check:

```bash
aws sts get-caller-identity
python3 --version
docker info
```

If Docker is installed but stopped in CloudShell, start it and check again:

```bash
sudo service docker start
docker info
```

The existing `LabRole` and `LabInstanceProfile` must permit CloudFormation, EC2/VPC/NAT, ALB/ASG, RDS Oracle Multi-AZ, Secrets Manager/KMS service integration, SSM Run Command, ECR/ECS/Fargate, DynamoDB, S3 and CloudWatch/SNS. No custom IAM roles are created. Regional service availability does not prove lab policy permission; an AccessDenied response must be resolved against the actual Learners Lab restrictions.

Setup checks current Oracle 19 orderable options for the selected class, License Included, Multi-AZ and 20 GiB gp2 **before deploying the network**. It stops if no compatible option is advertised. If the lab permits `db.t3.medium` but the default class has no compatible option, use:

```bash
DB_INSTANCE_CLASS=db.t3.medium ./scripts/lab.sh setup your-email@example.com
```

The class changes the cost. Do not switch to BYOL without licences or silently substitute a different engine. If the lab denies Oracle/Multi-AZ/Secrets Manager, save the exact failure and revisit the configuration; this implementation does not fall back to dummy databases and claim success.

### Get the current project

Upload `anygroup-gp2-deployment.zip` to CloudShell and extract it into a **fresh directory**, so an older script/template is not accidentally used:

```bash
mkdir -p anygroup-managed-lab
unzip anygroup-gp2-deployment.zip -d anygroup-managed-lab
cd anygroup-managed-lab
chmod +x scripts/*.sh
```

If your previous deployment is still running, tear it down using its matching project version first. The supplied older run was already torn down. Routine setup is intended for a clean lab; it does not migrate or preserve production data.

## 2. One-command setup

From the extracted project root:

```bash
./scripts/lab.sh setup your-email@example.com
```

Replace the example address with the SNS recipient. Email is optional, but a confirmed subscription is needed to demonstrate email notifications. Setup cannot confirm the subscription for you: accept the SNS confirmation email yourself.

This one command performs the following sequence:

1. Check tools/Docker and validate the four CloudFormation deployment templates with AWS.
2. Check account identity, running EC2 capacity and orderable Oracle Multi-AZ options.
3. Deploy the network, core website/RDS, observability and catalogue foundation stacks.
4. Build and publish the AMD64 catalogue image to ECR if the requested immutable tag is absent; reuse an existing tag without overwriting it.
5. Seed DynamoDB and upload all three product images.
6. Use SSM on one backend to create/seed Oracle demo tables and a SELECT-only application user. Passwords stay in Secrets Manager and the backend; they are not printed or returned to CloudShell.
7. Activate the catalogue using the verified ECR image digest.
8. Wait for ECS/target health, run functional/security/database smoke checks and capture read-only configuration evidence.

Allow time for RDS creation and Multi-AZ provisioning. Keep the CloudShell session open. Long creation/failover operations should finish before recording the presentation. On any failed phase, the command exits without printing “Setup complete”; it does not silently delete partially created resources. Inspect the failing stack/command, then retry an appropriate phase or explicitly tear down.

### Optional arguments

```bash
./scripts/lab.sh setup your-email@example.com v1
```

`AWS_REGION`, `DB_INSTANCE_CLASS`, `NOTIFICATION_EMAIL` and `EVIDENCE_DIR` can be supplied as environment variables. Stack-name overrides are `NETWORK_STACK_NAME`, `CORE_STACK_NAME`, `OBS_STACK_NAME` and `MICROSERVICE_STACK_NAME`; keep the default `anygroup-gp2` resource prefix so evidence collection can attribute resources.

```bash
EVIDENCE_DIR=evidence/managed-baseline ./scripts/lab.sh setup your-email@example.com v1
```

New runs normally receive a UTC timestamp directory. Choose a new directory rather than overwriting a result you intend to submit. Repeating setup reseeds **synthetic** data and can reuse an immutable image; use a new image tag for changed application content.

### Expected outputs

Setup saves `smoke.json` and `configuration/summary.json` plus supporting JSON files. Retrieve the current storefront URL in CloudFormation → core stack → Outputs → `AlbDnsName`, or run:

```bash
aws cloudformation describe-stacks --stack-name anygroup-gp2-core \
  --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" --output text
```

Open `http://<AlbDnsName>/`. The page displays a **Legacy system** section with real order/account API data and an **Additional feature** section with catalogue products and images. Use Refresh account & orders to retry either legacy panel; failures are shown independently rather than replaced with hardcoded demo records. Important routes:

| Route | What it demonstrates |
|---|---|
| `/api/health` | Backend process and EC2/AZ identity; not DB readiness |
| `/api/db` | Real SQL access and seeded order count; no password or standby connection |
| `/api/orders` | Orders read from Oracle through the application DB user |
| `/api/account` | Synthetic customer read from Oracle |
| `/catalogue/health` | Catalogue process liveness and release version |
| `/catalogue/ready` | DynamoDB/S3 accessibility |
| `/catalogue/products` | Three seeded catalogue products |
| `/catalogue/products/P1001/image-url` | Short-lived signed HTTPS access to a private image |

The cart is a browser counter, not checkout. Do not record full signed URL query strings.

## 3. Routine commands

| Task | Single command |
|---|---|
| Set up the complete prototype | `./scripts/lab.sh setup your-email@example.com` |
| Check all four stack statuses | `./scripts/lab.sh status` |
| Repeat smoke checks and configuration capture | `./scripts/lab.sh test` |
| Publish/activate a catalogue image and verify it | `./scripts/lab.sh update v2` |
| Run the sustained frontend scaling load experiment | `./scripts/lab.sh load` |
| Force RDS failover and verify preserved SQL data | `./scripts/lab.sh failover` |
| Delete the synthetic deployment and check for orphans | `./scripts/lab.sh teardown` |

The numbered helper scripts remain available for diagnostics. You do not need to execute every helper for routine setup. `test` is read-only; `setup`, `update`, `failover` and `teardown` change the specified lab resources. `failover` deliberately interrupts the database and should be run separately from load/update experiments.

## 4. Lab verification and presentation evidence

### 4.1 Baseline checks

```bash
./scripts/lab.sh test
```

A smoke PASS requires real Oracle order/customer queries, available private/encrypted Multi-AZ RDS with a distinct standby AZ and automated backups, working catalogue products/images, denied unsigned image access, two running catalogue tasks in two AZs, a pinned digest and at least two healthy targets per service.

A configuration capture also checks four private EC2 instances, six project SGs, two available NAT gateways in different subnets, private task ENIs and RDS settings. It captures NAT/EIP metadata, route tables, RDS events and application-secret metadata. It never retrieves secret values. Missing API permissions result in PARTIAL/FAIL; empty reads cannot establish a security PASS.

In the console, show each application subnet's route to its same-AZ NAT gateway. Show Oracle connectivity through the backend SG and DB TCP 1521 rule; no public database access. The shared LabRole can access more AWS resources than a production service role even though the database application user is SELECT-only.

### 4.2 Database failover

```bash
./scripts/lab.sh failover
```

This command requests `reboot-db-instance --force-failover` on the core stack's RDS instance. It first verifies a working SQL-backed order response, then samples `/api/orders`, records the trigger, checks the RDS primary AZ/endpoint and compares order data before/after. It allows up to ten minutes and runs ordinary smoke/configuration checks after a successful failover.

A failover PASS requires an available Multi-AZ instance with a **changed primary AZ**, unchanged endpoint and the same non-empty order rows. Request failures are preserved in JSONL; a PASS does not mean zero interruption. Inspect `before.json`, `trigger.json`, `requests.jsonl`, `after.json` and `summary.json` in the failover evidence directory. Present the actual failed/successful sample counts and timeline. This is one deliberate DB failover, not a whole-AZ outage or production SLA.

Show RDS → Connectivity & security / Configuration, the primary and secondary AZs, automated backup settings and Events. Show CloudWatch RDS CPU/free-storage metrics and the configured SNS alarm actions. A Multi-AZ standby is not a readable replica.

### 4.3 Backup and restore

Backup retention is one day for the short-lived synthetic lab. Show the retention setting and `LatestRestorableTime` only once RDS has produced it. Multi-AZ is not a replacement for backups. A configured backup policy does not prove successful restoration.

For a restore demonstration, take a manual snapshot in the RDS Console, wait for it to become available, restore to a distinctly named **private** test instance using the existing DB subnet group/SG, and test real SQL data through a controlled backend session. Do not overwrite the working stack's endpoint. Delete the restored instance and manual snapshot afterwards. This optional experiment creates additional billable resources and is not part of routine setup. Record actual observations before claiming restore verification.

### 4.4 Frontend scaling

```bash
./scripts/lab.sh load
```

This generates 2,400 frontend requests over eight minutes at about 5 requests/s, then captures configuration/activity. The configured target is 50 requests per target per minute, with frontend minimum/desired 2 and maximum 4. The load is deliberately small and is not a production capacity benchmark. A successful HTTP load result does not prove scaling.

During the experiment, show EC2 Auto Scaling → frontend group → Activity, Instances and Automatic scaling; show its AWS-managed target-tracking CloudWatch alarms and `RequestCountPerTarget`. Record whether desired/in-service capacity actually rises, whether new targets become healthy and whether scale-in later returns to two. Do not run load during an image update, DB failover or manual instance failure. The baseline is four EC2 and the configured frontend peak is six, below the documented nine-instance EC2 lab ceiling.

If scaling does not occur, preserve the result and inspect:

```bash
aws autoscaling describe-policies --auto-scaling-group-name anygroup-gp2-frontend-asg
aws autoscaling describe-scaling-activities --auto-scaling-group-name anygroup-gp2-frontend-asg
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names anygroup-gp2-frontend-asg
aws cloudwatch describe-alarms
```

Use the actual ASG name from stack Outputs if it differs. Check the policy's ALB/target-group resource label, managed alarm state/history, minute-level metric, maximum capacity, suspended processes, warmup and account constraints. AWS-managed target-tracking alarm names may not begin with the project prefix; the console/all-alarm query is necessary. Duration alone is not a guaranteed fix.

### 4.5 EC2 recovery and notifications

For a frontend recovery experiment, start a functional probe in one CloudShell tab:

```bash
ALB_DNS=$(aws cloudformation describe-stacks --stack-name anygroup-gp2-core \
  --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" --output text)
python3 scripts/part14_probe_availability.py "http://$ALB_DNS/catalogue/products/P1001" \
  --duration 300 --expect-json-key product.product_id --expect-json-value P1001 \
  --output evidence/frontend-recovery/requests.jsonl
```

In the console, deliberately terminate **one frontend ASG instance**, noting its ID and trigger time. Do not terminate both tiers or manipulate the RDS standby. Capture ASG replacement Activity, restored two-target health and a matching delivered SNS notification after confirmation. The collector does not inject failures or prove recovery automatically. Configuration and subscription confirmation do not prove alert delivery.

### 4.6 Catalogue release and reversal

```bash
./scripts/lab.sh update v2
```

Change the catalogue source before publishing `v2` if demonstrating a changed-code release. Immutable tags are never overwritten; the script reuses an existing tag and says so. For an explicit reversal to the retained `v1` image:

```bash
./scripts/lab.sh update v1
```

Capture ECR digests, ECS rollout Events, task identity, health and functional smoke. Identical digests demonstrate a configuration/version-label change, not changed code. Explicit reversal does not demonstrate a triggered ECS circuit-breaker rollback. RDS data is not automatically rolled back with catalogue code; production needs data-migration compatibility planning.

### 4.7 Security and cost observations

The smoke check verifies signed image access and unsigned HTTP 403. For network denial, use SSM on a frontend to attempt a short TCP connection to the RDS endpoint/1521 and preserve the denied result; use the working backend SQL query as the allowed-path control. Do not display secret values in SSM output or recordings.

Keep a cost owner, dated pricing assumptions and measured run duration in [data/cost_model_inputs.json](data/cost_model_inputs.json). Include two NAT gateways/EIPs and processing, Multi-AZ Oracle licensing/storage/backups, Secrets Manager, both ALBs, EC2/EBS, tasks, storage, requests, logs and transfer. A Multi-AZ rate already accounts for its standby; do not multiply it twice. An Academy balance change is not precise workload attribution or a production forecast. The reported $0.60 belongs to earlier tests, not a measured cost for this implementation.

For the stakeholder pitch, use production normal/promotion/co-location scenarios at comparable reliability/security. Lab cleanup supports temporary-environment cost control; production customer-serving resources must remain available.

### 4.8 Historical evidence

`evidence/` and [data/lab_evidence_review.json](data/lab_evidence_review.json) preserve the supplied 6 October 2026 NAT-instance/dummy-DB run. That run recorded three successful baseline/configuration-update/reversal smoke checks, signed/unsigned image access behaviour, 273/280 successful probe samples and 1,200 HTTP 200 load responses without demonstrated scale-out, followed by cleanup. Both catalogue tags used the same image digest. These are historical observations only. Capture new evidence for NAT gateways, real SQL, RDS Multi-AZ/failover and updated cleanup before claiming those work in the lab.

### 4.9 Zip and download the evidence folder

Wait for the load, availability probe and other tests to finish before archiving their outputs. After running the teardown in Section 5, include its final cleanup evidence too. Save any console screenshots or notification captures you want to keep under `evidence/`.

From the **project root in CloudShell**, create a dated archive, check its integrity and print its absolute download path:

```bash
EVIDENCE_ARCHIVE="anygroup-gp2-evidence-$(date -u +%Y%m%dT%H%M%SZ).zip"
zip -r "$EVIDENCE_ARCHIVE" evidence/
unzip -t "$EVIDENCE_ARCHIVE"
printf '%s/%s\n' "$PWD" "$EVIDENCE_ARCHIVE"
```

The ZIP preserves all run folders inside `evidence/`, including JSON summaries, configuration captures and JSONL probe samples. It leaves the original evidence files in place. Keep historical and current runs in their separate dated folders.

Download it to your computer:

1. In CloudShell, choose **Actions → Download file**.
2. Paste the **absolute path printed by the command**, including the dated ZIP filename. Do not paste the `evidence/` directory path.
3. Choose **Download** and save the ZIP locally. Extract it to confirm the expected run folders and files are present.

If Download file is unavailable in the AWS Console's embedded CloudShell toolbar, open the full **CloudShell console** and use its Actions menu. These steps follow the [AWS CloudShell download instructions](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html#step-3-download-file).

Recreate and download a new archive if you collect more evidence afterwards. The evidence ZIP is separate from `anygroup-gp2-deployment.zip`, which contains the implementation and excludes live evidence.

## 5. Teardown and budget control

```bash
./scripts/lab.sh teardown
```

Type `DELETE` when prompted. For deliberately unattended removal of this synthetic lab:

```bash
./scripts/lab.sh teardown --yes
```

The sequence is catalogue → observability → empty image bucket → core/RDS → network/NAT/EIPs. It then checks tagged/named project resources, including RDS instances, snapshots/backups/subnet groups, Secrets Manager, NAT gateways and EIPs. When the core stack still exists, the wrapper records its managed-secret ARN and checks that specific secret after deletion. A repeated teardown with no stack uses project-prefix/tag checks.

**RDS `DeletionPolicy` and `UpdateReplacePolicy` are `Delete` for this synthetic lab. Teardown deletes its data and automated backups without a final snapshot.** This prevents retained DB snapshots accumulating charges after repeated tests. Preserve required screenshots/results first. Production requires a different retention/deletion policy and explicit data-protection approval. Manually created restore instances/snapshots must also be removed; the collector reports matching resources but does not delete them.

Verify a PASS with zero matching active resources. Inspect collection errors instead of accepting a PARTIAL result as cleanup proof. RDS creation/deletion can take longer than EC2. NAT gateways cannot be stopped; deletion ends their gateway-hour charges. Stopping the lab session alone is not the teardown procedure.

## 6. Diagnostics and advanced phase commands

Use CloudFormation Events on the failing stack first. A tool/lab permission failure is not proof that the architecture is functioning. Common issues:

| Failure | Check |
|---|---|
| Oracle orderable preflight fails | Lab engine/class permissions, regional Oracle 19 Multi-AZ/gp2 options; supported `DB_INSTANCE_CLASS` override |
| RDS/managed-secret creation denied | Lab's RDS, Secrets Manager and KMS service permissions; save the exact Event |
| Backend bootstrap signal fails | EC2 system log, SSM, `/var/log/cloud-init-output.log`, AZ-local NAT routes and Python package installation |
| SSM seed command fails | Run Command status, private RDS routing/SG, managed/app secret access; the script deliberately suppresses raw driver/password output |
| `/api/db` or `/api/orders` returns 503 | SQL credentials/schema/seed, RDS availability, SG/port and backend journal; health alone is not readiness |
| Image tag already exists | Reuse it for reversal or choose a new tag for changed code |
| ECS health/deployment fails | Digest/AMD64 architecture, task role permissions, logs, readiness, ALB routing and image availability |
| Teardown fails | Remaining dependants, non-empty S3, deletion protection or manual DB resources; inspect Events and rerun cleanup |

Advanced phase commands, when isolating a failure rather than repeating routine setup:

```bash
./scripts/part13_deploy_all.sh validate
./scripts/part13_deploy_all.sh foundation your-email@example.com
python3 scripts/part15_seed_database.py
./scripts/part13_deploy_all.sh feature v1
```

Foundation creates ECR/DynamoDB without requiring an existing image and preserves an already-active catalogue's activation parameters. Images and DynamoDB/S3 data must exist before feature activation. Credentials are retrieved only on the backend. Avoid `GetSecretValue` in the recording or any command that prints passwords.

## 7. Local validation and packaging

These commands run locally without creating AWS resources:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-validation.txt
python scripts/part13_validate_iac.py --require-lint --tests --write-report
python scripts/part13_package.py
```

The generated **`02-core-infrastructure-stack.template.json`** is semantically identical to the readable core YAML and is used for deployment and AWS validation. The synchroniser compresses the storefront HTML in user data so the template fits AWS’s 51,200-byte inline limit. The frontend decompresses it during bootstrap and fills in its EC2/AZ identity. Edit `frontend/index.html` rather than the generated payload. After editing `backend-service/app.py`, `frontend/index.html` or readable core YAML:

```bash
python scripts/sync_backend_template.py
python scripts/sync_security_reference.py
python scripts/part13_validate_iac.py --require-lint --tests --write-report
python scripts/part13_package.py
```

The validator checks core JSON/source consistency, CloudFormation schema/imports, user-data shell/embedded Python, storefront JavaScript and mocked regressions. The ZIP uses a source allowlist and excludes live evidence, credentials and the virtual environment. Local PASS does not establish lab deployment, IAM permission, RDS failover or actual spending.

Sources: [assignment](instructions.md), [case study](AnyGroupLLC_case_study.md), [NAT comparison](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-comparison.html), [RDS Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html), [RDS managed credentials](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-secrets-manager.html), [Oracle licensing](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Oracle.Concepts.Licensing.html), [DB CloudFormation reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-rds-dbinstance.html).
