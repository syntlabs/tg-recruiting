from os import getenv
from logging import getLogger

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from keyboards import (
    create_respond_to_vacancy_markup,
    create_vacancies_markup,
)
from utils import load_locales, crud_vacancies
from fsm import FSMResumeForm


locales = load_locales()

router = Router(name=__name__)


@router.callback_query(F.data.endswith("_select_vacancy_cbd"))
async def select_vacancy(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    vacancy_title = callback_query.data.replace("_select_vacancy_cbd", "")
    await state.update_data({"selected_vacancy": vacancy_title})

    user_language = callback_query.from_user.language_code
    vacancy = crud_vacancies(vacancy_title)
    if vacancy is None:
        await callback_query.message.edit_text(
            text=locales["vacancy_not_found"][user_language]
        )

    await callback_query.message.edit_text(
        text="\n".join([vacancy[0], vacancy[1]]),
        reply_markup=create_respond_to_vacancy_markup(user_language),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.callback_query(F.data == "back_cbd")
async def back_to_select_vacancy(
    callback_query: CallbackQuery, state: FSMContext
):
    user_language = callback_query.from_user.language_code
    await callback_query.message.edit_text(
        text=locales["user_start_message"][user_language],
        reply_markup=create_vacancies_markup("user"),
    )
    await state.update_data({"selected_vacancy": None})


@router.callback_query()
async def handle_respond_to_vacancy_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    await callback_query.message.delete()
    user_language = callback_query.from_user.language_code
    message_to_user = locales["resume_message"][user_language]
    await callback_query.message.answer(message_to_user)
    await state.set_state(FSMResumeForm.in_process)


@router.callback_query()
async def handle_back_btn_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    await state.set_state(None)

    user_language = callback_query.from_user.language_code
    await callback_query.message.answer(
        locales["user_start_message"][user_language],
        reply_markup=create_vacancies_markup("user"),
    )
