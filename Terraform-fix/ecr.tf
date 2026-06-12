resource "aws_ecr_repository" "flask_app" {
  name                 = "${var.environment}-flask-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
  }
}