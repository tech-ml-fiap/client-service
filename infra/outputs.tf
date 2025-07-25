output "alb_dns" {
  description = "URL pública da aplicação"
  value       = "http://${aws_lb.app.dns_name}"
}

output "cluster_name"            { value = aws_ecs_cluster.this.name }
output "service_name"            { value = var.service_name }
output "ecs_task_definition_arn" { value = aws_ecs_task_definition.app.arn }
