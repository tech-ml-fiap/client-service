
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.51" }
  }
}
provider "aws" { region = var.aws_region }
