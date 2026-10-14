#!/usr/bin/env bash
set -euo pipefail

CHART_DIR="platform/helm/blackbox-platform"
RENDERED_FILE="$(mktemp)"
trap 'rm -f "$RENDERED_FILE"' EXIT

echo "==> Linting Helm chart"
helm lint "$CHART_DIR"

echo "==> Rendering chart"
helm template platform-dev "$CHART_DIR" \
  --set api.image.repository=example/api \
  --set api.image.tag=test \
  --set worker.image.repository=example/worker \
  --set worker.image.tag=test \
  --set autoscaling.api.enabled=true \
  --set autoscaling.worker.enabled=true \
  > "$RENDERED_FILE"

RESOURCE_COUNT="$(grep -c '^kind:' "$RENDERED_FILE")"
HPA_COUNT="$(grep -c '^kind: HorizontalPodAutoscaler' "$RENDERED_FILE")"

if [[ "$RESOURCE_COUNT" -ne 7 || "$HPA_COUNT" -ne 2 ]]; then
  echo "FAIL: found $RESOURCE_COUNT resources and $HPA_COUNT HPAs"
  exit 1
fi

echo "PASS: $RESOURCE_COUNT resources rendered, including $HPA_COUNT HPAs"
echo "NOTE: Placeholder images used; nothing deployed."
