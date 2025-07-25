variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "db_host"     { type = string }
variable "db_port"     { type = string }
variable "db_user"     { type = string }
variable "db_password" { type = string }
variable "db_name"     { type = string }

variable "cluster_name" { type = string default = "clientservice-cluster" }
variable "service_name" { type = string default = "clientservice-svc" }
variable "container_port" { type = number default = 8000 }
