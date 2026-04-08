# Spendly Django API — production image
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=spendly.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY manage.py ./
COPY spendly ./spendly
COPY api ./api

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# WEB_CONCURRENCY can be set in Kubernetes / docker-compose
CMD ["sh", "-c", "exec gunicorn spendly.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${WEB_CONCURRENCY:-3} \
    --threads 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -"]
