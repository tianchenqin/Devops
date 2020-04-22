provider "aws" {
  region = "cn-north-1"
  shared_credentials_file = "/root/.aws/credentials"
  profile = "default"
#  access_key = "AKIATOXEOJWQKIGKYJ72"
#  secret_key = "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"
}

#variable "web_port"{
#  description = "the server port to receive http requests"
#  type = number
#  default = 8080
#}
resource "aws_instance" "TQFirstInstance" {
  ami           = "ami-0e855a53ec7c8057e"
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.webserverSG.id]
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello World" > index.html
              nohup busybox httpd -f -p ${var.web_port} &
              EOF
  lifecycle {
    create_before_destroy = true
  }
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

resource "aws_s3_bucket" "terraform_state_store" {
  bucket = "terraformstatetianchentest"
  
  #prevent accidental deletion of this S3 bucket
  lifecycle {
    prevent_destroy = true
  }

  #Enable versioning so we can see the histroy
  versioning {
    enabled = true
  }

  #Enable server-side encryption by default
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name = "terraformstatetianchentest-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

terraform {
  backend "s3" {
     #the configuration of my S3 backend!
     key = "terraform.tfstate"


  }
}

data "aws_secretsmanager_secret_version" "rootpass"{
  secret_id = "cnawsroot"
}

output "public_ip" {
  value = aws_instance.TQFirstInstance.public_ip
  description = "server port display"
}

