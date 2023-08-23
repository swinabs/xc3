Introduction
Welcome to the user manual for the Alert Feature of the XC3! This manual is designed to
provide developers with all the information they need to understand, install, configure, and effectively use the codebase. The main purpose of this feature is to send an alert to the end user on three levels: AWS account level, AWS resources level and IAM user level when the pre defined cost threshold crossed.

Functional requirements
➢ Implementing an end-to-end alerting mechanism that covers all stages of the alerting
process.
➢ Defining the specific threshold criteria or conditions that trigger the alerts.
➢ Generating alerts promptly when the threshold is met.
➢ Sending the alert information to relevant communication channels, such as email, SMS,
or instant messaging services.
➢ Ensuring the proper integration and functionality of the communication channels to
transmit the alerts effectively.
➢ Providing a means to configure and customize the alerting system to accommodate
different requirements.
➢ Handling and addressing potential errors or exceptions that may occur during the
alerting process.
➢ Ensuring the scalability and performance of the alerting mechanism to handle large
volumes of data and alerts.
Inputs: Outputs: Alerts
Make a parameterized variable for the threshold

System Requirements
Software Requirements
The bare minimum software requirements to run the AlertFeature are:
➢ Terraform 1.0+
➢ Python 3.9
➢ AWScli
➢ AWS cloud access with administrative privilege ➢ IDE/Code editor

Chapter 3 Configuration
This chapter emphasizes on how to configure the AWS Lambda function and associated resources using Terraform. The provided configuration allows the developers to set up a notification mechanism for CloudWatch Alarms through email and Slack notifications.
This chapter emphasizes on how to configure the AWS Lambda function and associated resources using Terraform. The provided configuration allows the developers to set up a notification mechanism for CloudWatch Alarms through email and Slack notifications.

Terraform variables
1. Navigate to xc3/infrastructure and configure the terraform.auto.tf.vars file.
Update the variables according to the requirements of your project.
Maximum Budget should be the maximum budget for your project.
Threshold should be the desired threshold to check the cost and trigger the alarm Cloud watch Namespace is the space to hold all the cloud watch metrics
Metric Name is the value for the total cost metric name
2. Once variables are configured, execute the following commands:
  terraform apply

Enter yes after being prompted to enter.

The successful apply should see the infrastructures for alerting feature added to the existing XC3 infrastructure.
The configuration uses Terraform variables to customize the behavior of the resources. We will have to Review and adjust these variables according to the requirements:
File name: variables.tf

Variables to be configured
1. sender_email: The sender's email address for notifications. Default: swinabs@gmail.com
2. recipient_email: The recipient's email address for notifications. Default: swinabs@gmail.com
3. region: The AWS region where the resources will be deployed. Default: ap-southeast- 2
4. slack_channel_url: The URL of the Slack channel for notifications. Default: (leave empty)

Steps to Configure
Follow these steps to configure the notification mechanism using AWS Lambda and Terraform:
1. Edit Variables: Open the variables.tf file and adjust the values of the variables based on your preferences. These variables will customize the notifications and resource settings.
2. Python Notification Script (notifier.py): The provided Python script defines the logic for handling CloudWatch Alarm notifications. You can customize this script to format
notifications, change the content, or add additional actions.
3. Deploy the Configuration: Open your terminal and navigate to the directory containing
the configuration files. Run the following Terraform commands:
terraform init terraform plan terraform apply

Terraform will initialize, create an execution plan, and apply the plan to create the AWS Lambda function, IAM roles, policies, and other required resources.

Review Resources
Once Terraform applies the configuration, review the created resources in your AWS
Management Console to ensure they match your expectations.

Cleaning Up
When you no longer need the configured resources, use the following command to destroy them and clean up:
terraform destroy

Installation
This chapter guides you through the installation process of the required tools and resources to
set up CloudWatch Alarm notifications using AWS Lambda and Terraform. 4.1 Deployment
With the code and configuration customized, follow these steps to deploy the CloudWatch Alarm notification system:
1. Open a terminal window and navigate to the directory containing the downloaded code and configuration files.
2. Run the following commands in sequence to deploy the resources:
terraform init terraform plan terraform apply
2. These commands initialize Terraform, create an execution plan, and apply the plan to provision AWS Lambda, IAM roles, policies, and other resources.
3. Review the resources created in your AWS Management Console to ensure they match your expectations.

Clean Up
When you're finished with the CloudWatch Alarm notification system, follow these steps to
clean up:
In the terminal, navigate to the same directory as before and run the following command:
terraform destroy

 Code Structure

Cost Metric Lambda Function
Terraform file with resources for creating lambda function and required IAM roles and policies, cloud watch event is inside the infrastructure->modules->serverless folder with file name get_cost_metric.tf
The variables that are used in this file are firstly listed in the variables.tf file along with all other necessary variables for the alerting feature.
xc3->infrastructure->variables.tf

Then only the variables needed for the module should be listed and values should be passed under the serverless module in the file
xc3->infrastructure->main.tf
 After that, again we need to list the variables that will be used in the serverless module and have received the values from the main.tf file. It should be done in the file
xc3->infrastructure->serverless->variables.tf

The python file that is necessary to create lambda function is placed inside src>alert folder with name cost_metric_lambda.py

Cloud watch Alarms and SNS Topic
Terraform file for creating resources SNS topic and Cloud watch Alarms are placed under module xc3
infrastructure->modules->xc3 folder with name main.tf

Testing Cost Metric Lambda Function
If you want to test the lambda function to calculate the cost percentage and push to cloud watch metrics, you can follow the following steps
Function name: {namespace}-cost_metric_lambda
Select the "Test" option and set up a test using the default test JSON. Provide a name for your test and run it.
 After the successful run of cost metric lambda you will be able to see the metrics at the Cloud watch metrics under the Cloud watch namespace that you have provided in terraform.auto.tf.vars
10

 Monitoring the Cloud watch
You can search Cloud watch in top search bar to get the Cloud watch Alarms, then click All Alarms to view all existing alarms.
The alarms with state with Ok mean the cost data related to the specific alarms hasn’t crossed the threshold and the alarms with In Alarm means the alarms has been triggered as the cost data is greater than the threshold mentioned.

SNS Topic
After alarm is triggered by cloud watch the message is sent from the cloud watch to SNS topic with
the details of the Alarm Triggered.
The SNS topic can be viewed at

SNS Topic Name: {namespace}-cost-exceeds-threshold-topic

Response Data From SNS Topic
After message is received from Cloud watch SNS Topic sends the message to the lambda function
that is subscribed to it. The message format in which the SNS topic sends can be seen below.

It contains all the details
AlarmName, Alarm Description, AWSAccountId, Threshold, MetricName and Namespace that might be required to send notification.
Now, you will be introduced to the structure of the notifier.py Python script and the associated Terraform configuration files (notifier.tf and variables.tf). These files collectively define the AWS Lambda function and the necessary infrastructure to handle CloudWatch Alarm notifications via email and Slack.

Python Script : notifier.py
This a Python script designed to be used as an AWS Lambda function. The Lambda function is meant to handle CloudWatch Alarm notifications by sending email and Slack notifications when a certain threshold is breached. Here's a breakdown of its purpose and functionality:

➢ Import Statements: The script imports necessary libraries/modules for AWS services, JSON handling, operating system interactions, and HTTP requests.
➢ Lambda Handler Function (`lambda_handler`): This function is the entry point for the Lambda execution. It takes two parameters, `event` and `context`, which are provided by the Lambda service when the function is triggered.
➢ Extracting SNS Message: The SNS message is extracted from the `event` parameter. SNS (Simple Notification Service) is a messaging service used for sending notifications to various endpoints, including email, SMS, and more.
➢ Extracting Alarm Details: The script extracts relevant details from the SNS message, such as alarm name, description, AWS account ID, region, and threshold.
➢ Composing Email Body: The script composes an HTML-formatted email body that contains the extracted alarm details. The body includes stylized CSS and information presented in a table format.
➢ Sending Email: The `send_email` function sends the composed email using AWS SES (Simple Email Service). It includes the subject and HTML body of the email.
➢ Sending Slack Notification: The `send_slack` function sends a notification to a Slack channel using an HTTP POST request. It formats the message with the extracted alarm details.
➢ Return Statement: The Lambda handler function returns a success message indicating that the email and Slack notifications have been sent successfully.

➢ Send Email and Slack Notifications: The script calls the `send_email` and `send_slack` functions to send the notifications.
In summary, this code sets up an AWS Lambda function that is triggered when a CloudWatch Alarm is triggered. The Lambda function sends an email and a Slack notification to notify a user or team about the alarm details, such as the breach of a certain threshold in AWS account costs. The email content is formatted using HTML, and the Slack message is sent via an HTTP POST request.

Terraform Configuration: notifier.tf

The notifier.tf file defines the infrastructure resources required for the AWS Lambda function,
IAM roles, policies, and permissions.
This Terraform code is used to create an AWS Lambda function along with the required IAM roles and permissions to set up a notification mechanism for CloudWatch Alarms using AWS Lambda. Let's break down the purpose of each section of the code:
➢ Create an Archive File (`data "archive_file" "lambda_zip" { ... }`): This section creates a zip archive file containing the Python script "notifier.py" (presumably containing notification logic) that will be uploaded and used by the Lambda function. The script is compressed into a zip file named "notifier.zip."
➢ Create an AWS Lambda Function (`resource "aws_lambda_function" "notifier" { ... }`): This section defines an AWS Lambda function named "${var.namespace}- notifier". It specifies various configuration options for the Lambda function, including runtime, handler, timeout, memory size, role, and environment variables. The Lambda function will use the archive file created in the previous step as its source code.
➢Create an IAM Role for the Lambda Function (`resource "aws_iam_role" "notifier_role" { ... }`): This section creates an IAM role named "${var.namespace}-


notifier_role" that will be assumed by the Lambda function. The trust policy allows the Lambda service to assume this role.
➢ Attach Policies to the IAM Role (`resource "aws_iam_role_policy_attachment" ...`): These sections attach various policies to the IAM role created in step 3. These policies include the AWS managed policy "AWSLambdaBasicExecutionRole" (providing basic execution permissions for Lambda) and a custom policy that grants permission to send emails via Amazon SES. Additionally, the policy "AmazonSESFullAccess" is attached to allow full access to Amazon Simple Email Service (SES).
➢ Add SNS Trigger Permission (`resource "aws_lambda_permission" ...`): This section grants permission to the Lambda function to be triggered by an Amazon SNS topic. The Lambda function will be allowed to execute when the SNS topic (likely used for CloudWatch Alarms) publishes messages to it.
Overall, the code's purpose is to set up an AWS Lambda function that can be triggered by CloudWatch Alarms through an SNS topic. The Lambda function handles notifications by sending emails and potentially other actions, and it is appropriately configured with IAM roles, policies, and permissions to execute these actions securely within the AWS environment. The use of Terraform allows for infrastructure-as-code management and provisioning of these resources.

Terraform Variables: variables.tf
The variables.tf file defines input variables that customize the behavior of the Terraform
configuration.
This code defines Terraform variables that can be used to customize and parameterize the configuration of infrastructure resources. Variables in Terraform allow you to make your code more flexible and reusable by separating the values that can change from the actual resource definitions.
Here's the purpose of each variable defined in the code:

sender_email: This variable is used to specify the email address of the sender. It is intended to be used as a parameter in the Terraform code to provide the sender's email address for notifications or other purposes.
recipient_email: This variable is used to specify the email address of the recipient. Similar to the sender's email, it is intended to be used as a parameter in the Terraform code to provide the recipient's email address for notifications or other uses.
region: This variable is used to specify the AWS region where the infrastructure resources will be deployed. It is intended to allow users to choose the region in which their resources will be provisioned.
slack_channel_url: This variable is used to specify the URL of a Slack channel. It is intended to be used as a parameter to provide the URL of the Slack channel where notifications or messages should be sent.
The `description` field for each variable provides a brief explanation of what each variable is used for, aiding in documentation and understanding. The `type` field specifies the data type of the variable, such as string, number, or boolean. The `default` field provides a default value that will be used if no value is explicitly provided when running Terraform.
By defining these variables, you can write more flexible and reusable Terraform configurations. Users can customize the behavior of the infrastructure by providing different values for these variables without modifying the main resource definitions. This promotes consistency, makes it easier to manage changes, and allows you to reuse the same Terraform code with different configurations.

Troubleshooting
If you encounter any issues while setting up or using the CloudWatch Alarm notification mechanism with the provided Terraform configuration and notifier.py script, refer to the following troubleshooting tips to help resolve common problems.

 Issue: Lambda Function Execution Failure Solution:
1. Check the CloudWatch Logs for the Lambda function to identify any error messages or exceptions thrown during execution.
2. Review the IAM role permissions associated with the Lambda function. Ensure that it has necessary permissions to execute Lambda functions, access SES, and send messages to the specified Slack channel.
3. Verify that the Python script notifier.py is correctly formatted and contains the necessary code. Any syntax errors or missing modules could lead to execution failures.

Issue: Email or Slack Notifications Not Received Solution:
1. Confirm that the email sender's and recipient's email addresses are correctly provided in the Terraform variables. Make sure they are valid email addresses.
2. Ensure that the AWS Simple Email Service (SES) is correctly configured in your AWS account, and the sender's email address is verified.
3. Double-check the Slack channel URL provided in the variables. Ensure it is the correct URL for the intended Slack channel.

 Issue: Missing Terraform Variables Solution:
1. Ensure that you have correctly defined and set the required Terraform variables in your variables.tf file. Review the variable names and descriptions to ensure accuracy.
2. Check that you have provided appropriate default values for the variables, or you have provided custom values when executing Terraform commands.

 FAQs (Frequently Asked Questions) Q1: What is the purpose of the notifier.py script?
Answer: The notifier.py script is a Python script that serves as the logic for the AWS Lambda function. It extracts information from CloudWatch Alarm notifications, such as alarm details and thresholds, and sends notifications through email and Slack.
Q2: How do I customize the email and Slack notifications?
Answer: You can customize the content and formatting of email and Slack notifications by modifying the respective sections in the notifier.py script. Update the HTML email body or Slack message text according to your preferences.
Q3: Can I modify the notification triggers or actions?
Answer: Yes, you can customize the notification triggers and actions by modifying the CloudWatch Alarm configurations that trigger the Lambda function. Additionally, you can extend the notifier.py script to perform additional actions based on your requirements.
Q4: How do I handle security for sensitive information?
Answer: Handle sensitive information, such as email addresses and Slack URLs, securely. Consider using AWS Secrets Manager or Parameter Store to store sensitive data and retrieve it securely within your Lambda function.
Q5: What if I encounter errors during Terraform execution?
Answer: Refer to the "Troubleshooting" section in this manual for guidance on addressing common issues. Check your Terraform command syntax, IAM role permissions, and resource configurations.
Q6: Can I deploy the Lambda function to a different AWS region?
Answer: Yes, you can modify the region variable in the variables.tf file to specify the desired AWS region for deployment.

Chapter 8 Contact Information
If you have any questions, feedback, or need further assistance with setting up and using the CloudWatch Alarm notification mechanism using Terraform, you can reach out to us through the following channels:
• Email: For inquiries and communication, you can contact us via email at swinabs@gmail.com.
• GitHub: You can explore the code, report issues, or contribute to the project on GitHub by visiting our repository: https://github.com/swinabs.
• Slack: Join our Slack community to connect with fellow users, share experiences, and get help from experts. Join our Slack channel at https://slack.example.com.
We are committed to providing you with the support and assistance you need to successfully implement and manage CloudWatch Alarm notifications using Terraform. Feel free to contact us at any time.


