module "security" {
  source = "../../modules/security"

  name   = "${var.project_name}-${var.environment}-application"
  vpc_id = module.network.vpc_id

  tags = module.resource_metadata.common_tags

  allowed_ingress_rules = {}

  allowed_egress_rules = {
    https = {
      description           = "HTTPS outbound to any IPv4 destination"
      from_port             = 443
      to_port               = 443
      protocol              = "tcp"
      destination_cidr_ipv4 = "0.0.0.0/0"
    }
  }
}
