FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY app.py .

RUN useradd --system --uid 10001 appuser
USER 10001

EXPOSE 8080

CMD ["python", "app.py"]
