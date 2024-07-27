from asyncio import sleep
from math import ceil
from typing import Any, Iterable, Sequence, Optional, Union
from pickle import load as pickle_load, dump as pickle_dump
from json import load as json_load
from logging import getLogger

from aiogram.fsm.storage.memory import MemoryStorage, MemoryStorageRecord
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup


logger = getLogger(__name__)


def save_storage(storage: Any) -> None:
    """
    This function saves the storage.

    Args:
    storage: The storage to save.
    """
    try:
        with open("storage.pickle", "wb") as storage_file:
            pickle_dump(storage, storage_file)
    except Exception as e:
        print(f"Failed to save storage: {e}")


def load_storage() -> None:
    """
    This function loads the storage.

    Returns:
    The loaded storage.
    """
    try:
        with open("storage.pickle", "rb") as storage_file:
            return pickle_load(storage_file)
    except FileNotFoundError:
        return MemoryStorage()
    except Exception as e:
        print(f"Failed to load storage: {e}")
        return MemoryStorage()


def crud_vacancies(
    vacancy_title: str,
    vacancy_description: Optional[str] = None,
    *,
    delete: bool = False,
) -> Optional[Sequence[str]]:
    """This function uses to perform crud operations on vacancies.

    Args:
        vacancy_title (str): Uses for all operations.
        vacancy_description (Optional[str], optional): Uses for create and update operations. Defaults to None.
        delete (bool, optional): Uses for delete vacancy. Defaults to False.

    Returns:
        Optional[Sequence[str]]: Returns if a read operation is specified.
        Returns None if the vacancy is not found.
    """
    vacancies = []
    try:
        with open("/usr/src/app/vacancies.pickle", "rb") as vacancies_file:
            vacancies: Iterable[Sequence[str]] = pickle_load(vacancies_file)
    except FileNotFoundError:
        pass

    if delete:
        vacancies = [v for v in vacancies if v[0] != vacancy_title]
    elif vacancy_description is not None:
        # Update or create a vacancy with the given title and description
        updated_vacancy = [vacancy_title, vacancy_description]
        vacancies = [
            v if v[0] != vacancy_title else updated_vacancy for v in vacancies
        ]
        if updated_vacancy not in vacancies:
            vacancies.append(updated_vacancy)
    else:
        try:
            return next(filter(lambda v: v[0] == vacancy_title, vacancies))
        except StopIteration:
            return None

    with open("/usr/src/app/vacancies.pickle", "wb") as vacancies_file:
        pickle_dump(vacancies, vacancies_file)


def load_locales() -> dict:
    with open("/usr/src/app/locales.json", encoding="utf-8") as locales_file:
        locales = json_load(locales_file)
    return locales


def get_user_from_state(
    state: FSMContext, user_id: Union[int, str]
) -> Optional[tuple[StorageKey, MemoryStorageRecord]]:
    def filter_func(record: int) -> bool:
        nonlocal user_id
        try:
            return str(user_id) == str(getattr(record[0], "chat_id"))
        except AttributeError:
            return False

    try:
        user = next(
            filter(
                filter_func,
                tuple(state.storage.storage.items()),
            )
        )
        logger.debug(f"{user = }")
        return user
    except StopIteration:
        return None
    except Exception as e:
        logger.info(f"Can't find user: {e}")


async def notify_everyone_user_about_new_vacancy(
    message: Message, state: FSMContext, vacancy_title: str
):
    unhired_users = []
    for record in state.storage.storage.items():
        try:
            # Is private chat and User is not hired
            if getattr(record[0], "chat_id") > 0 and not getattr(
                record[1], "data"
            ).get("is_hired"):
                unhired_users.append(
                    (
                        getattr(record[0], "chat_id"),
                        record[1].data.get("language", "en"),
                    )
                )
        except AttributeError:
            pass
        except Exception as e:
            logger.error("Error notify everyone user about new vacancy: %s", e)

    max_notifications_per_minute = 70  # Telegram limits are 100 per minute

    for user_id, language in unhired_users:
        text = load_locales()["new_vacancy_has_opened_message"][
            language
        ].format(vacancy_title)
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="/start")]],
                    resize_keyboard=True,
                ),
            )
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
        await sleep(60 / max_notifications_per_minute)
