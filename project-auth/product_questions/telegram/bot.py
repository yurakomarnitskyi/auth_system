import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

from asgiref.sync import sync_to_async

import django

from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_system.settings")
django.setup()

from product_questions.models import Comment


logging.basicConfig(level=logging.INFO)
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Send instructions for bot. Logs the chat id
    """
    logging.info(f'New chat was register, chat id: {message.from_user.id}')
    await message.answer("Hello! This is bot for Laptop_site administration.")


@sync_to_async
def save_comment(comment_id, text):
    """
    :param comment_id: parent comment id
    :param text: new comment text
    create a new comment in the database
    """
    parent_comment = Comment.objects.get(pk=comment_id)
    laptop_id = parent_comment.laptop_id
    Comment.objects.create(parent_comment_id=parent_comment, user='admin', comment_text=text, laptop_id=laptop_id)


@dp.message(F.reply_to_message)
async def reply_handler(message: types.Message):
    """
    processes reply messages
    call the save_comment function to save the comment with the message text to the database
    inform user about result
    """
    message_text = message.reply_to_message.text
    comment_id = re.search(r'.*id: (\d*).*', message_text)
    if comment_id:
        comment_id = comment_id.group(1)
        await save_comment(comment_id, message.text)
        await message.reply("Answer was posted!")
    else:
        await message.answer("This is not a question. Comment wasn't posted")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
