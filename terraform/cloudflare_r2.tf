resource "aws_s3_bucket" "pyntar_storage" {
  provider = aws.cloudflare # Membelokkan pembuatan ke Cloudflare R2
  bucket   = "pyntar-cc-storage-fix"
}