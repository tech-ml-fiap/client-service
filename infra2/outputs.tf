output "cluster_name"        { value = aws_ecs_cluster.this.name }
output "service_name"        { value = aws_ecs_service.this.name }
output "task_definition_arn" { value = aws_ecs_task_definition.this.arn }

output "default_subnets" { value = jsonencode(data.aws_subnets.default.ids) }
output "default_sg"      { value = data.aws_security_group.default.id }

output "alb_dns_name"    { value = aws_lb.this.dns_name }