from rest_framework import serializers

from .models import Comment
from accounts.models import UserAccount


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'parent_comment_id', 'user', 'user_name', 'laptop_id', 'comment_text', 'created_at']

    def get_user_name(self, obj):
        return obj.user.name if obj.user else None
