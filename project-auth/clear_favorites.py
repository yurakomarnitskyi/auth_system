import datetime
import logging
import os
import sys

import django
import redis
from dotenv import load_dotenv
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_system.settings")
django.setup()

from favorites.models import Favorites

load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True, db=0)

logging.basicConfig(level=logging.INFO,
                    filename='/tmp/postgres_update.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )


def clear_old_records():
    """
    Deletes outdated 'favorites' records from PostgreSQL.

    Identifies and removes any 'favorites' records in the PostgreSQL database that have not
    been updated in the last 30 days.
    """
    try:
        now = timezone.now()
        days_ago = now - datetime.timedelta(days=90)
        count, _ = Favorites.objects.filter(updated_at__lt=days_ago).delete()
        logging.info(f"Data was deleted successfully. Deleted {count} records")
    except Exception:
        logging.exception("Error occurred")


if __name__ == "__main__":
    clear_old_records()
