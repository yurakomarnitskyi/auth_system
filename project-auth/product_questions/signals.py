import asyncio

from aiogram import Bot

from django.db.models.signals import post_save
from django.dispatch import receiver

from product_questions.models import Comment


async def send_update_info(text, bot):
    async with bot.session:
        await bot.send_message(340678127, text)


@receiver(post_save, sender=Comment)
def save_comment(sender, instance, **kwargs):
    """
    Send Telegram message with question data when user (is_staff=False) posts a question
    """
    if instance.user != 1:  # if not admin
        bot = Bot(token='')
        message = (
            str(f'User {instance.user} posted comment on laptop {instance.laptop_id}:\n{instance.comment_text}'
                f'\n\nComment id {instance.pk}'))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_update_info(message, bot))
        loop.close()
