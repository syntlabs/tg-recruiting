from os import getenv
from logging import getLogger
from typing import Literal

from aiogram import Router, F
from aiogram.enums import ParseMode, ChatAction
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from keyboards import (
    edit_vacancy_markup,
    cancel_action_markup,
    create_vacancies_markup,
)
from utils import load_locales, crud_vacancies, get_user_from_state
from fsm import (
    FSMAddVacancy,
    FSMEditVacancy,
    FSMDialogueWithUser,
    FSMDialogueWithStaff,
)


logger = getLogger(__name__)

locales = load_locales()

router = Router(name=__name__)
router.callback_query.filter(
    F.message.chat.id == int(getenv("staff_chat_id"))
)


@router.callback_query(F.data == "add_vacancy_cbd", StateFilter(None))
async def handle_add_vacancy_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    user_language = callback_query.from_user.language_code
    await callback_query.message.edit_text(
        locales["add_vacancy_message"][user_language],
        reply_markup=cancel_action_markup,
    )
    await state.set_state(FSMAddVacancy.in_process)


@router.callback_query(F.data.endswith("_select_vacancy_cbd"))
async def select_vacancy(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    vacancy_title = callback_query.data.replace("_select_vacancy_cbd", "")
    await state.set_data({"selected_vacancy": vacancy_title})

    await callback_query.message.edit_text(
        vacancy_title, reply_markup=edit_vacancy_markup
    )


@router.callback_query(F.data.endswith("_vacancy_cbd"))
async def perform_operation_with_vacancy(
    callback_query: CallbackQuery, state: FSMContext
):
    user_language = callback_query.from_user.language_code
    operation = callback_query.data.replace("_vacancy_cbd", "")
    state_data = await state.get_data()
    selected_vacancy = state_data.get("selected_vacancy", None)
    if not selected_vacancy:
        logger.error("No selected vacancy")
        return

    match operation:
        case "view":
            vacancy = crud_vacancies(selected_vacancy)
            await callback_query.message.edit_text(
                text=f"Title: {vacancy[0]}\nDescription:\n{vacancy[1]}",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        case "edit":
            await callback_query.message.edit_text(
                text=locales["edit_vacancy_message"][user_language]
            )
            await state.set_state(FSMEditVacancy.in_process)
        case "delete":
            crud_vacancies(selected_vacancy, delete=True)
            await callback_query.answer("Deletion completed")


@router.callback_query(F.data.in_(("back_cbd", "cancel_cbd")))
async def back_to_select_vacancy(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    await state.clear()

    user_language = callback_query.from_user.language_code
    await callback_query.message.edit_text(
        text=locales["list_of_vacancies_message"][user_language],
        reply_markup=create_vacancies_markup("staff"),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.callback_query(F.data == "accept_user_cbd")
async def accept_user(callback_query: CallbackQuery, state: FSMContext):
    await _perform_action_with_user("accept", callback_query, state)


@router.callback_query(F.data == "reject_user_cbd")
async def reject_user(callback_query: CallbackQuery, state: FSMContext):
    await _perform_action_with_user("reject", callback_query, state)


@router.callback_query(F.data == "ask_question")
async def ask_question(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.pin(disable_notification=True)

    user_id = (
        callback_query.message.text.split("\n", maxsplit=1)[0]
        if callback_query.message.text
        else callback_query.message.caption.split("\n", maxsplit=1)[0]
    )
    user = get_user_from_state(state, user_id)

    await callback_query.bot.send_chat_action(
        chat_id=user_id, action=ChatAction.TYPING
    )
    await callback_query.answer()
    await state.set_state(FSMDialogueWithUser.in_process)
    await state.update_data({"dialogue_with": user_id})
    user[1].state = FSMDialogueWithStaff.in_process


async def _perform_action_with_user(
    action: Literal["accept", "reject"],
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await callback_query.message.unpin()
    await state.set_state(None)
    await state.update_data({"dialogue_with": None})

    user_id = (
        callback_query.message.text.split("\n", maxsplit=1)[0]
        if callback_query.message.text
        else callback_query.message.caption.split("\n", maxsplit=1)[0]
    )
    user = get_user_from_state(state, user_id)

    if not user:
        await callback_query.answer("User not found.")
        await callback_query.message.delete()
        return

    user[1].data.update({"is_hired": 1 if action == "accept" else 0})
    user[1].state = None

    user_language = user[1].data.get("language", "en")

    if action == "accept":
        await callback_query.answer("User has been hired.")
    else:
        await callback_query.answer("User has been rejected.")

    await callback_query.message.edit_reply_markup(reply_markup=None)
    if caption := callback_query.message.caption:
        await callback_query.message.edit_caption(
            caption=caption
            + str("\n✅ Hired" if action == "accept" else "\n❌ Rejected"),
            caption_entities=callback_query.message.caption_entities,
        )
    else:
        text = callback_query.message.md_text
        await callback_query.message.edit_text(
            text=text
            + str("\n✅ Hired" if action == "accept" else "\n❌ Rejected")
        )

    await callback_query.bot.send_message(
        chat_id=user_id,
        text=(
            locales["user_is_hired"][user_language]
            if action == "accept"
            else locales["user_is_rejected"][user_language]
        ),
    )
