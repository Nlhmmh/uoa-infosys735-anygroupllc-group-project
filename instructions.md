Group Project 2
Due 23 Oct by 17:00 Points 100 Submitting a file upload Available 23 Sep at 10:00 - 26 Oct at 16:00
Overview

In this assessment, we will continue to work with the company AnyGroupLLC. To ensure your proposed solution from part 1 follows good design principles and best practices, please make use of the Well-Architected Framework to verify and improve your design. Then, it is time to implement a cloud architecture solution and deliver a pitch presentation to the stakeholders at AnyGroupLLC.

There are three key learning outcomes of this assessment.

Get familiar with the cloud design principles and understand the importance and the benefits of using the Well-Architected Framework in the design process.
Provide a business context to allow students to implement a cloud architecture solution that is not constrained by the scripted process and descriptions that students see in course labs. 
Provide an opportunity for students to practice teamwork and presentation skills, particularly focusing on pitching their prototype solution.
 

Objectives

Make use of the Well-Architected Framework to ensure the architecture design aligns with best practices and to identify areas for improvement.
Implement the proposed architecture solution using AWS services.
Pitch your solution to the corporate customer with technical and business values.
 

Instructions

Improve your proposed design solution from part 1 to include an additional feature and to align with the best practices (10 marks)
Recall the additional question from the case study, the CTO, CFO and IT manager have asked for some additional features that can assist with their work. The group needs to select ONE of the additional features and design a new solution to include this additional feature.
Choose TWO pillars from the Well-Architected Framework. Check your proposal from part 1 against the design principles and the best practices from the chosen pillars to identify the area of improvement.
If your proposal from part 1 has already met all the best practices from the chosen pillars, please clearly illustrate and explain how it aligns with the framework.
Alternatively, if your proposal has not met all the best practices, please describe which area requires improvement and design a new solution to address this.
Note: If you could check your solution with FOUR or more pillars from the Well-Architected Framework and demonstrate that you can design a more well-rounded solution that covers the best practices from all of the chosen pillars, you can potentially receive up to 5 bonus marks on this task.
Create presentation slides to include the following items:
A new architecture diagram with the new feature and design improvement based on the Well-Architected Framework.
For your two chosen pillars, please explain how the existing/new design aligns with each of the pillars, as well as highlight the area of improvement and the design updates (if any).
Implement a basic outline of your solution on the AWS platform.
A recommendation is to use the Learners Lab environment.
Core components you have to implement (30 marks): 
VPC's, subnets, AZ, NAT server instances1
Security Groups, NACLs
ELB's, autoscaling (SNS, CloudWatch)
EC2's, web servers, S3 buckets
Infrastructure Tiers (e.g. web tier, app tier, db tier)2
Note 1: You could choose NAT gateway instead of NAT server instances. But, be mindful with the high hourly cost rate of the NAT gateway.
Note 2: You do not need to implement actual app servers or actual db servers - they are additional as we have stated below, however, you should implement 'dummy' EC2 servers which are appropriately named to represent app servers or db servers.
Additional components you can implement (20 marks): 
Lambda
ElastiCache
Datastore (DynamoDB, Amazon RDS) with Master/Slave setting
Infrastructure as Code (CloudFormation)
Other options that can contribute to business value
Note: A minimum of one additional component is required for a pass, two for an A range grade.
Record a pitch presentation of your implementation (40 marks)
The presentation length should be within 15 minutes.
Every team member must present a portion of the presentation.
The presentation should include the architecture diagram of your solution and discuss how the design aligns with the chosen pillars of the Well-Architected Framework, and highlight the area of improvement and design updates. Please make use of the presentation slides you created in Task 1.
The presentation should demonstrate the actual implementation of the cloud infrastructure. The implementation demonstration should be based around AWS management console. You should show the configuration of basic and additional components first, and then demonstrate the additional services.
It should also explain the technical rationale, address the business goals and highlight the value proposition.
Don't forget that you are presenting your proposed solution to the client. The information presented should be clear and sound with a good presentation structure and flow.
 

Submissions

Presentation slides that include the final architecture diagram with the additional feature and the explanations on how your design follows the Well-Architected Framework. This can be in a slideshow or a PDF format.
A text file includes the URL for the presentation recording. This can be a Zoom cloud recording, a YouTube link or a shared GoogleDrive/OneDrive link. 
Students also need to complete the group member TeamMates assessment. If you do not submit this and provide feedback on ALL of your group members, there is a 10% penalty in your mark.
 

Q&A

Q: How do I access Learners Lab?

A: It is in the AWS Academy. HereLinks to an external site. is the link. 

Note: Learners Lab has service restrictions. Please read through the README carefully to understand the environment, particularly the "Service usage and other restrictions" section to understand what services are available. This sandbox environment has very stricted rules on IAM services due to security reason. Students must use the pre-configured LabRole and LabInstanceProfile rather than create their own IAM users/roles. Based on the past experience Google Chrome is the best browser choice as some other browsers tend to have hight chances of connection/access issues. 

Q: How much is the budget in the Learners Lab?

A: $50 per student. 

Note: The budgets were provided by AWS, and the lecturers don't have the authority to increase your quota. Some AWS services have a continuous charging rate when services are kept alive. The team should be cautious and should delete those services while they are not using the lab environment. 

Q: Can we use our own AWS account for the project?

A: Yes, you may use your own AWS account. Please note this would be at your own cost. Having said that, you could sign up a new free-tier account with selected services for 6 months. AWS offers $100 credits at the start and can gain $100 more as you explore some AWS services. 

Q: How should we demonstrate our solution?

A: Each team should prepare an architecture diagram for your solution and present it in the pitch presentation video. But a high portion of the pitch presentation should be demonstrating your implementation via the AWS management console. It is crucial to show that the components/services are functioning. It is also important to highlight the technical rationale or business value that your solution contains.

Q: Do we have to cover all the work patterns mentioned in part 1?

A: No, due to service access restrictions and budget limitations of the Learners Lab environment, you might not be able to demonstrate a working solution with all proposed patterns. So, this is not a requirement. It would be a great bonus if you are able to implement the patterns and discuss them.

 

Marking outline

10% - Solution improvement

30% - Infrastructure implementation (Basic)

20% - Infrastructure implementation (Additional)

40% - Presentation

Rubric
Marking rubric
Marking rubric
Criteria	Ratings	Pts
This criterion is linked to a learning outcomeSolution improvement
New solution includes the additional feature and aligns with the design principles of two pillars.
10 to >7.5 Pts
Well-designed architecture diagram with the additional feature well integrated; the design also aligns well with all the design principles; the explanation was clearly and well described.
7.5 to >5.0 Pts
Architecture diagram with the additional feature well integrated; and the design mostly aligns with the design principles; The explanation covers most of the best practices, but misses some points.
5 to >2.5 Pts
Architecture diagram attempts to include the additional feature, but the feature is not well-integrated; the design only aligns with around two-thirds of the best practices; the explanation missed some key points..
2.5 to >0 Pts
Architecture diagram did not include or could not integrate the additional feature; the design aligns with only half or less of the best practices; the explanation was poorly written.
10 pts
This criterion is linked to a learning outcomeInfrastructure (Basic)
Core Components
(VPC, SG, ELB, EC2, Tiers, etc)
30 to >22.5 Pts
The infrastructure was well configured and clearly presented; all compenents are functioning
22.5 to >15.0 Pts
The infrastructure was configured and presented as per requirements; most of the components are functioning.
15 to >7.5 Pts
Some components are not configured and presented as per requirements; Some components are not functioning.
7.5 to >0 Pts
Components omitted and/or poorly configured; many components are not functioning
30 pts
This criterion is linked to a learning outcomeInfrastructure (Additional)
Demonstrated well in the presentation
Lambda, ElastiCache, Datastore, IaC etc
20 to >15.0 Pts
More than one additional service was presented; well configurated and integrated; clear explanation on technical rationale and strong business value
15 to >10.0 Pts
Meet the requriement (one additional service well presented with clear explanation on the business value/techincal rationale)
10 to >5.0 Pts
Demonstrated one additional service but omits business value/technical rationale
5 to >0 Pts
Poorly demonstrated, contents below expected standards
20 pts
This criterion is linked to a learning outcomePresentation
Solutions Architect Pitch to Corporate Customer
40 to >30.0 Pts
Excellent presentation with clear value proposition; won the deal + commission + reward
30 to >20.0 Pts
Good presentation and clearly outlining business and technical value
20 to >10.0 Pts
Solution was presented in an understandable manner; but lacks ability to describe business and technical value well
10 to >0 Pts
Poorly presented; key points missing, value not clear
40 pts
Total points: 100