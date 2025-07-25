terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.51" }
#    template = { source = "hashicorp/template", version = "~> 2.3" }
  }
}

provider "aws" { region = var.aws_region }

############################
# Rede – VPC/Subnet default
############################
data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}


############################
# ECR (garantia extra)
############################
resource "aws_ecr_repository" "repo" {
  name = var.service_name
  lifecycle { prevent_destroy = false }
}

############################
# Security Group
############################
resource "aws_security_group" "app_sg" {
  name        = "${var.service_name}-sg"
  description = "Public access to application"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

############################
# Instance Profile usando LabRole existente
############################
data "aws_iam_role" "lab" {
  name = var.execution_role_name   # "LabRole"
}

data "aws_iam_instance_profile" "lab_profile" {
  name = var.execution_role_name   # assume que o instance-profile tem o mesmo nome
}

############################
# User-data – instala Docker, roda migration e servidor
############################
data "template_file" "user_data" {
  template = file("${path.module}/user_data.sh.tpl")
  vars = {
    region      = var.aws_region
    image_uri   = var.image_uri
    port        = var.container_port
    db_host     = var.db_host
    db_port     = var.db_port
    db_user     = var.db_user
    db_password = var.db_password
    db_name     = var.db_name
  }
}

############################
# EC2
############################
resource "aws_instance" "app" {
  ami                         = "ami-013168dc3850ef002"   # Amazon Linux 2 us-east-1
  instance_type               = "t3.micro"
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.app_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = data.aws_iam_instance_profile.lab_profile.name
  user_data                   = data.template_file.user_data.rendered

  tags = { Name = var.service_name }
}

############################
# Outputs
############################
output "public_url" {
  description = "Endereço público da aplicação"
  value       = "http://${aws_instance.app.public_ip}:${var.container_port}"
}
