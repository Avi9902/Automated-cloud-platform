CREATE TABLE IF NOT EXISTS schema_migrations (
    version       VARCHAR(100) PRIMARY KEY,
    description   VARCHAR(255) NOT NULL,
    applied_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
