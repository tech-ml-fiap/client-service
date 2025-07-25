output "alb_dns" {
  value       = "http://${aws_lb.app.dns_name}"
  description = "URL pública da aplicação"
}

output "cluster_name"            { value = aws_ecs_cluster.this.name }
output "ecs_task_definition_arn" { value = aws_ecs_task_definition.app.arn }
output "service_name"            { value = var.service_name }
