# Create a zip archive of the Lambda function code
data "archive_file" "zip" {
  type        = "zip"
  source_file = "../src/alert/cost_metric_lambda.py"
  output_path = "${path.module}/cost_metric_lambda.zip"
}

# Define an IAM role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${var.namespace}-cost-metric-lambda-role"

  # Define the trust policy to allow the Lambda service to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

# Attach the AWS Lambda basic execution role policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define a custom IAM policy for Cost Explorer and CloudWatch access
resource "aws_iam_policy" "custom_policy" {
  name        = "${var.namespace}-CustomCostExplorerCloudWatchPolicy"  # Name of the custom policy
  description = "Custom policy for Cost Explorer and CloudWatch access"

  # Define the policy document allowing ce:GetCostAndUsage, cloudwatch:PutMetricAlarm, and cloudwatch:PutMetricData actions
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the custom policy to the IAM role
resource "aws_iam_role_policy_attachment" "cost_explorer_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.custom_policy.arn
}

# Define a custom IAM policy for S3 bucket access
resource "aws_iam_policy" "s3_bucket_access_policy" {
  name        = "${var.namespace}-S3BucketAccessPolicy"
  description = "Custom IAM policy for S3 bucket access"

  # Define the policy document allowing read access to the specific S3 bucket
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*",
          "arn:aws:s3:::${var.s3_xc3_bucket.id}"
        ]
      },
    ]
  })
}

# Attach the S3 bucket access policy to the IAM role
resource "aws_iam_role_policy_attachment" "s3_bucket_access_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_bucket_access_policy.arn
}


# Define an AWS Lambda function resource
resource "aws_lambda_function" "cost_metric_lambda" {
  function_name    = "${var.namespace}-cost_metric_lambda"
  runtime          = "python3.9"
  handler          = "cost_metric_lambda.handler"
  timeout          = 60
  memory_size      = 128
  role             = aws_iam_role.lambda_role.arn  # IAM role ARN for the Lambda function's permissions
  filename         = data.archive_file.zip.output_path

  # Set the environment variable for the Lambda function
  environment {
    variables = {
      BUCKET = var.s3_xc3_bucket.bucket
      MAXIMUM_BUDGET = var.maximum_budget
      CLOUDWATCH_NAMESPACE = var.cloudwatch_namespace
      METRIC_NAME = var.metric_name
    }
  }
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "LambdaScheduleRule"
  description         = "Schedule Lambda to run every day"
  schedule_expression = "cron(0 0 * * ? *)"  # Run at 00:00 UTC every day
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  arn       = aws_lambda_function.cost_metric_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_metric_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}
