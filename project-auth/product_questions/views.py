from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Comment
from .serializers import CommentSerializer
from rest_framework import status


class CommentViewSet(APIView):
    """
    A viewset for viewing and editing comment instances.
    """
    # serializer_class = CommentSerializer
    # queryset = Comment.objects.all()

    def get(self, request):
        laptop_id = self.request.query_params.get('laptop_id')
        queryset = Comment.objects.filter(laptop_id=laptop_id)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response("You're not authorized to comment, please log in", status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['user'] = request.user.pk
        serializer = CommentSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
