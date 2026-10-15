import concurrent.futures
import urllib.request
import time
import math
from collections import Counter

URL = "http://127.0.0.1:18080/healthz"
TARGET_RPS = 300
DURATION = 10
TIMEOUT = 5
WORKERS = 400

statuses = Counter()
errors = Counter()
latencies = []
queue_delays = []

def request_once(scheduled_at):
    started_at = time.perf_counter()
    queue_delay_ms = (started_at - scheduled_at) * 1000
    try:
        req = urllib.request.Request(URL, method="GET")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            response.read()
            status = response.status
        latency_ms = (time.perf_counter() - started_at) * 1000
        return status, latency_ms, queue_delay_ms, None
    except Exception as exc:
        latency_ms = (time.perf_counter() - started_at) * 1000
        return None, latency_ms, queue_delay_ms, type(exc).__name__

total = TARGET_RPS * DURATION
run_start = time.perf_counter()
futures = []

with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
    for i in range(total):
        scheduled_at = run_start + i / TARGET_RPS
        delay = scheduled_at - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        futures.append(pool.submit(request_once, scheduled_at))

    for future in concurrent.futures.as_completed(futures):
        status, latency, queue_delay, error = future.result()
        latencies.append(latency)
        queue_delays.append(queue_delay)
        if status is not None:
            statuses[status] += 1
        if error:
            errors[error] += 1

elapsed = time.perf_counter() - run_start
ordered = sorted(latencies)
ordered_queue = sorted(queue_delays)

def percentile(values, p):
    if not values:
        return float("nan")
    index = max(0, math.ceil(p * len(values) / 100) - 1)
    return values[index]

successes = sum(n for code, n in statuses.items() if 200 <= code < 300)
completed = len(latencies)

print("\n=== Controlled Load Test Results ===")
print(f"Target rate: {TARGET_RPS} requests/sec")
print(f"Duration: {DURATION} seconds")
print(f"Requests attempted: {total}")
print(f"Requests completed: {completed}")
print(f"HTTP statuses: {dict(statuses)}")
print(f"Errors: {dict(errors)}")
print(f"Elapsed time: {elapsed:.2f} seconds")
print(f"Achieved throughput: {completed / elapsed:.2f} requests/sec")
print(f"Successful HTTP responses: {successes}")
print(f"Error rate: {(total - successes) / total * 100:.2f}%")

if ordered:
    print(f"Mean latency: {sum(ordered) / len(ordered):.2f} ms")
    print(f"p95 latency: {percentile(ordered, 95):.2f} ms")
    print(f"p99 latency: {percentile(ordered, 99):.2f} ms")
    print(f"Maximum latency: {max(ordered):.2f} ms")
    print(
        "p95 client scheduling delay: "
        f"{percentile(ordered_queue, 95):.2f} ms"
    )
