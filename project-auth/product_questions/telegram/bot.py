import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

from asgiref.sync import sync_to_async

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from product_questions.models import Comment


logging.basicConfig(level=logging.INFO)
TOKEN = ''
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Send an instruction to the bot. Logs the chat id.
    """
    logging.info(f'New chat was register, chat id: {message.from_user.id}')
    await message.answer("Hello! This is bot for Laptop_site administration.")


@sync_to_async
def save_comment(laptop_comment_id, text):
    parent_comment = Comment.objects.get(pk=laptop_comment_id)
    Comment.objects.create(parent_comment_id=parent_comment, user_id=1, comment_text=text)


@dp.message(F.reply_to_message)
async def reply_handler(message: types.Message):
    message_text = message.reply_to_message.text
    laptop_comment_id = re.search(r'.*Comment id (\d*)', message_text).group(1)
    await save_comment(laptop_comment_id, message.text)
    await message.reply("Answer was posted!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
