data "aws_caller_identity" "current" {}

module "network" {
  source = "./modules/network"

  env_code = var.env_code
}

module "databases" {
  source = "./modules/databases"

  env_code      = var.env_code
  vpc_id        = module.network.vpc_id
  db_subnet_ids = module.network.subnet_private_db_ids
}

module "idp" {
  source = "./modules/idp"

  env_code = var.env_code
}

module "bff" {
  source = "./modules/bff"

  env_code                 = var.env_code
  cognito_user_pool_id     = module.idp.user_pool_id
  cognito_user_pool_domain = module.idp.user_pool_domain
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

  env_code             = var.env_code
  issuer               = module.idp.issuer
  audience             = module.frontend.serverless_app_audience
  user_pool_id         = module.idp.user_pool_id
  vpc_id               = module.network.vpc_id
  lambda_subnet_ids    = module.network.subnet_private_lambda_ids
  db_security_group_id = module.databases.apidb_security_group_id
  db_resource_id       = module.databases.apidb_resource_id
  db_host              = module.databases.apidb_host
}
