data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../src/alert/notifier.py"
  output_path = "${path.module}/notifier.zip"
}

resource "aws_lambda_function" "notifier" {
  function_name    = "${var.namespace}-notifier"
  runtime          = "python3.9"
  handler          = "notifier.lambda_handler"
  timeout          = 60
  memory_size      = 128
  role             = aws_iam_role.notifier_role.arn
  filename         = data.archive_file.lambda_zip.output_path

  environment {
    variables = {
      sender_email = var.sender_email
      recipient_email = var.recipient_email
      region = var.region
      slack_channel_url = var.slack_channel_url
      ACCOUNT_ID = var.account_id
    }
  }
}

# Create an IAM role for the Lambda function
resource "aws_iam_role" "notifier_role" {
  name = "${var.namespace}-notifier_role"

  # Define the trust policy to allow the Lambda service to assume this role
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# Attach the necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution_attachment" {
  role       = aws_iam_role.notifier_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define a custom IAM policy for Send Email permissions
resource "aws_iam_policy" "notifier_custom_policy" {
  name        = "${var.namespace}-CombinedLambdaCustomPolicy"
  description = "Custom IAM policy for combined Lambda function"

  # Define the policy document allowing the "ses:SendEmail" action
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach the custom policy to the IAM role
resource "aws_iam_role_policy_attachment" "notifier_custom_policy_attachment" {
  role       = aws_iam_role.notifier_role.name
  policy_arn = aws_iam_policy.notifier_custom_policy.arn
}

# Attach the Amazon SES policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_ses_policy_attachment" {
  role       = aws_iam_role.notifier_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

# Add the SNS topic trigger to the Lambda function
resource "aws_lambda_permission" "lambda_sns_trigger_permission" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notifier.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.alert_sns_topic_arn
}