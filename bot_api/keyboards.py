from typing import List, Union, Callable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from bot_api.data import RequestObject, Companies


class KeyboardManager:
    def __init__(
            self,
            buttons: Union[List[str], Callable] = None,
            callbacks: Union[List[str], Callable] = None,
            dynamic_data: bool = False
    ):
        self.buttons = buttons
        self.callbacks = callbacks
        self.dynamic_data = dynamic_data

    def create_inline_keyboard(self) -> InlineKeyboardMarkup:
        if self.dynamic_data:
            self.buttons = self.buttons()
            self.callbacks = self.callbacks()
        buttons = [
            [InlineKeyboardButton(text=button, callback_data=callback)]
            for button, callback in zip(self.buttons, self.callbacks)
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def create_reply_keyboard(self) -> ReplyKeyboardMarkup:
        keyboards = [
            [KeyboardButton(text=button)] for button in self.buttons
        ]
        return ReplyKeyboardMarkup(keyboard=keyboards)


def creating_kb_with_request() -> KeyboardManager:
    keyboard = KeyboardManager(
        buttons=RequestObject.update_buttons,
        callbacks=RequestObject.update_callbacks,
        dynamic_data=True
    )

    return keyboard


def creating_kb_with_db_companies_list() -> KeyboardManager:
    keyboard = KeyboardManager(
        buttons=Companies.update_buttons,
        callbacks=Companies.update_callbacks,
        dynamic_data=True
    )

    return keyboard


if __name__ == '__main__':
    pass
