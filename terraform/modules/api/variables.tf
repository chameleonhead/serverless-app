variable "env_code" {
  type = string
}

variable "user_pool_id" {
  type = string
}

variable "issuer" {
  type = string
}

variable "audience" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "lambda_subnet_ids" {
  type = list(string)
}

variable "db_security_group_id" {
  type = string
}

variable "db_secret_arn" {
  type = string
}

variable "db_cluster_identifier" {
  type = string
}
