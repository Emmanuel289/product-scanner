
data "aws_caller_identity" "current" {}

# --- Random id resource for assigning unique bucket names --- #
resource "random_id" "suffix" {
  byte_length = 4
}


# --- S3 Bucket for uploads --- #
resource "aws_s3_bucket" "uploads" {
  bucket        = "product-scanner-uploads-${random_id.suffix.hex}"
  force_destroy = true
}

# --- ECR repository for hosting lambda images --- #
resource "aws_ecr_repository" "lambda_repo" {
  name                 = "product-scanner-textract-lambda"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

# --- Build & Push Docker Image --- #
resource "null_resource" "build_and_push_image" {

  triggers = {
    dockerfile_hash = filemd5("${path.module}/../core/Dockerfile")
    source_hash     = filemd5("${path.module}/../core/app.py")
  }

  provisioner "local-exec" {
    command = <<EOT
aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.lambda_repo.repository_url}
docker build -t ${aws_ecr_repository.lambda_repo.repository_url}:latest -f ${path.module}/../core/Dockerfile --platform linux/amd64 --provenance false --no-cache ${path.module}/../core
docker push ${aws_ecr_repository.lambda_repo.repository_url}:latest
  EOT
  }

  depends_on = [aws_ecr_repository.lambda_repo]
}

data "aws_ecr_image" "lambda_image" {
  repository_name = aws_ecr_repository.lambda_repo.name
  image_tag       = "latest"

  depends_on = [null_resource.build_and_push_image]
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
  name               = "product_scanner_textract_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
}

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "product_scanner_textract_policy"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# --- Lambda container --- #
resource "aws_lambda_function" "textract_lambda" {
  function_name = "product-scanner-textract-lambda"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 30
  memory_size   = 1024
  ephemeral_storage {
    size = 1024
  }

  depends_on = [null_resource.build_and_push_image]
}

# --- Allow S3 to Invoke Lambda --- #
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.textract_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}

# --- S3 Trigger ---- #
resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.textract_lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
