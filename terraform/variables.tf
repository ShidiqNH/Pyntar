variable "region" {
  type    = string
  default = "ap-southeast-1" # Region utama infrastruktur AWS (Singapore)
}

variable "subdomain_name" {
  type    = string
  default = "cloud.shidiq.com"
}

variable "cloudflare_account_id" {
  type        = string
  description = "Account ID panjang yang ada di halaman utama R2 Cloudflare"
  default     = "XXX" 
}

variable "cloudflare_access_key" {
  type        = string
  description = "Access Key ID hasil dari Create API Token"
  default     = "XXX" 
}

variable "cloudflare_secret_key" {
  type        = string
  description = "Secret Access Key hasil dari Create API Token"
  default     = "XXX"
}