terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# 2. Provider Jalur Khusus untuk nembak Cloudflare R2 (JANGAN SAMPAI HILANG/SALAH KETIK)
provider "aws" {
  alias                       = "cloudflare"
  region                      = "us-east-1" 
  access_key                  = var.cloudflare_access_key
  secret_key                  = var.cloudflare_secret_key
  skip_credentials_validation = true
  skip_region_validation      = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = "https://${var.cloudflare_account_id}.r2.cloudflarestorage.com"
  }
}