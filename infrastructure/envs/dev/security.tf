module "security" {
  source = "../../modules/security"

  name   = "${var.project_name}-${var.environment}-application"
  vpc_id = module.network.vpc_id

  tags = module.resource_metadata.common_tags

  allowed_ingress_rules = {}
}
