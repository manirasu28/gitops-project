#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
python manage.py wait_for_db --timeout=60

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Django application..."
exec gunicorn --bind 0.0.0.0:8000 --workers 1 tms.wsgi:application 