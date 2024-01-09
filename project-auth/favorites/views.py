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
ttl_cookie = 2_592_000  # 30 days
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True, db=0)


class SaveFavorite(APIView):
    """
    API View for managing user's favorite laptops. Handles GET and POST requests.
    """
    def get(self, request, *args, **kwargs):
        response = Response()
        favorites_id = get_favorites_id(request, response)

        favorites = r.lrange(favorites_id, 0, -1)
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
    Adds a laptop to a user's favorites list in Redis.

    This function updates the user's favorites list with a given laptop ID. If the favorites list
    for the given ID exists in Redis, it adds the laptop ID to this list. If not, it attempts to
    fetch and update the list from the Django Favorites model. In case the favorites list does not
    exist in both Redis and the Django model, it creates a new entry in Redis.

    Args:
        favorites_id (str or int): The identifier for the user's favorites list.
        laptop_id (str or int): The laptop ID to be added to the favorites list.
    """
    favorites_id = str(favorites_id)
    laptop_id = str(laptop_id)

    if favorites_id in r.keys():
        users_favorites_list = r.lrange(favorites_id, 0, -1)
        if laptop_id not in users_favorites_list:
            r.lpush(favorites_id, laptop_id)
            r.expire(favorites_id, ttl_redis)
    else:
        try:
            users_favorites_list = list(Favorites.objects.get(favorites_id=favorites_id).saved_laptops)
            if laptop_id not in users_favorites_list:
                users_favorites_list.append(laptop_id)
            for i in users_favorites_list:
                r.lpush(favorites_id, i)
            r.expire(favorites_id, ttl_redis)
        except Favorites.DoesNotExist:
            r.lpush(favorites_id, laptop_id)
            r.expire(favorites_id, ttl_redis)


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
