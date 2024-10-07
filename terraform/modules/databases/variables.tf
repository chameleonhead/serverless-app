variable "env_code" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "db_subnet_ids" {
  type = list(string)
}

variable "cicd_subnet_ids" {
  type = list(string)
}
