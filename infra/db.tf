resource "aws_dynamodb_table" "products" {
  name         = "product-scanner-products"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }

  tags = {
    Project = "product-scanner"
  }
}
