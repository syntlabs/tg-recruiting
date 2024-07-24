from os import getenv
from logging import basicConfig, getLogger, INFO
from json import load as json_load
from asyncio import run

from aiogram import Bot, Dispatcher

from utils import load_storage, save_storage
from routers import router as main_router
from handlers.callback_query import router as callback_query_router


logger = getLogger(__name__)
BOT_TOKEN = getenv("BOT_TOKEN")
storage = None


with open("/usr/src/app/locales.json", encoding="utf-8") as f:
    locales = json_load(f)


async def main():
    global storage
    storage = load_storage()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_routers(callback_query_router, main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO)
    try:
        run(main())
    except Exception as e:
        logger.critical("BOT STOPPED: %s", e)

        save_storage(storage)
