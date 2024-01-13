from django.db.models.signals import post_save
from django.dispatch import receiver

from product_questions.models import Comment


@receiver(post_save, sender=Comment)
def save_comment(sender, instance, **kwargs):
    """
    Signal receiver that sends a Telegram message when a new comment is posted by a non-staff user.

    Triggered on saving a Comment instance. If the user is not staff, formats a message
    with comment details and sends it to Telegram using an asynchronous task.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Comment): The instance of the Comment model that was saved.
        **kwargs: Additional keyword arguments passed with the signal.
    """
    pass
