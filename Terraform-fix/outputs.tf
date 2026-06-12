output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "Akses aplikasi Flask kamu melalui URL Load Balancer ini"
}

output "rds_endpoint" {
  value       = aws_db_instance.mysql.endpoint
  description = "Endpoint koneksi database"
}

output "cloudflare_r2_bucket_name" {
  value = cloudflare_r2_bucket.media_bucket.name
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.flask_app.repository_url
  description = "Gunakan URL ini untuk melakukan docker push dari terminal lokal kamu"
}