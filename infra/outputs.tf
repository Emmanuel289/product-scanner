output "image_bucket" {
  description = "The bucket where images are uploaded"
  value       = aws_s3_bucket.uploads.arn
}
output "lambda_function_arn" {
  description = "The lambda function that scans the images"
  value       = aws_lambda_function.scanner.arn
}

output "api_url" {
  value = "${aws_api_gateway_stage.prod.invoke_url}/scan"
}
