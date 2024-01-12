import asyncio
import os

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.parse_mode import ParseMode

from django.db.models.signals import post_save
from django.dispatch import receiver

from dotenv import load_dotenv

from product_questions.models import Comment

load_dotenv()
CHAT_ID = os.getenv('CHAT_ID')
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)


async def send_update_info(text, bot):
    """
    This function is designed to send a message to a predefined chat on Telegram. It includes
    'Answer question' and 'Delete question' as inline keyboard buttons for interactive responses.

    Args:
        text (str): The message text to be sent.
        bot: The Telegram bot instance used for sending the message.
    It requires an active session with the Telegram bot and access to the specific CHAT_ID.
    """
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
    Signal receiver that sends a Telegram message when a new comment is posted by a non-staff user.

    Triggered on saving a Comment instance. If the user is not staff, formats a message
    with comment details and sends it to Telegram using an asynchronous task.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Comment): The instance of the Comment model that was saved.
        **kwargs: Additional keyword arguments passed with the signal.
    """
    if not instance.user.is_staff:
        message = (
            str(f'<b>{instance.user.name}</b> posted comment (id: {instance.pk}) on laptop {instance.laptop_name}:'
                f'\n\n{instance.comment_text}'))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_update_info(message, bot))
        loop.close()
