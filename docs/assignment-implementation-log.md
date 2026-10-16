# Automated Cloud-Agnostic Platform
## Assignment Implementation and Troubleshooting Report

## 1. Project Overview

This project implements a cloud-agnostic application platform with
containerized services, Kubernetes deployment, infrastructure-as-code
components, and Prometheus monitoring.

The assignment requirements include:
- Shared and dedicated tenant environments
- API health, readiness, and metrics endpoints
- Background job processing using Redis
- PostgreSQL persistence and startup migrations
- Kubernetes deployment and cloud infrastructure automation
- Monitoring, reliability, scalability, and cost awareness
- Infrastructure and application separation

The implementation should be evaluated against the assignment requirements
and the actual code and configuration present in this repository.

## 2. Application Endpoints

The platform API exposes the following endpoints:

| Endpoint | Purpose |
|---|---|
| `/healthz` | Application health check |
| `/readyz` | Readiness check, including Redis and PostgreSQL |
| `/metrics` | Prometheus metrics endpoint |

A successful readiness response was verified:

```json
{
  "status": "ready",
  "redis": true,
  "postgres": true
}
```

The API exports application metrics including:
- `platform_http_requests_total`
- `platform_uptime_seconds`

## 3. Platform Components

The environment includes:
- Kubernetes using a Kind cluster on an Ubuntu EC2 instance
- Platform API exposed internally through a Kubernetes Service
- Redis for queue-related application functionality
- PostgreSQL for persistent application data
- Prometheus installed using the prometheus-community Helm chart
- Kubernetes node exporter
- kube-state-metrics
- Alertmanager
- Prometheus Pushgateway

The monitoring components run in the `monitoring` namespace.
The platform API, Redis, and PostgreSQL run in the `default` namespace.

## 4. Application Monitoring

Prometheus is configured to scrape the following targets:

| Job | Target | Verified status |
|---|---|---|
| platform-api | `platform-api.default.svc.cluster.local:8080/metrics` | UP |
| prometheus | `localhost:9090/metrics` | UP |

Both targets were verified through the Prometheus targets API.

The following queries were used to validate application metrics:

```promql
platform_http_requests_total
```

```promql
platform_uptime_seconds
```

Prometheus is accessed locally through port forwarding and an SSH tunnel.
Port 9090 is not intended to be exposed publicly.

## 5. Monitoring Deployment

Prometheus was installed/upgraded using Helm:

```bash
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  -f platform/monitoring/prometheus-values.yaml
```

Deployment readiness was checked with:

```bash
kubectl rollout status deployment/prometheus-server \
  -n monitoring --timeout=180s
```

The rollout completed successfully.

The monitoring pods were checked with:

```bash
kubectl get pods -n monitoring
```

The Prometheus server subsequently showed `2/2 Running`, and its
application and self-monitoring targets were verified as UP.

## 6. Troubleshooting and Resolutions

### Issue 1: Prometheus configuration failed to load

Observed error:

```text
yaml: unmarshal errors:
line 303: field global already set in type config.plain
```

Cause:
The rendered Prometheus configuration contained conflicting configuration
sections. The previous configuration was not accepted by Prometheus.

Resolution:
The Helm values file was revised so the chart generates the default
Prometheus global and scrape configuration, while the custom values specify
the additional platform API scrape job and rule file paths.

The rendered configuration was checked before upgrading the release.

Validation:
- Helm deployment rollout succeeded.
- Prometheus server became ready.
- The platform API and Prometheus targets reported UP.

### Issue 2: Config reloader connection refused

Observed behavior:
The configuration reloader could not connect to the Prometheus server
while the main server was crashing.

Cause:
The main Prometheus process was failing to start because of its invalid
configuration.

Resolution:
The Prometheus configuration was corrected and the Helm release upgraded.
The reloader connection-refused messages were associated with the previous
server startup failure.

### Issue 3: Windows SSH key not found on EC2

Observed behavior:
The Windows path `/c/Users/...` and Windows Downloads directory could not
be accessed from the EC2 Ubuntu shell.

Cause:
Windows Git Bash and the remote EC2 shell are separate environments.

Resolution:
The SSH tunnel was initiated from Windows Git Bash, where the private key
was actually stored.

### Issue 4: SSH authentication failed with the first key

Observed error:

```text
Permission denied (publickey)
```

Resolution:
The correct EC2 key pair was identified as `devops-assignment-key.pem`.
The SSH connection then succeeded.

### Issue 5: Prometheus browser access

Resolution:
Prometheus was accessed through a local port-forward and an SSH tunnel,
rather than opening port 9090 to the public internet.

## 7. Validation Commands

Check platform resources:

```bash
kubectl get pods
kubectl get services
kubectl get pods -n monitoring
```

Check API readiness:

```bash
kubectl port-forward svc/platform-api 8080:8080
```

In another terminal:

```bash
curl -s http://localhost:8080/healthz
curl -s http://localhost:8080/readyz
curl -s http://localhost:8080/metrics
```

Check Prometheus targets while its port-forward is running:

```bash
curl -s http://localhost:9090/api/v1/targets
```

Check the application metrics query:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=platform_http_requests_total'
```

## 8. Secure Access

Prometheus web access uses local port forwarding and SSH tunneling.

Kubernetes port-forward command:

```bash
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
```

Windows Git Bash SSH tunnel command:

```bash
ssh -i ~/Downloads/devops-assignment-key.pem \
  -N -L 9090:localhost:9090 \
  ubuntu@<EC2_PUBLIC_IP>
```

Replace `<EC2_PUBLIC_IP>` with the current address of the EC2 instance.
Do not commit private keys, access tokens, passwords, or other secrets.

## 9. Submission Notes and Remaining Verification

The monitoring deployment and the two Prometheus targets listed above
were verified in the running environment.

Before submission, also verify:
- The API, worker, Redis, and PostgreSQL manifests and behavior
- Terraform configuration and infrastructure deployment
- Queue processing and failure handling
- Database migration and rollback strategy
- Shared and dedicated tenant isolation
- Load testing, autoscaling, and availability requirements
- Monitoring alerts and any required Grafana dashboards
- Cloud-agnostic deployment to the second required target

Do not mark a requirement as completed unless its implementation and
validation are present. Record any missing functionality as a limitation
or future task.

## 10. Reproducibility

Keep deployment configuration, scripts, infrastructure code, and this
report in version control. Exclude credentials, private keys, state files
containing secrets, and environment-specific sensitive data.
