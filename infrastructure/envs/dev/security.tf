module "security" {
  source = "../../modules/security"

  name   = "${var.project_name}-${var.environment}-application"
  vpc_id = module.network.vpc_id

  tags = module.resource_metadata.common_tags

  allowed_ingress_rules = {
    api_from_load_balancer = {
      description              = "API traffic from the load balancer security group"
      from_port                = 8080
      to_port                  = 8080
      protocol                 = "tcp"
      source_security_group_id = module.load_balancer_security.security_group_id
    }
  }

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

module "load_balancer_security" {
  source = "../../modules/security"

  name   = "${var.project_name}-${var.environment}-load-balancer"
  vpc_id = module.network.vpc_id

  tags = module.resource_metadata.common_tags

  allowed_ingress_rules = {
    http = {
      description      = "Public HTTP traffic to the load balancer"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      source_cidr_ipv4 = "0.0.0.0/0"
    }
  }

  allowed_egress_rules = {
    api = {
      description                   = "Forward HTTP traffic to the application security group"
      from_port                     = 8080
      to_port                       = 8080
      protocol                      = "tcp"
      destination_security_group_id = module.security.security_group_id
    }
  }
}
