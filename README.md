# Cloud-Agnostic Automated Deployment Platform

## 1. Project Objective

Build an automated deployment platform for shared and dedicated tenant environments, supporting infrastructure as code, Kubernetes deployments, application health checks, background job processing, database migrations, monitoring, and CI/CD automation.

The project includes a local Kind development environment and is intended to support cloud deployment through reusable Terraform infrastructure.

## 2. Architecture

The platform is organized into the following layers:

- **Infrastructure:** Terraform configuration and infrastructure validation.
- **Platform:** Kubernetes manifests, Helm charts, and deployment automation.
- **API application:** Python HTTP service exposing health, readiness, and Prometheus-style metrics endpoints.
- **Background worker:** Consumes jobs from Redis and handles processing, recovery, and failure paths.
- **Data services:** Redis for job queues and PostgreSQL for relational storage.
- **Database migrations:** Versioned SQL migrations with migration history and concurrency protection.
- **CI/CD:** Jenkins pipeline for validation, image builds, database migration, deployment, and smoke tests.
- **Monitoring:** Application metrics endpoint, with further monitoring and alerting integration planned.

## 3. Deployment Targets

### Local Kubernetes

- Cluster: `devops-platform`
- Distribution: Kind
- Namespace: `default`
- Deployment management: Helm
- Helm release: `platform`
- API service: `platform-api`
- Worker deployment: `platform-worker`

### Cloud Kubernetes

Terraform configuration is validated through the CI/CD workflow. Provisioning a complete cloud Kubernetes environment through Terraform has not yet been verified.

## 4. Application Contract

| Component | Configuration |
|---|---|
| API port | 8080 |
| Liveness endpoint | `/healthz` |
| Readiness endpoint | `/readyz` |
| Metrics endpoint | `/metrics` |
| Background worker | Redis job queue consumer |
| Redis queue | `platform-jobs` |
| Redis processing queue | `platform-jobs:processing` |
| Redis dead-letter queue | `platform-jobs:dead-letter` |
| Database | PostgreSQL |
| API Kubernetes Service | `platform-api` |
| Deployment method | Helm |

### API Endpoints

- `/healthz` reports whether the API process is alive.
```

Check the Kubernetes deployment:

```bash
kubectl get pods
- Configure Redis persistence and evaluate high availability.
- Complete the business database schema and define migration rollback or recovery procedures.
- Improve worker retry policies, idempotency, and multi-replica recovery behavior.
- Enable and test autoscaling and disruption budgets where appropriate.
- Validate performance using a rate-controlled load generator and realistic application operations.
- Test the 2,250 RPS peak target and p95 latency objective of less than 400 ms.
- Implement and test the shared 99.9% and dedicated 99.95% availability objectives.
- Validate the EU data-residency requirement for any cloud deployment.
- Implement comprehensive monitoring, alerting, backup, recovery, and operational runbooks.
- Validate the monthly cost targets under baseline and peak load.

## 9. Development Status

This project is under active development. The local Kind environment, Helm deployment, database migration runner, Redis worker, Jenkins workflow, and short-duration health-endpoint tests have been implemented and tested.

Cloud provisioning, tenant isolation, realistic peak-load validation, and production availability requirements remain unfinished or unverified.

Implementation status is reported according to available verification evidence; a successful local deployment or CI pipeline is not, by itself, proof of production readiness.
kubectl get deployments
kubectl get services
helm status platform
```

Test the API through port-forwarding for basic smoke tests:
- Implement and verify shared and dedicated tenant isolation.
- Validate security boundaries, IAM permissions, secrets management, and network policies.
- Add and verify image scanning, image signing, and artifact promotion.

```bash
kubectl port-forward service/platform-api 18080:8080
```

In another terminal:

```bash
curl -i http://127.0.0.1:18080/healthz
curl -i http://127.0.0.1:18080/readyz
curl -i http://127.0.0.1:18080/metrics
```

Port-forwarding is intended for development access and basic smoke tests, not as the preferred path for high-rate load testing.

## 8. Known Gaps and Remaining Work

- Provision and validate the cloud environment through Terraform.
- `/readyz` checks TCP connectivity to Redis and PostgreSQL.
- `/metrics` exposes application metrics, including HTTP request counts and uptime.

The readiness check confirms service connectivity; it does not validate database business queries or migration completion by itself.

## 5. Implemented and Verified

### API and Containers
./platform/scripts/validate-helm.sh

- API container image built and loaded into the Kind cluster.
- API Kubernetes Deployment and ClusterIP Service deployed.
- Liveness, readiness, and metrics endpoints tested successfully.
- API readiness verified against Redis and PostgreSQL connectivity.
- The 150, 300, and 750 RPS tests completed with zero errors.
- The 1,500 RPS test did not sustain the requested rate and showed high client scheduling delay.

```bash
- Python thread-creation limits were encountered during a separate test attempt.
- API CPU throttling counters have shown nonzero cumulative values; further measurement during load is required to determine its impact.
- The assignment's 2,250 RPS peak target has not been validated.
- End-to-end API operations, database queries, queue throughput, and sustained-load behavior need additional testing.
- These short tests do not establish production capacity, production readiness, or the required availability SLOs.

## 7. Local Validation

From the repository root, validate the Helm chart:
- API runs as a non-root user in its container.

### Kubernetes and Helm

- Kind cluster configured for local development.

### Performance Test Limitations

- These tests exercise only the lightweight `/healthz` endpoint.
- API and worker deployed through the Helm release `platform`.
- Redis and PostgreSQL deployed as Kubernetes services.
- PostgreSQL persistent volume claim created and bound.
- PostgreSQL credentials supplied through a Kubernetes Secret.
- API and worker rollout checks passed.
- Helm chart lint and template validation included in CI/CD.

The current development Helm configuration has one API replica and one worker replica. HPA and PDB features are disabled in the current values; actual autoscaling behavior has not been verified.

### Redis Worker

- Worker consumes jobs from the Redis `platform-jobs` queue.
- A processing queue is used while jobs are being handled.
- Abandoned processing jobs are recovered during worker startup.
- Invalid JSON jobs are sent to the dead-letter queue.
- Failed jobs can be requeued.

**Limitations:** This is a development implementation, not a fully validated production job-processing system. Recovery behavior, duplicate processing, retry limits, Redis persistence, and multi-replica worker coordination require further testing.

### PostgreSQL Migrations

- Versioned SQL migration files implemented.
- Migration runner retries PostgreSQL connections during startup.
- Applied migration versions are recorded in `schema_migrations`.
- Migration execution uses a PostgreSQL advisory lock to help prevent concurrent execution.
- The migration Job completed successfully in Kind.
- Re-running the migration runner confirmed that an already-applied migration was skipped.

Performance tests were run against the internal Kubernetes Service at `platform-api:8080/healthz` using a temporary in-cluster Python load generator.

| Target RPS | Duration | Successful Requests | Error Rate | Achieved RPS | p95 Latency | Result |
|---:|---:|---:|---:|---:|---:|---|
| 150 | 10 seconds | 1,500 / 1,500 | 0.00% | 149.94 | 1.80 ms | Passed |
| 300 | 10 seconds | 3,000 / 3,000 | 0.00% | 299.57 | 1.88 ms | Passed |
| 750 | 10 seconds | 7,500 / 7,500 | 0.00% | 744.15 | 5.60 ms | Passed |
| 1,500 | 10 seconds planned | 14,951 / 15,000 | 0.33% | 858.48 | 1,038.75 ms | Not passed |

The current migration creates the migration history table. A complete business database schema and migration rollback strategy remain future work.

### Jenkins CI/CD

The Jenkins pipeline validates Terraform and Helm configuration and performs the following workflow:


## 6. Performance Validation
1. Validate repository configuration.
2. Build the API, worker, and migration images.
3. Run the database migration Job.
4. Deploy the application through Helm to Kind.
5. Verify API and worker rollouts.
6. Run application smoke tests.

The latest reported pipeline execution completed with `Finished: SUCCESS`.
The successful build verifies the implemented development pipeline. It does not prove that cloud infrastructure has been provisioned through Terraform, that images have been published to a remote registry, or that a production deployment has occurred.

