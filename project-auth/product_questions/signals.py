import asyncio
import os

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from django.db.models.signals import post_save
from django.dispatch import receiver

from dotenv import load_dotenv

from product_questions.models import Comment

load_dotenv()
CHAT_ID = os.getenv('CHAT_ID')
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)


async def send_update_info(text, bot):
    """Send Telegram message to a specific chat with given text and buttons 'Answer question', 'Delete question'"""
    markup = InlineKeyboardBuilder()

    answer = types.InlineKeyboardButton(text='\U00002705 Answer question', callback_data="answer_question")
    markup.add(answer)
    delete = types.InlineKeyboardButton(text='\U0000274C Delete question', callback_data="delete_question")
    markup.add(delete)

    async with bot.session:
        await bot.send_message(CHAT_ID, text, reply_markup=markup.as_markup())


@receiver(post_save, sender=Comment)
def save_comment(sender, instance, **kwargs):
    """
    Send Telegram message with question data when user (is_staff=False) posts a question
    """
    if not instance.user.is_staff:
        message = (
            str(f'User {instance.user.name} posted comment (id: {instance.pk}) on laptop {instance.laptop_id}:'
                f'\n\n{instance.comment_text}'))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_update_info(message, bot))
        loop.close()
