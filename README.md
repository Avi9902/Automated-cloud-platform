# Cloud-Agnostic Automated Deployment Platform

## Objective

Build an automated deployment platform supporting cloud infrastructure and
local Kubernetes, tenant environments, application health checks, job
processing, autoscaling, and operational monitoring.

## Architecture Layers

- Infrastructure: Terraform configuration and reusable infrastructure modules.
- Platform: Kubernetes manifests, Helm charts, and deployment automation.
- Applications: API and background worker containers.
- Data services: Redis job queue and PostgreSQL database.
- CI/CD: Jenkins pipeline for Terraform and Helm validation.
- Tenants: Shared and dedicated environment support is planned.
- Documentation: Architecture, deployment instructions, and operational runbooks.

## Deployment Targets

- Local Kubernetes: Kind cluster named `devops-platform` on the development EC2 instance.
- Cloud Kubernetes: Not yet provisioned through Terraform.

## Application Contract

- API port: 8080
- Liveness endpoint: `/healthz`
- Readiness endpoint: `/readyz`
- Metrics endpoint: `/metrics`
- Worker: Consumes jobs from the Redis `platform-jobs` queue.
- Database: PostgreSQL.
- Queue: Redis.

## Implemented and Verified

- API container image built and loaded into the Kind cluster.
- API Kubernetes Deployment and ClusterIP Service.
- API health, readiness, and metrics endpoints.
- API readiness check confirms TCP connectivity to Redis and PostgreSQL.
- Background worker deployed to Kubernetes.
- Redis Deployment and ClusterIP Service.
- PostgreSQL Deployment, ClusterIP Service, Secret reference, and persistent volume claim.
- Redis queue job test performed during local development.
- Jenkins pipeline validates Terraform formatting and configuration.
- Jenkins pipeline runs Helm lint and Helm template validation.
- Latest reported Jenkins build completed with `Finished: SUCCESS`.

## CI/CD Validation

The Jenkins pipeline validates the repository's Terraform and Helm
configuration. The Helm lint output may recommend adding a chart icon; this
is informational and does not cause validation to fail.

The pipeline's successful result proves configuration validation passed.
It does not prove that Terraform has provisioned cloud infrastructure,
that images have been published to a registry, or that a production
deployment has occurred.

## Known Gaps and Limitations

- Cloud infrastructure has not yet been provisioned through Terraform.
- Automated image build and registry publishing in Jenkins are not yet verified.
- Security scanning, image signing, promotion, and automated deployment are not
  yet verified as implemented.
- Database startup migrations are not yet implemented or verified.
- The worker currently uses a simple Redis list consumer; durable job
  acknowledgements and retry/dead-letter handling are not implemented.
- Redis persistence and high availability are not configured.
- Kubernetes autoscaling configuration may be rendered by Helm, but actual
  scaling behavior has not been verified.
- Tenant isolation, availability targets, load testing, and zero-downtime
  releases remain to be implemented and/or tested.
- Monitoring integration and alerting require further verification.

## Local Helm Validation

From the repository root, run:

    ./platform/scripts/validate-helm.sh

This lints the Helm chart and renders Kubernetes resources with placeholder
API and worker image references. It validates configuration only; it does
not deploy those resources or prove runtime behavior.

## Development Status

This repository is under active development. Features are marked complete
only when implementation and verification evidence are available. Local Kind
testing and Jenkins configuration validation do not, by themselves, establish
production readiness.
