#!/usr/bin/env bash
# build.sh

# Install dependencies
pip install -r requirements.txt

# Collect static files for Django
python manage.py collectstatic --noinput
