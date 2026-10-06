# INFOSYS 735 Group Project 2 — Rubric and Assessment Checklist

Use this file to check the project and final submission against [instructions.md](instructions.md). It contains the full four-pillar assessment, rubric audit, evidence checks, submission risks and references moved from the presentation guide.

Create the slides and prepare the recording using [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md). Follow [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md) for deployment, testing and teardown. The target is the highest marking bands and substantive four-pillar coverage; bonus marks remain discretionary.

## Assessment coverage and checks before submission

### Highest-band requirements and where to demonstrate them

| Assessment | Highest-band requirement from the brief | Main slides / demonstration | Supporting appendix |
|---|---|---|---|
| Solution improvement, 10 marks | Integrated additional feature; clear new architecture; alignment and improvements explained against design principles | 2–5, 7, 10–12 | Full four-pillar assessment and GP1 comparison |
| Basic infrastructure, 30 marks | All required components configured, functioning and clearly presented | 5–7 configuration; 9 functionality; 10 monitoring/recovery/scaling | Component-to-console checklist |
| Additional infrastructure, 20 marks | More than one well-integrated additional component with technical rationale and business value | 5 CloudFormation; 8 ECS/Fargate, ECR, DynamoDB; 9 feature | Integration/data-flow details |
| Presentation, 40 marks | Clear solutions-architect pitch, strong value proposition, business/technical rationale and sound flow | All 12 main slides; console navigation included | Sources, limitations and questions |
| Potential bonus, up to 5 | Four or more pillars with a well-rounded design assessment | Operational Excellence: 5; Security: 7; Reliability: 10; Cost Optimisation: 11; summary: 2/12 | All principle areas, improvements and unresolved gaps |

### Submission checklist

- [ ] Main deck has updated production and actual lab diagrams with the new feature integrated.
- [ ] GP1 alignment/gap statements have been checked against the original submission.
- [ ] Four pillars have specific improvements, rationale, evidence and remaining limitations.
- [ ] Every basic component is configured and functioning, and shown in the AWS Console.
- [ ] More than one additional component is shown as part of a coherent feature, with business/technical rationale.
- [ ] Basic and additional configuration appears before the working additional-feature demonstration.
- [ ] No unsupported zero-downtime, scaling, changed-code rollback, savings, PCI or production-capacity claim.
- [ ] All four members speak; the complete recording is within 15 minutes.
- [ ] Graphs, counts, dates, digests and service names match the recorded run.
- [ ] Submit slides or PDF and a text file with an accessible recording URL.
- [ ] Every member completes TeamMates feedback for all other members; the brief states a 10% penalty for omission.

## Appendix A — Full four-pillar assessment for submitted slides

Create readable appendix slides from the following tables. Preserve the principle area, existing alignment/gap, improvement, evidence and limitation columns. Use two appendix slides for Operational Excellence and Security if required for text size; one or two each for Reliability and Cost Optimisation. These appendix slides are included in the submitted deck/PDF but do not need to be narrated within the 14:15 main sequence.

The principle areas below are paraphrases mapped to the current AWS framework. The GP1 column describes the retained proposal as documented in README.md; verify it against the original GP1 submission before using it as a historical claim. These tables assess selected controls and improvements; they do not claim the lab implements every production best practice.
### A.1 Operational Excellence

GP1 provided a managed-service/multi-tier operations concept. GP2 addresses manual provisioning, ambiguous release identity and limited operational evidence.

| Principle area | GP1 alignment / gap | GP2 response | Evidence and remaining limitation |
|---|---|---|---|
| Business ownership | Stakeholder needs identified; workload accountability unspecified | Bounded catalogue pilot, business acceptance criteria and named owner roles | OE-03; actual team names/client approval pending |
| Useful monitoring | CloudWatch/SSM proposed; signals not demonstrated | Application logs, target/capacity/error alarms, SNS, versioned responses and dependency readiness | OE-01/REL-03; delivery and operational response pending; production tracing/audit requires expansion |
| Safe operational automation | Infrastructure largely conceptual | Four stacks, dependency ordering, bootstrap signals, explicit SG defaults, preflight quota checks and repeatable scripts | OE-01; local validation passes; AWS Events and recreate test pending |
| Reversible release increments | Microservices direction proposed; rollback unproven | Catalogue-only routing, immutable image tags, digest pinning, ECS circuit breaker and controlled EC2 updates | OE-02; configuration update/reversal verified with the same digest; distinct application-code update and triggered rollback untested; route removal does not restore a legacy catalogue |
| Runbook maintenance | Small IT team needs repeatable processes | Deployment/test/incident/cleanup runbook; review procedure after each test | OE-03; reviews and process effectiveness unmeasured |
| Failure preparation | Multi-AZ design alone did not establish recovery | Separate EC2/task failure scenarios and continuous functional endpoint sampling | REL-02/REL-03; no AZ-outage or production DR validation |
| Lessons from incidents | No documented experimental feedback | Record trigger, failed samples, restoration, root cause and runbook change | OE-03; findings remain blank until tests run |
| Managed platforms | AWS services proposed to reduce operational burden | Fargate, DynamoDB and S3 for the bounded service | ADD-01; application/image maintenance remains the team's responsibility; time savings unmeasured |

Business value: the IT team can reproduce the pilot and identify/reverse a release without rebuilding the full backend. This is a proposed operational benefit until measured in the lab/client environment.

AWS basis: [Operational Excellence principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/oe-design-principles.html).

### A.2 Reliability

GP1 retained two AZs, load balancing, Auto Scaling and proposed RDS Multi-AZ. GP2 turns selected recovery behaviours into testable mechanisms.

| Principle area | GP1 alignment / gap | GP2 response | Evidence and remaining limitation |
|---|---|---|---|
| Automatic restoration | Redundancy designed; behaviour unverified | ELB health-based EC2 replacement, ECS desired-state recovery, unhealthy/capacity alarms | REL-01/REL-02/REL-03; actual recovery and notifications pending |
| Recovery exercises | No captured failure timeline | Manual single-instance/task failure plus request probes and capacity checks | REL-02/REL-03; observed recovery is not a contractual RTO; data restore is not tested |
| Distributed capacity | Multi-AZ layout retained | Two frontend/backend instances and two Fargate tasks; assert actual task AZ placement | REL-01 verified by saved AZ/target snapshots; dummy DB nodes do not replicate/fail over; the lab NAT is a single failure point |
| Measured demand | Production visit estimate does not determine sizing | Frontend request-count scaling with bounded sustained load and latency/status recording | REL-04; lab thresholds are deliberately small; backend/task demand scaling and production capacity are not validated |
| Automated changes | Proposed design lacked consistent update behaviour | Stack dependencies, startup signals, one-instance batches, pinned application images | OE-01/OE-02; updates temporarily permit one EC2 per tier; healthy customer flows require separate verification |

Production improvements retain AZ-local NAT paths, real database backup/restore/failover, appropriately sized compute and agreed recovery objectives. These are production design requirements, not resources deployed by the lab templates. `/catalogue/health` is process liveness; `/catalogue/ready` tests dependency access and product/image endpoints test the actual feature. Dependency failure should be diagnosed rather than restarting every healthy container.

Business value: reduce dependence on one web/app instance and gain evidence of how the pilot behaves during a failure. Do not claim zero downtime or support for 500,000 visits/day from small lab tests.

AWS basis: [Reliability principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel-dp.html).

### A.3 Security

GP1 proposed edge protection, private tiers, role-based administration, encryption and audit services. GP2 makes selected controls inspectable and adds negative tests, while identifying constraints explicitly.

| Principle area | GP1 alignment / gap | GP2 response | Evidence and remaining limitation |
|---|---|---|---|
| Roles and permissions | Least-privilege production IAM proposed | LabRole/LabInstanceProfile credentials, no static application keys, IMDSv2 on NAT/web/app/DB EC2 | SEC-01; the shared lab role is not least privilege; production task/execution/admin roles must be separated and scoped |
| Auditable changes | CloudTrail/Config proposed, not deployed here | Stack Events, immutable tags/digests, application logs and dated evidence captures | OE-01/SEC-03; app logs do not replace API/security audit; production audit configuration remains required |
| Layered controls | Edge/VPC/tier separation proposed | Private compute, internal ALB, tier ingress, NACLs, explicit default-egress suppression, non-root container and private S3 | SEC-01/SEC-02; NACLs remain broad and SGs enforce fine-grained isolation; no lab WAF claim |
| Controls as code | Security plan and implementation could drift | Authoritative templates, generated security matrix/fragments and static checks | SEC-01 effective rules verified; SEC-02 image denial verified; frontend-to-DB denied path still needs a test |
| Data protection | Private/encrypted storage and TLS proposed | S3/DynamoDB/ECR encryption, S3 HTTPS-only policy and short-lived signed image access | SEC-01/SEC-02; lab ALB/application HTTP is restricted to synthetic public products; production needs validated TLS on client/service hops and appropriate key/data controls |
| Controlled data access | Direct staff access/security scope undefined | Public read-only catalogue API; task credentials read metadata/images; no public DB/SSH/RDP | SEC-02; signed URLs are bearer access, not user authentication; production staff access and sensitive data scope need discovery |
| Incident response | CISO's previous attacks require a response process | Identify alert/affected endpoint, preserve evidence, isolate through IaC, reverse a bad release, verify and review | SEC-03; drill pending; production WAF/rate controls, origin restrictions and security auditing remain design work |

Production retains CloudFront/OAC, AWS WAF, Shield Standard, Secrets Manager/KMS and proposed audit services. Restrict the production ALB origin so clients cannot bypass edge filtering. Specify validated TLS endpoints/certificates for each relevant hop rather than presenting private HTTP as encryption. The prototype is not a payment service and does not establish PCI compliance.

Business value: give the CISO evidence that private tiers and image access behave as intended and make the production security gaps visible before launch.

AWS basis: [Security principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec-design.html).

### A.4 Cost Optimisation

GP1 proposed cloud elasticity and operating expenditure. GP2 adds resource lifecycle controls and a measurement protocol, rather than unsupported savings claims.

| Principle area | GP1 alignment / gap | GP2 response | Evidence and remaining limitation |
|---|---|---|---|
| Financial ownership | CFO concerns known; owner and attribution absent | Named cost role, budget checkpoints and blank cost/usage input model | COST-01; actual owner, rates and budget captures pending |
| Usage-based capacity | Elasticity proposed without working evidence | Frontend scaling, on-demand DynamoDB and short-lived lab resources | REL-04/COST-02; two ALBs and two tasks remain baseline charges; scale-in/cleanup need proof |
| Workload efficiency | No cost/output denominator | Proposed attributable cost per successful functional request; latency/error observations | COST-01; both quantities and the same measurement window are required; a lab result is not a production forecast |
| Managed operational work | Small team spends time on maintenance | Bounded service uses Fargate/DynamoDB/S3; retain legacy system during pilot | ADD-01/COST-01; managed platforms do not automatically lower every workload's bill; staff-time savings remain unmeasured |
| Expenditure attribution | Resource inventory/cleanup were not proven | Project/component tags, three-day logs, ECR image retention, inventory and dependency-aware teardown | COST-01/COST-02; tags require billing/usage evidence to show cost; orphan checks have a defined scope |

The gateway endpoints route S3/DynamoDB calls without the NAT path and have no additional endpoint charge; service/storage/request charges still apply. The single NAT is a documented lab cost/reliability trade-off, not the recommended production design. Include both ALBs, public IPv4, EBS, Fargate deployment peaks, transfer and observability when costing the solution.

Business value: the CFO receives an accountable pilot investment and evidence to compare the next step. Compare production options at equivalent resilience/security; do not quote invented percentages or imply that a smaller lab proves production savings.

AWS basis: [Cost Optimisation principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/cost-dp.html), [gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html).

## Appendix B — Rubric audit, evidence checklist and submission risks

The extracted rubric/evidence material below is a working checklist. It records design coverage and the supplied run; successful final demonstration, confirmed GP1 comparison and the completed deck/recording remain team tasks.

### B.1 Solution Improvement — 10 Marks

| Audit Item | Evidence | Status |
|---|---|---|
| Continues GP1 | Compare production recommendation to actual original submission | GP1 comparison must be confirmed |
| One additional feature | Strangler Fig microservices modernisation | Catalogue route and functional smoke verified; final pitch pending |
| Product catalogue correctly described as pilot | Feature documentation | Complete |
| Architecture improved rather than replaced | Production diagram specification and bounded extraction | Design documented; final slide graphic pending |
| Four selected Well-Architected pillars | Operational Excellence, Reliability, Security, Cost Optimisation | Design documented; partial runtime observations in the main guide, Section 4.27.6 |
| Existing strengths identified | Retained GP1/WAF assessment | Confirm against actual GP1 submission |
| Gaps identified | repeatability, recovery, security verification and cost attribution | Design documented; remaining experimental gaps identified in the main guide, Section 4.27.6 |
| Improvements mapped to business value | stakeholder sections | Complete |
| Trade-offs acknowledged | microservices/cost sections | Complete |
| Live evidence | deployment/demo | Saved runtime baseline verified; final console recording pending |


---

### B.2 Basic Infrastructure — 30 Marks

| Required Component | Final Design | Evidence Needed | Status |
|---|---|---|---|
| VPC | `10.0.0.0/16` | VPC console | Saved VPC configuration verified; console recording pending |
| 2 AZs | A + B | subnet/AZ view | Actual subnet/EC2/task distribution verified |
| Subnets | 2 public + 2 app + 2 DB | subnet view | Six-subnet configuration captured |
| NAT | NAT EC2 | routes/instance | Instance/routes captured and bootstrap-dependent stacks completed; failure resilience not tested |
| SGs | tier-based SGs | SG rules | Effective configuration verified; DB negative connectivity test pending |
| NACLs | public/app/DB | NACL associations | Rules and associations captured; broad rules acknowledged |
| ELB | public + internal ALB | listener/health | Rules and healthy target groups verified; console recording pending |
| Auto Scaling | frontend + backend ASG | ASG console | Two AZ-distributed ASGs captured; recovery/scale-out evidence incomplete |
| SNS | operations topic | confirmed email | Subscription confirmed at update; delivery evidence missing |
| CloudWatch | alarms/logs | alarm/log console | Alarm states captured; failure delivery/log demonstration pending |
| EC2 | 2 frontend + 2 backend + 2 DB + NAT | EC2 view | Seven-instance lab baseline verified |
| Web server | Apache | storefront | Storefront smoke verified |
| S3 | private product images | bucket security/objects | Private/encrypted bucket and product-image access verified |
| Web tier | frontend ASG | target health | Two healthy frontend targets verified |
| App tier | backend ASG / Fargate | target health | Two healthy backend/catalogue targets verified |
| DB tier | dummy primary/standby | `/api/db` + EC2 | Two dummy DB nodes and successful connectivity verified; replication absent |


---

### B.3 Additional Infrastructure — 20 Marks

| Additional Service | Integration | Business/Technical Value | Status |
|---|---|---|---|
| ECS/Fargate | `/catalogue/*` | independent service runtime | Running tasks/rollout and functional integration verified |
| DynamoDB | catalogue metadata | service-owned prototype store | Three seeded products verified by smoke |
| CloudFormation | all lab infrastructure | repeatability / identifiable changes | Four successful stack snapshots and deployment update verified |
| ECR | Fargate image source | container delivery | Push transcript and pinned running digest verified; both tags use same image |
| S3 relationship | image objects | scalable private media storage | All three private images verified by smoke |
| CloudWatch/SNS | service health | operational visibility | Alarm configuration and subscription verified; delivery evidence missing |


---

### B.4 Presentation — 40 Marks

| Requirement | Plan | Status |
|---|---|---|
| ≤15 minutes | 14:15 including all demos, plus 0:45 buffer | Rehearsal pending |
| All members present | 4-speaker allocation | Planned |
| Stakeholder pitch | presentation framed as recommendation to AnyGroupLLC CTO/CFO/CISO/IT leadership | Planned |
| Client-focused story | problem → recommendation → proof → value → trade-offs → next step | Planned |
| Updated architecture | Production/lab diagram specifications in this guide | Final graphical slides pending |
| CloudFormation live demo | show four stacks, status, resources and outputs in Management Console | Pending live |
| Core AWS live demo | VPC, EC2, ASGs, public/internal ALBs and target groups | Pending live |
| Application live demo | storefront + legacy `/api/*` path + DB connectivity | Saved smoke verified; presentation recording pending |
| Additional-feature live demo | ECS/Fargate, ALB catalogue rule, DynamoDB, S3 product images | Saved configuration and smoke verified; presentation recording pending |
| Observability live demo | CloudWatch alarms/logs + SNS subscription | Alarm/subscription snapshots captured; delivery/log/recording proof pending |
| Reliability evidence | frontend/backend replacement activity and target health | Probe captured interruption; post-failure replacement evidence missing |
| Technical rationale | feature/WAF/architecture | Complete |
| Business value | stakeholder mapping | Complete |
| Trade-offs | explicit | Complete |
| Strong ending | staged modernisation recommendation | Planned |

---

### B.5 Four-Pillar Bonus Readiness

All four pillars are selected and assessed in Appendix A, with dedicated presentation coverage. The supplied 6 October observations and remaining gaps are recorded in Section 4.27.6 of [the main instructions](IaC_Deployment_and_Usage_Instructions.md). Bonus readiness requires substantive explanations and evidence, not labels.

| Pillar | Required proof before a strong claim | Status |
|---|---|---|
| Operational Excellence | Successful stacks/bootstrap, update/reversal, operational ownership and runbook review | Stacks/configuration release verified; same image content; Events/owner/review pending |
| Reliability | AZ placement, functional request observations, replacement/full-capacity restoration and measured scaling | Baseline/probe/load verified; replacement/scaling/delivery evidence incomplete |
| Security | Effective rules/private addresses/S3 controls, denied access and clear production improvements/incident response | Configuration/unsigned image denial verified; DB negative test/drill pending |
| Cost Optimisation | Ownership, dated price/usage model, attribution boundaries and cleanup/budget evidence | Inventory/cleanup verified; owner/prices/usage/budget pending |

The lab does not implement every production best practice. Explain the production improvements and remaining discovery items, preserve the evidence boundaries and let the rubric assessment determine any bonus.

---

### B.6 Final Evidence Checklist

#### Architecture

```text
[ ] production architecture matches final feature
[ ] lab architecture matches actual deployment
[ ] production vs lab differences are clearly labelled
```

#### CloudFormation

```text
[ ] all 4 stacks successful
[ ] all 4 stacks shown live in AWS Management Console
[ ] Resources tab evidence captured
[ ] Outputs tab evidence captured
[ ] stack outputs/imports visible
[ ] latest templates used
[ ] no manually maintained duplicate infrastructure
```

#### Network

```text
[ ] VPC
[ ] 6 subnets
[ ] routes
[ ] NAT
[ ] NACLs
[ ] S3/DynamoDB endpoints
```

#### Core

```text
[ ] public ALB
[ ] internal ALB
[ ] 2 frontend targets
[ ] 2 backend targets
[ ] dummy DB primary
[ ] dummy DB standby
```

#### Website

```text
[ ] improved AnyGroup Market UI
[ ] product cards
[ ] product images
[ ] search
[ ] platform status
[ ] frontend ID/AZ
[ ] backend ID/AZ
[ ] both DB statuses
```

#### Catalogue

```text
[ ] ECR image
[ ] ECS service
[ ] 2 running Fargate tasks
[ ] 2 healthy catalogue targets
[ ] DynamoDB items
[ ] S3 images
[ ] /catalogue/products
[ ] /catalogue/products/P1001/image-url
```

#### Monitoring

```text
[ ] SNS confirmed
[ ] frontend alarms
[ ] backend alarms
[ ] catalogue alarm
[ ] catalogue logs
```

#### Reliability

```text
[ ] frontend failure/replacement
[ ] backend failure/replacement
[ ] actual successful/failed requests and capacity restoration recorded
[ ] Auto Scaling Activity History evidence captured
[ ] target-health evidence captured
[ ] backup screenshots ready for presentation
```

#### Cost / Cleanup

```text
[ ] budget captured
[ ] cleanup script tested
[ ] all stacks deleted when finished
[ ] S3 emptied
[ ] ECR cleaned
[ ] no orphaned EC2/ALB/ECS/S3/DynamoDB resources
```

---

### B.7 Final Risks Before Submission

The main remaining project risks are:

| Risk | Effect | Control |
|---|---|---|
| Updated core stack fails in lab | no final demo | inspect CREATE_FAILED event; fix evidence-based |
| Backend targets unhealthy | legacy demo fails | inspect user data/service/SG/internal ALB |
| Fargate role/service issue | catalogue unavailable | validate LabRole + ECS service events |
| Product images missing | storefront incomplete | verify S3 keys and image-url endpoint |
| SNS unconfirmed | notification demo fails | confirm email before test |
| Auto Scaling reaches 9 EC2 limit | replacement/scale conflict | do not combine peak scale and replacement tests |
| Budget exhausted | lab disabled | deploy/test/capture/teardown quickly |
| Slides diverge from deployment | credibility loss | update slides from final live architecture only |
| Demo is too long | presentation over 15 min | rehearse; keep console navigation pre-positioned |

---

### B.8 Final Recommendation

The final project recommendation is:

```text
KEEP
→ the documented GP1 tier/AZ design, after confirming the original submission

IMPROVE
→ operations through CloudFormation, monitoring and repeatable procedures

PROVE
→ operational repeatability, recovery, security isolation and cost lifecycle through dated evidence

PILOT
→ Product Catalogue as one Strangler Fig microservice

MEASURE
→ deployment independence, recovery, security behaviour, expenditure, team effort and business value

DECIDE
→ whether another function should be extracted
```

The most important project message is:

> **AnyGroupLLC does not need a risky full rewrite to begin modernising. It can retain the existing application boundary, extract one bounded service, operate old and new paths together, and use real evidence to decide the next step.**

---

## Appendix C — Source references and authoring checks

Use these sources in the submitted deck's references. Cite the assignment and case for requirements; cite AWS for principle definitions; cite the team's actual run for metrics and implementation observations. Label the original GP1 submission as a source only after locating and checking it.

| Source | Use |
|---|---|
| [instructions.md](instructions.md) | Marking bands, four-pillar bonus, console sequence, timing, submissions and TeamMates |
| [AnyGroupLLC_case_study.md](AnyGroupLLC_case_study.md) | Stakeholder priorities, current technology, demand assumptions and selected CTO question |
| [README.md](README.md) | Architecture, feature rationale and retained design assessment |
| [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md) | Main operational instructions and supplied runtime observations |
| Full templates in `cloudformation/` | Actual configured resources, routing, security and scaling |
| Supplied `evidence/` files | Actual results, versions, target/AZ snapshots and cleanup; raw files kept separately from deployment ZIP |
| AWS principle links in Appendix A | Current framework basis, paraphrased and applied to this project |

Before exporting the deck/PDF, verify the twelve main-slide titles, four speaker names, the 14:15 allocation, readable diagrams and all placeholders. Ensure the appendix remains readable at normal viewing size. Show unsuccessful observations accurately. A proposed production control, configured mechanism, saved runtime result and current live console state are four different evidence states; use the right label for each.
