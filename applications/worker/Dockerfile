FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir redis==5.2.1

COPY worker.py .

RUN useradd --system --uid 10001 appuser
USER 10001

CMD ["python", "worker.py"]
