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
