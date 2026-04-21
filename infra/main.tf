locals {
  dockerfile_hash = filemd5("${path.module}/../core/Dockerfile")
  source_hash     = filemd5("${path.module}/../core/app/handler.py")
  scripts_dir     = "${path.module}/../core/scripts"
  image_tag       = md5("${local.dockerfile_hash}-${local.source_hash}")
}

data "aws_caller_identity" "current" {}

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
resource "terraform_data" "build_and_push_image" {

  triggers_replace = {
    dockerfile_hash = local.dockerfile_hash,
    source_hash     = local.source_hash
  }

  provisioner "local-exec" {
    working_dir = local.scripts_dir
    interpreter = ["bash", "-c"]
    command     = "AWS_MODE=local IMAGE_TAG=${local.image_tag} REPO_URL=${aws_ecr_repository.lambda_repo.repository_url} AWS_REGION=${var.region} ./build_lambda_image.sh"
  }

  depends_on = [aws_ecr_repository.lambda_repo]
}
# --- Lambda container --- #
resource "aws_lambda_function" "scanner" {
  function_name = "product-scanner"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}:${local.image_tag}"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 30
  memory_size   = 1024
  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      SCANNER_BUCKET = aws_s3_bucket.uploads.bucket
      PRODUCTS_TABLE = aws_dynamodb_table.products.name
    }
  }

  depends_on = [terraform_data.build_and_push_image]
}

# --- S3 Trigger ---- #
resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.scanner.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
