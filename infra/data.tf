# infra/data.tf

# 1) Pega a VPC default
data "aws_default_vpc" "default" {}

# 2) Pega todas as subnets da VPC default
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_default_vpc.default.id]
  }
}

# 3) Pega o security group "default" da VPC default
data "aws_security_group" "default" {
  name   = "default"
  filter {
    name   = "vpc-id"
    values = [data.aws_default_vpc.default.id]
  }
}
