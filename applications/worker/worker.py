import json
import os
import signal
import time
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_NAME = os.getenv("QUEUE_NAME", "platform-jobs")
PROCESSING_QUEUE = f"{QUEUE_NAME}:processing"
DEAD_LETTER_QUEUE = f"{QUEUE_NAME}:dead-letter"

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


def recover_abandoned_jobs(client):
    recovered = 0

    # Run before consuming jobs. This assumes a single worker replica.
    while client.lmove(
        PROCESSING_QUEUE, QUEUE_NAME, src="RIGHT", dest="LEFT"
    ):
        recovered += 1

    if recovered:
        print(f"Recovered {recovered} abandoned job(s)", flush=True)


def main():
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

    try:
        client.ping()
        recover_abandoned_jobs(client)

        while running:
            try:
                raw_job = client.blmove(
                    QUEUE_NAME,
                    PROCESSING_QUEUE,
                    timeout=2,
                    src="LEFT",
                    dest="RIGHT",
                )

                if raw_job is None:
                    continue

                try:
                    job = json.loads(raw_job)
                except json.JSONDecodeError:
                    client.lmove(
                        PROCESSING_QUEUE,
                        DEAD_LETTER_QUEUE,
                        src="RIGHT",
                        dest="RIGHT",
                    )
                    print("Invalid JSON moved to dead-letter queue", flush=True)
                    continue

                try:
                    process_job(job)
                    client.lrem(PROCESSING_QUEUE, 1, raw_job)
                except Exception as exc:
                    print(f"Job failed; requeueing: {exc}", flush=True)
                    client.lmove(
                        PROCESSING_QUEUE,
                        QUEUE_NAME,
                        src="RIGHT",
                        dest="LEFT",
                    )
                    time.sleep(2)

            except redis.RedisError as exc:
                print(f"Redis connection error: {exc}", flush=True)
                time.sleep(3)

    finally:
        client.close()
        print("Worker stopped", flush=True)


if __name__ == "__main__":
    main()
