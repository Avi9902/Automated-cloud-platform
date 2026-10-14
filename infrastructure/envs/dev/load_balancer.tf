module "load_balancer" {
  source = "../../modules/load_balancer"

  name              = "${var.project_name}-${var.environment}-alb"
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.public_subnet_ids
  security_group_id = module.load_balancer_security.security_group_id

  target_port       = 8080
  health_check_path = "/healthz"

  tags = module.resource_metadata.common_tags
}
