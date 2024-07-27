from pickle import load
from typing import Literal, Optional, Iterable, Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils import load_locales


locales = load_locales()


def create_vacancies_markup(
    user_type: Literal["user", "staff"] = "user"
) -> Optional[InlineKeyboardMarkup]:
    vacancies = None
    try:
        with open("/usr/src/app/vacancies.pickle", "rb") as vacancies_file:
            vacancies: Iterable[Sequence[str]] = load(vacancies_file)
    except FileNotFoundError:
        pass

    if user_type == "user" and not vacancies:
        return None

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
    if vacancies:
        inline_kb.inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=vacancy[0],
                    callback_data=f"{vacancy[0]}_select_vacancy_cbd",
                )
            ]
            for vacancy in vacancies
        ]

    if user_type == "staff":
        inline_button_text = "Add vacancy"
        inline_kb.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=inline_button_text, callback_data=f"add_vacancy_cbd"
                )
            ]
        )

    return inline_kb


# Markups for clients
def create_respond_to_vacancy_markup(
    language: str = "en",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=locales["respond_btn_text"][language],
                    callback_data="respond_to_vacancy_cbd",
                )
            ],
            [
                InlineKeyboardButton(
                    text=locales["back_btn_text"][language],
                    callback_data="back_cbd",
                )
            ],
        ]
    )


# Markups for staff
edit_vacancy_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Full version", callback_data="view_vacancy_cbd"
            )
        ],
        [
            InlineKeyboardButton(
                text="Edit vacancy", callback_data="edit_vacancy_cbd"
            )
        ],
        [
            InlineKeyboardButton(
                text="Delete vacancy", callback_data="delete_vacancy_cbd"
            )
        ],
        [InlineKeyboardButton(text="<< Back", callback_data="back_cbd")],
    ]
)

cancel_action_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_cbd")]
    ]
)

reply_to_the_resume_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Accept", callback_data="accept_user_cbd")],
        [InlineKeyboardButton(text="Reject", callback_data="reject_user_cbd")],
        [
            InlineKeyboardButton(
                text="Ask a question", callback_data="ask_question"
            )
        ],
    ]
)
