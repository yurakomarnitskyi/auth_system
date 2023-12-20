import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from asgiref.sync import sync_to_async

import django
from django.core.exceptions import ObjectDoesNotExist

from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_system.settings")
django.setup()

from accounts.models import UserAccount
from product_questions.models import Comment


logging.basicConfig(level=logging.INFO)
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()


class ConfirmCommentDeletion(StatesGroup):
    confirm_deletion = State()


class SendAnswer(StatesGroup):
    sending_answer = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Send instructions for bot. Logs the chat id
    """
    logging.info(f'New chat was register, chat id: {message.from_user.id}')
    await message.answer("Hello! This is bot for Laptop_site administration.")


@dp.callback_query(F.data == "answer_question", StateFilter(None))
async def answer_comment_button(callback: types.CallbackQuery, state: FSMContext):
    comment_id = get_comment_id_from_message(callback.message.text)

    await callback.message.answer(f"Please send your answer to comment with id {comment_id}")
    await state.set_state(SendAnswer.sending_answer)
    await state.update_data(comment_id=comment_id)
    await callback.answer()


@dp.callback_query(F.data == "delete_question", StateFilter(None))
async def delete_button_handler(callback: types.CallbackQuery, state: FSMContext):
    comment_id = get_comment_id_from_message(callback.message.text)

    await callback.message.answer(text=f"Are you sure you want to delete comment with id "
                                       f"{comment_id}?",
                                  reply_markup=yes_no_keyboard())
    await state.set_state(ConfirmCommentDeletion.confirm_deletion)
    await state.update_data(comment_id=comment_id)
    await callback.answer()


@dp.message(SendAnswer.sending_answer)
async def answer_comment(message: Message, state: FSMContext):
    state_info = await state.get_data()
    comment_id = state_info['comment_id']

    if comment_id:
        try:
            await save_comment_to_db(comment_id, message.text)
            await message.reply("Answer was posted", reply_markup=ReplyKeyboardRemove())
        except ObjectDoesNotExist:
            await message.answer(f"Comment with id {comment_id} does not exist",
                                 reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Something went wrong", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(ConfirmCommentDeletion.confirm_deletion, F.text.in_(['Yes', 'No']))
async def delete_comment_confirm(message: Message, state: FSMContext):
    state_info = await state.get_data()
    comment_id = state_info['comment_id']

    if message.text == 'No':
        await message.answer("Comment was not deleted", reply_markup=ReplyKeyboardRemove())
    if message.text == "Yes":
        if comment_id:
            try:
                await delete_comment_from_db(comment_id)
                await message.answer(f"Comment {comment_id} was successfully deleted",
                                     reply_markup=ReplyKeyboardRemove())
            except ObjectDoesNotExist:
                await message.answer(f"Comment with id {comment_id} does not exist",
                                     reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Something went wrong", reply_markup=ReplyKeyboardRemove())
    await state.clear()


def yes_no_keyboard():
    yes = KeyboardButton(text="Yes")
    no = KeyboardButton(text="No")
    return ReplyKeyboardMarkup(keyboard=[[yes, no]], resize_keyboard=True)


def get_comment_id_from_message(message_text):
    search_id = re.search(r'.*id: (\d*).*', message_text)
    if search_id:
        comment_id = search_id.group(1)
        return comment_id
    else:
        return None


@sync_to_async
def delete_comment_from_db(comment_id):
    Comment.objects.get(pk=comment_id).delete()


@sync_to_async
def save_comment_to_db(comment_id, text):
    """
    :param comment_id: parent comment id
    :param text: new comment text
    create a new comment in the database
    """
    parent_comment = Comment.objects.get(pk=comment_id)
    laptop_id = parent_comment.laptop_id
    user = UserAccount.objects.get(pk=1)
    Comment.objects.create(parent_comment_id=parent_comment, user=user, comment_text=text, laptop_id=laptop_id)


@dp.message(F.reply_to_message)
async def reply_handler(message: types.Message):
    """
    processes reply messages
    call the save_comment function to save the comment with the message text to the database
    inform user about result
    """
    base_message_text = message.reply_to_message.text
    comment_id = get_comment_id_from_message(base_message_text)

    if comment_id:
        try:
            await save_comment_to_db(comment_id, message.text)
            await message.reply("Answer was posted!")
        except ObjectDoesNotExist:
            await message.reply(f"Comment with id {comment_id} does not exist")
    else:
        await message.reply("This is not a comment")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
