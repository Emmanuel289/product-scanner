variable "region" {
  type        = string
  description = "AWS region to deploy to"
  default     = "us-east-1"
}

variable "image_tag" {
  type        = string
  description = "Image tag for image in ECR repo to be used for lambda invocation"
  default     = "latest"
}
