from logging import getLogger
from os import getenv

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import create_vacancies_markup, reply_to_the_resume_markup
from utils import load_locales
from fsm import FSMResumeForm, FSMDialogueWithStaff


logger = getLogger(__name__)

locales = load_locales()

router = Router(name=__name__)

message_header_for_hr_chat = "{user_info}\n{message_title}\n"


@router.message(CommandStart())
async def handle_start_cmd(message: Message, state: FSMContext):
    m = await message.answer(
        text="del kb", reply_markup=ReplyKeyboardRemove()
    )
    await m.delete()
    await message.answer(
        locales["user_start_message"][message.from_user.language_code],
        reply_markup=create_vacancies_markup("user"),
    )
    user_language = message.from_user.language_code
    await state.update_data({"language": user_language})


@router.message(StateFilter(FSMResumeForm.in_process))
async def record_users_resume(message: Message, state: FSMContext):
    user_language = message.from_user.language_code

    if not any((message.text, message.photo)):
        await message.answer(
            locales["resume_message_doesnt_meet_requirements"][user_language]
        )
        return

    state_data = await state.get_data()
    vacancy_title = state_data.get("selected_vacancy", "No selected vacancy.")
    await state.set_state(None)

    username = message.from_user.username
    username = f"\nUsername: @{username}" if username else ""
    message_header = message_header_for_hr_chat.format(
        user_info=f"{message.from_user.id}{username}",
        message_title=locales["new_resume_has_been_received"]["en"].format(
            vacancy_title
        ),
    )

    message_to_hr_chat = await message.send_copy(
        chat_id=getenv("staff_chat_id"),
        message_thread_id=getenv("staff_message_thread_id"),
    )
    if message.caption:
        header_offset = len(message_header)
        if caption_entities := message.caption_entities:
            for entity in caption_entities:
                entity.offset += header_offset

        previous_caption = message_to_hr_chat.caption

        await message_to_hr_chat.edit_caption(
            caption=f"{message_header}{previous_caption}",
            caption_entities=caption_entities,
            reply_markup=reply_to_the_resume_markup,
        )
    else:
        previous_text = message_to_hr_chat.md_text
        await message_to_hr_chat.edit_text(
            text=f"{message_header}{previous_text}",
            reply_markup=reply_to_the_resume_markup,
        )

    await message.answer(
        locales["resume_has_been_sent_message"][user_language]
    )


@router.message(StateFilter(FSMDialogueWithStaff.in_process))
async def perform_dialogue_with_staff(message: Message):
    await message.send_copy(
        chat_id=getenv("staff_chat_id"),
        message_thread_id=getenv("staff_message_thread_id"),
    )
