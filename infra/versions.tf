terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.32.0"
    }
  }
}


provider "aws" {
  region     = var.region
  access_key = ""
  secret_key = ""

  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    s3        = "https://s3.localhost.localstack.cloud:4566"
    s3control = "https://localhost.localstack.cloud:4566"
    ecr       = "https://localhost.localstack.cloud:4566"
    lambda    = "https://localhost.localstack.cloud:4566"
    iam       = "https://localhost.localstack.cloud:4566"
  }
}
