#!/bin/sh
python3 manage.py makemigrations
python3 manage.py migrate

uwsgi --module=tsingleap_backend.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=tsingleap_backend.settings \
    --env POSTGRES_DB="tsingleap_db" \
    --env POSTGRES_USER="tsingleap_backend" \
    --env POSTGRES_PASSWORD="tsingleap_backend_password" \
    --env POSTGRES_HOST="tsingleap-database.TsingLeap.secoder.local" \
    --env POSTGRES_PORT="5432" \
    --env TSINGLEAP_SECRET_SALT="$TSINGLEAP_SECRET_SALT" \
    --env TSINGLEAP_EMAIL_HOST_PASSWORD="$TSINGLEAP_EMAIL_HOST_PASSWORD" \
    --master \
    --http=0.0.0.0:80 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum
