# infra/ecr/provider.tf


provider "aws" {
  region = var.aws_region

  # <<– assume a LabRole APENAS neste módulo
  assume_role {
    role_arn     = "arn:aws:iam::049015295261:role/LabRole"
    session_name = "terraform-ecr"
  }
}
