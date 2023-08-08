import boto3
import json
from botocore.exceptions import ClientError
import urllib3
import os

def lambda_handler(event, context):
    # Extract the message from the SNS event
    sns_message = event['Records'][0]['Sns']['Message']
    message_data = json.loads(sns_message)

    # Extract the relevant values from the message
    cost_percentage = message_data.get('cost_percentage', 0.0)
    maximum_budget = message_data.get('maximum_budget', 0.0)
    total_cost = message_data.get('total_cost', 0.0)

    account_id = str(os.environ['ACCOUNT_ID'])


    email_status = send_email(cost_percentage, maximum_budget, total_cost)
    slack_status = send_slack(cost_percentage, total_cost, maximum_budget)



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



def send_email(cost_percentage, maximum_budget, total_cost):
    SENDER = "swinabs@gmail.com"
    RECIPIENT = "swinabs@gmail.com"
    AWS_REGION = "ap-southeast-2"
    SUBJECT = "Cost Reminder"
    


 BODY_TEXT = "Alarm Triggered"
    BODY_HTML = f""" 
        <html>
        <head>
            <style>
                /* CSS styles... */
                .container {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ccc;
                }}
                .header {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    text-align: center;
                }}
                .logo {{
                    text-align: center;
                }}
                .logo img {{
                    max-width: 200px;
                    height: auto;
                }}
                .message {{
                    margin-top: 20px;
                }}
                .message h2 {{
                    color: red;
                }}
                .message p {{
                    margin: 10px 0;
                }}
                
            </style>
        </head>
        <body>
    <div class="container">
        <div class="header">
            <h2>Your AWS Account Cost Alert</h2>
        </div>
        
        <div class="message">
            <p><b>Dear User,</b></p>
            <p>Your AWS account with Id {account_id}  has exceeded the threshold of {cost_percentage:.2f}%. Below is the cost breakdown:</p>
            <table style="border-collapse: collapse; width: 50%;">
                <tr>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Total Cost</td>
                    <td style="border: 1px solid #dddddd; text-align: right; padding: 8px;">${total_cost:.2f}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Maximum Budget</td>
                    <td style="border: 1px solid #dddddd; text-align: right; padding: 8px;">${maximum_budget:.2f}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Cost Percentage</td>
                    <td style="border: 1px solid #dddddd; text-align: right; padding: 8px;">{cost_percentage:.2f}%</td>
                </tr>
            </table>
        </div>
        <div class="message">
            <p style="color:red;"><b>This is an automated mail. Please do not reply.<b></p>
            <p>Best regards,<br>XC3 Team</p>
            <div class="logo">
            <img src="" alt="Your Logo">
        </div>
        </div>
    </div>
</body>

        </html>
        """
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

def send_slack(cost_percentage, total_cost, maximum_budget):
    http = urllib3.PoolManager()
    
    # slack_url = os.environ["slack_channel_url"]
    slack_url =  "https://hooks.slack.com/services/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"
    
    message_text = f"Dear User,\n\n"
    message_text += f"Your AWS account cost has exceeded the threshold of {cost_percentage:.2f}%. Below is the cost breakdown:\n"
    message_text += f"---------------------------\n"
    message_text += f"Total Cost    : ${total_cost:.2f}\n"
    message_text += f"---------------------------\n"
    message_text += f"Maximum Budget: ${maximum_budget:.2f} \n"
    message_text += f"---------------------------\n"
    message_text += f"Cost Percentage : {cost_percentage:.2f}% \n"
    message_text += f"---------------------------\n"
    message_text += f"Best Regards,\n XGrid Team"

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
