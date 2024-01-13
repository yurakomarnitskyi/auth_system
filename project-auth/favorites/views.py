import os
import random
import string

from dotenv import load_dotenv

import redis

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Favorites

load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
ttl_redis = 86_400  # 24h
ttl_cookie = 7_776_000  # 90 days
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True, db=0)


class FavoritesView(APIView):
    """
    API View for managing user's favorite laptops. Handles GET and POST requests.
    """
    def get(self, request, *args, **kwargs):
        response = Response()
        favorites_id = get_favorites_id(request, response)

        favorites = get_favorites(favorites_id)
        response.data = {"favorites": favorites}
        return response

    def post(self, request, *args, **kwargs):
        laptop_id = request.data.get('laptop_id')
        response = Response()

        favorites_id = get_favorites_id(request, response)
        add_favorites(favorites_id, laptop_id)

        response.data = {'message': 'Saved successfully'}
        response.status = status.HTTP_200_OK
        return response


def generate_custom_id(length=10):
    """Function for generating unique favorites_id."""
    while True:
        characters = string.ascii_letters + string.digits
        custom_id = ''.join(random.choice(characters) for _ in range(length))
        if not Favorites.objects.filter(favorites_id=custom_id).exists():
            return custom_id


def add_favorites(favorites_id, laptop_id):
    """
    Adds a laptop to a user's favorites list, both in the database and Redis cache.

    Args:
        favorites_id (int or str): The identifier for the user's favorites list.
        laptop_id (str): The identifier of the laptop to be added.

    Raises:
        Exception: If database or Redis operations fail.
    """
    favorites_id = str(favorites_id)
    laptop_id = str(laptop_id)

    favorites_key = f'favorites:{favorites_id}'

    favorites_obj, created = Favorites.objects.get_or_create(
        favorites_id=favorites_id,
        defaults={'saved_laptops': []}
    )
    if laptop_id not in favorites_obj.saved_laptops:
        favorites_obj.saved_laptops.append(laptop_id)
        favorites_obj.save()

    r.sadd(favorites_key, laptop_id)
    r.expire(favorites_key, ttl_redis)


def get_favorites_id(request, response):
    """
    Retrieves or generates a unique identifier for a user's favorites list.

    If the user is authenticated, their primary key is used as the identifier. For unauthenticated
    users, the function looks for an identifier in the cookies. If it doesn't exist, a new one is
    generated. Sets or updates identifier in the response cookies.

    Args:
        request: The HTTP request object, used to check user authentication and cookies.
        response: The HTTP response object, used to set the favorites identifier cookie.

    Returns:
        str: A unique identifier for the user's favorites list.
    """
    if request.user.is_authenticated:
        return request.user.pk

    favorites_id = request.COOKIES.get('favorites_id', None)
    if not favorites_id:
        favorites_id = generate_custom_id()
    response.set_cookie('favorites_id', favorites_id, max_age=ttl_cookie, secure=True, httponly=True, samesite='None')
    return favorites_id


def get_favorites(favorites_id):
    """
    Retrieves a user's favorite laptops from Redis cache or PostgreSQL database.

    Args:
        favorites_id (str): The identifier for the user's favorites list.

    Returns:
        list: A list of laptop IDs that are marked as favorites by the user.
    """
    favorites_key = f'favorites:{favorites_id}'

    # Try to get the favorites from Redis set
    if r.exists(favorites_key):
        return list(r.smembers(favorites_key))
    else:
        # Retrieve data from PostgreSQL
        try:
            favorites_obj = Favorites.objects.get(favorites_id=favorites_id)
            laptop_ids = favorites_obj.saved_laptops

            # Save the data to Redis set for future access
            if laptop_ids:
                r.sadd(favorites_key, *laptop_ids)
                r.expire(favorites_key, ttl_redis)

            return laptop_ids
        except Favorites.DoesNotExist:
            return []
