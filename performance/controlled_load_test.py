import concurrent.futures
import math
import time
import urllib.request
from collections import Counter

URL = "http://platform-api:8080/healthz"
TARGET_RPS = 2250
DURATION = 10
TIMEOUT = 5
WORKERS = 300

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


def percentile(values, p):
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = max(0, math.ceil(p * len(ordered) / 100) - 1)
    return ordered[index]


total = TARGET_RPS * DURATION
run_start = time.perf_counter()
next_to_submit = 0
futures = set()

with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
    while next_to_submit < total or futures:
        now = time.perf_counter()

        # Submit only requests whose scheduled start time has arrived.
        while next_to_submit < total:
            scheduled_at = run_start + next_to_submit / TARGET_RPS
            if scheduled_at > now:
                break

            futures.add(pool.submit(request_once, scheduled_at))
            next_to_submit += 1

        if futures:
            done, futures = concurrent.futures.wait(
                futures,
                timeout=0.001,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )

            for future in done:
                status, latency, queue_delay, error = future.result()
                latencies.append(latency)
                queue_delays.append(queue_delay)

                if status is not None:
                    statuses[status] += 1
                if error:
                    errors[error] += 1
        elif next_to_submit < total:
            time.sleep(min(0.001, max(
                0,
                run_start + next_to_submit / TARGET_RPS
                - time.perf_counter(),
            )))

elapsed = time.perf_counter() - run_start
completed = len(latencies)
successes = sum(
    count for code, count in statuses.items()
    if 200 <= code < 300
)

print("\n=== Bounded Load Test Results ===")
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

if latencies:
    print(f"Mean latency: {sum(latencies) / len(latencies):.2f} ms")
    print(f"p95 latency: {percentile(latencies, 95):.2f} ms")
    print(f"p99 latency: {percentile(latencies, 99):.2f} ms")
    print(f"Maximum latency: {max(latencies):.2f} ms")
    print(
        "p95 client scheduling delay: "
        f"{percentile(queue_delays, 95):.2f} ms"
    )
