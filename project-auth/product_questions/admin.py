from django.contrib import admin
from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'parent_comment_id', 'user_id', 'laptop_id', 'comment_text', 'created_at')


admin.site.register(Comment, CommentAdmin)
