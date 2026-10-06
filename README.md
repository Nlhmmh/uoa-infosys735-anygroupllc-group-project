# INFOSYS 735 Group Project 2 — Full Project Documentation

**Course:** INFOSYS 735 — Cloud Computing Architecture  
**Case:** AnyGroupLLC  
**Assessment:** Group Project 2  
**Production Region:** `ap-southeast-6` — AWS Asia Pacific (New Zealand)  
**Learner Lab Region:** `us-east-1`  
**Selected Additional Feature:** Incremental Microservices Modernisation using the Strangler Fig Pattern  
**Pilot Boundary:** Existing Product Catalogue function  
**Selected Well-Architected Pillars:** Operational Excellence, Reliability, Security and Cost Optimisation

**Assessment Target:** Four substantive pillar assessments and the highest rubric bands; bonus marks remain discretionary

**Infrastructure Source of Truth:** Four Learner Lab CloudFormation stacks

**Verification State:** Local checks and the 6 October lab baseline/configuration update/reversal/cleanup verified; recovery, scaling, notification delivery and cost evidence incomplete

**Main instructions:** [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md)

**Slide authoring guide:** [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md)

**Rubric checklist:** [Rubric_and_Assessment_Checklist.md](Rubric_and_Assessment_Checklist.md)

**Presentation Limit:** 15 minutes  
**Team Presentation:** All four speakers participate

---

## Document Purpose

This document is the complete project reference for the AnyGroupLLC Group Project 2 solution.

It combines:

- assignment and rubric requirements;
- case-study requirements;
- the retained Group Project 1 production architecture;
- the selected additional feature;
- Learner Lab constraints;
- the Well-Architected assessment;
- the final production architecture;
- the final Learner Lab architecture;
- networking and security;
- load balancing and Auto Scaling;
- monitoring and notification;
- S3;
- the Strangler Fig catalogue service;
- CloudFormation Infrastructure as Code;
- cost and cleanup controls;
- links to slide authoring in `Presentation_and_Slide_Content.md` and assessment checks in `Rubric_and_Assessment_Checklist.md`.

The project follows one traceability chain throughout:

```text
Assignment Requirement
        ↓
AnyGroupLLC Business Need
        ↓
Architecture Decision
        ↓
AWS Implementation
        ↓
Verification Evidence
        ↓
Business Value
        ↓
Presentation Evidence
        ↓
Marks
```

---


# 1. Final Requirements and Rubric Matrix

## 1.1 Assessment Structure

Group Project 2 has four base marking areas.

| Assessment Area | Marks | What High-Marking Work Requires |
|---|---:|---|
| Solution Improvement | 10 | One clearly integrated new feature, updated architecture, detailed Well-Architected evaluation, clear rationale |
| Basic Infrastructure | 30 | Required AWS infrastructure correctly configured, functioning, and demonstrated |
| Additional Infrastructure | 20 | More than one well-integrated additional AWS component, with technical and business justification |
| Presentation | 40 | Strong solutions-architect pitch, live evidence, good flow, technical reasoning, business value |
| **Total** | **100** | |
| Potential Bonus | **Up to +5** | Strong evaluation of four or more Well-Architected pillars with a genuinely well-rounded design |

The presentation is the largest individual marking area, but the presentation depends on working infrastructure and evidence.

---

## 1.2 Non-Negotiable Assignment Requirements

The project must:

1. continue from the AnyGroupLLC Group Project 1 solution;
2. select **one** additional feature from the case-study additional question;
3. assess the architecture against **four AWS Well-Architected pillars**, meeting the two-pillar minimum and targeting the bonus;
4. identify what was already strong in Group Project 1;
5. identify gaps;
6. improve the design where appropriate;
7. provide an updated architecture;
8. implement the required AWS infrastructure;
9. demonstrate the implementation;
10. explain technical rationale;
11. explain business value;
12. keep the stakeholder pitch within 15 minutes;
13. ensure every team member presents;
14. use evidence rather than unsupported claims.

---

## 1.3 Required Basic Infrastructure

The required implementation includes:

- VPC;
- Availability Zones;
- subnets;
- NAT server instance or NAT Gateway;
- Security Groups;
- Network ACLs;
- Elastic Load Balancing;
- Auto Scaling;
- SNS;
- CloudWatch;
- EC2;
- web server(s);
- S3 bucket(s);
- web tier;
- application tier;
- database tier.

The assignment permits dummy application/database EC2 instances where a real production application or database is unnecessary for the prototype.

That flexibility is important because Group Project 2 is testing architectural behaviour, not reproducing the full production estate.

---

## 1.4 Additional Infrastructure Requirement

At least one additional component is required for a pass.

More than one well-integrated additional component is expected for an A-range result.

The locked additional-service set is:

```text
Amazon ECS / AWS Fargate
→ catalogue microservice runtime

Amazon DynamoDB
→ prototype catalogue metadata

AWS CloudFormation
→ Infrastructure as Code for the complete environment
```

Supporting services:

```text
Amazon ECR
→ catalogue container registry

Application Load Balancing
→ Strangler Fig routing

Amazon CloudWatch
→ observability

Amazon SNS
→ notification

Amazon S3
→ product-image storage
```

These services form one coherent architecture rather than a collection of unrelated AWS services.

---

## 1.5 AnyGroupLLC Business Context

AnyGroupLLC is a large North American supermarket organisation expanding into New Zealand.

Relevant case-study characteristics include:

```text
Average website traffic
→ approximately 500,000 visits/day

Event / promotion traffic
→ can be much higher

IT team
→ approximately 15 people

Current operational problem
→ patching, infrastructure management and firefighting consume staff time
```

Existing technical environment:

```text
Frontend
→ Apache

Backend
→ .NET Core

Database
→ Oracle

Images
→ central image server
```

Group Project 1 already proposed moving product images to S3 and using a more resilient AWS architecture.

---

## 1.6 Stakeholder Requirements

### CTO

Main concerns:

- high availability;
- scalability;
- website resilience;
- successful New Zealand launch;
- productivity;
- interest in microservices;
- interest in personalisation.

Project response:

```text
Retain multi-AZ architecture
+
ALB / Auto Scaling
+
ECS/Fargate catalogue pilot
+
Strangler Fig migration
+
CloudFormation
+
monitoring
```

### CFO

Main concerns:

- cost;
- OpEx vs CapEx;
- forecasting;
- supply-chain performance;
- stockouts.

Project response:

```text
elastic infrastructure
+
cost-conscious Learner Lab prototype
+
managed services
+
repeatable cleanup
+
no unnecessary production-sized Oracle deployment in the lab
```

The project does **not** implement AI/ML forecasting because only one additional feature is required and the team selected microservices modernisation.

### CISO

Main concerns:

- security;
- previous DDoS-related downtime;
- customer trust;
- PCI/data/reputation risk.

Project response:

```text
CloudFront / WAF / Shield Standard in production
+
private application tiers
+
Security Groups
+
NACLs
+
private S3
+
SSM rather than inbound SSH/RDP
+
least-privilege production IAM
+
monitoring and audit services
```

The project must not claim full PCI compliance because the complete payment scope is not specified.

---

## 1.7 Group Project 1 Baseline to Retain

The production foundation from Group Project 1 remains valid and should be extended rather than replaced.

Retain:

```text
Region
→ ap-southeast-6

Availability
→ two AZs

VPC
→ 10.0.0.0/16

Public subnets
→ two

Private application subnets
→ two

Private database subnets
→ two

Edge
→ Route 53
→ CloudFront
→ WAF
→ Shield Standard

Web
→ internet-facing ALB
→ frontend EC2 ASG

Application
→ internal ALB
→ .NET backend EC2 ASG

Database
→ RDS for Oracle Multi-AZ

Images
→ private S3
→ CloudFront OAC

Management
→ Systems Manager
→ CloudWatch
→ CloudTrail
→ AWS Config
→ Secrets Manager
→ KMS
```

The Group Project 2 work adds:

```text
Strangler Fig catalogue microservice
+
DynamoDB prototype metadata
+
ECR
+
CloudFormation as source of truth
+
stronger monitoring/evidence
+
controlled failure testing
```

---

## 1.8 Requirements-to-Evidence Matrix

| Requirement | Architecture / Implementation Response | Evidence to Capture | Final Status |
|---|---|---|---|
| Continue GP1 | Production architecture retained and extended | Old-vs-new architecture explanation | Design complete |
| One additional feature | Strangler Fig microservices modernisation | Feature rationale + `/catalogue/*` route | Catalogue route and functional smoke verified; final pitch pending |
| Four Well-Architected pillars | Operational Excellence, Reliability, Security, Cost Optimisation | Principle assessment + live evidence per pillar | Design documented; partial lab evidence reviewed 6 October |
| VPC / AZs / subnets | Two-AZ VPC with six subnets | VPC console / CloudFormation | Saved lab configuration verified; console recording pending |
| NAT | NAT EC2 in lab; HA NAT Gateways in production | EC2/routes | Instance/routes captured and bootstrap-dependent stacks completed; failure resilience not tested |
| SGs / NACLs | Tier-based controls | SG/NACL console | Saved effective configuration verified; DB forbidden-flow test pending |
| ELB | Public + internal ALB | listeners/target groups | Rules and healthy target groups verified; console recording pending |
| Auto Scaling | frontend ASG + backend ASG | ASG activity / replacement | Two AZ-distributed ASGs captured; recovery/scale-out evidence incomplete |
| SNS | operations topic | confirmed subscription + test | Subscription confirmed at update; delivery evidence missing |
| CloudWatch | alarms + catalogue logs | alarms/logs | Alarm states captured; failure delivery/log demonstration pending |
| EC2 | frontend/backend/dummy DB | instance/AZ evidence | Seven-instance lab baseline verified |
| Web server | Apache frontend | storefront | Storefront smoke verified |
| S3 | private image bucket | security + objects | Private/encrypted bucket and product-image access verified |
| Web/app/DB tiers | frontend → backend → dummy DB | live platform status + AWS console | Functional smoke verified; dummy DBs do not replicate |
| Additional components | ECS/Fargate, DynamoDB, CloudFormation | console + routes + data | Working integrated baseline verified; console recording pending |
| Live demonstration | storefront + APIs + console | presentation evidence | Saved functional checks verified; presentation recording pending |
| 4 presenters | 4-speaker allocation | presentation plan | planned |
| ≤15 minutes | timed 12-slide plan | rehearsal timing | planned |

---

## 1.9 Unknowns That Must Not Be Invented

The following remain unknown unless the client or assignment provides further evidence:

- exact production SLA;
- numerical RTO;
- numerical RPO;
- exact promotional traffic multiplier;
- exact Oracle edition/version/features;
- Oracle licence model;
- complete PCI scope;
- complete payment architecture;
- exact production CPU/memory utilisation;
- exact production scaling thresholds;
- final production catalogue datastore;
- cross-region DR requirement.

These must remain:

```text
client discovery items
or
production validation items
```

rather than assumptions presented as facts.

---

# 2. Additional Feature Decision

## 2.1 Final Decision

The selected additional feature is:

> **Incremental Microservices Modernisation using the Strangler Fig Pattern**

The pilot extraction boundary is:

> **The existing Product Catalogue function**

The catalogue itself is **not** the new business feature.

AnyGroupLLC already has product catalogue functionality.

The new capability is:

```text
Existing backend function
        ↓
extract one bounded capability
        ↓
deploy it independently
        ↓
route selected traffic to it
        ↓
run it beside the existing backend
        ↓
observe and evaluate it
        ↓
decide whether further extraction is worthwhile
```

---

## 2.2 Selected Technical Pipeline

```text
Path-Based Routing
        ↓
ECS / Fargate Catalogue Service
        ↓
DynamoDB
        ↓
S3 image reference
```

Supporting delivery/operations:

```text
Docker source
→ Amazon ECR
→ ECS/Fargate

CloudFormation
→ infrastructure

CloudWatch
→ service visibility

SNS
→ operational notification
```

---

## 2.3 Why Strangler Fig Fits AnyGroupLLC

A big-bang rewrite would introduce unnecessary delivery and operational risk.

Strangler Fig allows:

- the old backend to continue operating;
- one function to be extracted;
- routing to be changed incrementally;
- rollback to remain practical;
- operational behaviour to be measured before wider adoption;
- the small IT team to learn incrementally;
- architecture modernisation without claiming the entire application must become microservices.

The pattern is especially suitable because the case does **not** prove that the existing application is monolithic or that every function should become a microservice.

The project therefore treats catalogue extraction as a controlled pilot.

---

## 2.4 Alternatives Considered

| Option | Why It Was Not Selected as the Main Feature |
|---|---|
| Personalisation | Business value is possible, but it adds data/ML scope and is less directly demonstrable within the project timeframe |
| AI/ML forecasting | Relevant to CFO, but data quality, model design and business validation would become the dominant project scope |
| Infrastructure automation only | Valuable, but CloudFormation is better used as an Operational Excellence improvement while the customer-visible feature remains microservices modernisation |
| Full microservices rewrite | Too broad, high risk, unnecessary for the assignment |
| Kubernetes / EKS | Adds orchestration complexity that is not justified for a small pilot |
| Service mesh | Unnecessary for a single extracted service |

---

## 2.5 Business Value

### For the CTO

- lower-risk modernisation;
- independent service deployment;
- isolated scaling;
- measurable pilot;
- clearer service boundary;
- easier future evolution if the pilot succeeds.

### For IT Operations

- smaller change scope;
- easier rollback;
- repeatable deployment;
- reduced dependence on manual configuration;
- better observability.

### For the CFO

- avoids a large rewrite before value is proven;
- supports staged investment;
- managed services reduce infrastructure-management burden;
- pilot results can inform future funding.

### For the CISO

- limits blast radius of the pilot;
- keeps new service behind private routing;
- retains layered security;
- allows independent monitoring.

---

## 2.6 Success Criteria

The pilot is successful if the team can prove:

```text
1. Existing website remains available
2. Existing backend remains available
3. /catalogue/* reaches the new service
4. Catalogue service can be deployed independently
5. Two Fargate tasks can remain healthy
6. Catalogue metadata is retrieved from DynamoDB
7. Product images are shown from private S3 through controlled access
8. CloudWatch can observe the service
9. Infrastructure can be recreated with CloudFormation
10. The new service can coexist with legacy functionality
```

---

## 2.7 Decision Gate After the Pilot

The pilot should not automatically lead to full microservices adoption.

The next extraction should only proceed after evaluating:

- deployment independence;
- operational burden;
- latency;
- failure isolation;
- team skills;
- data ownership;
- monitoring complexity;
- support cost;
- business benefit.

---

## 2.8 Key Trade-Offs

Microservices modernisation adds:

- network communication;
- more deployment units;
- more monitoring;
- service/data ownership decisions;
- possible distributed-data consistency issues;
- more operational knowledge requirements;
- additional cost.

Therefore the correct recommendation is:

> **Use microservices selectively where independent deployment/scaling and service ownership create sufficient value.**

---

# 3. Learner Lab Capability and Budget Validation

## 3.1 Purpose

The production design should not be copied literally into the AWS Academy Learner Lab.

The lab must prove:

```text
architecture behaviour
+
integration
+
security relationships
+
failure handling
+
observability
```

rather than production scale.

---

## 3.2 Region Restrictions

General Learner Lab access is restricted to:

```text
us-east-1
us-west-2
```

The project uses:

```text
us-east-1
```

Production remains:

```text
ap-southeast-6
```

This difference must be stated explicitly during the presentation.

---

## 3.3 IAM Restrictions

The Learner Lab restricts arbitrary IAM creation.

Pre-created identities:

```text
LabRole
LabInstanceProfile
```

Project use:

```text
EC2
→ LabInstanceProfile

ECS task role
→ LabRole

ECS execution role
→ LabRole
```

Production must instead use separate least-privilege roles.

The lab IAM model is a sandbox constraint, not the production recommendation.

---

## 3.4 EC2 Limits

Documented limits:

| Constraint | Learner Lab Position |
|---|---|
| Instance sizes | nano, micro, small, medium, large |
| Purchase model | On-Demand only |
| Maximum concurrently running EC2 | 9 per supported Region |
| Maximum concurrent vCPU | 32 |
| EBS maximum | 100 GB |
| Supported EBS examples | gp2, gp3, sc1, standard |
| Marketplace AMIs | unsupported |
| EC2 Fleet | unsupported |

Important warning:

```text
Do not intentionally approach dangerous account-wide instance thresholds.
```

The current final lab design uses:

```text
NAT EC2            1
Frontend EC2       2
Backend EC2        2
Dummy DB EC2       2
--------------------
Baseline           7
```

Frontend scale-out:

```text
Frontend 2 → 4
Total    7 → 9
```

Therefore the project reaches the Learner Lab maximum if the frontend reaches its configured maximum.

Do not run additional EC2 replacement/scaling experiments while already at 9.

---

## 3.5 RDS Restrictions

RDS is available, including engines such as Oracle.

However Learner Lab limits include:

- small instance-size classes only;
- storage up to 100 GB;
- gp2 constraints in the documented lab environment;
- Provisioned IOPS unsupported;
- Enhanced Monitoring unsupported;
- continued budget risk while RDS remains active.

The production RDS design should therefore not be recreated literally in the lab.

Instead the lab uses:

```text
Dummy DB Primary EC2
→ Private DB Subnet A

Dummy DB Standby EC2
→ Private DB Subnet B
```

These demonstrate:

- DB-tier isolation;
- two-AZ placement;
- backend connectivity;
- primary/standby architecture representation.

They do **not** implement RDS or Oracle replication.

---

## 3.6 Budget Constraint

Assignment budget:

```text
$50 per student
```

Budget display updates may lag; check the active lab documentation for its current update behaviour.

Therefore the displayed remaining budget is not a real-time meter.

Main cost risks:

```text
EC2
Application Load Balancers
NAT resources
Fargate tasks
RDS if created
unnecessary resources left running
```

Budget strategy:

```text
deploy
→ test immediately
→ capture evidence
→ remove temporary resources
→ tear down when finished
```

---

## 3.7 Supported Project Services

The Learner Lab documentation supports the major services needed for the prototype:

- VPC;
- EC2;
- EC2 Auto Scaling;
- Elastic Load Balancing;
- ECS;
- Fargate;
- ECR;
- DynamoDB;
- CloudFormation;
- CloudWatch;
- SNS;
- S3;
- Systems Manager;
- Route 53 DNS functionality;
- WAF;
- RDS;
- KMS;
- Secrets Manager;
- Config;
- CloudTrail with restrictions.

---

## 3.8 Services Requiring Caution

### Route 53

Route 53 DNS is available, but domain registration is not permitted.

The lab therefore does not depend on a purchased/custom domain.

### CloudFront

The supplied Learner Lab supported-service list did not explicitly confirm CloudFront.

Therefore:

```text
Production
→ CloudFront retained

Learner Lab
→ do not make the working prototype depend on CloudFront
```

### Shield

Shield remains part of the production security architecture but is not required for the Learner Lab demonstration.

### AWS WAF

WAF is available but is not necessary to prove the selected primary Well-Architected improvements.

It may be added only if the core implementation is stable and there is sufficient time/budget.

### CloudTrail

CloudTrail may be used conceptually/where supported, but CloudTrail-to-CloudWatch integration has Learner Lab restrictions.

---

## 3.9 Learner Lab Feasibility Decision

The selected project is feasible because the key implementation services are available:

```text
CloudFormation
VPC
EC2
Auto Scaling
ALB
CloudWatch
SNS
S3
ECR
ECS/Fargate
DynamoDB
```

The main constraint is not service availability.

It is disciplined use of:

```text
instance count
budget
IAM
Region
cleanup
```

---

# 4. Well-Architected Pillar Assessment

## 4.1 Four Selected Pillars

The project assesses **Operational Excellence, Reliability, Security and Cost Optimisation** as four selected pillars. Each assessment identifies the GP1 baseline, a gap, a GP2 response, evidence, stakeholder value and remaining limitations. Four-pillar coverage targets the assignment's potential bonus; a service list or pillar label alone does not establish alignment.

The original GP1 submission is not included in this repository. Its baseline below is the retained architecture summarised in this README, and should be checked against the submitted GP1 artefact before the final old-versus-new slide. Current AWS runtime verification is pending; earlier narrative references to a live network are historical statements, not current evidence.

## 4.2 Assessment and Evidence Method

```text
AWS principle → GP1 alignment → gap → GP2 design/implementation → evidence → business value → limitation
```

The tables paraphrase AWS's principles and map them to this project. They distinguish implemented source configuration, proposed production controls and unexecuted tests. Use Section 4.27 of `IaC_Deployment_and_Usage_Instructions.md` for the test sequence and evidence interpretation. Use `data/part13_static_validation_report.json` for current local checks; it does not establish runtime success.

| Responsibility | Proposed owner role | Required action before recording |
|---|---|---|
| Pilot business outcome | CTO / catalogue product owner | Confirm success criteria and further-extraction decision |
| Deployment and operations | Team operations owner | Assign a real name; run update/reversal and keep runbook current |
| Incident response and security | Team security owner; CISO for production | Assign a real name; review denied flows and incident drill |
| Cost and resource lifecycle | Team cost owner; CFO for production | Assign a real name; record assumptions, usage and cleanup |
| Evidence and presentation | All four presenters | Reconcile claims with dated captures; rehearse together |

These are proposed responsibilities, not a claim that the client has accepted an operating model.

## 4.3 Operational Excellence

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

## 4.4 Reliability

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

## 4.5 Security

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

## 4.6 Cost Optimisation

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

## 4.7 Assessment Summary

| Pillar | Main improvement | Evidence status | Stakeholder |
|---|---|---|---|
| Operational Excellence | Repeatable, identifiable and reversible deployment | Stacks and configuration update/reversal verified; same image content; ownership/Events review pending | IT manager / CTO |
| Reliability | Health-based restoration and measured recovery/scaling | Baseline/probe/load verified; replacement/scaling/delivery evidence incomplete | CTO |
| Security | Inspectable layered controls and denied-access tests | Effective configuration and image rejection verified; DB forbidden-flow test pending | CISO |
| Cost Optimisation | Ownership, usage measurement and complete resource lifecycle | Inventory/cleanup verified; owner/prices/usage/budget pending | CFO |

The bonus claim depends on the depth of this assessment, production improvements and captured implementation evidence. It is not a guarantee of marks.

# 5. Group Project 2 Full Production Architecture

## 5.1 Text Full Architecture Diagram

```text
                                  ANYGROUPLLC CUSTOMERS
                                           │
                                           ▼
                                   ┌──────────────┐
                                   │   Route 53   │
                                   │     DNS      │
                                   └──────┬───────┘
                                          │
                                          ▼
                    ┌────────────────────────────────────────┐
                    │              CloudFront                │
                    │     global delivery / edge cache       │
                    └───────────────┬────────────────────────┘
                                    │
                              AWS WAF│
                         Shield Std. │
                                    ▼
                       ┌─────────────────────────┐
                       │ Internet-Facing ALB     │
                       │ HTTPS / health routing  │
                       └────────────┬────────────┘
                                    │
                             Web traffic
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
               ▼                                         ▼
      ┌──────────────────┐                      ┌──────────────────┐
      │ Frontend EC2     │                      │ Frontend EC2     │
      │ Linux / Apache   │                      │ Linux / Apache   │
      │ AZ A             │                      │ AZ B             │
      └────────┬─────────┘                      └────────┬─────────┘
               │                                         │
               └────────────────────┬────────────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │      Internal ALB       │
                       │ private app routing     │
                       └────────────┬────────────┘
                                    │
                ┌───────────────────┴─────────────────────┐
                │                                         │
         /catalogue/*                              Existing API/default
                │                                         │
                ▼                                         ▼
   ┌──────────────────────────┐               ┌─────────────────────────┐
   │ ECS/Fargate Catalogue    │               │ .NET Backend ASG        │
   │ Service                  │               │ Windows EC2             │
   │ minimum multi-AZ tasks   │               │ multi-AZ                │
   └────────────┬─────────────┘               └────────────┬────────────┘
                │                                          │
                │                                          ▼
                │                              ┌─────────────────────────┐
                │                              │ RDS for Oracle          │
                │                              │ Multi-AZ                │
                │                              │ private DB subnets      │
                │                              └─────────────────────────┘
                │
                ├─────────────► production catalogue data boundary
                │               (final datastore after discovery)
                │
                └─────────────► image references
                                           │
                                           ▼
                                ┌──────────────────────────┐
                                │ Private Amazon S3        │
                                │ product images           │
                                │ versioning/lifecycle     │
                                └────────────┬─────────────┘
                                             │
                                      CloudFront OAC
                                             │
                                             └────────► customer image delivery


MANAGEMENT / OPERATIONS PLANE

CloudFormation
→ complete infrastructure definition

CloudWatch
→ metrics / alarms / logs

SNS
→ operational notifications

Systems Manager
→ administration without public SSH/RDP

CloudTrail
→ API audit

AWS Config
→ configuration/compliance visibility

Secrets Manager
→ secrets

KMS
→ key management / encryption controls
```

---

## 5.2 Logical Architecture Structure

The production architecture uses a layered structure.

```text
Edge
→ DNS / CDN / web protection

Presentation Tier
→ Apache frontend ASG

Application Routing Tier
→ internal ALB

Legacy Application Tier
→ .NET backend ASG

Modernised Service Tier
→ ECS/Fargate catalogue service

Data Tier
→ RDS for Oracle Multi-AZ
→ production catalogue data boundary

Object Tier
→ private S3 images

Operations Plane
→ CloudFormation / CloudWatch / SNS / SSM / audit/security services
```

The key Group Project 2 improvement is not the removal of the legacy backend.

It is controlled coexistence:

```text
Existing backend remains
+
new catalogue service operates independently
```

---

## 5.3 Networking and Security

### 5.3.1 Production VPC

```text
VPC
10.0.0.0/16
```

Subnet layout:

```text
AZ A
├── Public A        10.0.0.0/24
├── Private App A   10.0.10.0/24
└── Private DB A    10.0.20.0/24

AZ B
├── Public B        10.0.1.0/24
├── Private App B   10.0.11.0/24
└── Private DB B    10.0.21.0/24
```

### 5.3.2 Internet and NAT

Production:

```text
Internet Gateway
→ attached to VPC

NAT Gateway A
→ Public A

NAT Gateway B
→ Public B
```

Private app subnets use an AZ-local NAT path where practical.

DB subnets should not require a general public internet route.

### 5.3.3 VPC Endpoints

Retain:

```text
S3 Gateway Endpoint
```

If DynamoDB becomes the production catalogue datastore after discovery, use the appropriate private endpoint strategy for DynamoDB as well.

### 5.3.4 Public Exposure

Publicly reachable:

```text
CloudFront
Public ALB
```

Private:

```text
Frontend EC2
Internal ALB
Backend EC2
Fargate tasks
RDS
S3 origin
```

### 5.3.5 Production Security Group Flow

```text
Internet / CloudFront
        │
        ▼
Public ALB
HTTPS :443
        │
        ▼
Frontend SG
HTTP/private application port
        │
        ▼
Internal ALB SG
        │
        ├──► Backend SG : application port
        │
        └──► Catalogue SG : application port
                         │
Backend SG               │
   │                      │
   ▼                      └──► AWS services / data boundary
RDS SG
Oracle listener
```

Production should use final validated ports, certificates and application configuration.

### 5.3.6 Administration

Preferred:

```text
Systems Manager
```

Avoid:

```text
public bastion unless genuinely required
public SSH
public RDP
```

### 5.3.7 Edge Protection

Production retains:

```text
AWS WAF
→ request filtering / managed rules / rate controls

Shield Standard
→ baseline DDoS protection

CloudFront
→ edge absorption / caching / delivery
```

These directly support the CISO's concerns about prior availability/security incidents.

---

## 5.4 Core AWS Infrastructure

### Frontend

Production baseline retained from GP1:

```text
Linux / Apache
EC2 Auto Scaling Group
multi-AZ
baseline target: 2 instances
GP1 sizing target: m7i.large class
```

The exact production size must be validated with real traffic and utilisation.

### Backend

Production baseline:

```text
Windows / .NET Core
EC2 Auto Scaling Group
multi-AZ
baseline target: 4 instances
approximately 2 per AZ
GP1 sizing target: m7i.xlarge class
```

Again, final production sizing requires measured utilisation/load testing.

### Database

Production recommendation:

```text
RDS for Oracle
Multi-AZ
private database subnets
```

GP1 sizing target:

```text
8 vCPU
32 GiB memory class
2 TiB-class storage target
gp3 target
```

Do not claim an exact Oracle edition or licence model.

Those remain production discovery items.

### Catalogue Service

Production:

```text
ECS service
→ Fargate
→ minimum multi-AZ task placement
```

The Learner Lab task size `256 CPU / 512 MiB` is a prototype value only.

Production task sizing should come from load testing.

---

## 5.5 Load Balancing and Auto Scaling

### Public ALB

Role:

```text
CloudFront
→ Public ALB
→ Frontend ASG
```

Responsibilities:

- health-based frontend routing;
- TLS termination where selected;
- removal of unhealthy targets;
- stable application entry point.

### Internal ALB

Role:

```text
Frontend
→ Internal ALB

Internal ALB
├── /catalogue/* → Fargate catalogue
└── legacy/default/API → .NET backend
```

This is the production Strangler routing point.

### Frontend Auto Scaling

Production policy should be based on measured demand.

Possible metrics:

- ALB requests per target;
- CPU;
- latency;
- other workload-specific signals.

Do not copy the Learner Lab threshold of `50` requests/target/minute into production.

That low threshold exists only to make scaling demonstrable in a small sandbox.

### Backend Auto Scaling

Production backend should also scale according to measured demand and health.

### Fargate Scaling

The catalogue service can scale separately from the legacy backend.

This independent scaling is one of the strongest reasons to use an extracted service.

---

## 5.6 Monitoring and Notification

### CloudWatch

Production monitoring should cover:

#### Edge / ALB

- request count;
- 4XX/5XX;
- target response time;
- healthy/unhealthy host count.

#### Frontend

- ASG desired/in-service count;
- CPU/memory through appropriate agents/metrics where required;
- application logs;
- replacement events.

#### Backend

- target health;
- capacity;
- errors;
- latency;
- application logs.

#### Catalogue

- ECS running/desired tasks;
- target health;
- container logs;
- errors;
- latency.

#### Database

- CPU;
- storage;
- connections;
- DB health;
- backup/failover signals.

#### Security

- WAF blocked requests;
- unusual traffic;
- CloudTrail activity;
- Config state where relevant.

### SNS

Operational alarms publish to an operations SNS topic.

Production notification destinations should follow the client's operational process.

---

## 5.7 S3

### Production Role

S3 stores product images.

Recommended production path:

```text
Customer
→ CloudFront
→ OAC
→ private S3
```

### Controls

Use:

```text
Block Public Access
BucketOwnerEnforced
server-side encryption
HTTPS-only access
versioning
lifecycle management
```

Production retention/versioning requirements should be aligned with business recovery and governance requirements.

### Catalogue Relationship

The service should store/reference:

```text
image_key
```

rather than storing image bytes inside DynamoDB.

Example:

```text
product_id = P1001
image_key  = products/P1001.jpg
```

---

## 5.8 Strangler Fig Catalogue Microservice

### Production Flow

```text
Frontend request
        ↓
Internal ALB
        ↓
/catalogue/*
        ↓
Catalogue Target Group
        ↓
ECS/Fargate Service
        ↓
Catalogue data boundary
        ↓
S3 image reference
```

### Deployment Flow

```text
Catalogue source
        ↓
Docker build
        ↓
ECR
        ↓
ECS/Fargate
```

### Observability

```text
Container stdout/stderr
→ CloudWatch Logs

Target health
→ CloudWatch Alarm
→ SNS
```

### Prototype vs Production Data

Learner Lab:

```text
DynamoDB
→ prototype service-owned catalogue metadata
```

Production:

```text
final catalogue data strategy
→ must be decided after dependency/data-ownership discovery
```

Do not claim DynamoDB is automatically the final production replacement for Oracle catalogue data.

### Non-Goals

The pilot does not:

- migrate the full backend;
- migrate the full Oracle database;
- prove all functions should become microservices;
- redesign payment;
- redesign checkout;
- add personalisation;
- add AI forecasting;
- define RTO/RPO;
- implement multi-region DR.

---

## 5.9 CloudFormation Infrastructure as Code

CloudFormation is the project infrastructure source of truth.

### Stack Structure

```text
01-network-stack.yaml
        ↓
02-core-infrastructure-stack.yaml
        ↓
03-observability-stack.yaml
        ↓
04-microservice-stack.yaml
```

### 01 — Network

Owns:

```text
VPC
6 subnets
Internet Gateway
route tables
NAT EC2 in lab
NACLs
S3 Gateway Endpoint
DynamoDB Gateway Endpoint
network exports
```

### 02 — Core

Updated Learner Lab stack owns:

```text
Public ALB
Internal ALB
Frontend Launch Template
Frontend ASG
Frontend Target Group
Backend Launch Template
Backend ASG
Backend Target Group
Dummy DB Primary
Dummy DB Standby
core Security Groups
private S3 catalogue image bucket
frontend scaling policy
```

### 03 — Observability

Owns:

```text
SNS operations topic
optional email subscription
frontend alarms
backend alarms
public ALB error alarm
```

### 04 — Microservice

Owns:

```text
ECR
DynamoDB
ECS cluster
Fargate task definition
Fargate service
catalogue target group
internal ALB /catalogue/* listener rule
catalogue SG
CloudWatch log group
catalogue health alarm
catalogue healthy-capacity alarm
```

### Two-Phase Microservice Deployment

Phase 1:

```text
DeployService=false
→ create ECR and supporting infrastructure
```

Then:

```text
build Docker image
→ push to ECR
→ seed DynamoDB
→ upload S3 images
```

Phase 2:

```text
DeployService=true
ContainerImageDigest=sha256:<verified ECR digest>
→ create ECS service
→ create /catalogue/* route
→ run 2 tasks
```

### Infrastructure vs Application/Data Actions

CloudFormation manages infrastructure.

The following remain delivery/data actions:

```text
Docker build/push
DynamoDB seed
sample S3 object upload
SNS email confirmation
```

These are not infrastructure drift.

### Latest Local Static Validation

Latest updated artefacts were locally validated with:

```text
4 / 4 templates parsed
38 cross-stack imports matched
0 unmatched imports
95 declared CloudFormation resources
updated deployment-script syntax PASS
CloudFormation schema lint PASS
30 mocked regression tests PASS
rendered storefront JavaScript syntax PASS
```

Important:

```text
AWS runtime validation
→ still required
```

A local/static pass is distinct from runtime proof. The supplied 6 October lab files now verify the baseline, deployment version-label update/reversal and scoped cleanup; see [the main guide, Section 4.27](IaC_Deployment_and_Usage_Instructions.md#4276-results-from-the-supplied-6-october-2026-lab-run) for the remaining gaps.

---

# 6. Group Project 2 Lab Feasible Architecture

## 6.1 Text Full Architecture Diagram

```text
                                  INTERNET
                                     │
                                     ▼
                           ┌──────────────────┐
                           │   PUBLIC ALB     │
                           │    HTTP :80      │
                           └────────┬─────────┘
                                    │
                              default /*
                                    │
                                    ▼
                         ┌───────────────────────┐
                         │ Frontend Target Group │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
          ┌──────────────────┐              ┌──────────────────┐
          │ Frontend EC2 A   │              │ Frontend EC2 B   │
          │ Apache           │              │ Apache           │
          │ Private App A    │              │ Private App B    │
          └────────┬─────────┘              └────────┬─────────┘
                   │                                 │
                   │ Apache reverse proxy            │
                   │ /api/* and /catalogue/*         │
                   └──────────────┬──────────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    INTERNAL ALB     │
                       │      HTTP :80       │
                       └─────────┬───────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 │                                │
            priority 100                     priority 50
              /api/*                       /catalogue/*
                 │                                │
                 ▼                                ▼
       ┌────────────────────┐          ┌─────────────────────┐
       │ Backend Target     │          │ Catalogue Target    │
       │ Group              │          │ Group               │
       └─────────┬──────────┘          └──────────┬──────────┘
                 │                                │
       ┌─────────┴──────────┐           ┌─────────┴──────────┐
       ▼                    ▼           ▼                    ▼
┌──────────────┐    ┌──────────────┐  Fargate A          Fargate B
│ Backend EC2 A│    │ Backend EC2 B│      │                   │
│ Private App A│    │ Private App B│      └─────────┬─────────┘
└──────┬───────┘    └──────┬───────┘                │
       │                    │                        ├──► DynamoDB
       └─────────┬──────────┘                        │
                 │ TCP 1521                          └──► Private S3
          ┌──────┴─────────┐                              images
          │                │
          ▼                ▼
┌────────────────┐  ┌────────────────┐
│ Dummy DB       │  │ Dummy DB       │
│ Primary        │  │ Standby        │
│ Private DB A   │  │ Private DB B   │
└────────────────┘  └────────────────┘


NETWORK SUPPORT

Public Subnet A
→ NAT EC2
→ outbound internet for private app subnets

Gateway Endpoints
→ S3
→ DynamoDB


OPERATIONS

CloudFormation
→ all infrastructure

CloudWatch
→ alarms/logs

SNS
→ email notification
```

---

## 6.2 Lab Resource Baseline

EC2:

```text
NAT                  1
Frontend              2
Backend               2
Dummy DB              2
-----------------------
Total                 7
```

Frontend ASG:

```text
Min       2
Desired   2
Max       4
```

Backend ASG:

```text
Min       2
Desired   2
Max       2
```

Catalogue:

```text
Fargate CPU     256
Fargate memory  512 MiB
Desired tasks   2
```

Fargate tasks are not EC2 instances, but they still consume budget.

---

## 6.3 Why Production Components Are Simplified or Omitted

| Production Component | Learner Lab Treatment | Justification |
|---|---|---|
| `ap-southeast-6` | use `us-east-1` | Learner Lab Region restriction |
| Route 53 custom domain | omitted | domain registration unavailable; ALB DNS is enough for demo |
| CloudFront | omitted from working dependency | lab documentation did not explicitly guarantee it; not needed to prove core feature |
| AWS WAF | production recommendation / optional lab extension | Security is assessed through existing controls and production improvements; adding the WAF service is not required to assess the pillar |
| Shield Standard | production architecture only | not required for the sandbox demonstration |
| HTTPS / ACM | lab uses HTTP | no custom domain required; simpler demo; production remains HTTPS |
| Two NAT Gateways | one NAT EC2 | lab cost reduction; known single point of failure accepted in prototype |
| Production-sized frontend | `t3.micro` class | prototype validates behaviour, not capacity |
| 4 production backend EC2 | 2 backend EC2 | one per AZ provides HA evidence while staying inside 9-EC2 limit |
| RDS Oracle Multi-AZ | 2 dummy DB EC2 | avoids RDS cost/licensing/sizing complexity; assignment permits dummy tier |
| Real RDS replication | not implemented | dummy nodes represent placement/connectivity only |
| Production IAM roles | LabRole / LabInstanceProfile | IAM restrictions in Learner Lab |
| Production S3 versioning | disabled in lab | easier cleanup of short-lived bucket |
| CloudTrail/Config full operations | mainly production/reference | project scope and lab restrictions; CloudWatch/SNS are primary operational evidence |
| Production catalogue datastore | DynamoDB prototype | service-owned metadata demo; final production data decision needs discovery |
| Production scale thresholds | low lab thresholds | lab thresholds are deliberately small for demonstration |

The prototype is deliberately:

```text
architecturally representative
but
capacity-reduced
```

---

## 6.4 Updated Lab Website

The lab frontend should look like a real supermarket storefront rather than an infrastructure test page.

It includes:

```text
AnyGroup Market branding
hero
product search
product cards
product images
category
price
availability
simple cart counter
Live Platform Status
```

Product path:

```text
Browser
→ Public ALB
→ Frontend EC2
→ Apache reverse proxy
→ Internal ALB
→ Catalogue Fargate
→ DynamoDB
→ S3 image URL
```

Legacy status path:

```text
Browser
→ Public ALB
→ Frontend EC2
→ Apache reverse proxy
→ Internal ALB
→ Backend EC2
→ Dummy DB Primary + Standby
```

The website therefore demonstrates both:

```text
legacy architecture
+
modernised service
```

on one page.

---

## 6.5 Lab Security Flow

Final updated flow:

```text
Internet
→ Public ALB :80

Public ALB SG
→ Frontend SG :80

Frontend SG
→ Internal ALB SG :80

Internal ALB SG
→ Backend SG :8080

Internal ALB SG
→ Catalogue SG :8080

Backend SG
→ DB SG :1521
```

No direct public ingress is required for:

- frontend EC2;
- backend EC2;
- dummy DB EC2;
- Fargate tasks;
- DynamoDB;
- S3.

---

## 6.6 Lab S3 Behaviour

Lab S3 remains private.

Controls:

```text
BlockPublicAcls = true
IgnorePublicAcls = true
BlockPublicPolicy = true
RestrictPublicBuckets = true

BucketOwnerEnforced

SSE-S3
AES256

Deny insecure transport
```

Lab versioning is intentionally disabled to simplify stack teardown.

The catalogue service creates short-lived presigned URLs for product images.

Production should use CloudFront/OAC instead.

---

## 6.7 Detailed Deployment Instructions

The complete operational deployment, testing and teardown procedure is maintained separately in:

```text
IaC_Deployment_and_Usage_Instructions.md
```

That document should be used during the actual Learner Lab deployment.

This full project document explains:

```text
what
why
architecture
requirements
presentation
rubric
```

The deployment document explains:

```text
exact commands
deployment sequence
validation
testing
teardown
```

---

# 7. Cost and Cleanup Validation

## 7.1 Budget and Ownership

The assignment gives $50 per student. Check the active lab balance before a session and assign a cost owner. The Academy display may lag, so preserve the displayed balance separately from measured usage and any attributable cost.

## 7.2 Complete Cost Model

`data/cost_model_inputs.json` is a blank input model, not a cost result. It covers EC2 by tier, both ALBs/LCUs, NAT, public IPv4, EBS, Fargate CPU/memory, S3, DynamoDB, ECR, monitoring/notification and transfer. Fill current regional rates, source/date, actual runtime/usage and ownership. Leave unknowns null.

Use observed instance/task hours when scaling or updating. Two Fargate tasks can temporarily become four during a rolling deployment. Fixed baseline costs remain even when the catalogue is quiet. Gateway endpoints have no additional endpoint charge; storage/requests still incur service charges.

The proposed efficiency measure is attributable workload cost divided by successful functional requests over the same measurement window. Do not divide an Academy balance change by load-generator HTML requests and call it catalogue cost efficiency.

## 7.3 Design Trade-Offs

| Choice | Prototype rationale | Production boundary |
|---|---|---|
| Seven small EC2 at baseline, frontend maximum four | Demonstrates tiering/recovery within the planned nine-instance ceiling | Size from measured business workload, not lab thresholds |
| Single NAT EC2 | Lower scope/cost; endpoints avoid that path for S3/DynamoDB | Single failure point and possible cross-AZ transfer; use resilient production egress |
| Two Fargate tasks | Managed catalogue runtime with redundant desired capacity | Still incurs task/network/ALB costs; compare alternatives at equivalent resilience |
| On-demand DynamoDB | Fits the tiny unpredictable metadata pilot | Validate query patterns, data ownership and actual request/storage cost |
| Dummy DB EC2 | Assignment permits a representative DB tier | Not Oracle/RDS, replication, backups or real failover |
| Short logs and five retained images | Limits short-lived prototype retention | Keep required audit evidence and active/rollback images; production retention differs |
| CloudFormation cleanup | Removes the environment in dependency order | Evidence/data must be preserved first; production data require retention/recovery policies |

## 7.4 Cleanup and Evidence

The script deletes microservice, observability, empties the unversioned S3 bucket, deletes core, then network. ECR `EmptyOnDelete` removes images when its repository is deleted; the script does not pre-delete images while tasks still run. Access/deletion failures abort and remain visible.

```bash
./scripts/part13_teardown_all.sh
python3 scripts/part14_collect_evidence.py --after-teardown --output evidence/after-teardown
```

The orphan check covers project tags, the four stack names and matching resource prefixes. Also inspect the console for untagged/manual resources. Record starting/final budget, session times, inventories, price/usage assumptions, stack deletion and the orphan report. Scoped cleanup has been captured and verified for the 6 October run; budget/price/usage results remain pending. See Section 4.27 of `IaC_Deployment_and_Usage_Instructions.md` for the full sequence.

# 8. Presentation and Slide Content

Use [Presentation_and_Slide_Content.md](Presentation_and_Slide_Content.md) for copy-ready content for 12 main slides, speaker notes, four-member timing, diagram specifications, console steps and the submission table. Use [Rubric_and_Assessment_Checklist.md](Rubric_and_Assessment_Checklist.md) for the full four-pillar assessment, rubric audit, evidence checklist, risks and references. Build the deck outside this repository using the presentation guide.

For all preparation, deployment, testing, evidence capture and teardown, use [IaC_Deployment_and_Usage_Instructions.md](IaC_Deployment_and_Usage_Instructions.md), the main operational guide. The architecture, case-study rationale, implementation and design assessment remain in this README.

# Source Basis

Current authoritative project files: `instructions.md`, `AnyGroupLLC_case_study.md`, the four full templates in `cloudformation/`, `catalogue-service/`, deployment/testing scripts, `IaC_Deployment_and_Usage_Instructions.md`, `Presentation_and_Slide_Content.md`, `Rubric_and_Assessment_Checklist.md`, generated security references and the static report. Earlier planning documents and the original GP1 submission are not included in this repository; the retained GP1 architecture must be checked against that submission before final claims.

The implemented lab templates describe public ALB → private frontend → internal ALB → backend/dummy DB or Fargate catalogue → DynamoDB/private S3. The reference fragments are generated snapshots and must not be deployed/merged as duplicate resources. The complete production recommendation includes components beyond the lab templates and is not claimed as an implemented production environment.
