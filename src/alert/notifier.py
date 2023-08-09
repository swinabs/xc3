import base64
import boto3
import json
from botocore.exceptions import ClientError
import urllib3
import datetime
import os
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Fetch the logo image URL from S3
bucket_name = os.environ['BUCKET']
logo_key = "logo.png"

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def lambda_handler(event, context):
    cost_explorer = boto3.client('ce', region_name = os.environ["region"] )

    current_time = datetime.datetime.utcnow()
    # calculate the start and end dates for the current month
    last_month = current_time-datetime.timedelta(days=1)
    start_date = datetime.datetime(last_month.year, last_month.month, 1).strftime('%Y-%m-%d')
    end_date = last_month.strftime('%Y-%m-%d')

    #retrieve the cost data using the Cost explorer
    response = cost_explorer.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['BlendedCost']
    )
    print(response)

    #transform the cost data as needed
    transformed_data = transform_data(response)

    # send email and Slack notifications with
    send_notification(transformed_data)

    return {
        'statusCode': 200,
        'body': json.dumps('Cost data retrieved and email sent')
    }

def transform_data(response):
    transformed_data = []
    total_cost = 0.0
    for result in response['ResultsByTime']:
        cost = float(result['Total']['BlendedCost']['Amount'])
        total_cost += cost
        transformed_data.append({
            'time': result['TimePeriod']['Start'],
            'cost': cost
        })
    transformed_data.append({
        'time': 'Total',
        'cost': total_cost
    })
    return transformed_data

def send_notification(response):
    # Prepaere the message text for email and slack
    message = ""
    total_cost_message = f"Your Total cost for this month: ${response[-1]['cost']:.2f}\n"
    for entry in response[:-1]:
        message += f"Time: {entry['time']} Cost: ${entry['cost']:.2f}\n"

    # insert total cost message at te beginning of the message
    message = total_cost_message + message

    csv_file_name = "/tmp/cost_data.csv"
    with open(csv_file_name, mode='w', newline='') as csv_file:
        fieldnames = ['Time', 'Cost']
        writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
        writer.writeheader()
        for entry in response:
            writer.writerow({'Time': entry['time'], 'Cost': entry['cost']})

    send_slack()
    send_email(message, csv_file_name)

def send_email(data, csv_file_name):
    SENDER = os.environ["sender_email"]
    RECIPIENT = os.environ["recipient_email"]
    AWS_REGION = os.environ["region"]
    SUBJECT = "AWS Account Cost Alert"
    # BODY_TEXT = "Alarm Triggered"
    # BODY_HTML = f"<html><body><h1>Cost Usage Reminder</h1><pre>Hello this is a reminder to notify you that your account has just crossed 50% threshold.</pre></body></html>"

    #Prepare HTML body with red color for total cost
    total_cost = data.splitlines()[0]
    total_cost_html = f'<span style="color: red;">{total_cost}</span>'

    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    # Create the email message
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT

    # Get the object (logo) from S3 Bucket
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket = bucket_name, Key = "logo.png")
    logo_data = response["Body"].read()

    # # Encode the logo image data in Base64
    # logo_base64 = base64.b64encode(logo_data).decode("utf-8")

    try:
        # Create the HTML version of the email body with logo
        html_body = f""" 
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
                <div class="logo">
                    <img src="data:image/png;{logo_data}" alt="Your Logo">
                </div>
                <div class="message">
                    <h2> {total_cost_html}</h2>
                    <p>Dear XC3 Customer,</p>
                    <p>Your AWS account cost exceeded 80%. Please find the cost breakdown below:</p>
                </div>
                <div class="message">
                    <p>Please find the attached file for detailed cost information.</p>
                    <p>Best regards,<br>XC3 Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        # Attach the HTML body
        html_part = MIMEText(html_body, 'html', CHARSET)
        msg.attach(html_part)
    except Exception as e:
        print("Error reading logo.png from S3", str(e))
    try:
        # Attach csv file
        with open(csv_file_name, 'rb') as attachment:
            csv_part = MIMEApplication(attachment.read())
            csv_part.add_header('Content-Disposition', f'attachment; filename="{csv_file_name}"')
            msg.attach(csv_part)

        response = client.send_raw_email(RawMessage={'Data': msg.as_string()})
        print("Email sent! Message ID: ", response)
    except ClientError as e:
        print("Failed to send email: ", str(e))

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
