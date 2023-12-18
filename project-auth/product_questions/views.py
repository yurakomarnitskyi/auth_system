from rest_framework import viewsets

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
