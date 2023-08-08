import boto3
import datetime
import json
import os


def handler(event, context):
    # Create a Cost Explorer client
    cost_explorer = boto3.client('ce')

    # Get the current date and time
    current_time = datetime.datetime.utcnow()

    # Calculate the start and end dates for the current month
    start_date = datetime.datetime(current_time.year, current_time.month, 1).strftime('%Y-%m-%d')
    end_date = current_time.strftime('%Y-%m-%d')

    # Retrieve the cost data for the specified time period
    response = cost_explorer.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'UnblendedCost'
        ]
    )

    # Extract the total cost from the response
    total_cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

    # Get the maximum budget from environment variables
    maximum_budget = float(os.environ['MAXIMUM_BUDGET'])

    # Calculate the cost percentage based on the maximum budget
    cost_percentage = (total_cost / maximum_budget) * 100

    # Publish the cost percentage as a custom metric to CloudWatch Metrics
    publish_to_cloudwatch(cost_percentage)

    

    return {
        'statusCode': 200,
        'body': json.dumps('Cost data retrieved and pushed to CloudWatch Metrics')
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
