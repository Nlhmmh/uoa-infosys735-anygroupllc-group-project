# INFOSYS 735 Group Project 2 — Rubric and Assessment Checklist

Use this file to check the project against [instructions.md](instructions.md). Prepare the stakeholder pitch with [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md), and deploy/test with [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md).

The current version uses two NAT gateways and integrated RDS Oracle Multi-AZ. Local implementation checks do not establish a successful lab run. The older 6 October 2026 evidence used a NAT instance and dummy DBs; preserve its status separately and collect new evidence. Do not transfer old PASS results to current resources.

## Assessment coverage and checks before submission

| Assessment | Highest-band requirement | Where to demonstrate |
|---|---|---|
| Solution improvement, 10 marks | Clear architecture; additional feature well integrated; alignment with design principles explained | Slide 3 diagram walkthrough; pillar slides 5/7/10/11; complete assessment appendix |
| Basic infrastructure, 30 marks | Required components configured, functioning and clearly shown | Slides 5–7 configuration; 9 application behaviour; 10 operational evidence |
| Additional infrastructure, 20 marks | More than one integrated additional service; sound technical rationale and strong business value | CloudFormation, RDS/Secrets Manager, ECS/Fargate/ECR and DynamoDB configuration before the catalogue demonstration |
| Presentation, 40 marks | Clear stakeholder value proposition and sound flow; AWS Console demonstration; all members speak; within 15 minutes | Whole 12-slide recording, planned at 14:15 including navigation |
| Potential bonus, up to 5 | Four or more pillars assessed comprehensively | Operational Excellence, Reliability, Security and Cost Optimisation: specific principles, alignment, updates and limitations |

The additional **business feature** remains the CTO's microservices request, implemented as an independent Product Catalogue. RDS improves the retained application/database tier; it does not change the selected feature to demand forecasting. More AWS services alone do not guarantee higher marks.

### Submission checks

- [ ] The main recording prominently shows and narrates the final Task 1 architecture diagram, integrated catalogue feature and four-pillar design decisions.
- [ ] The actual prototype diagram matches four EC2, two AZ-local NAT gateways, real Oracle Multi-AZ RDS and two catalogue tasks.
- [ ] Original GP1 alignment/gaps are checked against the actual submission, with clear updates in the submitted appendix.
- [ ] Every required basic component is shown and functioning; basic and additional configuration precede the working catalogue demonstration.
- [ ] RDS is integrated through real SQL data, not just an instance visible in the console.
- [ ] All four members speak and the complete recording is within 15 minutes.
- [ ] No unverified zero-downtime, failover, scaling, restore, savings, changed-code rollback, PCI or production-capacity claim.
- [ ] Submit slideshow/PDF and a text file with an accessible recording URL.
- [ ] Every member completes TeamMates feedback for all other members; omission incurs the stated 10% penalty.

## Appendix A — Full four-pillar assessment for submitted slides

Use the following 25 principle areas to prepare readable submitted appendix slides. Describe business needs and architecture choices in the main client narration; the original-design comparison supports assessment. The “existing need/alignment” column is a prompt, not proof that GP1 omitted a control. Verify historical claims against the actual GP1/Task 1 artefacts. Use current production cost decisions from Slide 11 and preserve lab results as supporting evidence.

### A.1 Operational Excellence

| Principle area | Existing need / alignment to check | Proposed design / update | Prototype and evidence boundary |
|---|---|---|---|
| Business ownership | Stakeholder priorities exist; verify operating accountability | Name deployment, alert, database and cost owners; agree client acceptance criteria | Roles/procedures need actual assignment and review |
| Useful observability | Verify monitoring and response coverage | CloudWatch ALB/ASG/RDS signals, logs, SNS actions and dependency-aware checks | Capture actual metrics, delivered alerts and operator response |
| Safe automation | Verify provisioning consistency | Four connected stacks, bootstrap signals, rolling updates and one-command setup | Capture Events; local lint is not deployment proof |
| Small reversible changes | Verify service/release coupling | Independent catalogue route, immutable tags/digests and explicit reversal | Distinct code digests if claiming a code release; automatic rollback is a separate test |
| Refine procedures | IT team needs repeatable processes | Main setup/test/failover/teardown runbook; revise after experiments | Record team review and procedure improvements |
| Anticipate failure | Availability plans need exercises | Isolated EC2 recovery, real RDS failover and backup restore | Actual trigger, failed requests, restored service and data evidence needed |
| Learn from events | Verify incident feedback process | Record results, causes, responsibility and runbook updates | Do not invent completed reviews or incident outcomes |
| Managed services | Maintenance consumes team effort | Managed NAT, RDS/credentials, Fargate, DynamoDB and S3 | App/code/security responsibility remains; staff-time savings unmeasured |

AWS basis: [Operational Excellence principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/oe-design-principles.html).

### A.2 Reliability

| Principle area | Existing need / alignment to check | Proposed design / update | Prototype and evidence boundary |
|---|---|---|---|
| Automatic recovery | Verify health-based recovery design | ASG/ECS recovery, RDS Multi-AZ failover and owned alerts | Settings plus actual replacement/failover/alert observations |
| Test recovery | Verify recovery and restore acceptance | Explicit RDS failover, data preservation, EC2 recovery and backup-restore exercises | Changed primary AZ/stable endpoint/SQL rows do not prove whole-AZ recovery |
| Distributed capacity | Verify failure domains | Two-AZ web/app/tasks, same-AZ NAT routes and Oracle synchronous standby | Snapshot of placement is not an outage test; standby is not readable |
| Demand-based capacity | Promotions create uncertain peaks | Frontend target tracking; propose validated backend/task/database sizing | Observe scale-out and scale-in; visits/day are not requests/day |
| Automate changes | Verify configuration drift/change control | Reviewed templates, dependency ordering and controlled release updates | Show Events and successful current smoke; treat data changes separately |

AWS basis: [Reliability principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel-dp.html).

### A.3 Security

| Principle area | Existing need / alignment to check | Proposed design / update | Prototype and evidence boundary |
|---|---|---|---|
| Strong identity | Verify permissions and separation | No static AWS keys; managed DB secrets; SELECT-only app DB user; production scoped IAM roles | Shared LabRole can access master/app secrets; it is not scoped production IAM |
| Traceability | Verify security auditing | Record stack/releases; propose API/security audit and investigation signals | Logs and Events do not replace deployed CloudTrail/security audit |
| Layered protection | Prior attacks and valuable data require defence | Proposed edge controls; private tiers, SG boundaries, NACLs and origin restrictions | No deployed CloudFront/WAF claim; NACLs are broad |
| Security as code | Verify control drift | Authoritative templates, security matrix/fragments and local checks | Capture effective rules and negative access tests in AWS |
| Data protection | Verify classification/encryption | Encrypted private RDS/S3, managed credentials, controlled images; production transport protection | HTTP/shared role/private Oracle TCP without added TLS remain limits; no PCI claim |
| Reduce direct data access | Verify staff/application permissions | SELECT-only app user; seed admin operation explicitly through SSM; controlled administration | Lab admin identity remains broad; real sensitive/payment data is absent |
| Incident preparation | Attacks require an owned response | Alert, investigate, isolate, recover, preserve evidence and review | Team drills and production security controls need validation |

AWS basis: [Security principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec-design.html).

### A.4 Cost Optimisation

| Principle area | Existing need / alignment to check | Proposed production design / update | Prototype and evidence boundary |
|---|---|---|---|
| Financial management | CFO wants accountable expenditure and OPEX/CAPEX comparison | Client workload owner, budget, alerts and regular Finance review | Named owner and dated model required; Academy balance is not exact attribution |
| Consumption model | Uncertain promotion demand creates peak-capacity risk | Scale with demand while retaining resilience baseline; evaluate commitments after measurement | Frontend policy/on-demand services configured; actual scale-in/out needs evidence |
| Business efficiency | Verify useful-output/cost measures | Cost per successful catalogue request alongside latency/errors | Cost and output must use the same window; unknowns remain blank |
| Reduce routine operations work | Small IT team spends weeks patching | Evaluate managed NAT/RDS/Fargate/storage against bills, staffing, maintenance, migration and training | Managed services need not lower every bill; staff-time savings unmeasured |
| Attribute expenditure | Verify service/environment ownership | Tags and shared-cost allocation; normal/promotion/co-location scenarios at equivalent security/reliability | Include NAT processing/EIPs, Oracle Multi-AZ licensing/storage, secrets and other charges; teardown is temporary-environment evidence |

Use the production cost method and assumptions in Slide 11. The reported previous $0.60 lab usage is not a measured saving or current Oracle/NAT price forecast. RDS lab teardown explicitly removes synthetic data/backups without a final snapshot; production needs different retention rules.

AWS basis: [Cost Optimisation principles](https://docs.aws.amazon.com/wellarchitected/latest/framework/cost-dp.html).

## Appendix B — Console and runtime evidence checks

| Area | Console / functional demonstration | Required current evidence |
|---|---|---|
| VPC/subnets/AZs | Resource map, six subnet placements and tier routing | Two AZs; public/app/DB separation |
| NAT/IGW/endpoints | Each NAT gateway/EIP and local app route; IGW and S3/DynamoDB endpoint routes | Two available gateways in distinct AZ subnets; correct route associations |
| SG/NACL | Effective ingress/egress and NACL associations | Allowed backend SQL; denied frontend-to-RDS; broad NACL limitation explained |
| EC2/web/app | Two private frontend and two private backend instances | Bootstrap Events, metadata, healthy target groups and working routes |
| ALB/ASG | Public/internal schemes, listener rules, request tracking | Actual scale-out/scale-in and restored healthy capacity |
| S3 | Encryption/public blocking/policy/object keys | Three images; signed success and unsigned denial |
| SNS/CloudWatch | Topic/subscription and ALB/ASG/RDS metrics/actions | Confirmed subscription plus matching delivered alert; ownership |
| CloudFormation | Four stack status/Resources/Outputs/Events | Successful current deployment and dependencies |
| RDS/Secrets Manager | Private Oracle SE2, Multi-AZ/AZs, encrypted storage, backup settings, secret metadata | Real SQL orders/customer; never reveal password values |
| RDS recovery | Before/after primary AZ, stable endpoint, Events and probe | Failover trigger, preserved rows, actual interruption; restore separately |
| ECR/ECS | Immutable digest, AMD64 definition, private tasks/AZs and rollout | Two healthy tasks, distinct digests if changed-code release claimed |
| DynamoDB/catalogue | Schema/seed data, ALB rule and storefront/API | Integrated additional feature works alongside SQL-backed retained routes |
| Cost/lifecycle | Production comparison assumptions; temporary-resource teardown | Scoped zero-resource checks including NAT/EIP/RDS/backup/secret resources; no unsupported saving claim |

Use `scripts/lab.sh setup`, `test`, `load`, `failover`, `update` and `teardown` as documented in the main guide. Explicit failover changes the database; collectors and ordinary tests do not inject failures. Long experiments happen before the 15-minute recording, with dated evidence shown during it.

### Current evidence status

- Local checks verify structure, schema, embedded code, generated references and mocked behaviour only.
- A new lab run is required for this managed-service version, including actual Oracle/Secrets Manager/SSM permissions.
- The 6 October run remains historical. Its dummy connectivity is not real SQL/replication; old cleanup excludes the new resource types.
- The historical version-label update/reversal used identical image content, and historical load did not demonstrate scale-out.
- Preserve failed outcomes and replace main-slide placeholders only with current observed values.

See [part13_iac_evidence_checklist.csv](part13_iac_evidence_checklist.csv), [data/part13_static_validation_report.json](data/part13_static_validation_report.json) and [data/lab_evidence_review.json](data/lab_evidence_review.json). The CSV separates current status from older observations.

## Appendix C — Submission risks and sources

| Risk | Required action |
|---|---|
| Diagram shown without explanation | Narrate the whole request path, integrated catalogue, four pillars and design updates on Slide 3 |
| Console becomes an unrelated service tour | Locate components on the diagram and connect each to stakeholder value |
| Lab permissions deny Oracle/Multi-AZ/managed credentials | Save exact failure; assess a permitted design explicitly; no silent dummy fallback |
| Real DB visible but unused | Demonstrate SQL-backed `/api/db`, `/api/orders`, `/api/account` and failover/data preservation |
| More services treated as automatic marks | Show integration, rationale and functioning behaviour |
| Historical evidence presented as current | Label version/date and collect new managed-service results |
| Backup setting treated as restore proof | Conduct and capture a real restore before claiming it |
| Retained resources after teardown | Check DB snapshots/backups/subnet groups, secrets, NAT/EIPs and all matching resources |
| Unknown costs converted to numbers | State assumptions and preserve blanks; compare equivalent production service levels |
| Recording exceeds 15 minutes or omits a member | Rehearse the complete 14:15 plan including console navigation |

Primary sources: [assignment brief](instructions.md), [case study](AnyGroupLLC_case_study.md), the group's verified Task 1/GP1 submission, current templates and dated lab evidence. AWS principles are linked in Appendix A; use [NAT guidance](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-comparison.html), [RDS Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html), [RDS managed credentials](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-secrets-manager.html) and [Oracle licensing](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Oracle.Concepts.Licensing.html) for technical claims.
