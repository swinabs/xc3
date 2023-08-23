import boto3
import json
import os
import urllib3


def lambda_handler(event, context):
    # Extract the SNS message from the Lambda event
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])

    # Extract relevant details from the SNS message
    alarm_name = sns_message['AlarmName']
    alarm_description = sns_message['AlarmDescription']
    aws_account_id = sns_message['AWSAccountId']
    region = sns_message['Region']
    threshold = sns_message['Trigger']['Threshold']

    # Compose the email subject and body
    subject = f"CloudWatch Alarm Triggered: {alarm_name}"
    body = (
        f"<html>"
        f"<head>"
        f"<style>"
        f"  body {{"
        f"    font-family: Arial, sans-serif;"
        f"    padding: 20px;"
        f"    background-color: #E5E4D9;"
        f"    border-radius: 5px;"
        f"  }}"
        f"  .container {{"
        f"    background-color: #ffffff;"
        f"    border-radius: 5px;"
        f"    padding: 20px;"
        f"    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);"
        f"  }}"
        f"  .property {{"
        f"    margin-bottom: 10px;"
        f"  }}"
        f"  .message {{"
        f"    padding: 10px;"
        f"    margin-top: 20px;"
        f"  }}"
        f"  .logo img {{"
        f"    max-width: 150px;"
        f"    height: auto;"
        f"  }}"
        f"  .property table {{"
        f"    width: 100%;"
        f"    border-collapse: collapse;"
        f"    border: 1px solid #ddd;"
        f"  }}"
        f"  .property th, .property td {{"
        f"    padding: 8px;"
        f"    text-align: left;"
        f"    border-bottom: 1px solid #ddd;"
        f"  }}"
        f"</style>"
        f"</head>"
        f"<body>"
        f"  <div class='container'>"
        f"    <h4>Alarm Details</h4>"
        f"    <p>Dear User,</p>"
        f"    <p>Your AWS account cost has exceeded, and the {alarm_name} has triggered. Details are as follows:</p>"
        f"    <table class='property'>"
        f"      <tr><th><strong>Property</strong></th><th><strong>Value</strong></th></tr>"
        f"      <tr><td>Alarm Name:</td><td>{alarm_name}</td></tr>"
        f"      <tr><td>Alarm Description:</td><td>{alarm_description}</td></tr>"
        f"      <tr><td>AWS Account ID:</td><td>{aws_account_id}</td></tr>"
        f"      <tr><td>Region:</td><td>{region}</td></tr>"
        f"      <tr><td>Threshold from Trigger:</td><td>{threshold}</td></tr>"
        f"    </table>"
        f"  </div>"
        f"  <div class='message'>"
        f"    <p>Best regards,<br>XC3 Team</p>"
        f"    <p style='color:red;'><b>This is an automated mail. Please do not reply.</b></p>"
        f"  </div>"
        f"</body>"
        f"</html>"
    )

    # Send the email
    send_email(subject, body)
    send_slack(alarm_name, alarm_description, aws_account_id, region, threshold, iam_user)

    return "Email and Slack notifications sent successfully"


def send_email(subject, body):
    # Configure the email sender
    sender_email = os.environ["sender_email"]
    recipient_email = os.environ["recipient_email"]
    aws_region = os.environ["region"]

    # Create an AWS Simple Email Service (SES) client
    ses = boto3.client('ses', region_name=aws_region)

    # Send the email
    response = ses.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': body}}
        }
    )

    return response


def send_slack(alarm_name, alarm_description, aws_account_id, region, threshold, iam_user):
    http = urllib3.PoolManager()

    # slack_url = os.environ["slack_channel_url"]
    #slack_url = "https://hooks.slack.com/services/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"

    message_text = f"Dear User,\n\n"
    message_text += f"Your AWS account cost has exceeded, and the {alarm_name} has triggered. Details are as follows:\n"
    message_text += f"---------------------------\n"
    message_text += f"Alarm Name     : {alarm_name}\n"
    message_text += f"---------------------------\n"
    message_text += f"Alarm Description: {alarm_description}\n"
    message_text += f"---------------------------\n"
    message_text += f"Account ID : {aws_account_id}\n"
    message_text += f"---------------------------\n"
    message_text += f"Region : {region}\n"
    message_text += f"---------------------------\n"
    message_text += f"Threshold : {threshold}\n"
    message_text += f"---------------------------\n"

    message_text += f"Best Regards,\nXGrid Team"

    messages = {"text": message_text}

    try:
        r = http.request(
            "POST",
            slack_url,
            body=json.dumps(messages),
            headers={"Content-Type": "application/json"}
        )
        print("Slack notification sent! Status code:", r.status)
        return True
    except Exception as e:
        print("Failed to send Slack notification:", str(e))
        return False
