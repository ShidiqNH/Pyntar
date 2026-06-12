resource "cloudflare_r2_bucket" "media_bucket" {
  account_id = var.cloudflare_account_id
  name       = "${var.environment}-flask-r2-bucket"
  location   = "APAC" # Mengarahkan lokasi bucket ke region Asia Pasifik agar low latency
}