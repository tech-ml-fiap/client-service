# new data.tf
# 1) Pega a VPC marcada como default
data "aws_vpc" "default" {
  filter {
    name   = "isDefault"
    values = ["true"]
  }
}

# 2) Pega todas as subnets da VPC default
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 3) Pega o security group "default" da mesma VPC
data "aws_security_group" "default" {
  name   = "default"
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
