data "aws_caller_identity" "current" {}

module "idp" {
  source = "./modules/idp"

  env_code = var.env_code
}

module "api" {
  source = "./modules/api"

  env_code     = var.env_code
  issuer       = module.idp.issuer
  user_pool_id = module.idp.user_pool_id
}

module "frontend" {
  source = "./modules/frontend"

  env_code = var.env_code
}
