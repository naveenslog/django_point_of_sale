#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    max_retries = 10
    retry_delay = 5
    
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                host=os.getenv('DB_HOST')
            )
            conn.close()
            return
        except OperationalError:
            print("Database not ready, waiting...")
            time.sleep(retry_delay)
    
    print("Could not connect to database after multiple attempts!")
    sys.exit(1)

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_pos.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    import django
    django.setup()

    from django.db import connection
    connection.schema_name = 'public'
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    # wait_for_db()
    main()
