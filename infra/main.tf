###############################################################################
# Terraform – client Service (Elastic Beanstalk + Docker + RDS)
###############################################################################
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws     = { source = "hashicorp/aws", version = "~> 5.0" }
    random  = { source = "hashicorp/random", version = "~> 3.5" }
  }
}

provider "aws" {
  region = "us-east-1"
}

#############################
# Variáveis vindas da CI
#############################
variable "app_version"  { type = string }   # commit SHA
variable "artifact_zip" { type = string }   # caminho do deploy.zip

variable "db_host"      { type = string }
variable "db_port"      { type = string }
variable "db_user"      { type = string }
variable "db_password"  { type = string }
variable "db_name"      { type = string }

variable "secret_key"   { type = string }
variable "algorithm"    { type = string }
variable "token_expire" { type = string }

#############################
# Bucket único de artefatos
#############################
data "aws_caller_identity" "me" {}

resource "aws_s3_bucket" "artifacts" {
  bucket        = "client-service-artifacts-${data.aws_caller_identity.me.account_id}"
  force_destroy = true
}

resource "aws_s3_object" "pkg" {
  bucket = aws_s3_bucket.artifacts.id
  key    = "build-${var.app_version}.zip"
  source = var.artifact_zip
  etag   = filemd5(var.artifact_zip)
}

#############################
# Elastic Beanstalk
#############################
resource "aws_elastic_beanstalk_application" "app" {
  name = "client-service"
}

resource "aws_elastic_beanstalk_application_version" "ver" {
  name        = var.app_version
  application = aws_elastic_beanstalk_application.app.name
  bucket      = aws_s3_bucket.artifacts.id
  key         = aws_s3_object.pkg.key
}

data "aws_elastic_beanstalk_solution_stack" "docker_al2_latest" {
  name_regex  = "^64bit Amazon Linux 2 v.*running Docker$"
  most_recent = true
}

resource "random_id" "suffix" { byte_length = 4 }

resource "aws_elastic_beanstalk_environment" "env" {
  name                = "client-service-env-${random_id.suffix.hex}"
  application         = aws_elastic_beanstalk_application.app.name
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.docker_al2_latest.name
  version_label       = aws_elastic_beanstalk_application_version.ver.name
  cname_prefix        = "client-service-${random_id.suffix.hex}"

  # Variáveis de ambiente
  dynamic "setting" {
    for_each = {
      DB_HOST                     = var.db_host
      DB_PORT                     = var.db_port
      DB_USER                     = var.db_user
      DB_PASSWORD                 = var.db_password
      DB_NAME                     = var.db_name
      SECRET_KEY                  = var.secret_key
      ALGORITHM                   = var.algorithm
      ACCESS_TOKEN_EXPIRE_MINUTES = var.token_expire
    }
    content {
      namespace = "aws:elasticbeanstalk:application:environment"
      name      = setting.key
      value     = setting.value
    }
  }

  # Roles padrão da conta Academy
  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = "LabRole"
  }
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "LabInstanceProfile"
  }
}

#############################
# Saída
#############################
output "service_url" {
  description = "Endpoint público da API"
  value       = "http://${aws_elastic_beanstalk_environment.env.endpoint_url}"
}
