output "cluster_name"              { value = aws_ecs_cluster.this.name }
output "ecs_task_definition_arn"   { value = aws_ecs_task_definition.app.arn }
output "default_subnets"           { value = data.aws_subnets.default.ids }
output "default_sg"                { value = aws_security_group.ecs_service.id }
output "service_name"              { value = var.service_name }
