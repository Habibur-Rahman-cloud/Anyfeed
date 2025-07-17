#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (for production)
python manage.py collectstatic --noinput

# Apply migrations (optional: uncomment if needed)
# python manage.py migrate
