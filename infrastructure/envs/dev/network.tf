module "network" {
  source = "../../modules/network"

  name = "${var.project_name}-${var.environment}"

  vpc_cidr = "10.20.0.0/16"

  availability_zones = [
    "ap-southeast-2a",
    "ap-southeast-2b",
  ]

  public_subnet_cidrs = [
    "10.20.1.0/24",
    "10.20.2.0/24",
  ]

  private_subnet_cidrs = [
    "10.20.11.0/24",
    "10.20.12.0/24",
  ]

  tags = module.resource_metadata.common_tags
}
