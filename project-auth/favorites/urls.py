from django.urls import path
from .views import SaveFavorite

urlpatterns = [
    path('', SaveFavorite.as_view(), name='save-favorites'),
]
