# Member 3 — Step-by-Step Presentation Guide

Your part is **Slides 7–10**, covering security, database/catalogue configuration, the working website, and recovery/scaling results. You start after Member 2 and hand over to Member 4 for production costs.

Use this alongside [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md). It follows the same scripts and timing. [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md) remains the deployment guide.

**Preferred recording:** Show AWS Console pages for configuration/recovery, the website for the feature, and the inbox for an actually received SNS alert. Terminal/Session Manager is optional. JSON files, probe/load outputs and test summaries below are for private preparation and checking, not screens to show in the pitch.

**Read this guide before rehearsal. During recording, read only the quoted “Say” text.** The numbered actions tell you what to show while speaking. Detailed configuration checks are preparation, not extra narration. The script uses simple English; do not add a separate introduction or read every field.

## 1. Your timing and story

| Slide | Topic | Your elapsed time | Full recording time | Duration |
|---|---|---|---|---|
| 7 | How we protect access and data | 0:00–1:10 | 6:40–7:50 | 1:10 |
| 8 | Database and catalogue setup | 1:10–2:50 | 7:50–9:30 | 1:40 |
| 9 | Working orders, account and catalogue | 2:50–4:10 | 9:30–10:50 | 1:20 |
| 10 | Recovery and scaling test results | 4:10–5:40 | 10:50–12:20 | 1:30 |
| **Total** | **Your section, including navigation and handoff** | **5:40** | **6:40–12:20** | **5:40** |

Your client story is: **protect access → explain the additional services → show them working → show recovery and capacity results**. Keep the architecture connections visible: backend to Oracle; catalogue to DynamoDB/S3; frontend scaling; Oracle primary and standby.

Member 2 finishes with “Member 3 will explain security.” Start Slide 7 immediately. At the end of Slide 10, say “Member 4 will explain production costs.” Member 4 then starts Slide 11.

There are 326 quoted script words in your four slides. That is about three and a half minutes at the planning pace of 90 words/minute. The rest of your 5:40 is for pointing, pauses and prepared tab switches. Actual timing needs rehearsal. The full group aims for 14:00 with one minute spare; do not treat that spare minute as extra speaking time.

## 2. Prepare before recording

### Step 1 — Agree who controls the screen

1. Confirm with the group that you present Slides 7, 8, 9 and 10.
2. Agree whether you will click or another person will operate the screen while you speak. One operator must know the tab order below.
3. Replace “Member 4” in your final sentence with the person's name.
4. Put the same architecture diagram in your slides, or prepare a readable crop for each topic. Use the group's catalogue colour consistently.
5. Keep your notes on a second screen or printed sheet. Share only the presentation/console window.

### Step 2 — Rebuild after destroying all resources

Follow **A–K in order**, before recording. Run each block separately and wait for it to finish. Setup, rotation and failover must pass before you continue. Use this same CloudShell tab for the whole sequence.

The routine sequence is **setup → manual rotation → database failover → scaling to four → frontend termination/replacement → final check**. Use `scripts/lab.sh`; you do not need to run every numbered helper. Setup creates the services, seeds the test data and performs initial rotation automatically.

#### A. Start the lab and get the current project

1. Start AWS Academy Learners Lab, wait for it to be ready, then open the AWS Console.
2. Select **US East (N. Virginia), `us-east-1`**, and open the full **CloudShell** console.
3. In CloudFormation, confirm the previous four project stacks have finished deletion. Wait if any is still deleting; resolve failed deletion using the main guide before rebuilding.
4. Use **Actions → Upload file** to upload the current `anygroup-gp2-deployment.zip`. It contains the implementation and excludes all Markdown files and old raw evidence. Keep this guide open on your computer, along with your previously downloaded evidence.
5. Starting in CloudShell's home directory, extract into a fresh folder:

```bash
cd
MEMBER3_WORKDIR="anygroup-member3-lab-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$MEMBER3_WORKDIR"
unzip anygroup-gp2-deployment.zip -d "$MEMBER3_WORKDIR"
cd "$MEMBER3_WORKDIR"
chmod +x scripts/*.sh
```

If CloudShell already has the exact current source, use that project directory instead. Do not mix it with an older copy. [AWS CloudShell upload/download instructions](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html#step-4-upload-file).

#### B. Check tools and create a new evidence folder

Run from the extracted **project root**:

```bash
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""
aws sts get-caller-identity
python3 --version
python3 -m pip --version
docker info
```

The account must be your active Learners Lab account. CloudShell supplies AWS credentials. If Docker is installed but stopped, run:

```bash
sudo service docker start
docker info
```

Create one new run folder, separate from the 7–8 October evidence:

```bash
export MEMBER3_RUN_DIR="evidence_new/member3-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$MEMBER3_RUN_DIR"
printf 'Project directory: %s\n' "$PWD"
printf 'Evidence directory: %s\n' "$MEMBER3_RUN_DIR"
```

Keep the printed paths. If you reopen CloudShell, return to this project directory, re-export the region variables and set `MEMBER3_RUN_DIR` to the **existing run folder**. Do not generate another run name halfway through.

#### C. Set up the complete prototype

Replace the example email address with your SNS recipient:

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/setup" ./scripts/lab.sh setup your-email@example.com v2
```

A fresh ECR repository builds tag `v2`; an existing immutable tag is reused. The tag matches your presentation example, but does not prove a code-release/reversal test or guarantee the old digest. Show the actual running image later.

This one command validates templates, creates four stacks and the network/website/Oracle services, builds the catalogue image, seeds DynamoDB/S3/Oracle, deploys the rotation Lambda and schedule, waits for initial rotation, activates ECS, runs smoke checks and captures configuration.

**Wait for “Setup complete”.** RDS/Multi-AZ creation can take time; there is no fixed total setup duration. Keep the shell open. If a phase fails, inspect its output and stack Events before continuing. Partly created resources are not automatically removed.

| File below `$MEMBER3_RUN_DIR` | Check after success |
|---|---|
| `setup/rotation/summary.json` | Initial rotation `status: PASS`; SQL-backed APIs pass |
| `setup/smoke.json` | `status: PASS` |
| `setup/configuration/summary.json` | `status: CAPTURED`; no collection errors; inspect the captured security checks |

`CAPTURED` means configuration was collected; it is not a recovery/restore result. Initial rotation alone does not give the manual before/after comparison.

If preflight reports no compatible default Oracle option, the main guide documents `DB_INSTANCE_CLASS=db.t3.medium`. Use that only after checking the exact error and permitted option; it changes the instance class and cost. Keep the same setup arguments/evidence folder if retrying. Do not substitute a dummy database and keep the Oracle claims.

#### D. Confirm SNS and open the new website

1. Confirm the **new** SNS subscription using its confirmation email. Check it under **SNS → Topics → operations topic → Subscriptions**. Confirmation does not prove an alarm email was delivered.
2. Retrieve the new ALB DNS:

```bash
ALB_DNS="$(aws cloudformation describe-stacks \
  --stack-name "${CORE_STACK_NAME:-anygroup-gp2-core}" \
  --region "$AWS_REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='AlbDnsName'].OutputValue | [0]" \
  --output text)"
printf 'Website: http://%s/\n' "$ALB_DNS"
```

3. Open the URL. Check account/orders, three product images and `Apples` search. Save a dated screenshot for Slide 9. The old ALB URL and resource IDs may no longer work.

#### E. Test application-password rotation

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/rotation" ./scripts/lab.sh rotate
```

Allow up to ten minutes for rotation, plus the following smoke/configuration checks. Check `rotation/summary.json` for **PASS**, `sql_backed_apis: PASS` and `data_preserved: true`; check `rotation/smoke.json` for PASS. Prepare the app secret's schedule, linked Lambda and last-rotation field for Slide 8.

This supplies fresh evidence for “Our manual test passed.” It does not prove uninterrupted availability during rotation. Do not run failover or load at the same time. Keep failed outputs and resolve the cause before continuing.

#### F. Test database failover

After rotation has finished and the website works:

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/failover" ./scripts/lab.sh failover
```

The command deliberately reboots RDS with failover and **already probes `/api/orders`** during the interruption. You do not need a separate `part14_probe_availability.py` command for this database test. It allows up to ten minutes, then runs normal smoke/configuration checks after successful recovery.

Check `failover/summary.json`: **PASS**, primary AZ changed, endpoint unchanged and orders preserved. Keep `before.json`, `trigger.json`, `after.json` and `requests.jsonl` for the measured interruption/failure count.

Save RDS Events, primary/secondary AZs and the 5xx alarm state/history promptly in `failover/screenshots/`. Save an actually received alarm email if you want to claim delivery, hiding the personal address in the presentation. Wait for the command and following smoke check to finish before load. Temporary database errors are part of this observation.

#### G. Run the eight-minute scaling load

After failover has finished and the website works again:

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/scaling" ./scripts/lab.sh load
```

Wait about **eight minutes for the workload**, then for configuration capture. While it runs, watch **EC2 → Auto Scaling Groups → frontend group**:

1. **Automatic scaling:** target 50 requests per target per minute.
2. **Activity:** alarm-triggered capacity change and successful launches.
3. **Instance management:** new instances become InService/healthy.
4. **Target Groups → frontend group → Targets:** new serving targets become healthy.

Save dated screenshots in `scaling/screenshots/`. Do not manually raise desired capacity to make scaling appear successful.

Check the actual HTTP status counts in `scaling/load.json`. The command finishing is not proof of all HTTP 200 responses. Also inspect `scaling/configuration/frontend_activity.json`, `autoscaling.json` and `frontend_targets.json`: HTTP success alone does not prove new servers were created.

If the capture precedes healthy new targets, wait for the console to show health and collect an extra read-only snapshot in a separate folder:

```bash
python3 scripts/part14_collect_evidence.py \
  --output "$MEMBER3_RUN_DIR/scaling/after-warmup"
```

If scaling does not occur, preserve the result and use the main guide's scaling troubleshooting commands. Do not claim “two to four” without Activity/capacity/health evidence. Later scale-in is a separate observation; capture it before claiming it.

#### G.1. Terminate one frontend and verify replacement at desired capacity four

Do this after the load command has finished and **four frontend instances/targets are healthy**. The load was only the trigger for growth; its HTTP-result statistics will not be shown in your pitch.

1. Confirm frontend **Desired capacity = 4**, four InService instances and four healthy targets. Save the growth/health views. Keep automatic scaling enabled and leave desired capacity unchanged.
2. Use your existing CloudShell tab to capture the before-state and start a ten-minute functional probe in the background:

```bash
python3 scripts/part14_collect_evidence.py \
  --output "$MEMBER3_RUN_DIR/frontend-recovery/before"
python3 scripts/part14_probe_availability.py \
  "http://$ALB_DNS/catalogue/products/P1001" \
  --duration 600 --expect-json-key product.product_id --expect-json-value P1001 \
  --output "$MEMBER3_RUN_DIR/frontend-recovery/requests.jsonl" \
  > "$MEMBER3_RUN_DIR/frontend-recovery/probe.log" 2>&1 &
MEMBER3_PROBE_PID=$!
printf 'Probe PID: %s\n' "$MEMBER3_PROBE_PID"
```

The collector creates the parent folder. The probe checks the website/frontend-to-catalogue path and validates P1001; it does not terminate anything. Keep this CloudShell tab open. Its ten-minute duration is preparation time, not presentation time.

3. Open **EC2 → Instances**. Match an instance ID to the frontend ASG's Instance management list. Select **one frontend instance**, then **Instance state → Terminate instance**, and confirm. Use the EC2 Instances action; do not decrement ASG desired capacity. Do not select backend instances.
4. Record the selected ID and UTC trigger time in your notes/screenshot. Show that desired capacity remains four; healthy capacity may temporarily fall to three while replacement starts. Report the actual count rather than forcing that intermediate state.
5. Open **Auto Scaling Groups → frontend → Activity**. Capture the replacement cause, launch status and **new instance ID**. Show this separately from the two earlier demand-driven launches.
6. Wait for the replacement to become **InService** and for **four frontend targets to be healthy**. Verify a product request through the website. Running state alone is insufficient.
7. While four targets are restored, save a dated screenshot and collect the after-state. Then wait for the probe to finish:

```bash
python3 scripts/part14_collect_evidence.py \
  --output "$MEMBER3_RUN_DIR/frontend-recovery/after"
wait "$MEMBER3_PROBE_PID"
```

8. Inspect `frontend-recovery/requests.summary.json` and the detailed JSONL privately. Retain actual errors and successful responses; neither probe completion nor a configuration capture is a combined recovery PASS. Verify all conditions below.

| Recovery proof | What must be captured |
|---|---|
| Deliberate failure | Terminated frontend ID and recorded trigger time |
| Desired capacity unchanged | Before/after ASG desired count is four |
| Automatic replacement | Activity launch/cause and a new frontend ID |
| Restored serving capacity | Four InService/healthy instances and four healthy frontend targets |
| Functional path | Successful P1001 requests after replacement; actual failures retained |

If automatic scale-in changes desired capacity during the experiment, that changes the test conditions. Do not claim recovery to four from that run. Keep the actual result and repeat the controlled sequence after another **automatic** growth to four, or report recovery to the actual desired count. Do not manually increase capacity and describe it as demand-driven scaling.

Replacement and bootstrapping can take several minutes. Record the experiment beforehand; present its dated console captures or an edited console clip in Slide 10. Label cuts/faster playback. Keep the HTTP load summary for internal checks or an appendix, and show ASG growth and replacement in the main pitch. [AWS EC2 termination/replacement guidance](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-scaling-manually.html).

#### H. Check the final deployment

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/final-check" ./scripts/lab.sh test
./scripts/lab.sh status
```

Check `final-check/smoke.json` is PASS and `final-check/configuration/summary.json` has no collection errors. Refresh the website and check your Slide 9 actions.

Now follow **Step 3 onwards** to copy the new IDs and preload console tabs. Keep the resources running for rehearsal and final recording. Complete all experiments before your 5:40 presentation section.

#### I. Use the new results in your slides

| Presentation item | Source below `$MEMBER3_RUN_DIR` |
|---|---|
| Security configuration — Slide 7 | `setup/configuration/` or `final-check/configuration/`, plus current console |
| Rotation — Slide 8 | `rotation/summary.json` and metadata |
| Working website — Slide 9 | Current website and `final-check/smoke.json` |
| AZ switch/data preservation/failures — Slide 10 | `failover/summary.json`, `before.json`, `after.json`, `requests.jsonl` |
| Automatic capacity/healthy targets — Slide 10 | `scaling/configuration/`, screenshots and `after-warmup/` if needed |
| Frontend replacement — Slide 10 | `frontend-recovery/before/`, `after/`, Activity/ID screenshots and `requests.summary.json` |
| Load — internal check/appendix only | `scaling/load.json`; do not display its HTTP totals or latency in the main pitch |
| Alarm response — Slide 10 | `failover/configuration/alarms.json` and captured alarm history |

The **7–8 October dates/numbers elsewhere in this guide are historical examples**. A new run can have different failover duration, failure count, AZ direction, scaling time and HTTP results. Update the selected console event dates and any appendix figures to match the new measured results. The default Slide 10 does not display a numerical test report. If you use old evidence instead, keep its original date and identify it as historical.

This read-only command prints an overview and calculates the first observed failover interruption:

```bash
python3 - "$MEMBER3_RUN_DIR" <<'PY'
from datetime import datetime
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
for phase, name in (("setup", "smoke.json"), ("rotation", "summary.json"),
                    ("failover", "summary.json"), ("final-check", "smoke.json")):
    data = json.loads((root / phase / name).read_text())
    print(phase, "status:", data.get("status"))
    if phase == "failover":
        print("Primary AZ:", data.get("primary_az_before"), "to", data.get("primary_az_after"))
        print("Endpoint unchanged:", data.get("endpoint_unchanged"))
        print("Orders preserved:", data.get("orders_preserved"))
        probe = data.get("probe", {})
        if "samples" in probe and "successes" in probe:
            print("Failed samples:", probe["samples"] - probe["successes"])
load = json.loads((root / "scaling" / "load.json").read_text())
print("Load requests:", load["requests"], "HTTP status counts:", load["status_counts"])
print("Load seconds:", load["elapsed_seconds"])
samples = [json.loads(line) for line in
           (root / "failover" / "requests.jsonl").read_text().splitlines() if line.strip()]
first_failure = next((i for i, row in enumerate(samples) if not row["functional_success"]), None)
if first_failure is None:
    print("No interruption observed in these samples.")
else:
    recovered = next((row for row in samples[first_failure + 1:] if row["functional_success"]), None)
    if recovered is None:
        print("No successful response observed after the first failure.")
    else:
        start = datetime.fromisoformat(samples[first_failure]["timestamp_utc"])
        end = datetime.fromisoformat(recovered["timestamp_utc"])
        print("First observed interruption, seconds:", round((end - start).total_seconds(), 2))
PY
```

This interval is the first failed response to the next successful response, not the whole reboot or a guaranteed recovery time. Inspect remaining samples for further interruptions. The command does not verify scaling; use Activity and target evidence for that.

Keep measured failover figures in preparation or the submitted appendix. The default spoken Slide 10 uses RDS Events/status and working website orders; do not add a numerical probe report or terminal to its 1:30 slot.

#### J. Zip and download the evidence before recording

Save console screenshots under your current run folder, then run. Screenshots saved only on your computer are not automatically in CloudShell: upload them into the run folder before archiving, or add them to the downloaded evidence folder locally.

```bash
MEMBER3_ARCHIVE="member3-evidence-$(date -u +%Y%m%dT%H%M%SZ).zip"
zip -r "$MEMBER3_ARCHIVE" "$MEMBER3_RUN_DIR"
unzip -t "$MEMBER3_ARCHIVE"
printf '%s/%s\n' "$PWD" "$MEMBER3_ARCHIVE"
```

In the full CloudShell console, choose **Actions → Download file**, paste the printed absolute ZIP path, and download. Extract it locally to check the folders. Keep the infrastructure running for the live configuration/website demo. [AWS CloudShell download steps](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html#step-3-download-file).

#### K. Clean up after the final recording

After the group has recorded and saved its screenshots/results:

```bash
EVIDENCE_DIR="$MEMBER3_RUN_DIR/teardown" ./scripts/lab.sh teardown
```

Type `DELETE` when prompted. Check `teardown/summary.json` for PASS, zero matching active project resources and no collection errors. Teardown deletes the synthetic database/images; stopping the lab session alone is not teardown. Repeat **J** to download a new archive including cleanup evidence.

If a phase fails, keep its output and inspect the failing stack Events, Lambda logs or test summary. For Oracle preflight/AccessDenied errors, use the main guide and lab restrictions. Do not repeatedly run setup over the failure without understanding it.

If resources are already running and you only need another check, skip rebuilding and use:

```bash
./scripts/lab.sh status
EVIDENCE_DIR="evidence_new/presentation-check-$(date -u +%Y%m%dT%H%M%SZ)" ./scripts/lab.sh test
```

### Step 3 — Find the correct resources

Open **CloudFormation → Stacks**. The default stack names are `anygroup-gp2-network`, `anygroup-gp2-core`, `anygroup-gp2-observability` and `anygroup-gp2-microservice`. If the team used other names, use those. Outputs identify resources without guessing their generated names.

Copy these values into a private preparation sheet. Do not read IDs aloud.

| What you need | Where to find it | Your current value |
|---|---|---|
| Website DNS | Core stack → Outputs → `AlbDnsName` | [FILL BEFORE REHEARSAL] |
| Frontend security group | Core Outputs → `FrontendSecurityGroupId` | [FILL] |
| Public load-balancer security group | Core Outputs → `PublicAlbSecurityGroupId` | [FILL] |
| Backend security group | Core Outputs → `BackendSecurityGroupId` | [FILL] |
| Internal load-balancer security group | Core Outputs → `InternalAlbSecurityGroupId` | [FILL] |
| Database security group | Core Outputs → `DbSecurityGroupId` | [FILL] |
| Image bucket | Core Outputs → `CatalogueImageBucketName` | [FILL] |
| Database identifier | Core Outputs → `DatabaseInstanceIdentifier` | [FILL] |
| Application secret | Core Outputs → `DatabaseApplicationSecretArn`; default name `anygroup-gp2/backend-db` | [FILL] |
| Frontend Auto Scaling group | Core Outputs → `FrontendAutoScalingGroupName` | [FILL] |
| Catalogue repository | Microservice Outputs → `EcrRepositoryName` | [FILL] |
| Catalogue cluster/service | Microservice Outputs → `CatalogueClusterName`, `CatalogueServiceName` | [FILL] |
| Product table | Microservice Outputs → `CatalogueTableName` | [FILL] |
| Catalogue target group | Microservice Outputs → `CatalogueTargetGroupArn` | [FILL] |
| App subnet access list | Network Resources → `PrivateAppNetworkAcl` → physical ID | [FILL] |

The expected database name is `anygroup-gp2-rds-oracle`. Physical IDs, bucket suffixes, current primary AZ and image versions can change after a new setup. Use the current outputs for live views; keep the historical test date on saved evidence.

### Step 4 — Prepare your console tabs

Use bookmarks or a written tab order. Open the views below, select the correct resource and scroll to the needed fields. You should switch prepared tabs during recording instead of searching for services.

| Order | Tab/view | Ready position |
|---|---|---|
| 1–3 | EC2 → Security Groups → frontend, backend, database | Inbound rules, one group per prepared view |
| 4 | VPC → Network ACLs → private app ACL | Inbound/outbound rules and subnet associations |
| 5–7 | S3 → image bucket | Permissions, Properties and Objects → `products/` |
| 8 | RDS → database | Configuration and Connectivity & security fields |
| 9 | Secrets Manager → application secret | Rotation configuration, metadata only |
| 10 | ECR → private repository → Images | Running image tag and digest |
| 11–13 | ECS → cluster → catalogue service | Tasks/deployment, task network details and task definition |
| 14 | EC2 → Target Groups → catalogue group | Healthy targets |
| 15 | DynamoDB → product table → Explore table items | Three products and image references |
| 16 | Website | Legacy section; search empty; products loaded |
| 17–18 | Website platform status / ECS target health | Connected backend/database; healthy catalogue service |
| 19 | Backend Session Manager, optional | Read-only query output ready |
| 20 | RDS Events / database details | Correct test date, primary AZ, available state and endpoint |
| 21–23 | Frontend ASG Activity / captured capacity / target health | Alarm cause, two successful launches and four healthy targets |
| 24 | Frontend replacement Activity / Instance management / Targets | Old ID/new ID, desired 4 and four restored healthy targets; probe stays private |
| 25 | CloudWatch alarm History/Actions, plus inbox | Match alarm name, state/reason/time to the received SNS alert |

You do not need to keep every tab in one long row. Group/bookmark them by slide and close unrelated tabs. Screenshots can combine adjacent configuration fields when they cannot fit on one readable screen; label screenshots with their capture date. Keep the AWS Console as the main demonstration.

### Step 5 — Prepare the dated test evidence

For a fresh rebuild, use the **current-run paths in Step 2.I** first. The table below lists the older 7–8 October evidence as a historical reference. Keep its numbers only when presenting that dated run.

Inspect the following files privately before recording. Use them to validate your statements and choose the correct console event dates. Do not display the files, JSON or test summaries during the default pitch.

| Claim | Saved file under `evidence_new/` | Fields/result to prepare |
|---|---|---|
| Application password rotation passed | `rotation-20261008T025207Z/summary.json` | `status: PASS`, `rotation_enabled: true`, schedule `rate(30 days)`, `sql_backed_apis: PASS`, `data_preserved: true` |
| Checks passed after rotation | `rotation-20261008T025207Z/smoke.json` | PASS; SQL data, product/image checks and healthy targets |
| Database failover preserved data | `rds-failover-20261007T043910Z/summary.json` | Primary `us-east-1b` to `us-east-1a`; `endpoint_unchanged: true`; `orders_preserved: true`; 98 successes out of 143 samples |
| Observed interruption | Same folder: `requests.jsonl` | 45 failed requests; approximately 61 seconds from first failure to first success, as recorded in the main presentation guide |
| Scaling was automatic | `scaling-20261007T044349Z/configuration/frontend_activity.json` | `Cause`: alarm changed desired capacity 2 to 4; two launch entries with `StatusCode: Successful` |
| Four frontend servers served traffic | Same configuration folder: `autoscaling.json`, `frontend_targets.json` | Frontend desired 4; four healthy targets |
| Historical load — internal check/appendix only | `scaling-20261007T044349Z/load.json` | Keep for analysis; do not show HTTP counts in the main pitch |
| Alarm detected failover errors | Post-failover capture `20261007T044215Z/configuration/alarms.json` | Project target-5xx alarm in ALARM after failover; later captures may show OK |

Label 7 October failover/scaling results as **Recorded test — 7 Oct 2026**. Label the rotation result **Recorded test — 8 Oct 2026**. JSON timestamps are UTC. If the console uses another timezone, select UTC or explain the difference in the caption.

A current database primary AZ or frontend count can differ from the saved test. Show the current setting as current and the saved observation as historical. A newly created resource may not retain the old resource's Events or Activity. Use the saved captures when necessary; never present them as a live event.

## 3. Slide 7 — How we protect access and data

**Budget: 1:10. Full recording: 6:40–7:50.** Your goal is to explain how the design controls access after the client's previous attacks, and what production still needs.

### Prepare the security views

1. Open **EC2 → Network & Security → Security Groups**.
2. Find the frontend group using the ID from core Outputs. Select **Inbound rules**. Prepare the row with TCP **80** and source equal to the **public ALB security-group ID**.
3. Prepare the backend group's inbound row: TCP **8080**, source equal to the **internal ALB security-group ID**.
4. Prepare the database group's inbound row: TCP **1521**, source equal to the **backend security-group ID**. Check that there is no public-source database rule.
5. Write the source group's human name beside each ID in your notes. A source SG ID is an allowed service group, not an IP address.
6. Open **VPC → Network ACLs**. Select the project's private app ACL. Prepare its rules and subnet associations. These ACL rules are broad; do not claim they enforce every tier restriction.
7. Open the image bucket in **S3**. Under **Permissions**, prepare Block public access and the bucket policy containing the deny rule for insecure transport. Under **Properties**, prepare default encryption. Under **Objects**, open `products/` to show the three `.jpg` files.
8. Check the saved unsigned-image **HTTP 403** result privately; it is not an on-screen demo step. Do not test private access using a logged-in S3 “Open” button: that uses your authorised session. The website's signed links are the allowed image path.

The security-group view uses the console's rule list; no edits are needed. [AWS security-group rule guidance](https://docs.aws.amazon.com/en_en/vpc/latest/userguide/working-with-security-group-rules.html).

### Step 7.1 — Show approved traffic paths, 0:00–0:30

1. Briefly point to the private tiers on the architecture.
2. Switch to the three prepared inbound-rule views: frontend, backend, then database.
3. Point to **port** and **source group** in each row. Spend about ten seconds per view; speak across the three views.
4. On the database row, show that the backend group is the source. The rotation Lambda also uses this group; do not describe it as exclusive to backend EC2 instances.

**Say:**

> Your past attacks make controlled access important. These security groups allow specific service paths. The database accepts the backend group, which the rotation function also uses. The application user can read data only.

### Step 7.2 — Show subnet rules, 0:30–0:42

1. Switch to the prepared NACL.
2. Point to the broad rules and associated private app subnets.
3. Avoid opening an edit dialog or reading every rule number.

**Say:**

> Subnet rules are broad. Security groups provide the specific restrictions.

### Step 7.3 — Show private image storage, 0:42–1:00

1. Point to public-access blocking and the secure-transport policy in S3 Permissions.
2. Switch to prepared Properties/Objects views to show encryption and the three image keys.
3. Keep this view in S3 Permissions/Properties/Objects. The unsigned-request result stays in preparation; do not show signed URL queries.
4. Keep this to eighteen seconds; point without reading the whole policy.

**Say:**

> Storage is encrypted. Images are private. A temporary signed link lets the browser display an image; it does not identify the customer.

### Step 7.4 — State the production work, 1:00–1:10

1. Return to the architecture, with production controls marked as proposals.
2. Point to HTTPS, edge filtering and audit. Then move directly to Slide 8.

**Say:**

> Production still needs separate identities, HTTPS, attack filtering and audit.

**Know the limit:** Storage encryption is deployed; HTTPS at the website entry and extra Oracle transport encryption are not. Shared LabRole is a lab constraint. Frontend-to-database blocking is configured but has no direct negative-test evidence. Do not claim payment compliance or that attacks are impossible.

## 4. Slide 8 — Database and catalogue setup

**Budget: 1:40. Full recording: 7:50–9:30.** Show the additional components' configuration before using the catalogue on Slide 9.

### Prepare the additional-service views

1. Open **RDS → Databases → `anygroup-gp2-rds-oracle`**, or the current identifier from Outputs.
2. Locate the configuration/connectivity fields in advance. Console placement can change; look for the field labels in the table below.
3. Prepare **Secrets Manager → Secrets → `anygroup-gp2/backend-db` → Rotation configuration**. The settings may appear in a section rather than a separate tab. Do not choose **Retrieve secret value**.
4. Open **ECR → Private registry/repositories → your catalogue repository → Images**. Match the running task's image reference to the repository digest. Do not assume that a tag is active merely because it exists.
5. Open **ECS → Clusters → your catalogue cluster → Services → catalogue service**. Prepare running tasks, deployment status, task networking and task definition. Use subnet details to show each task's AZ if the task view does not display it directly.
6. Open the catalogue target group in **EC2 → Target Groups → Targets**. Prepare its two healthy targets as the serving check.
7. Open **DynamoDB → Tables → catalogue table → Explore table items**. Load the three items and the `product_id` / `image_key` columns. The action name may be “Explore items” in your console.

| RDS field | Expected prototype setting |
|---|---|
| Status | Available |
| Engine | Oracle SE2 |
| Licence model | License Included |
| Instance class | `db.t3.small` |
| Storage | 20 GiB gp2; encrypted |
| Multi-AZ | Yes |
| Primary and secondary AZ | Different AZs; use actual current values |
| Publicly accessible | No |
| DB subnet group | Project's private DB subnets |
| Automated backup retention | One day |

For this RDS **DB instance deployment**, the standby is managed and does not serve read traffic. You do not need a second separately listed database or a readable endpoint to prove the standby exists: show **Multi-AZ** and **secondary AZ**. [AWS Multi-AZ instance guidance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html).

### Step 8.1 — Show Oracle and its standby, 0:00–0:30

1. Briefly locate backend-to-Oracle on the diagram, then show RDS.
2. Point to Multi-AZ and the primary/secondary AZs.
3. Point to private access, encryption and backup retention. The remaining fields should be visible in the prepared view; do not read every value.
4. Keep the current database primary separate from the dated failover result on Slide 10.

**Say:**

> RDS keeps Oracle and a standby in another zone. The standby helps recovery but cannot serve reads. Backups are enabled. Failover briefly interrupts database access.

### Step 8.2 — Show application password rotation, 0:30–0:40

1. Switch to the application's secret Rotation configuration.
2. Point to automatic rotation enabled, **30 days**, linked Lambda and the last-rotation field.
3. Show the current last-rotation field in Secrets Manager. Check the PASS summary privately before filming; do not open it on screen.
4. Do not click “Rotate secret immediately” or show the password.

**Say:**

> Rotation is scheduled every thirty days. Our manual test passed.

The application's secret uses the project's Lambda to change both the stored password and Oracle password. The RDS-managed master secret is separate. The saved test proves completed manual rotation and successful checks afterwards; it does not prove uninterrupted access during rotation or a future scheduled run. [AWS rotation types](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html).

### Step 8.3 — Show the packaged catalogue software, 0:40–0:50

1. Switch to ECR Images.
2. Point to the active tag and digest. The saved 8 October run used `v2`; use the actual running version for the live demo.
3. Do not read the long digest or open image-building tools.

**Say:**

> This fixed image version identifies the catalogue software.

### Step 8.4 — Show the independent catalogue service, 0:50–1:15

1. Switch to the ECS service's prepared Tasks view. Point to desired/running count **2** and the completed deployment.
2. Show the tasks' private networking and different AZs through prepared task/subnet views.
3. Briefly show the task definition's image reference and **X86_64** setting.
4. Show the catalogue target group's healthy targets. This is the serving check; container health may show UNKNOWN if no container health check is configured.

**Say:**

> Fargate runs two catalogue tasks across two zones. We can release this service separately from the backend.

### Step 8.5 — Show product data and image references, 1:15–1:35

1. Switch to DynamoDB items.
2. Point to **P1001, P1002 and P1003** in `product_id`.
3. Point to `image_key`, such as `products/P1001.jpg`, and connect it to the S3 files shown earlier.
4. Do not edit items. Say why this separate service matters to the CTO.

**Say:**

> DynamoDB holds product details and image references. The images are in S3. This gives the CTO a practical first microservice.

### Step 8.6 — Move to the website, 1:35–1:40

1. Point to the catalogue branch on the diagram; its `/catalogue/*` route goes to this service.
2. Switch to the already-loaded website. The basic and additional configuration demonstration is now complete.

**Say:**

> Now, the working website.

**Know the limit:** An image tag/digest identifies software; it does not prove a tested code release and reversal. Production migration, Oracle licensing, data synchronisation and sizing still need work. Do not reboot, restore, rotate or build during this segment.

## 5. Slide 9 — Working orders, account and catalogue

**Budget: 1:20. Full recording: 9:30–10:50.** Show the website and AWS Console. Raw API JSON, smoke summaries and terminal output are not in the default flow.

### Prepare the views

1. Open the current `http://<AlbDnsName>/`. Check account/orders and three product images before filming.
2. Make Legacy system and Additional feature labels readable. Practise searching `Apples` and clearing it.
3. Prepare the website's Live platform status section, ECS catalogue Tasks, and catalogue Target Groups → Targets.
4. Verify smoke/API results privately. Keep Session Manager ready only if choosing the optional SQL substitution.

### Step 9.1 — Refresh orders/account, 0:00–0:20

Show Legacy system → Your account & orders. Click Refresh account & orders once. Point to Processing/Ready and Demo Customer/Active after loading.

**Say:**

> The legacy section reads orders and account data from Oracle. These orders are Processing and Ready. The demo account is Active.

### Step 9.2 — Show products/search, 0:20–0:40

Show Additional feature → Product catalogue. Point to images, enter `Apples`, show Fresh Apples, then clear the search. The cart remains a browser counter.

**Say:**

> The catalogue shows products and images. Searching for apples narrows the list. Both services are part of one website.

### Step 9.3 — Show connected services, 0:40–0:50

Scroll to Live platform status. Point to backend/database connected status and stored-order count. Do not open API JSON.

**Say:**

> The website status shows that the backend and database are connected.

### Step 9.4 — Show the serving catalogue in AWS, 0:50–1:10

Switch to prepared ECS Tasks and catalogue target health. Point to two running tasks and healthy targets. This is the default console cue.

**Say:**

> These two catalogue tasks are running. Healthy targets show the service can receive requests.

**Optional SQL instead:** You may replace this cue with the prepared Session Manager query below. Say, “Here are the stored Oracle rows. They are test data. Checkout is outside this prototype.” It replaces the ECS cue and its paragraph inside the same twenty seconds; no extra time or terminal waiting is added.

### Step 9.5 — Continue to reliability, 1:10–1:20

Return to the website or architecture. Advance to Slide 10 yourself. There is no member handoff here and no smoke-result screen.

**Say:**

> Our website works. I will now explain recovery and scaling.

### Optional SQL preparation — do this before filming

Oracle does not use the Aurora console query editor. Open **EC2 → Instances → a backend instance → Connect → Session Manager → Connect**. Use a backend instance, not the frontend, because the backend has the Oracle connection and driver.

Run the same read-only command as the main presentation guide:

```bash
sudo -i
set -a
source /etc/anygroup-backend.env
set +a

/opt/anygroup-backend-venv/bin/python - <<'PY'
import sys
sys.path.insert(0, "/opt")
from anygroup_backend import OWNER, connect

with connect() as db:
    with db.cursor() as cursor:
        for table in ("demo_orders", "demo_customers"):
            cursor.execute(f"SELECT * FROM {OWNER}.{table}")
            print("Table:", table)
            print([column[0] for column in cursor.description])
            for row in cursor:
                print(row)
PY
```

Expect the two orders and Demo Customer / Active. This command uses the existing connection without printing passwords. Keep the SELECT/output visible for recording; do not display environment-variable values or install clients during the demo. If it fails during preparation, use the default website/ECS console flow instead. Do not change the database or open public access to make it work.


## 6. Slide 10 — Recovery and scaling test results

**Budget: 1:30. Full recording: 10:50–12:20.** Use the AWS Console for RDS recovery, automatic frontend growth and replacement. Show the inbox briefly for a real received SNS alert. Do not show generated test evidence or terminal output.

### Prepare the console and email

1. Complete the experiments in Step 2 before recording. Verify their results privately; keep the resources running.
2. RDS → Databases → database → Events/Logs & events: prepare the actual failover event, primary AZ, available state and endpoint. Verify endpoint/data checks internally; show working website orders as the user-visible outcome.
3. EC2 → Auto Scaling Groups → frontend → Activity: prepare the demand alarm/cause that grew desired capacity from two to four. Prepare Instance management and frontend Target Groups → Targets.
4. Prepare the EC2 termination view or console-only recording, replacement Activity/new ID, unchanged desired four and four restored healthy targets. Use Step 2.G.1; Running state alone does not prove serving recovery.
5. CloudWatch → Alarms → the actual test alarm → History/Actions: prepare state transition, reason, event time and operations SNS action.
6. Open the corresponding received email. Match alarm name, old/new state, reason and event time against CloudWatch. Keep the useful subject/body visible and hide the recipient address, unrelated mail and subscription/unsubscribe links.
7. Prefer live console history/current state. To show the termination click, use a recording of the AWS Console and label any cut waiting period. No JSON-report or screenshot collage is required. Keep the long wait outside this 1:30 slot.

### Which SNS email should you show?

The current templates send **CloudWatch alarm-state notifications**, not direct emails for every ASG launch/termination. The capacity alarm triggers below two; terminating one of four leaves three, so that capacity rule is not breached. Other alarm conditions must actually occur before their alerts can be claimed.

Use the matching alert you actually received, for example `anygroup-gp2-alb-target-5xx` after RDS failover. Check the email's reason and event time; do not use a startup/missing-data alert as proof of a frontend failure. An SNS confirmation email shows subscription confirmation, and a manual published message tests delivery; neither proves metric-driven incident notification. [AWS alarm-to-SNS guidance](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Notify_Users_Alarm_Changes.html).

If you specifically want emails for instance launch/termination, ASG activity notifications must be configured separately; they are not currently enabled by these templates. For this presentation, a real CloudWatch-to-SNS alert is sufficient. Do not claim an ASG event notification was configured merely because the topic exists.

### Step 10.1 — Show RDS recovery, 0:00–0:20

Show RDS Events/current status and the selected primary AZ. Briefly show working website orders. No probe JSON or measured-count terminal is displayed.

**Say after verification:**

> RDS Events show the switch to the standby. The endpoint stayed the same. The website shows that our orders are still available.

### Step 10.2 — Show growth from two to four, 0:20–0:45

Show the demand alarm/cause in ASG Activity, both successful launches, four InService instances and four healthy targets. Do not open the load-result file.

**Say:**

> The scaling alarm increased frontend capacity from two to four. Both new servers became healthy. This was an automatic response to demand.

### Step 10.3 — Show frontend replacement, 0:45–1:10

Show one recorded EC2 termination, the old ID/new ID in Activity/Instance management, desired still four and four restored healthy targets. Verify the functional path privately and through the website. Use this paragraph only when replacement checks passed; otherwise state the actual result.

**Say after verification:**

> We then terminated one frontend server. Desired capacity stayed at four, and the group launched a replacement. We restored four healthy targets and verified product requests.

### Step 10.4 — Show the alarm and received email, 1:10–1:25

First point to CloudWatch History/Actions. Then switch to the prepared alert email, showing the matching alarm name, reason and time. It may be the RDS-failover alert; say which event it belongs to. Do not wait for new mail during recording.

**Say only when a matching email was received:**

> This email matches the alarm shown in CloudWatch. It confirms that the alert reached our operator.

**If no matching email arrived:** stay on CloudWatch Actions and say, “CloudWatch is configured to send alerts through SNS. Email delivery remains to be verified.” This replaces the email paragraph within the same fifteen seconds.

### Step 10.5 — Hand over, 1:25–1:30

Member 4 starts Slide 11. Your part finishes by full-recording time 12:20.

**Say:**

> Member 4 will explain production costs.

**Limits:** Console screenshots, a confirmed subscription or completed test commands do not prove every outcome. Verify replacement/health/working requests and actual email receipt before claiming them. No whole-AZ, uninterrupted failover, production-capacity or guaranteed recovery-time claim is made. Restore and scale-in remain separate tests. Logs and saved evidence remain useful internal support, even though the pitch stays in AWS Console/website/email.

## 7. What to do if a view is slow or something fails

| Situation | Your action | Short line if needed |
|---|---|---|
| Console view takes over ten seconds | Show its prepared dated screenshot; move on | “This is the configuration captured on [date].” |
| Session Manager is slow | Use the default ECS/target-health cue | The website already shows working orders/account |
| Old RDS Events/ASG Activity missing | Use a dated AWS Console recording; keep raw files private | “This console recording is from our test on [date].” |
| Frontend currently has two servers | Show current count, then the saved four-target result | “This capture shows the capacity created during the test.” |
| Product images stop loading | Refresh once if time allows; fix before the final take | “The live image request has failed. This capture is from the earlier successful test.” |
| Website/database unavailable | State the issue; use clearly dated evidence only for that take, then correct it before final recording | “The live service is unavailable. This is the result from the recorded test.” |
| You are behind schedule | Keep the default console flow; shorten repeated metadata or ECS health views | Keep the architecture connection, security, additional-service setup, working catalogue and recovery/scaling results |

Do not say a live test passed while an error is on screen. Fallback sentences are only for a problem; they are not extra planned narration. If you use one, use time saved by shortening repeated details or navigation.

## 8. Simple answers to likely questions

These are for preparation or later questions. Do not add them to the five-minute-forty-second script.

| Question | Short answer |
|---|---|
| Why can RDS be unavailable during failover? | It switches the primary database to the standby. Our test saw a temporary interruption, then requests worked again. |
| Does another AZ mean a readable replica? | This deployment has a recovery standby. It cannot serve application reads. |
| Why use a separate catalogue? | We can change and release that function separately while orders and account keep their existing path. |
| What does the rotation Lambda do? | It changes the application password in Oracle and Secrets Manager, tests database access, then makes the new secret version current. |
| Is the thirty-day rotation already proved? | The schedule is configured. Initial and manual rotations passed; a future scheduled run has not yet been observed. |
| Are product images public? | The bucket is private. The website gives a temporary signed link for an image. Anyone with that valid link can use it. |
| Is the SQL account read-only? | It has SELECT access to application data. It can change its own password for rotation; it cannot write application rows. |
| Did all load requests succeeding prove production capacity? | No. These were small HTML requests at about five per second. Production needs a realistic workload and peak-demand test. |
| Have we proved all recovery paths? | No. Even after frontend replacement is verified, scale-in, backup restore and production recovery targets need separate tests. |
| Is this the real .NET application and customer data? | Python represents the application, and the records are synthetic. Real migration is a later acceptance step. |

## 9. Your rehearsal and final checklist

1. Practise your four slides alone using the exact views, with a stopwatch starting at 0:00 for your part.
2. Reach Slide 8 by **1:10**, Slide 9 by **2:50**, Slide 10 by **4:10**, and finish by **5:40**. Optional SQL replaces the ECS cue; either version stays within the same 5:40 allocation.
3. Speak one sentence at a time. Pause briefly, point to the matching field, then continue. Do not fill quiet navigation time with extra technical detail.
4. Practise these terms: **A-Z**, **Oracle**, **Fargate**, **DynamoDB**, **standby**, **failover** and **rotation**. Say “load balancer” instead of repeating ALB, and “security group” instead of SG.
5. Rehearse once with Member 2's handoff and Member 4's start. Make sure the operator knows when Slide 11 begins.
6. Check the playback: can the client read the field you point to? Can they understand the design reason and the measured limit?

- [ ] Fresh rebuild and separate experiments completed; new evidence downloaded and changed Slide 10 figures updated.
- [ ] Right region and current resource IDs recorded privately.
- [ ] Security groups, NACLs and S3 views prepared; no secrets or signed queries on screen.
- [ ] RDS primary/secondary AZ, private access, encryption and backups visible.
- [ ] Application rotation metadata ready; current value and dated test result distinguished.
- [ ] ECR version matches running ECS tasks; two tasks across two AZs and target health visible.
- [ ] DynamoDB product/image references ready.
- [ ] Website shows refreshed orders/account, three product images and search.
- [ ] Default website/ECS flow ready; Session Manager is an optional substitution, not an extra demo.
- [ ] RDS failover, automatic 2-to-4 growth and verified frontend replacement labelled with test dates; load statistics omitted.
- [ ] Received SNS alert matches CloudWatch event/time; email delivery is claimed only if actually received.
- [ ] No unsupported uninterrupted failover, scheduled recurrence, production-capacity or savings claim.
- [ ] Handoff to Member 4 happens after Slide 10, by full-recording time 12:20.

The full principle assessment belongs in the submitted appendix prepared from [Rubric_and_Assessment_Checklist.md](Rubric_and_Assessment_Checklist.md). Your live section explains the client value and shows the implementation; it does not need to read the appendix tables.
