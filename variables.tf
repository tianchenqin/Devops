variable "web_port"{
  description = "the server port to receive http requests"
  type = number
}

variable "db_remote_state_bucket" {
  description = "The name of the S3 bucket for the database's remote state"
  type = string
}

variable "db_remote_state_key" {
  description = "the path of the database's remote state in S3"
  type = string
}

Variable "cluster_name" {
  description = "the name to use for all the cluster resource"
  type = string
}
