import io
import os.path
from typing import List, Optional
from queue import Queue

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

from log_settings.logger_init import logger
from bot_api.settings import folder


API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
TARGET_FOLDER_NAME = folder
MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
JSON_FILE = os.path.abspath(os.path.join('project-for-exhibition-bot-54bcd9716d4c.json'))

result_queue = Queue()


def authenticate_google_drive_api():
    credentials = service_account.Credentials.from_service_account_file(
        filename=JSON_FILE,
        scopes=SCOPES,
    )

    if credentials.expired:
        credentials.refresh(Request())

    return credentials


def get_drive_file_by_name(credentials, target_folder_name, file_name) -> Optional[List]:

    service = build(API_NAME, API_VERSION, credentials=credentials)
    query = f"name contains '{file_name}' and '{target_folder_name}' in parents"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    file = results.get('files', [])

    return file if file else None


def get_file_content(credentials, file: dict):
    service = build(API_NAME, API_VERSION, credentials=credentials)
    try:
        request = service.files().get_media(fileId=file.get('id'))
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        file_content = file_stream.getvalue()
        return file_content

    except Exception as exc:
        logger.warning(msg=f'Файл нельзя загрузить методом get_media: {exc}')
        if 'fileNotDownloadable' in str(exc):
            try:
                request = service.files().export_media(
                    fileId=file.get('id'),
                    mimeType=MIME_TYPE)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                file_content = file_stream.getvalue()
                return file_content
            except Exception as exc:
                logger.warning(msg=f'Ошибка при использовании export_media для файла {file.get("name")}: {str(exc)}')


def run_file_updating(file_name: str) -> Optional[bytes]:
    credentials = authenticate_google_drive_api()

    file = get_drive_file_by_name(
        credentials=credentials, target_folder_name=TARGET_FOLDER_NAME, file_name=file_name
    )

    if file:
        file_content = get_file_content(credentials=credentials, file=file[0])
        return file_content
    else:
        return None


if __name__ == '__main__':
    authenticate_google_drive_api()
