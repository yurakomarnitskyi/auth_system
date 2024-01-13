from django.urls import path

from .views import Favorites

urlpatterns = [
    path('', Favorites.as_view(), name='save-favorites'),
]
