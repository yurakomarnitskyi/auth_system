from django.urls import path

from .views import CommentViewSet

urlpatterns = [
    path('', CommentViewSet.as_view(), name='save-favorites'),
]
