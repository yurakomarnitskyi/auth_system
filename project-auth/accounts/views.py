from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def my_view(request):
    if request.user.is_authenticated:
        return Response({"message": "Ви авторизовані"})
    else:
        return Response({"message": "Ви не авторизовані"})
