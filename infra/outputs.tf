output "lambda_function_arn" {
  description = "The id of the Lambda function"
  value       = aws_lambda_function.textract_lambda.arn
}
