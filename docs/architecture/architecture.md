# Cloud-Agnostic Deployment Platform — Architecture

## 1. Status

Design in progress. This document describes the proposed architecture,
not a claim that the complete platform has been deployed or tested.

## 2. Proposed Architecture

- Infrastructure layer: Terraform modules and provider-specific resources.
- Platform layer: Kubernetes, Helm, policies, monitoring, and scaling.
- Application layer: deployment configuration for the supplied API and worker.
- CI/CD: Jenkins for build, testing, security scanning, artifact signing,
  promotion, and deployment.
- GitOps: evaluate a pull-based deployment model for reconciliation and auditability.
- Data: PostgreSQL for persistent relational data and Redis for the job queue.

## 3. Deployment Targets

- Local target: kind on the EC2 development host.
- Cloud target: AWS Kubernetes infrastructure, pending account permission
  and region-constraint validation.

## 4. Proposed Release Strategy

- API: canary release with progressive traffic shifting and health,
  error-rate, and latency gates.
- Worker: controlled rolling deployment with graceful shutdown and
  queue draining before termination.
- Rollback: automatically stop promotion and restore the last known-good
  application artifact when release gates fail.
- Database: expand/contract migrations; destructive changes must wait until
  old application versions no longer depend on the old schema.

## 5. Tenant Model

- Shared environment: shared platform resources with tenant-aware
  authorization, quotas, and observability.
- Dedicated environment: isolated deployment and data resources from a
  reusable tenant template.
- EU tenants: data, backups, and other in-scope data stores must remain
  in approved EU regions.

## 6. Initial Decisions and Trade-offs

1. Terraform: chosen for infrastructure provisioning and reusable modules.
   Alternative: provider-specific templates; rejected as the only IaC
   approach because they reduce portability.
2. kind: chosen for the local Kubernetes target. Limitation: it does not
   reproduce managed cloud networking or managed database behavior.
3. Jenkins: chosen as the planned CI/CD system. Alternative: GitHub Actions;
   not selected for this implementation.
4. API canary: chosen to limit exposure to a new release. Alternative:
   all-at-once deployment, which increases release risk.
5. Worker draining: chosen to reduce interrupted jobs. Limitation:
   jobs may run for up to 60 seconds, so termination grace periods and
   queue visibility/acknowledgment behavior must be verified against the
   actual worker implementation.

## 7. Main Risks

1. AWS organization policies may restrict required services or regions.
2. Non-backward-compatible database migrations may prevent safe rollback.
3. Peak traffic may exceed application or database connection capacity.
4. Local kind results do not prove managed-cloud production behavior.
5. The supplied application contract does not establish all retry,
   idempotency, and queue acknowledgment semantics.

## 8. Not Yet Verified

- Cloud infrastructure provisioning and remote Terraform state.
- Jenkins pipelines and artifact signing.
- Zero-downtime releases and automatic rollback under load.
- 15x autoscaling, SLO attainment, backup restoration, and cost estimates.
- Dedicated tenant provisioning and regional failover.
