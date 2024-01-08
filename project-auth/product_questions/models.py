from accounts.models import UserAccount, UserAccountManager

from django.db import models


def get_deleted_user():
    try:
        user = UserAccount.objects.get(email='deleted_account@fake.email', name='Deleted account')
    except UserAccount.DoesNotExist:
        user = UserAccount.objects.create_user(email='deleted_account@fake.email', name='Deleted account')
    return user


class Comment(models.Model):
    parent_comment_id = models.ForeignKey('self', on_delete=models.CASCADE, to_field='id', blank=True, null=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET(get_deleted_user))
    laptop_id = models.CharField(max_length=24)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
