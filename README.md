# INFOSYS 735 Group Project 2 — Full Project Documentation

**Course:** INFOSYS 735 — Cloud Computing Architecture  
**Case:** AnyGroupLLC  
**Assessment:** Group Project 2  
**Production Region:** `ap-southeast-6` — AWS Asia Pacific (New Zealand)  
**Learner Lab Region:** `us-east-1`  
**Selected Additional Feature:** Incremental Microservices Modernisation using the Strangler Fig Pattern  
**Pilot Boundary:** Existing Product Catalogue function  
**Primary Well-Architected Pillars:** Operational Excellence and Reliability  
**Supporting / Bonus Pillars:** Security and Cost Optimisation  
**Infrastructure Source of Truth:** AWS CloudFormation  
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
- the final presentation plan;
- the final rubric audit.

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
3. assess the architecture against at least **two AWS Well-Architected pillars**;
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
| One additional feature | Strangler Fig microservices modernisation | Feature rationale + `/catalogue/*` route | Design complete; runtime pending |
| At least two WAF pillars | Operational Excellence + Reliability | Pillar matrix + implementation evidence | Assessment complete |
| VPC / AZs / subnets | Two-AZ VPC with six subnets | VPC console / CloudFormation | Network live |
| NAT | NAT EC2 in lab; HA NAT Gateways in production | EC2/routes | Network live |
| SGs / NACLs | Tier-based controls | SG/NACL console | IaC prepared |
| ELB | Public + internal ALB | listeners/target groups | IaC prepared |
| Auto Scaling | frontend ASG + backend ASG | ASG activity / replacement | IaC prepared |
| SNS | operations topic | confirmed subscription + test | pending live |
| CloudWatch | alarms + catalogue logs | alarms/logs | pending live |
| EC2 | frontend/backend/dummy DB | instance/AZ evidence | pending updated core deployment |
| Web server | Apache frontend | storefront | pending updated core deployment |
| S3 | private image bucket | security + objects | IaC prepared |
| Web/app/DB tiers | frontend → backend → dummy DB | live platform status + AWS console | pending live |
| Additional components | ECS/Fargate, DynamoDB, CloudFormation | console + routes + data | pending live |
| Live demonstration | storefront + APIs + console | presentation evidence | pending |
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

Budget information can lag approximately:

```text
8–12 hours
```

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

## 4.1 Pillar Selection

Primary pillars:

```text
Operational Excellence
Reliability
```

Supporting / bonus candidates:

```text
Security
Cost Optimisation
```

The project should prioritise depth in the two primary pillars before claiming bonus breadth.

---

## 4.2 Review Method

Every improvement follows:

```text
AWS Principle
        ↓
GP1 Alignment
        ↓
Gap
        ↓
GP2 Improvement
        ↓
Implementation
        ↓
Evidence
        ↓
Business Value
        ↓
Trade-Off
```

---

## 4.3 Operational Excellence

### Existing Strengths

Group Project 1 already included:

- monitoring concepts;
- Systems Manager;
- CloudWatch;
- managed AWS services;
- multi-tier architecture.

### Main Gap

Much of the original architecture remained conceptual and operationally manual.

The team needed stronger evidence of:

- repeatable deployment;
- reversible change;
- infrastructure consistency;
- documented operational procedures;
- observable workloads.

### Group Project 2 Improvements

```text
CloudFormation for all infrastructure
+
deployment scripts
+
stack outputs/imports
+
CloudWatch alarms/logs
+
SNS
+
documented deployment/testing/teardown
+
small Strangler Fig change
```

### Why This Matters to AnyGroupLLC

The IT team is relatively small.

Infrastructure as Code can reduce:

- manual configuration;
- inconsistent environments;
- forgotten resources;
- recovery time for environment recreation;
- repeated troubleshooting caused by drift.

### Evidence

Show:

- CloudFormation stacks;
- template files;
- stack resource relationships;
- successful deployment;
- update/redeployment;
- teardown/recreation;
- runbook;
- CloudWatch/SNS.

---

## 4.4 Reliability

### Existing Strengths

Group Project 1 already designed:

- two AZs;
- ALBs;
- Auto Scaling;
- RDS Multi-AZ;
- resilient S3;
- multiple web/backend instances.

### Main Gap

Reliability was mostly architectural rather than demonstrated.

The project needed evidence of:

- health-based routing;
- automatic replacement;
- workload continuity;
- service desired-state recovery;
- observability during failure.

### Group Project 2 Improvements

Production:

```text
2-AZ frontend ASG
+
2-AZ backend ASG
+
RDS Multi-AZ
+
2+ Fargate tasks
+
health-aware ALBs
```

Learner Lab:

```text
2 frontend EC2
+
2 backend EC2
+
dummy DB primary/standby placement
+
2 Fargate tasks
+
public and internal ALB
+
failure/replacement tests
```

### Reliability Test Story

Frontend:

```text
2 healthy frontend targets
        ↓
terminate 1 frontend
        ↓
ALB stops routing to failed target
        ↓
surviving frontend continues
        ↓
ASG creates replacement
        ↓
2 healthy targets restored
```

Backend:

```text
2 healthy backend targets
        ↓
terminate 1 backend
        ↓
internal ALB routes to survivor
        ↓
/api/* remains available
        ↓
backend ASG restores capacity
```

Fargate:

```text
Desired tasks = 2
        ↓
task failure
        ↓
ECS service restores desired state
```

### Business Value

- reduces website downtime risk;
- supports promotions/events;
- improves recovery behaviour;
- provides confidence before wider modernisation;
- reduces single-instance dependence.

---

## 4.5 Security — Supporting / Bonus Pillar

Existing production strengths:

- WAF;
- Shield Standard;
- private tiers;
- SGs;
- NACLs;
- SSM;
- private S3;
- Secrets Manager;
- KMS;
- CloudTrail;
- Config.

Group Project 2 evidence:

```text
only public ALB exposed
private frontend/backend/DB/Fargate
SG-to-SG relationships
no inbound SSH/RDP
private S3
no hard-coded credentials
CloudFormation-managed controls
```

Security should only be claimed as a strong bonus pillar if the implementation evidence is actually captured.

---

## 4.6 Cost Optimisation — Supporting / Bonus Pillar

Relevant improvements:

- small lab instance sizes;
- Fargate instead of dedicated ECS hosts;
- dummy DB instead of real Oracle/RDS in the lab;
- one NAT EC2 instead of production NAT Gateways;
- DynamoDB on-demand prototype model;
- S3 object storage;
- CloudFormation teardown;
- explicit budget checks;
- removal of idle resources.

Again, claim Cost Optimisation strongly only when cleanup/budget evidence is available.

---

## 4.7 Pillar Summary

| Pillar | GP1 Strength | GP2 Gap | GP2 Response |
|---|---|---|---|
| Operational Excellence | Good conceptual operations architecture | Limited IaC/repeatability evidence | CloudFormation, scripts, runbooks, observability |
| Reliability | Strong multi-AZ design | Failure behaviour not proven | real health/replacement tests |
| Security | Strong layered design | lab evidence incomplete | SG isolation, private tiers, private S3 |
| Cost Optimisation | cloud elasticity discussed | cleanup/budget evidence weak | small resources, teardown, lab discipline |

---

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
35 cross-stack imports matched
0 unmatched imports
94 declared CloudFormation resources
updated deployment-script syntax PASS
```

Important:

```text
AWS runtime validation
→ still required
```

A local/static pass is not a claim that every Learner Lab resource has successfully deployed.

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
| AWS WAF | production-only / optional lab extension | available, but primary marks focus on Operational Excellence and Reliability |
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
INFOSYS735_GP2_IaC_Deployment_and_Usage_Instructions.md
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

## 7.1 Budget Rule

Assignment budget:

```text
$50 per student
```

Treat it as a hard ceiling.

Do not rely on the displayed balance as real-time data because it may lag by 8–12 hours.

---

## 7.2 Cost-Conscious Design Decisions

Lab choices intentionally reduce cost:

```text
t3.micro-class EC2
+
7-instance steady-state baseline
+
Fargate instead of ECS host fleet
+
dummy DB instead of RDS Oracle
+
single NAT EC2 instead of two NAT Gateways
+
DynamoDB PAY_PER_REQUEST
+
short-lived infrastructure
+
CloudFormation teardown
```

Production decisions are not downgraded because of the student-lab budget.

---

## 7.3 Main Cost Risks

Highest-risk resources:

- EC2 left running;
- public/internal ALBs;
- Fargate tasks;
- NAT resources;
- accidental RDS;
- resources forgotten outside CloudFormation.

Budget controls:

```text
Before session
→ inspect stacks/resources/budget

During session
→ build only required resources
→ test immediately
→ capture evidence immediately

End session
→ remove temporary resources
→ tear down if work is complete
→ check for orphans
```

---

## 7.4 Cleanup Strategy

The teardown script follows dependency-aware cleanup.

Actual script sequence:

```text
1. Best-effort ECR image cleanup
2. Delete microservice stack
3. Delete observability stack
4. Empty core S3 bucket
5. Delete core stack
6. Delete network stack
7. Inspect for orphaned resources
```

Why S3 is emptied manually:

```text
CloudFormation cannot delete a non-empty bucket
```

---

## 7.5 Cleanup Verification

After teardown verify:

```text
CloudFormation
→ no project stacks

EC2
→ no project instances

Auto Scaling
→ no project ASGs

ELB
→ no project load balancers / target groups

ECS
→ no project service/tasks

ECR
→ no leftover repository/images if stack deletion succeeded

DynamoDB
→ no project table

S3
→ no project bucket

SNS
→ no project topic

VPC
→ no project VPC/network resources
```

Use tags where possible:

```text
Project = INFOSYS735-GP2
Environment = LearnerLab
ManagedBy = CloudFormation
```

---

## 7.6 Cost Validation Evidence

Do not invent an actual cost number.

Capture the following from the live lab:

| Evidence | Status |
|---|---|
| Starting displayed budget | Pending live capture |
| Resource count before deployment | Pending |
| Resource count after deployment | Pending |
| Displayed budget after testing | Pending |
| Stack teardown complete | Pending |
| Orphan-resource check | Pending |
| Final displayed budget | Pending |

The cost story should focus on:

```text
design discipline
+
controlled lifecycle
+
evidence
```

not unsupported savings percentages.

---

# 8. Presentation

## 8.1 Presentation Objective

The final presentation is not a classroom-style explanation of AWS services.

It should be delivered as a **solutions-architect pitch to the stakeholders at AnyGroupLLC**.

The presentation should answer the questions that the CTO, CFO, CISO and IT leadership would care about:

```text
What business problem are we solving?
        ↓
What did we change from the previous design?
        ↓
Why is this change safer and better for AnyGroupLLC?
        ↓
How does the proposed production architecture work?
        ↓
What did we actually build in AWS?
        ↓
Can we prove that it works?
        ↓
What business value does AnyGroupLLC receive?
        ↓
What trade-offs and next steps remain?
```

The presentation should sound like a professional recommendation:

> **“Here is the architecture we recommend for AnyGroupLLC, here is why we recommend it, and here is the live AWS evidence that proves the prototype works.”**

Avoid presenting the deck as:

```text
“Here is VPC.”
“Here is EC2.”
“Here is S3.”
```

Instead connect every AWS component to:

```text
business problem
→ architecture decision
→ live evidence
→ stakeholder value
```

---

## 8.2 Presentation Timing and Format

Maximum presentation time:

```text
15 minutes
```

Recommended target:

```text
13:30–14:15
```

Recommended buffer:

```text
45–90 seconds
```

The presentation should combine:

```text
Pitch Slides
+
Live AWS Management Console Demo
```

The live demo is a core part of the pitch, not an optional appendix.

The team should show configured AWS components directly in the AWS Management Console, including:

```text
CloudFormation
VPC
EC2
Auto Scaling
Load Balancers
Target Groups
ECS / Fargate
DynamoDB
S3
CloudWatch
SNS
```

CloudFormation must be shown explicitly because Infrastructure as Code is one of the project's strongest Operational Excellence improvements.

---

## 8.3 Four-Speaker Allocation

| Speaker | Approx. Time | Responsibility | Main Stakeholder Perspective |
|---|---:|---|---|
| **Speaker 1** | 0:00–3:00 | Business problem, stakeholder needs, GP1 baseline, Well-Architected gaps | CTO / CFO / CISO |
| **Speaker 2** | 3:00–6:00 | Recommended feature, production architecture, lab simplifications | CTO / IT leadership |
| **Speaker 3** | 6:00–10:15 | Live AWS Management Console demo: CloudFormation, network, compute, ALB/ASG, legacy path | CTO / IT Operations |
| **Speaker 4** | 10:15–14:15 | Live catalogue demo, monitoring/reliability evidence, cost/trade-offs, recommendation | CFO / CISO / CTO |
| **Buffer** | 14:15–15:00 | Demo delay, transitions, closing | — |

Replace `Speaker 1–4` with the real team member names in the final slide deck.

---

## 8.4 Pitch Narrative

The recommended narrative is:

```text
AnyGroupLLC is expanding
        ↓
Existing architecture is already strong
        ↓
Main GP2 gaps are operational repeatability and proven reliability
        ↓
We retain the strong production foundation
        ↓
We introduce one controlled Strangler Fig microservice pilot
        ↓
We manage infrastructure through CloudFormation
        ↓
We prove the design live in AWS
        ↓
We show old and new application paths working together
        ↓
We show health, scaling, monitoring and failure evidence
        ↓
We recommend staged modernisation rather than a full rewrite
```

The pitch should continuously distinguish:

```text
PRODUCTION RECOMMENDATION
vs
LEARNER LAB PROTOTYPE
```

---

## 8.5 Slide 1 — Executive Recommendation

### Slide Title

**Modernising AnyGroupLLC Without a Risky Full Rewrite**

### Slide Content

```text
Our recommendation:

Retain the reliable GP1 production foundation
        +
Improve operational control with CloudFormation
        +
Prove reliability with live AWS evidence
        +
Pilot catalogue modernisation using Strangler Fig
```

Stakeholder outcome:

- safer New Zealand expansion;
- reduced infrastructure-management burden;
- improved resilience;
- staged investment;
- controlled modernisation.

### Speaker Notes — Speaker 1

“AnyGroupLLC does not need to replace a working platform to modernise successfully. Our recommendation is to retain the strong two-Availability-Zone architecture from Group Project 1, improve how the environment is operated through Infrastructure as Code and observability, and test microservices through one controlled catalogue pilot. This gives the CTO a modernisation path, the CFO staged investment rather than a large rewrite, the CISO controlled exposure, and the IT team a more repeatable operating model.”

---

## 8.6 Slide 2 — Why Change Is Needed

### Slide Title

**Growth Increases Both Traffic Risk and Operational Pressure**

### Slide Content

```text
≈500,000 visits/day
+
higher promotion/event traffic
+
New Zealand expansion
+
small IT team
+
previous availability/security concerns
```

Stakeholder concerns:

```text
CTO
→ availability, scalability, productivity

CFO
→ cost, investment control, operational efficiency

CISO
→ downtime, security, reputation

IT Team
→ less manual setup and firefighting
```

### Speaker Notes — Speaker 1

“The technical design must support more than traffic. AnyGroupLLC also has a relatively small IT team and a history of availability and security concerns. A design that scales but is difficult to operate would not solve the full business problem. Our Group Project 2 improvement therefore focuses on both Reliability and Operational Excellence.”

---

## 8.7 Slide 3 — What We Improved from Group Project 1

### Slide Title

**Keep the Strong Foundation, Fix the Gaps**

### Slide Content

**Retain:**

```text
2 AZs
CloudFront / WAF / Shield
Public ALB
Frontend ASG
Internal ALB
Backend ASG
RDS Oracle Multi-AZ
Private S3
```

**Improve:**

```text
Manual / conceptual deployment
→ CloudFormation

Reliability designed on paper
→ live failure and health evidence

Server-oriented application
→ one controlled microservice extraction
```

### Speaker Notes — Speaker 1

“Our Group Project 1 architecture was already a strong production design. We did not redesign it unnecessarily. We focused on the gaps: repeatable deployment, stronger operational evidence, and a controlled way to evaluate microservices. This is why our primary Well-Architected pillars are Operational Excellence and Reliability.”

---

## 8.8 Slide 4 — Additional Feature Decision

### Slide Title

**A Strangler Fig Pilot Instead of a Full Rewrite**

### Slide Content

```text
Existing Backend
      │
      ├── existing functions stay in place
      │
      └── Product Catalogue extracted
                 ↓
          ECS / Fargate
                 ↓
             DynamoDB
                 ↓
          S3 image reference
```

Why this approach:

- incremental;
- reversible;
- independently deployable;
- independently observable;
- lower migration risk;
- measurable before wider adoption.

### Speaker Notes — Speaker 2

“The catalogue already exists, so we are not claiming the catalogue itself as a new feature. The new capability is incremental service extraction. We route only catalogue traffic to a new independently deployed service while the rest of the backend continues operating. This lets AnyGroupLLC test whether the operational and scaling benefits of microservices justify the additional complexity before committing to more migration.”

---

## 8.9 Slide 5 — Recommended Production Architecture

### Slide Title

**Production Recommendation for AnyGroupLLC New Zealand**

### Slide Content

```text
Customers
→ Route 53
→ CloudFront
→ AWS WAF / Shield Standard
→ Public ALB
→ Frontend ASG
→ Internal ALB
   ├── /catalogue/* → ECS/Fargate
   │                   → catalogue data boundary
   │                   → private S3 image references
   │
   └── existing API → .NET Backend ASG
                       → RDS for Oracle Multi-AZ
```

Management:

```text
CloudFormation
CloudWatch / SNS
Systems Manager
CloudTrail / Config
Secrets Manager / KMS
```

### Speaker Notes — Speaker 2

“This remains our production recommendation. It uses the New Zealand Region, two Availability Zones, edge delivery and protection, separate public and internal load balancing, a multi-AZ frontend and backend, and RDS for Oracle Multi-AZ. The Group Project 2 change is deliberately narrow: catalogue traffic can be routed to the new service without replacing the existing .NET backend.”

---

## 8.10 Slide 6 — Why the Learner Lab Looks Different

### Slide Title

**The Prototype Proves Behaviour, Not Production Capacity**

### Slide Content

```text
Production                     Learner Lab
──────────────────────────────────────────────────
ap-southeast-6                 us-east-1
CloudFront / WAF / Shield      simplified
2 NAT Gateways                 1 NAT EC2
Production EC2 sizing          t3.micro-class
4 backend baseline             2 backend EC2
RDS Oracle Multi-AZ            dummy DB primary/standby
HTTPS/custom DNS               ALB DNS + HTTP demo
```

Lab baseline:

```text
1 NAT
2 Frontend
2 Backend
2 Dummy DB
= 7 EC2
```

### Speaker Notes — Speaker 2

“The lab is intentionally smaller. It is constrained by the educational environment, including a maximum of nine running EC2 instances and a $50-per-student budget. We therefore preserve architecture relationships rather than production capacity. The two dummy database EC2 instances demonstrate private DB-tier placement and connectivity, not Oracle or RDS replication.”

---

# 8.11 Live Demonstration Strategy

The live demonstration should be integrated into the pitch.

Do not wait until the final minute and rapidly click through the console.

The demo should prove the architecture in a deliberate order.

Recommended sequence:

```text
CloudFormation
        ↓
Network
        ↓
Compute / Auto Scaling
        ↓
Load Balancing
        ↓
Storefront + Legacy Path
        ↓
Catalogue Microservice
        ↓
DynamoDB + S3
        ↓
CloudWatch + SNS
        ↓
Reliability evidence
```

Keep the required AWS Console tabs open before the presentation starts.

---

## 8.12 Slide 7 + Live Demo — Infrastructure as Code

### Slide Title

**Operational Excellence: The Environment Is Defined, Not Hand-Built**

### Slide Content

```text
01-network
→ 02-core
→ 03-observability
→ 04-microservice
```

Key message:

> CloudFormation is the infrastructure source of truth.

### Live AWS Management Console Demo — Speaker 3

Open:

```text
AWS Management Console
→ CloudFormation
→ Stacks
```

Show the four stacks:

```text
anygroup-gp2-network
anygroup-gp2-core
anygroup-gp2-observability
anygroup-gp2-microservice
```

For one or two stacks, show:

```text
Status
Resources
Outputs
```

Recommended proof points:

```text
Network stack
→ VPC/subnet exports

Core stack
→ public ALB
→ internal ALB
→ frontend ASG
→ backend ASG
→ dummy DB nodes
→ S3

Observability stack
→ SNS / alarms

Microservice stack
→ ECS / ECR / DynamoDB / catalogue route
```

### Speaker Notes — Speaker 3

“One of our strongest Operational Excellence improvements is that the environment is defined through CloudFormation rather than maintained as a collection of manual console configurations. These four stacks separate network, core infrastructure, observability and the new microservice. The AWS Console is being used here to verify the deployed resources, not as a second source of configuration.”

---

## 8.13 Slide 8 + Live Demo — Core Infrastructure and Legacy Path

### Slide Title

**The Existing Application Path Remains Highly Available**

### Slide Content

```text
Internet
→ Public ALB
→ Frontend ASG ×2
→ Internal ALB
→ Backend ASG ×2
→ Dummy DB Primary + Standby
```

### Live AWS Management Console Demo — Speaker 3

Show:

```text
VPC
→ VPC + 6 subnets across 2 AZs

EC2
→ NAT
→ 2 frontend instances
→ 2 backend instances
→ DB primary
→ DB standby

Auto Scaling Groups
→ frontend ASG
→ backend ASG

EC2 → Load Balancers
→ public ALB
→ internal ALB

EC2 → Target Groups
→ 2 healthy frontend targets
→ 2 healthy backend targets
```

Then open the website:

```text
http://<PUBLIC-ALB-DNS>/
```

Show the `Live Platform Status` section:

```text
Web Tier
→ frontend instance / AZ

Legacy API
→ backend instance / AZ

Database Tier
→ primary reachable
→ standby reachable
```

### Speaker Notes — Speaker 3

“This is our retained legacy path. The public load balancer sends the customer request to one of two frontend instances. Apache then forwards application requests to the private internal load balancer, which distributes them across two backend instances. The backend can reach both private dummy database nodes on the database port. The small status panel on the website gives us visible proof that the complete frontend-to-backend-to-database path is functioning.”

---

## 8.14 Slide 9 + Live Demo — Strangler Fig Catalogue

### Slide Title

**The New Catalogue Service Runs Beside the Existing Backend**

### Slide Content

```text
/catalogue/*
      ↓
Internal ALB
      ↓
Catalogue Target Group
      ↓
ECS / Fargate ×2
      ↓
DynamoDB
      ↓
S3 image references
```

### Live AWS Management Console Demo — Speaker 4

Show:

```text
EC2 → Load Balancers → Internal ALB
→ listener rules
→ priority 50 /catalogue/*
→ priority 100 /api/*
```

Show:

```text
ECS
→ cluster
→ catalogue service
→ Desired = 2
→ Running = 2
```

Show:

```text
Target Groups
→ catalogue target group
→ 2 healthy Fargate IP targets
```

Show:

```text
DynamoDB
→ catalogue table
→ P1001 / P1002 / P1003
```

Show:

```text
S3
→ private image bucket
→ products/P1001.jpg
→ products/P1002.jpg
→ products/P1003.jpg
```

Return to storefront and show:

```text
product cards
images
price
availability
search
```

### Speaker Notes — Speaker 4

“This is the new feature operating beside the legacy backend. The internal ALB uses path-based routing: `/api/*` stays on the old backend while `/catalogue/*` goes to Fargate. The catalogue service runs two tasks, reads product metadata from DynamoDB, and uses image keys for objects stored privately in S3. The storefront then renders the live product cards. This coexistence is the Strangler Fig behaviour we wanted to prove.”

---

## 8.15 Slide 10 + Live Demo — Reliability and Observability

### Slide Title

**We Can See Failures and Recover from Them**

### Slide Content

```text
CloudWatch
├── frontend unhealthy
├── frontend capacity
├── ALB 5XX
├── backend unhealthy
├── backend capacity
└── catalogue unhealthy
        ↓
       SNS
        ↓
operations notification
```

Reliability evidence:

```text
terminate one frontend
→ site continues
→ ASG replaces

terminate one backend
→ /api/* continues
→ ASG replaces
```

### Live AWS Management Console Demo — Speaker 4

Show:

```text
CloudWatch
→ Alarms
```

Show relevant alarms.

Show:

```text
CloudWatch
→ Log groups
→ catalogue log group
```

Show:

```text
SNS
→ Topic
→ Subscription = Confirmed
```

If a live failure test has already been performed, show:

```text
Auto Scaling
→ Activity history
→ replacement event
```

and/or:

```text
Target Group
→ health transition evidence
```

If performing the failure live would consume too much time or risk the environment, use previously captured evidence while explaining the test.

### Speaker Notes — Speaker 4

“Reliability is not only a diagram. CloudWatch gives us health and capacity signals, SNS provides notification, and Auto Scaling restores lost EC2 capacity. We can show the replacement event directly in the console. This is the improvement over Group Project 1: the recovery behaviour is now observable and demonstrable.”

---

## 8.16 Slide 11 — Cost, Trade-Offs and Stakeholder Value

### Slide Title

**A Controlled Investment, Not a Big-Bang Rewrite**

### Slide Content

**Prototype cost controls:**

```text
$50/student
7 EC2 steady state
small EC2 sizes
dummy DB
single NAT EC2
Fargate
CloudFormation teardown
```

**Trade-offs:**

- more components;
- distributed-service monitoring;
- service/data ownership;
- networking complexity;
- team skills;
- additional cost.

**Stakeholder value:**

```text
CTO
→ safe modernisation + scalability

CFO
→ staged investment + cost discipline

CISO
→ controlled exposure + observable health

IT Team
→ repeatable infrastructure + less manual configuration
```

### Speaker Notes — Speaker 4

“Microservices introduce complexity, so we are not recommending migration for its own sake. The catalogue pilot gives AnyGroupLLC evidence before further investment. The Learner Lab also demonstrates cost discipline through small resources, a dummy database and repeatable teardown. In production, AnyGroupLLC can retain the stronger edge, database and multi-AZ architecture while making future extraction decisions based on measured value.”

---

## 8.17 Slide 12 — Closing Recommendation

### Slide Title

**Modernise Incrementally, Measure, Then Decide the Next Boundary**

### Slide Content

```text
KEEP
→ reliable GP1 foundation

IMPROVE
→ CloudFormation + observability

PROVE
→ health, scaling and recovery

PILOT
→ catalogue microservice

MEASURE
→ value and operational cost

DECIDE
→ next extraction only if justified
```

Final recommendation:

> **Retain the stable platform, modernise one bounded function at a time, and use operational evidence to decide whether further microservice adoption is worthwhile.**

### Speaker Notes — Speaker 4

“Our recommendation to AnyGroupLLC is staged modernisation. Keep the reliable production foundation, improve operational repeatability through Infrastructure as Code, and use the catalogue service as a controlled first pilot. If that pilot shows meaningful deployment, scaling and ownership benefits without creating excessive operational cost, then the organisation can select the next bounded service. This approach gives AnyGroupLLC a modernisation path without placing the New Zealand launch at unnecessary risk.”

---

## 8.18 Live Demo Checklist

Before the presentation, verify the following in the AWS Management Console.

### CloudFormation

```text
[ ] all four stacks visible
[ ] stack statuses successful
[ ] resources tab opens
[ ] outputs visible
```

### VPC

```text
[ ] VPC visible
[ ] six subnets visible
[ ] two AZs visible
[ ] route tables visible
[ ] NACLs visible
[ ] gateway endpoints visible
```

### EC2 / Auto Scaling

```text
[ ] NAT instance visible
[ ] 2 frontend instances visible
[ ] 2 backend instances visible
[ ] dummy DB primary visible
[ ] dummy DB standby visible
[ ] frontend ASG visible
[ ] backend ASG visible
```

### Load Balancing

```text
[ ] public ALB active
[ ] internal ALB active
[ ] frontend target group healthy
[ ] backend target group healthy
[ ] catalogue target group healthy
[ ] internal listener rules visible
```

### Website

```text
[ ] storefront loads
[ ] product cards load
[ ] images load
[ ] platform status loads
[ ] /api/health works
[ ] /api/db works
```

### ECS / Fargate

```text
[ ] ECS cluster active
[ ] catalogue service active
[ ] desired tasks = 2
[ ] running tasks = 2
```

### DynamoDB / S3

```text
[ ] product records visible
[ ] image keys correct
[ ] S3 images visible
[ ] bucket remains private
```

### Monitoring

```text
[ ] CloudWatch alarms visible
[ ] catalogue log group visible
[ ] SNS subscription confirmed
```

### Reliability Evidence

```text
[ ] frontend replacement evidence captured
[ ] backend replacement evidence captured
[ ] screenshots prepared as backup
```

---

## 8.19 Demo Risk Management

A live AWS demo can fail because of:

- lab-session expiry;
- browser delay;
- slow resource state changes;
- AWS console navigation;
- Fargate task restart;
- email notification timing;
- Auto Scaling replacement delay.

Therefore prepare:

```text
Live demo
+
backup screenshots
+
backup command outputs
```

The team should never spend several minutes waiting for a resource to change state.

If a live failure/replacement event is too slow, show:

```text
Auto Scaling Activity History
+
target health
+
captured evidence
```

and continue the pitch.

---

## 8.20 Presentation Quality Rules

### Do

- speak to AnyGroupLLC as the client;
- use “we recommend” and “this gives AnyGroupLLC…”;
- show live configuration evidence;
- show CloudFormation early in the demo;
- connect technical choices to business outcomes;
- state production vs lab differences explicitly;
- explain trade-offs;
- keep transitions rehearsed.

### Do Not

- read AWS service definitions;
- spend most of the presentation on diagrams;
- claim the dummy DB is RDS;
- claim the dummy DB is replicated;
- claim DynamoDB is definitely the production catalogue datastore;
- claim unsupported SLA/RTO/RPO numbers;
- call the catalogue itself the new feature;
- present the Learner Lab architecture as the production architecture;
- hide trade-offs.

---

## 8.21 Presentation Rehearsal Timing

Suggested rehearsal target:

```text
Slide 1   0:40
Slide 2   0:55
Slide 3   0:55
Slide 4   0:55
Slide 5   1:00
Slide 6   0:50
Slide 7   1:15 + CloudFormation demo
Slide 8   1:30 + core/legacy demo
Slide 9   1:45 + catalogue demo
Slide 10  1:20 + monitoring demo
Slide 11  0:50
Slide 12  0:35
--------------------------------
Target    ≈13:30–14:15
```

The team should rehearse with the AWS Console open, not only with slides.

# 9. Final Rubric Audit

## 9.1 Solution Improvement — 10 Marks

| Audit Item | Evidence | Status |
|---|---|---|
| Continues GP1 | Production architecture retained | Complete |
| One additional feature | Strangler Fig microservices modernisation | Complete |
| Product catalogue correctly described as pilot | Feature documentation | Complete |
| Architecture improved rather than replaced | Production diagram | Complete |
| Two primary WAF pillars | Operational Excellence + Reliability | Complete |
| Existing strengths identified | GP1/WAF analysis | Complete |
| Gaps identified | operational repeatability + reliability evidence | Complete |
| Improvements mapped to business value | stakeholder sections | Complete |
| Trade-offs acknowledged | microservices/cost sections | Complete |
| Live evidence | deployment/demo | Pending final live validation |

### Audit Judgment

Design quality is strong.

Full marks depend on successfully demonstrating the improvement rather than only explaining it.

---

## 9.2 Basic Infrastructure — 30 Marks

| Required Component | Final Design | Evidence Needed | Status |
|---|---|---|---|
| VPC | `10.0.0.0/16` | VPC console | Network deployed |
| 2 AZs | A + B | subnet/AZ view | Network deployed |
| Subnets | 2 public + 2 app + 2 DB | subnet view | Network deployed |
| NAT | NAT EC2 | routes/instance | Network deployed |
| SGs | tier-based SGs | SG rules | updated core pending live |
| NACLs | public/app/DB | NACL associations | network evidence needed |
| ELB | public + internal ALB | listener/health | pending live |
| Auto Scaling | frontend + backend ASG | ASG console | pending live |
| SNS | operations topic | confirmed email | pending live |
| CloudWatch | alarms/logs | alarm/log console | pending live |
| EC2 | 2 frontend + 2 backend + 2 DB + NAT | EC2 view | pending updated core |
| Web server | Apache | storefront | pending live |
| S3 | private product images | bucket security/objects | pending live |
| Web tier | frontend ASG | target health | pending live |
| App tier | backend ASG / Fargate | target health | pending live |
| DB tier | dummy primary/standby | `/api/db` + EC2 | pending live |

### Audit Judgment

All required components are represented in the final design/IaC.

The remaining risk is implementation evidence.

---

## 9.3 Additional Infrastructure — 20 Marks

| Additional Service | Integration | Business/Technical Value | Status |
|---|---|---|---|
| ECS/Fargate | `/catalogue/*` | independent service runtime | IaC ready |
| DynamoDB | catalogue metadata | service-owned prototype store | IaC ready |
| CloudFormation | all infrastructure | repeatability / reversible changes | in use |
| ECR | Fargate image source | container delivery | IaC ready |
| S3 relationship | image objects | scalable private media storage | IaC ready |
| CloudWatch/SNS | service health | operational visibility | IaC ready |

### Audit Judgment

The service set is coherent and should satisfy the “more than one well-integrated component” expectation if successfully demonstrated.

---

## 9.4 Presentation — 40 Marks

| Requirement | Plan | Status |
|---|---|---|
| ≤15 minutes | approximately 13:30–14:15 plus buffer | Planned |
| All members present | 4-speaker allocation | Planned |
| Stakeholder pitch | presentation framed as recommendation to AnyGroupLLC CTO/CFO/CISO/IT leadership | Planned |
| Client-focused story | problem → recommendation → proof → value → trade-offs → next step | Planned |
| Updated architecture | production + lab text diagrams | Complete |
| CloudFormation live demo | show four stacks, status, resources and outputs in Management Console | Pending live |
| Core AWS live demo | VPC, EC2, ASGs, public/internal ALBs and target groups | Pending live |
| Application live demo | storefront + legacy `/api/*` path + DB connectivity | Pending live |
| Additional-feature live demo | ECS/Fargate, ALB catalogue rule, DynamoDB, S3 product images | Pending live |
| Observability live demo | CloudWatch alarms/logs + SNS subscription | Pending live |
| Reliability evidence | frontend/backend replacement activity and target health | Pending live |
| Technical rationale | feature/WAF/architecture | Complete |
| Business value | stakeholder mapping | Complete |
| Trade-offs | explicit | Complete |
| Strong ending | staged modernisation recommendation | Planned |

---

## 9.5 Bonus-Pillar Audit

### Security

Claim strongly only if evidence shows:

```text
private workloads
SG isolation
NACLs
private S3
no public SSH/RDP
no hard-coded credentials
```

### Cost Optimisation

Claim strongly only if evidence shows:

```text
resource sizing
budget awareness
cleanup
stack deletion
orphan check
```

Do not claim bonus depth only because the architecture mentions security/cost services.

---

## 9.6 Final Evidence Checklist

### Architecture

```text
[ ] production architecture matches final feature
[ ] lab architecture matches actual deployment
[ ] production vs lab differences are clearly labelled
```

### CloudFormation

```text
[ ] all 4 stacks successful
[ ] all 4 stacks shown live in AWS Management Console
[ ] Resources tab evidence captured
[ ] Outputs tab evidence captured
[ ] stack outputs/imports visible
[ ] latest templates used
[ ] no manually maintained duplicate infrastructure
```

### Network

```text
[ ] VPC
[ ] 6 subnets
[ ] routes
[ ] NAT
[ ] NACLs
[ ] S3/DynamoDB endpoints
```

### Core

```text
[ ] public ALB
[ ] internal ALB
[ ] 2 frontend targets
[ ] 2 backend targets
[ ] dummy DB primary
[ ] dummy DB standby
```

### Website

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

### Catalogue

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

### Monitoring

```text
[ ] SNS confirmed
[ ] frontend alarms
[ ] backend alarms
[ ] catalogue alarm
[ ] catalogue logs
```

### Reliability

```text
[ ] frontend failure/replacement
[ ] backend failure/replacement
[ ] site remains available during controlled test
[ ] Auto Scaling Activity History evidence captured
[ ] target-health evidence captured
[ ] backup screenshots ready for presentation
```

### Cost / Cleanup

```text
[ ] budget captured
[ ] cleanup script tested
[ ] all stacks deleted when finished
[ ] S3 emptied
[ ] ECR cleaned
[ ] no orphaned EC2/ALB/ECS/S3/DynamoDB resources
```

---

## 9.7 Final Risks Before Submission

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

## 9.8 Final Recommendation

The final project recommendation is:

```text
KEEP
→ the strong GP1 two-AZ production foundation

IMPROVE
→ operations through CloudFormation, monitoring and repeatable procedures

PROVE
→ reliability with health-based routing and controlled replacement tests

PILOT
→ Product Catalogue as one Strangler Fig microservice

MEASURE
→ deployment independence, reliability, team effort and business value

DECIDE
→ whether another function should be extracted
```

The most important project message is:

> **AnyGroupLLC does not need a risky full rewrite to begin modernising. It can retain the reliable existing platform, extract one bounded service, operate old and new paths together, and use real evidence to decide the next step.**

---

# Source Basis

This consolidated document is based on the project artefacts produced for Group Project 2, including:

```text
INFOSYS735_GP2_Part01_Final_Requirements_and_Rubric_Matrix.md
INFOSYS735_GP2_Part02_Additional_Feature_Decision.md
INFOSYS735_GP2_Part03_Learner_Lab_Capability_and_Budget_Validation_Completed.md
INFOSYS735_GP2_Part04_Well_Architected_Pillar_Assessment.md
INFOSYS735_GP2_Part05_Group_Project_2_Logical_Architecture.md
INFOSYS735_GP2_Part07_Security_Implementation_Plan.md
INFOSYS735_GP2_Part08_Core_AWS_Infrastructure.md
INFOSYS735_GP2_Part11_S3_Implementation.md
INFOSYS735_GP2_Part12_Strangler_Fig_Catalogue_Microservice.md
INFOSYS735_GP2_Complete_Architecture_Diagram.md
INFOSYS735_GP2_Complete_Project_Plan_Compact.md
INFOSYS735_GP2_IaC_Deployment_and_Usage_Instructions.md
01-network-stack.yaml
02-core-infrastructure-stack.yaml
03-observability-stack.yaml
04-microservice-stack.yaml
```

Where older artefacts describe the previous one-ALB / one-backend / one-dummy-DB prototype, this document uses the **latest final lab architecture**:

```text
Public ALB
→ Frontend ASG ×2
→ Internal ALB
   ├── Backend ASG ×2
   │    → Dummy DB Primary + Standby
   │
   └── Fargate Catalogue ×2
        → DynamoDB
        → private S3
```

That updated architecture is the source of truth for final deployment, testing and presentation.
