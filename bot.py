import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.chat_action import ChatActionMiddleware

from bot_api.middlewares import CleanerMiddleware
from bot_api.settings import token
from bot_api.handlers import router


TOKEN = token.bot_token.get_secret_value()

dp = Dispatcher()
dp.include_router(router)
dp.callback_query.middleware(CallbackAnswerMiddleware())
dp.message.middleware(ChatActionMiddleware())
dp.message.middleware(CleanerMiddleware())
dp.callback_query.middleware(CleanerMiddleware())


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
