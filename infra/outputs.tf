output "image_bucket" {
  description = "The bucket where images are uploaded"
  value       = aws_s3_bucket.uploads.arn
}
output "lambda_function_arn" {
  description = "The lambda function that scans the images"
  value       = aws_lambda_function.scanner.arn
}

output "api_arn" {
  value = aws_api_gateway_rest_api.scanner_api.arn
}

output "region" {
  value = var.region
}

output "lambda_repository_url" {
  value = aws_ecr_repository.lambda_repo.repository_url
}

output "codebuild_arn" {
  value = module.codebuild_codepipeline.codebuild_arn
}
output "codepipeline_arn" {
  value = module.codebuild_codepipeline.codepipeline_arn
}

output "cognito_user_pool" {
  value = aws_cognito_user_pool.product_scanner.name
}
