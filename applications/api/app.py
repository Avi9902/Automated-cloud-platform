import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

START_TIME = time.time()
REQUEST_COUNT = 0
LOCK = threading.Lock()


def tcp_check(host, port, timeout=2):
    """Check whether a TCP connection to a dependency succeeds."""
    if not host:
        return False

    try:
        with socket.create_connection(
            (host, int(port)),
            timeout=timeout,
        ):
            return True
    except (OSError, ValueError):
        return False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global REQUEST_COUNT

        with LOCK:
            REQUEST_COUNT += 1
            count = REQUEST_COUNT

        if self.path == "/healthz":
            self.respond(
                200,
                '{"status":"alive"}',
                "application/json",
            )

        elif self.path == "/readyz":
            redis_ok = tcp_check(
                os.getenv("REDIS_HOST"),
                os.getenv("REDIS_PORT", "6379"),
            )

            postgres_ok = tcp_check(
                os.getenv("POSTGRES_HOST"),
                os.getenv("POSTGRES_PORT", "5432"),
            )

            ready = redis_ok and postgres_ok

            if ready:
                body = (
                    '{"status":"ready",'
                    '"redis":true,"postgres":true}'
                )
            else:
                body = (
                    '{"status":"not_ready","redis":'
                    + str(redis_ok).lower()
                    + ',"postgres":'
                    + str(postgres_ok).lower()
                    + '}'
                )

            self.respond(
                200 if ready else 503,
                body,
                "application/json",
            )

        elif self.path == "/metrics":
            uptime = time.time() - START_TIME

            body = (
                "# HELP platform_http_requests_total "
                "Total HTTP requests\n"
                "# TYPE platform_http_requests_total counter\n"
                f"platform_http_requests_total {count}\n"
                "# HELP platform_uptime_seconds "
                "Process uptime in seconds\n"
                "# TYPE platform_uptime_seconds gauge\n"
                f"platform_uptime_seconds {uptime:.2f}\n"
            )

            self.respond(
                200,
                body,
                "text/plain; version=0.0.4; charset=utf-8",
            )

        else:
            self.respond(
                404,
                '{"error":"not found"}',
                "application/json",
            )

    def respond(self, status, body, content_type):
        data = body.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            # The client disconnected before receiving the response.
            pass

    def log_message(self, fmt, *args):
        print(
            "%s - %s" % (self.address_string(), fmt % args),
            flush=True,
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        Handler,
    )

    print(f"API listening on port {port}", flush=True)
    server.serve_forever()
