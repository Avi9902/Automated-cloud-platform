# Cloud-Agnostic Automated Deployment Platform

## Objective

Build an automated deployment platform that supports cloud infrastructure
and a local Kubernetes target, zero-downtime application releases,
autoscaling, tenant isolation, and operational monitoring.

## Architecture Layers

- Infrastructure: provider-specific provisioning and reusable Terraform modules.
- Platform: Kubernetes, Helm, policies, and platform automation.
- Applications: deployment configuration for the supplied black-box API and worker.
- CI/CD: Jenkins pipelines for build, test, security scanning, image signing, promotion, and deployment. Implementation and verification are pending.
- Tenants: configuration for shared and dedicated tenant environments.
- Documentation: architecture, runbooks, recovery procedures, and evidence.

## Deployment Targets

- Local Kubernetes: kind running on the EC2 development instance.
- Cloud Kubernetes: planned; not yet provisioned.

## Application Contract

- API port: 8080
- Health endpoint: /healthz
- Readiness endpoint: /readyz
- Metrics endpoint: /metrics
- Worker: consumes jobs from Redis; jobs may run for up to 60 seconds.
- Data services: PostgreSQL and Redis.

The application is treated as a black box. Its implementation will not be rewritten.

## Delivery Status

This repository is under development. Features will be marked complete only
after implementation and verification. Architecture plans and untested
configurations are not evidence of a successful deployment.

## Local Helm Validation

Prerequisites: Helm 3 and a shell environment with the repository checked out.

Run the chart validation script from the repository root:

    ./platform/scripts/validate-helm.sh

The script lints the Helm chart and renders Kubernetes resources using
placeholder API and worker image references. It checks that seven resources,
including two HorizontalPodAutoscalers, are rendered.

This is configuration validation only. It does not deploy the application,
verify real image availability, prove autoscaling behavior, or establish
zero-downtime releases.

Jenkins polling validation test.
