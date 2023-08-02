import boto3
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError


def handler(event, context):
    bucket_name = os.environ['BUCKET']
    directory_name = 'cost-metrics'
    file_name = f'{directory_name}/total_account_cost.json'

    # Get the JSON file from S3
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        json_data = response['Body'].read().decode('utf-8')

        # Parse the JSON data to extract the cost information
        cost_data = json.loads(json_data)

        # Get the current month in the format "January", "February", etc.
        current_month = datetime.utcnow().strftime('%B')

        # Get the account ID from the cost_data dictionary
        account_id = list(cost_data.keys())[0]

        # Get the total cost for the current month
        total_cost = cost_data[account_id].get(current_month, 0.0)

        # Get the maximum budget from environment variables
        maximum_budget = float(os.environ['MAXIMUM_BUDGET'])

        # Calculate the cost percentage based on the maximum budget
        cost_percentage = (total_cost / maximum_budget) * 100

        # Publish the cost percentage as a custom metric to CloudWatch Metrics
        publish_to_cloudwatch(cost_percentage)

        return {
            'statusCode': 200,
            'body': json.dumps('Cost data retrieved from S3 and pushed to CloudWatch Metrics')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # JSON file is not found, provide an error message
            return {
                'statusCode': 400,
                'body': json.dumps(
                    'Total account cost JSON file not found. Please run the total account cost Lambda function first.')
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(
                    'Something Went Wrong.')
            }


def publish_to_cloudwatch(cost_percentage):
    cloudwatch = boto3.client('cloudwatch')

    # Get the namespace and metric name from environment variables
    cloudwatch_namespace = os.environ['CLOUDWATCH_NAMESPACE']
    metric_name = os.environ['METRIC_NAME']

    # Publish the cost percentage as a custom metric
    cloudwatch.put_metric_data(
        Namespace=cloudwatch_namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': cost_percentage,
                'Unit': 'Percent'
            }
        ]
    )
