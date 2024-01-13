from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    A serializer for the Comment model.

    get_user_name: A method to retrieve the name of the user who made the comment.
    user_name (SerializerMethodField): A read-only field to get the name of the user associated with the comment.
    """
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'parent_comment_id', 'user', 'user_name', 'laptop_id',
                  'laptop_name', 'comment_text', 'created_at']

    def get_user_name(self, obj):
        return obj.user.name if obj.user else None
