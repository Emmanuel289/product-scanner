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
