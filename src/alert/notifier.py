import boto3
import json
from botocore.exceptions import ClientError
import urllib3
import os


def lambda_handler(event, context):
    email_status = send_email()
    slack_status = send_slack()

    if email_status and slack_status:
        response_msg = 'Email and Slack Notification sent successfully'
        status_code = 200
    else:
        response_msg = 'Failed to send one or more notifications'
        status_code = 500

    return {
        'statusCode': status_code,
        'body': json.dumps(response_msg)
    }


def send_email():
    SENDER = os.environ["sender_email"]
    RECIPIENT = os.environ["recipient_email"]
    AWS_REGION = os.environ["region"]
    SUBJECT = "Cost Usage Reminder"
    BODY_TEXT = "Alarm Triggered"
    BODY_HTML = f"<html><body><h1>Cost Usage Reminder</h1><pre>Hello this is a reminder to notify you that your account has just crossed 50% threshold.</pre></body></html>"
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [RECIPIENT],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        print("Email sent! Message ID:", response['MessageId'])
        return True
    except ClientError as e:
        print("Failed to send email:", e.response['Error']['Message'])
        return False


def send_slack():
    http = urllib3.PoolManager()
    slack_url = os.environ["slack_channel_url"]

    messages = {"text": "Hello this is a reminder to notify you that your account has just crossed 50% threshold."}

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
