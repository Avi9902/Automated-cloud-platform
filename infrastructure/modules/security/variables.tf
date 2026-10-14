variable "name" {
  description = "Name prefix for security groups."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where security groups will be created."
  type        = string
}

variable "tags" {
  description = "Common tags applied to security groups."
  type        = map(string)
  default     = {}
}

variable "allowed_ingress_rules" {
  description = "Explicit ingress rules keyed by a unique rule name."
  type = map(object({
    description              = string
    from_port                = number
    to_port                  = number
    protocol                 = string
    source_security_group_id = optional(string)
    source_cidr_ipv4         = optional(string)
  }))
  default = {}

  validation {
    condition = alltrue([
      for rule in values(var.allowed_ingress_rules) :
      (rule.source_security_group_id != null) != (rule.source_cidr_ipv4 != null)
    ])
    error_message = "Each ingress rule must specify exactly one source: a security group ID or an IPv4 CIDR."
  }
}
