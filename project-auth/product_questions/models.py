from accounts.models import UserAccount, UserAccountManager

from django.db import models


def get_deleted_user():
    """
    Retrieves or creates a default UserAccount object for deleted accounts.
    This user account can be used as a placeholder for actions related to users who have deleted their accounts.

    :return UserAccount: A UserAccount instance with 'deleted_account@fake.email' as email
    and 'Deleted account' as name.
    """
    try:
        user = UserAccount.objects.get(email='deleted_account@fake.email', name='Deleted account')
    except UserAccount.DoesNotExist:
        user = UserAccount.objects.create_user(email='deleted_account@fake.email', name='Deleted account')
    return user


class Comment(models.Model):
    """
    A Django model representing comments made by users on laptops.

    Attributes:
        parent_comment_id (ForeignKey): A reference to another Comment instance that this
            comment is a reply to. It can be null for top-level comments.
        user (ForeignKey): A reference to the UserAccount of the user who made the comment.
            If the user's account is deleted, it is set to a default 'deleted account' user.
        laptop_id (CharField): The ID of the laptop that the comment is associated with.
        comment_text (TextField): The actual text content of the comment.
        created_at (DateTimeField): The timestamp indicating when the comment was created.
    """
    parent_comment_id = models.ForeignKey('self', on_delete=models.CASCADE, to_field='id', blank=True, null=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET(get_deleted_user))
    laptop_id = models.CharField(max_length=24)
    laptop_name = models.TextField()
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
