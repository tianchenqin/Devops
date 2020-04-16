provider "aws" {
  region = "cn-north-1"
  access_key = "AKIATOXEOJWQKIGKYJ72"
  secret_key = "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"
}

resource "aws_instance" "TQFirstInstance" {
  ami           = "ami-0e855a53ec7c8057e"
  instance_type = "t2.micro"
  tags = {
    Name = "terraform-example"
  }	
}
