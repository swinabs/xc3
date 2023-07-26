output "grafana_api_gateway" {
  value = aws_api_gateway_rest_api.apiLambda.id
}

output "notifier_lambda_function_arn" {
  value = aws_lambda_function.notifier.arn
}
