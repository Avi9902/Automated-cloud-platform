resource "aws_security_group" "this" {
  name        = "${var.name}-sg"
  description = "Security group managed by Terraform for ${var.name}."
  vpc_id      = var.vpc_id

  tags = merge(var.tags, {
    Name = "${var.name}-sg"
  })
}

resource "aws_vpc_security_group_ingress_rule" "this" {
  for_each = var.allowed_ingress_rules

  security_group_id            = aws_security_group.this.id
  description                  = each.value.description
  from_port                    = each.value.from_port
  to_port                      = each.value.to_port
  ip_protocol                  = each.value.protocol
  referenced_security_group_id = each.value.source_security_group_id
  cidr_ipv4                    = each.value.source_cidr_ipv4
}

resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.this.id
  description       = "Allow outbound HTTPS for approved external dependencies."
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}
