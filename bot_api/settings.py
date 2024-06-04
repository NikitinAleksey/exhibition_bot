import os

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


load_dotenv()


class BotToken(BaseSettings):
    bot_token: SecretStr = os.getenv('BOT_TOKEN', None)


class Url(BaseSettings):
    url: SecretStr = os.getenv('URL', None)


class Folder(BaseSettings):
    folder: SecretStr = os.getenv('TARGET_FOLDER_NAME', None)


token = BotToken()
url = Url()
folder = Folder()


if __name__ == '__main__':
    pass
