resource "aws_ecr_repository" "pyntar_repo" {
  name = "pyntar-backend"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "Pyntar-ECR"
  }
}