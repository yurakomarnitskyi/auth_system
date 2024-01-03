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
ttl_redis = 86_400  # 24h
ttl_cookie = 2_592_000  # 30 days
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=0)


def generate_custom_id(length=10):
    while True:
        characters = string.ascii_letters + string.digits
        custom_id = ''.join(random.choice(characters) for _ in range(length))
        if not Favorites.objects.filter(favorites_id=custom_id).exists():
            return custom_id


class SaveFavorite(APIView):
    def get(self, request, *args, **kwargs):
        response = Response()
        favorites_id = get_favorites_id(request, response)

        favorites = r.lrange(favorites_id, 0, -1)
        response.data = favorites
        return response

    def post(self, request, *args, **kwargs):
        laptop_id = request.data.get('laptop_id')
        response = Response()

        favorites_id = get_favorites_id(request, response)
        add_favorites(favorites_id, laptop_id)

        response.data = {'message': 'Product saved successfully'}
        response.status = status.HTTP_200_OK
        return response


def add_favorites(favorites_id, laptop_id):
    favorites_id = str(favorites_id)
    laptop_id = str(laptop_id)

    if favorites_id in r.keys():
        print('redis')
        users_favorites_list = r.lrange(favorites_id, 0, -1)
        if laptop_id not in users_favorites_list:
            r.lpush(favorites_id, laptop_id)
            r.expire(favorites_id, ttl_redis)
    else:
        try:
            users_favorites_list = list(Favorites.objects.get(favorites_id=favorites_id).saved_laptops)
            users_favorites_list.append(laptop_id)
            for i in users_favorites_list:
                r.lpush(favorites_id, i)
            r.expire(favorites_id, ttl_redis)
        except Favorites.DoesNotExist:
            r.lpush(favorites_id, laptop_id)
            r.expire(favorites_id, ttl_redis)


def get_favorites_id(request, response):
    if request.user.is_authenticated:
        return request.user.pk

    favorites_id = request.COOKIES.get('favorites_id', None)
    if not favorites_id:
        favorites_id = generate_custom_id()
    response.set_cookie('favorites_id', favorites_id, max_age=ttl_cookie, secure=True, httponly=True, samesite='None')
    return favorites_id
