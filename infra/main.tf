
data "aws_caller_identity" "current" {}

# --- Random id resource for assigning unique bucket names --- #
resource "random_id" "suffix" {
  byte_length = 4
}


# --- S3 Bucket for uploads --- #
resource "aws_s3_bucket" "uploads" {
  bucket        = "product-scanner-maximus"
  force_destroy = true
}

# --- ECR repository for hosting lambda images --- #
resource "aws_ecr_repository" "lambda_repo" {
  name                 = "product-scanner"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

# --- Build and push the lambda image --- #
resource "null_resource" "build_and_push_image" {

  triggers = {
    dockerfile_hash = filemd5("${path.module}/../core/Dockerfile")
    # source_hash     = filemd5("${path.module}/../core/app")
  }

  provisioner "local-exec" {
    command = "aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.lambda_repo.repository_url} && docker build -t ${aws_ecr_repository.lambda_repo.repository_url}:${var.image_tag} --platform linux/amd64 --provenance false --no-cache ${path.module}/../core && docker push ${aws_ecr_repository.lambda_repo.repository_url}:${var.image_tag}"

  }

  depends_on = [aws_ecr_repository.lambda_repo]
}

# --- IAM Assume Role Policy --- #
data "aws_iam_policy_document" "lambda_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# --- IAM Execution Policy --- #
data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
      "textract:DetectDocumentText",
      "s3:GetObject",
      "s3:PutObject",
    ]
    effect    = "Allow"
    resources = ["*"]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect    = "Allow"
    resources = ["*"]
  }

}
resource "aws_iam_role" "lambda_role" {
  name               = "product_scanner"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
}

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "product_scanner"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# --- Lambda container --- #
resource "aws_lambda_function" "scanner" {
  function_name = "product-scanner"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}:${var.image_tag}"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 30
  memory_size   = 1024
  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      SCANNER_BUCKET = aws_s3_bucket.uploads.bucket
    }
  }

  depends_on = [null_resource.build_and_push_image]
}

# --- Allow S3 to Invoke Lambda --- #
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scanner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}

# --- S3 Trigger ---- #
resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.scanner.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# ─── REST API ────────────────────────────────────────────────────
resource "aws_api_gateway_rest_api" "scanner_api" {
  name        = "product-scanner"
  description = "API Gateway for the Product Scanner"
}

# ─── /scan resource ──────────────────────────────────────────────
resource "aws_api_gateway_resource" "scan" {
  rest_api_id = aws_api_gateway_rest_api.scanner_api.id
  parent_id   = aws_api_gateway_rest_api.scanner_api.root_resource_id
  path_part   = "scan"
}

# ─── POST /scan ───────────────────────────────────────────────────
resource "aws_api_gateway_method" "scan_post" {
  rest_api_id   = aws_api_gateway_rest_api.scanner_api.id
  resource_id   = aws_api_gateway_resource.scan.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "scan_post" {
  rest_api_id             = aws_api_gateway_rest_api.scanner_api.id
  resource_id             = aws_api_gateway_resource.scan.id
  http_method             = aws_api_gateway_method.scan_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.scanner.invoke_arn
}

# ─── OPTIONS /scan (CORS preflight) ──────────────────────────────
resource "aws_api_gateway_method" "scan_options" {
  rest_api_id   = aws_api_gateway_rest_api.scanner_api.id
  resource_id   = aws_api_gateway_resource.scan.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "scan_options" {
  rest_api_id = aws_api_gateway_rest_api.scanner_api.id
  resource_id = aws_api_gateway_resource.scan.id
  http_method = aws_api_gateway_method.scan_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "scan_options_200" {
  rest_api_id = aws_api_gateway_rest_api.scanner_api.id
  resource_id = aws_api_gateway_resource.scan.id
  http_method = aws_api_gateway_method.scan_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "scan_options" {
  rest_api_id = aws_api_gateway_rest_api.scanner_api.id
  resource_id = aws_api_gateway_resource.scan.id
  http_method = aws_api_gateway_method.scan_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [aws_api_gateway_integration.scan_options]
}

# ─── Deployment + stage ───────────────────────────────────────────
resource "aws_api_gateway_deployment" "scanner" {
  rest_api_id = aws_api_gateway_rest_api.scanner_api.id

  depends_on = [
    aws_api_gateway_integration.scan_post,
    aws_api_gateway_integration.scan_options,
  ]

  # Force redeploy on config changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.scan,
      aws_api_gateway_method.scan_post,
      aws_api_gateway_integration.scan_post,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.scanner.id
  rest_api_id   = aws_api_gateway_rest_api.scanner_api.id
  stage_name    = "prod"
}

# ─── Lambda permission for API Gateway ───────────────────────────
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scanner.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.scanner_api.execution_arn}/*/*"
}
