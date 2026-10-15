import json
import os
import signal
import time
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_NAME = os.getenv("QUEUE_NAME", "platform-jobs")

running = True


def stop_worker(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, stop_worker)
signal.signal(signal.SIGINT, stop_worker)


def process_job(job):
    print(f"Processing job: {job}", flush=True)

    # Placeholder for actual job processing.
    # Keep each job's processing time within 60 seconds.
    time.sleep(1)

    print("Job completed", flush=True)


def main():
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

    while running:
        try:
            result = client.blpop(QUEUE_NAME, timeout=2)

            if result is None:
                continue

            _, raw_job = result

            try:
                job = json.loads(raw_job)
            except json.JSONDecodeError:
                print("Skipping invalid JSON job", flush=True)
                continue

            process_job(job)

        except redis.RedisError as exc:
            print(f"Redis connection error: {exc}", flush=True)
            time.sleep(3)

    client.close()
    print("Worker stopped", flush=True)


if __name__ == "__main__":
    main()
