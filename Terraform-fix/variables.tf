variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare Account ID"
}

variable "cloudflare_api_token" {
  type        = string
  description = "Cloudflare API Token dengan izin edit R2"
  sensitive   = true
}

variable "db_username" {
  type    = string
  default = "flask_user"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "flask_app_image" {
  type        = string
  description = "URI image Docker Flask. Jika pertama kali run, biarkan default atau kosong."
  default     = "" 
}

variable "gemini_api_key" {
  type        = string
  description = "API Key Gemini untuk ai_engine"
  sensitive   = true
}

variable "cloudflare_access_key" {
  type        = string
  description = "Access Key ID hasil dari Create API Token"
  sensitive   = true
}

variable "cloudflare_secret_key" {
  type        = string
  description = "Secret Access Key hasil dari Create API Token"
  sensitive   = true
}