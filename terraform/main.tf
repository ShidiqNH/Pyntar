provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_instance" "pyntar_server" {
  ami           = "ami-0c02fb55956c7d316" # Ubuntu
  instance_type = "t2.micro"

  key_name = "your-keypair" # IMPORTANT (SSH)

  user_data = <<-EOF
              #!/bin/bash
              
              # update system
              apt update -y
              
              # install docker
              apt install -y docker.io
              systemctl start docker
              systemctl enable docker

              # install git
              apt install -y git

              # clone project kamu
              git clone https://github.com/USERNAME/pyntar-backend.git

              cd pyntar-backend

              # build docker image
              docker build -t pyntar-backend .

              # run container
              docker run -d -p 8000:8000 pyntar-backend

              EOF

  tags = {
    Name = "Pyntar-AutoDeploy"
  }
}