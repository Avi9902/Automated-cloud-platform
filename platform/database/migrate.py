import os
import pathlib
import time

import psycopg


DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "platform")
DB_USER = os.getenv("POSTGRES_USER", "platform")
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]

MIGRATIONS_DIR = pathlib.Path("/migrations")


def connect_with_retry():
    for attempt in range(30):
        try:
            return psycopg.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5,
            )
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            print("PostgreSQL not ready; retrying...", flush=True)
            time.sleep(2)


def main():
    files = sorted(MIGRATIONS_DIR.glob("V*__*.sql"))
    if not files:
        raise RuntimeError("No versioned migration files found")

    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(100) PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            for path in files:
                version, description = path.stem.split("__", 1)

                cur.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = %s",
                    (version,),
                )
                if cur.fetchone():
                    print(f"Already applied: {version}", flush=True)
                    continue

                sql = path.read_text()
                print(f"Applying migration: {version}", flush=True)

                # Each migration and its version record commit together.
                with conn.transaction():
                    with conn.cursor() as migration_cur:
                        migration_cur.execute(sql)
                        migration_cur.execute(
                            """
                            INSERT INTO schema_migrations (version, description)
                            VALUES (%s, %s)
                            """,
                            (version, description.replace("_", " ")),
                        )

                print(f"Applied migration: {version}", flush=True)

    print("Database migrations completed successfully", flush=True)


if __name__ == "__main__":
    main()
