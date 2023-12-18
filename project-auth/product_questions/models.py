from accounts.models import UserAccount

from django.db import models


class Comment(models.Model):
    parent_comment_id = models.ForeignKey('self', on_delete=models.CASCADE, to_field='id', blank=True, null=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET('Deleted account'))
    laptop_id = models.IntegerField()
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
