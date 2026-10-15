FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir "psycopg[binary]==3.2.6"

COPY migrate.py /app/migrate.py
COPY migrations/ /migrations/

RUN useradd --system --uid 10001 appuser
USER 10001

CMD ["python", "/app/migrate.py"]
