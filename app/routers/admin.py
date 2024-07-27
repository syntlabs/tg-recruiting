from os import getenv
from logging import getLogger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils import load_locales


logger = getLogger(__name__)

locales = load_locales()

router = Router(name=__name__)
router.message.filter(F.from_user.id == int(getenv("admin_id")))


@router.message(Command("add_staff"))
async def add_staff(message: Message, state: FSMContext):
    _, staff_user_id = message.text.split()
    if not isinstance(staff_user_id, str):
        await message.answer("Using the command: /add_staff 1234567890")

    new_thread = await message.bot.create_forum_topic(
        chat_id=message.chat.id, name=f"HR {staff_user_id}"
    )
    thread_id = new_thread.message_thread_id
    link = f"https://t.me/c/{getenv("staff_chat_id_normal_view")}/{thread_id}"
    await message.answer(f"Link to thread for new staff: {link}")

    current_data = await state.storage.get_data("staff")
    current_data = current_data.get("message_thread_ids", [])
    current_data.append(new_thread.message_thread_id)
    await state.storage.update_data(
        "staff", {"message_thread_ids": current_data}
    )
