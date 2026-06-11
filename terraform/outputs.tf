output "app_url" {
  description = "Tautan subdomain kustom untuk backend Flask"
  value       = "http://${var.subdomain_name}"
}

output "aws_alb_dns_name" {
  description = "Salin alamat ini untuk value CNAME di hosting shidiq.com"
  value       = aws_lb.pyntar_alb.dns_name
}

output "ecr_repository_url" {
  description = "URL ECR untuk kebutuhan push image Docker"
  value       = aws_ecr_repository.pyntar_repo.repository_url
}

output "cloudflare_r2_bucket_name" {
  description = "Nama Bucket Cloudflare R2 yang berhasil terbuat"
  value       = aws_s3_bucket.pyntar_storage.bucket
}

# BONUS: Menampilkan URL Endpoint khusus Cloudflare R2 secara otomatis buat dipaste ke file .env Flask
output "cloudflare_r2_endpoint_url" {
  description = "S3 Endpoint URL untuk konfigurasi boto3 di Flask"
  value       = "https://${var.cloudflare_account_id}.r2.cloudflarestorage.com"
}