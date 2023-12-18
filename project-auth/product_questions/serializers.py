from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'parent_comment_id', 'user', 'laptop_id', 'comment_text', 'created_at']
