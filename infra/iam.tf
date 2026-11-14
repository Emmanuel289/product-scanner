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
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
    ]
    effect    = "Allow"
    resources = [aws_dynamodb_table.products.arn]
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


# --- Allow S3 to Invoke Lambda --- #
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scanner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}



# ─── Lambda permission for API Gateway ───────────────────────────
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scanner.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.scanner_api.execution_arn}/*/*"
}


resource "aws_cognito_user_pool" "product_scanner" {
  name   = var.cognito_user_pool_name
  region = var.region

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  schema {
    name                = "display_username"
    attribute_data_type = "String"
    mutable             = true
    required            = false
    string_attribute_constraints {
      min_length = 5
      max_length = 16
    }
  }
  password_policy {
    minimum_length  = 8
    require_numbers = true
    require_symbols = true
  }
  admin_create_user_config {
    allow_admin_create_user_only = false
    invite_message_template {
      email_message = "Your username is {username} and password is {####}"
      sms_message   = "Your username is {username} and password is {####}"
      email_subject = "Your Product Scanner Account has been created"
    }
  }
}


resource "aws_cognito_user_pool_client" "product_scanner" {
  name                                 = var.cognito_user_pool_name
  region                               = var.region
  access_token_validity                = 1
  user_pool_id                         = aws_cognito_user_pool.product_scanner.id
  callback_urls                        = var.call_back_urls
  default_redirect_uri                 = var.call_back_urls[0]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid"]
  supported_identity_providers         = ["COGNITO"]
}


resource "aws_cognito_user_pool_domain" "product_scanner" {
  domain                = var.cognito_user_pool_name
  user_pool_id          = aws_cognito_user_pool.product_scanner.id
  region                = var.region
  managed_login_version = 2
}
