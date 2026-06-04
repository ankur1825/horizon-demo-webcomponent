FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# INTENTIONAL_VULNERABILITY: container runs as root for SSDLC validation.
ENV TRUSTOPS_DB=/tmp/trustops_agent.db
ENV APP_ENV=demo

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
