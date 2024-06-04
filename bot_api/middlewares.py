from typing import Callable, Dict, Any, Awaitable, Union
import queue

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from log_settings.logger_init import logger


CLEANER_QUEUE: queue.Queue = queue.Queue()


class CleanerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        global CLEANER_QUEUE
        while not CLEANER_QUEUE.empty():
            event_to_be_cleaned = CLEANER_QUEUE.get()
            if isinstance(event_to_be_cleaned, Message):
                if event_to_be_cleaned.text != '/start':
                    try:
                        await event_to_be_cleaned.delete()
                    except Exception as exc:
                        logger.warning(msg=f'Ошибка: {exc}')
        CLEANER_QUEUE.put(event)
        result = await handler(event, data)
        if result:
            CLEANER_QUEUE.put(result)
        return result


if __name__ == '__main__':
    pass
