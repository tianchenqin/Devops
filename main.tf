provider "aws" {
  region = "cn-north-1"
  access_key = "AKIATOXEOJWQKIGKYJ72"
  secret_key = "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"
}

variable "web_port"{
  description = "the server port to receive http requests"
  type = number
  default = 8080
}
resource "aws_instance" "TQFirstInstance" {
  ami           = "ami-0e855a53ec7c8057e"
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.webserverSG.id]
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello World" > index.html
              nohup busybox httpd -f -p 8080 &
              EOF

  tags = {
    Name = "terraform-example"
  }	
}

resource "aws_security_group" "webserverSG" {
  name = "terraform-example-instance"
  ingress {
    from_port = var.web_port
    to_port = var.web_port
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
