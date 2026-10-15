import concurrent.futures
import time
import urllib.request
import statistics
from collections import Counter

URL = "http://127.0.0.1:18080/healthz"
DURATION_SECONDS = 15
REQUESTS_PER_SECOND = 10
TIMEOUT_SECONDS = 5

latencies = []
statuses = Counter()
errors = Counter()

def request_once(_):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(URL, method="GET")
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            response.read()
            status = response.status
        elapsed_ms = (time.perf_counter() - start) * 1000
        return status, elapsed_ms, None
    except Exception as exc:
        return None, (time.perf_counter() - start) * 1000, type(exc).__name__

total = DURATION_SECONDS * REQUESTS_PER_SECOND
start = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
    results = pool.map(request_once, range(total))

for status, latency, error in results:
    latencies.append(latency)
    if status is not None:
        statuses[status] += 1
    if error:
        errors[error] += 1

elapsed = time.perf_counter() - start
ordered = sorted(latencies)

def percentile(values, p):
    if not values:
        return float("nan")
    index = min(int((p / 100) * len(values)), len(values) - 1)
    return values[index]

successes = sum(count for code, count in statuses.items() if 200 <= code < 300)

print("\n=== Baseline Load Test Results ===")
print(f"Requests attempted: {total}")
print(f"Requests completed: {len(latencies)}")
print(f"HTTP statuses: {dict(statuses)}")
print(f"Errors: {dict(errors)}")
print(f"Elapsed time: {elapsed:.2f} seconds")
print(f"Throughput: {len(latencies) / elapsed:.2f} requests/sec")
print(f"Successful HTTP responses: {successes}")
print(f"Error rate: {(total - successes) / total * 100:.2f}%")
print(f"Mean latency: {statistics.mean(latencies):.2f} ms" if latencies else "Mean latency: N/A")
print(f"p95 latency: {percentile(ordered, 95):.2f} ms")
print(f"p99 latency: {percentile(ordered, 99):.2f} ms")
