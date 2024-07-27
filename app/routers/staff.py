from os import getenv
from logging import getLogger

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import StateFilter, Command, IS_ADMIN, ADMINISTRATOR
from aiogram.fsm.context import FSMContext

from keyboards import create_vacancies_markup
from fsm import FSMAddVacancy, FSMEditVacancy, FSMDialogueWithUser
from utils import (
    load_locales,
    crud_vacancies,
    notify_everyone_user_about_new_vacancy,
)


logger = getLogger(__name__)

locales = load_locales()

router = Router(name=__name__)
router.message.filter(F.chat.id == int(getenv("staff_chat_id")))


@router.message(Command("menu"))
async def handle_menu_cmd(message: Message, state: FSMContext):
    user_language = message.from_user.language_code
    await message.answer(
        text=locales["list_of_vacancies_message"][user_language],
        reply_markup=create_vacancies_markup("staff"),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.message(StateFilter(FSMAddVacancy.in_process))
async def add_vacancy(message: Message, state: FSMContext):
    try:
        vacancy_title, _ = message.text.split("\n", maxsplit=1)
        _, vacancy_description = message.md_text.split("\n", maxsplit=1)
    except ValueError:
        await message.answer("Description is required!")
        return
    crud_vacancies(vacancy_title, vacancy_description)

    await state.set_state(None)

    await notify_everyone_user_about_new_vacancy(message, state, vacancy_title)


@router.message(StateFilter(FSMEditVacancy.in_process))
async def edit_vacancy(message: Message, state: FSMContext):
    state_data = await state.get_data()
    vacancy_title = state_data.get("selected_vacancy", None)
    vacancy_description = message.md_text

    if not vacancy_title:
        logger.error("No vacancy title")
        return

    crud_vacancies(vacancy_title, vacancy_description)

    await state.set_state(None)


@router.message(StateFilter(FSMDialogueWithUser.in_process))
async def perform_dualogue_with_user(message: Message, state: FSMContext):
    state_data = await state.get_data()
    to_user = state_data.get("dialogue_with")

    if to_user is None:
        logger.critical("Couldn't get the user to send the message to.")
        return

    await message.send_copy(chat_id=to_user)
