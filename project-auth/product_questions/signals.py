import asyncio
import os

from aiogram import Bot

from django.db.models.signals import post_save
from django.dispatch import receiver

from dotenv import load_dotenv

from product_questions.models import Comment


async def send_update_info(text, bot):
    async with bot.session:
        await bot.send_message(340678127, text)


@receiver(post_save, sender=Comment)
def save_comment(sender, instance, **kwargs):
    """
    Send Telegram message with question data when user (is_staff=False) posts a question
    """
    if not instance.user.is_staff:
        load_dotenv()
        TOKEN = os.getenv('TOKEN')
        bot = Bot(token=TOKEN)
        message = (
            str(f'User {instance.user.name} posted comment (id: {instance.pk}) on laptop {instance.laptop_id}:'
                f'\n\n{instance.comment_text}'))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_update_info(message, bot))
        loop.close()
