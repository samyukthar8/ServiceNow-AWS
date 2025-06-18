# ServiceNow + AWS EC2 Provisioning with CMDB Update
This project demonstrates a bi-directional integration between ServiceNow and AWS, enabling seamless EC2 provisioning from the ServiceNow Employee Center with automatic CMDB updates.

# Use Case

Employees can raise a self-service request for an EC2 instance directly from the ServiceNow portal.

The request captures:

-->EC2 instance name

-->Operating System (via AMI selection)

Once submitted, the request flows through an approval workflow (e.g., manager approval).

Upon approval:

-->A new EC2 instance is provisioned in AWS

-->Key instance details are auto-updated in ServiceNow CMDB (using cmdb_ci_ec2_instance)
![image](https://github.com/user-attachments/assets/6a5c6ce9-e6ba-4d5f-9f94-9dd7870788cc)
![image](https://github.com/user-attachments/assets/6f3e8077-7075-4639-b2dc-6db6f79a69d1)
![image](https://github.com/user-attachments/assets/ff4a9915-7133-49b2-b59a-9c0fc11a8a12)
![image](https://github.com/user-attachments/assets/73e071ee-d54e-4eb1-98ea-e86ac868178a)
![image](https://github.com/user-attachments/assets/94a6b04f-984f-4f34-a96f-88b6bddd5633)

# Tech Stack

-->ServiceNow Flow Designer

Used to build the approval & provisioning workflow

Custom Action created using Integration Hub REST step

-->AWS Lambda

Handles EC2 provisioning using Python + Boto3

Also pushes instance data to ServiceNow CMDB via REST

-->AWS API Gateway

Acts as a bridge between ServiceNow and Lambda

-->CMDB Update

Uses OOB table cmdb_ci_ec2_instance from the Cloud Management Core plugin

# Deployment steps:

   1)Create catalog item shown in image,provide values of ami-id in choice value for os
   ![image](https://github.com/user-attachments/assets/730e092a-f81e-4c19-91a7-b69d31e89ee2)
   ![image](https://github.com/user-attachments/assets/422c03d5-7798-4cd8-96c2-ec3086f7d58e)
   
   2)Go to AWS and setup Lambda, paste the code given and also attach ec2 full access permissions.
   
   3)Create API gateway in aws and link to the Lambda
   
   4)In ServiceNow go to Intergration Hub->connections
  ->Configure connection&in connection alias configure the API gateway url
  ![image](https://github.com/user-attachments/assets/e5cec605-3508-4dba-8f50-5425ac1a44e3)
  -> Create custom action
  -> Do the settings and configure json payload as described in image
  ![image](https://github.com/user-attachments/assets/9cd3d4d6-6667-4909-afad-0d5c281132c5)
5)Create flow in a similar manner calling the custom action we created
![image](https://github.com/user-attachments/assets/454da73c-f799-4e0e-a6a4-8eef4170f79f)


