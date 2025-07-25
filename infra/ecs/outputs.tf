
output "alb_dns" {
  value = "http://${aws_lb.app.dns_name}"
}
