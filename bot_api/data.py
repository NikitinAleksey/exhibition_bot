from copy import copy
from typing import List, Dict
import queue

from bot_api.server_requests import Request
from database.db import get_companies_titles_list


class Companies:
    title: str = 'Выберите компанию: '
    _buttons: List[str] = []
    _callbacks: List[str] = []

    @classmethod
    def update_buttons(cls):
        cls._buttons = get_companies_titles_list()
        cls._buttons.append('⬅️ Назад')
        return cls._buttons

    @classmethod
    def update_callbacks(cls):
        cls._callbacks = cls._buttons[:-1]
        cls._callbacks.append('employee')
        return cls._callbacks


class RequestObject:
    make_a_choice: str = 'Выберите файл:'
    delete_file: str = 'Выберите файл для удаления:'
    file_link: str = 'Ссылка на файл {}: '
    _buttons: List[str] = []
    _callbacks: List[str] = []

    @classmethod
    def update_buttons(cls):
        cls._buttons = Request().get_files_list()
        cls._buttons.append('⬅️ Назад')
        return cls._buttons

    @classmethod
    def update_callbacks(cls):
        cls._callbacks = cls._buttons[:-1]
        cls._callbacks.append('employee')
        return cls._callbacks


class CompanyInfo:
    info_list: queue = queue.Queue()
    is_correct: str = 'Введенные данные верны?\n'
    buttons = ['Да', 'Нет']
    callbacks = copy(buttons)
    info_dict: Dict = {}

    @classmethod
    def string_repr(cls) -> str:
        result = {}
        while not cls.info_list.empty():
            part = cls.info_list.get()
            result.update(part)
            cls.info_dict.update(part)
        answer = cls.is_correct + '\n'.join([f'{key}: {value}' for key, value in result.items()])
        return answer

    @classmethod
    def validate_avito_id(cls, avito_id: str):
        if avito_id.isnumeric():
            return True
        return False


if __name__ == '__main__':
    pass
