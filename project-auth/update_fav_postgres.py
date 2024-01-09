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


def update_postgres_from_redis():
    """Copy 'favorites' data from redis to postgres"""
    try:
        for key in r.scan_iter():
            data = r.lrange(key, 0, -1)
            obj, created = Favorites.objects.update_or_create(favorites_id=key, defaults={'saved_laptops': data})
        logging.info("Data was updated successfully.")
    except Exception:
        logging.exception("Error occurred")


def clear_old_records():
    """Clear irrelevant 'favorites' data (no views for more than 30 days)"""
    try:
        now = timezone.now()
        thirty_days_ago = now - datetime.timedelta(days=30)
        count, _ = Favorites.objects.filter(updated_at__lt=thirty_days_ago).delete()
        logging.info(f"Data was deleted successfully. Deleted {count} records")
    except Exception:
        logging.exception("Error occurred")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        parameter = sys.argv[1]
        if parameter == "clear":
            clear_old_records()
        elif parameter == "update":
            update_postgres_from_redis()
