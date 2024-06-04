from aiogram.filters.state import State, StatesGroup


class Statements(StatesGroup):
    # Состояния команд
    MAIN_MENU = State()
    EMPLOYEE_MENU = State()

    # Ждем выбор клиента
    WAITING_CUSTOMER_CHOICE = State()

    # Ждем выбор действия в меню клиента
    WAITING_CUSTOMER_MENU_CHOICE = State()

    # Ждем выбор выборки для статистики
    WAITING_STATISTIC_PERIOD = State()
    WAITING_FOR_DATE_FROM = State()
    WAITING_FOR_DATE_TO = State()
    THE_CHOICE_IS_MADE = State()

    # Добавление нового клиента
    WAITING_FOR_TITLE = State()
    WAITING_FOR_AVITO_ID = State()
    WAITING_FOR_CLIENT_ID = State()
    WAITING_FOR_CLIENT_SECRET = State()
    WAITING_FOR_CHAT_WITH_CLIENT = State()
    WAITING_FOR_CHAT_ABOUT_CLIENT = State()
    WAITING_FOR_GOOGLE_DOC_LINK = State()
    GOT_ALL_CLIENT_INFO = State()

    # Удаление клиента
    WAITING_FOR_CLIENT_TO_DELETE = State()

    # Изменение клиента
    WAITING_FOR_CLIENT_TO_EDIT = State()
    WAITING_FOR_FIELD_TO_EDIT = State()
    WAITING_FOR_ATTRIBUTE_TO_EDIT = State()

    # Меню админа
    WAITING_FOR_ADMIN_ACTION = State()
    WAITING_FOR_NEW_ADMIN_NAME = State()
    WAITING_FOR_NEW_ADMIN_TG_ID = State()
    WAITING_FOR_ADMIN_TO_DELETE = State()


if __name__ == '__main__':
    pass
