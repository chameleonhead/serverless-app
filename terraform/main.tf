data "aws_caller_identity" "current" {}

module "idp" {
  source = "./modules/idp"

  env_code = var.env_code
}

module "bff" {
  source = "./modules/bff"

  env_code             = var.env_code
  cognito_user_pool_id = module.idp.user_pool_id
}

module "frontend" {
  source = "./modules/frontend"

  env_code                 = var.env_code
  user_pool_id             = module.idp.user_pool_id
  issuer                   = module.idp.issuer
  bff_auth_function_name   = module.bff.auth_function_name
  bff_auth_url_domain_name = module.bff.auth_function_domain_name
}

module "api" {
  source = "./modules/api"

  env_code     = var.env_code
  issuer       = module.idp.issuer
  audience     = module.frontend.serverless_app_audience
  user_pool_id = module.idp.user_pool_id
}
