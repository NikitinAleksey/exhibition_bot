import json
from typing import Dict, List, Literal, Union

import requests

from database.db import get_token_from_tokens_table, get_info_for_stats, insert_record_to_tokens_table, get_avito_id
from log_settings.logger_init import logger


SCOPES = [
    'items:info'
]
HEADERS = {
    'Authorization':
        'Bearer {token}',
    'Content-Type': 'application/json'
}
HEADERS_TO_GET_TOKEN = {'Content-Type': 'application/x-www-form-urlencoded'}

URL_TO_GET_TOKEN = 'https://api.avito.ru/token/'
URL_TO_ITEM = 'https://api.avito.ru/core/v1/accounts/{user_id}/items/{item_id}/'
URL_TO_ITEMS = 'https://api.avito.ru/core/v1/items'
URL_TO_ITEMS_STATS = 'https://api.avito.ru/stats/v1/accounts/{user_id}/items'
URL_TO_AUTOLOAD_GET_LAST_COMPLETED_REPORT = 'https://api.avito.ru/autoload/v2/reports/last_completed_report'

DATA_TO_GET_TOKEN = {
    'grant_type': 'client_credentials'
}


def get_updated_token(client_id: str, client_secret: str):
    data = DATA_TO_GET_TOKEN
    data['client_id'] = client_id
    data['client_secret'] = client_secret
    response = requests.post(URL_TO_GET_TOKEN, headers=HEADERS_TO_GET_TOKEN, data=data)
    content: Dict = json.loads(response.content)
    return content.get('access_token')


def get_items_list_info(company_name: str) -> Dict:
    token = get_token_from_tokens_table(company_name=company_name)
    headers = {
        'Authorization':
            f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=URL_TO_ITEMS, headers=headers)
    data = json.loads(response.content)

    if response.status_code == 200:
        return data
    elif response.status_code == 403:
        avito_id, client_id, client_secret = get_info_for_stats(company_name=company_name)
        new_token = get_updated_token(client_id=client_id, client_secret=client_secret)
        insert_record_to_tokens_table(avito_id=avito_id, token=new_token)

        return get_items_list_info(company_name=company_name)
    else:
        logger.info(msg=f'Неизвестный доселе код ответа: {response.status_code}')


def get_item_info(item_id: int, user_id: int):
    response = requests.get(url=URL_TO_ITEM.format(user_id=user_id, item_id=item_id), headers=HEADERS)
    return response.content


def get_items_id(company_name: str) -> List[int]:
    data = get_items_list_info(company_name=company_name)
    try:
        id_list = [item_info.get('id') for item_info in data.get('resources')]
        return id_list
    except Exception as exc:
        logger.info(msg=f'Ошибка: {exc}')


def get_items_stats(company_name: str, date_from: str, date_to: str, period: Literal['week', 'month', 'year']) \
        -> Union[Dict, str]:
    user_id = get_avito_id(company_name=company_name)
    items_ids = get_items_id(company_name=company_name)
    token = get_token_from_tokens_table(company_name=company_name)
    headers = HEADERS
    headers['Authorization'] = headers['Authorization'].format(token=token)
    data = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "fields": [
            "uniqViews", "uniqContacts", "uniqFavorites"
        ],
        "itemIds": items_ids,
        "periodGrouping": period
    }
    dump_data = json.dumps(data)
    response = requests.post(url=URL_TO_ITEMS_STATS.format(user_id=user_id), data=dump_data, headers=HEADERS)
    if response.status_code == 200:
        response = json.loads(response.content)
        return response.get('result').get('items')
    elif response.status_code == 403:
        avito_id, client_id, client_secret = get_info_for_stats(company_name=company_name)
        new_token = get_updated_token(client_id=client_id, client_secret=client_secret)
        insert_record_to_tokens_table(avito_id=avito_id, token=new_token)

        return get_items_stats(company_name=company_name, date_from=date_from, date_to=date_to, period=period)
    else:
        return response.content.decode(encoding='utf-8')


def insert_updated_token_to_db(company_name: str) -> None:
    avito_id, client_id, client_secret = get_info_for_stats(company_name=company_name)
    new_token = get_updated_token(client_id=client_id, client_secret=client_secret)
    insert_record_to_tokens_table(avito_id=avito_id, token=new_token)


def get_autoload_last_completed_report(company_name: str) -> Dict:
    token = get_token_from_tokens_table(company_name=company_name)
    headers = {'Authorization': f'Bearer {token}'}
    url = URL_TO_AUTOLOAD_GET_LAST_COMPLETED_REPORT
    response = requests.get(url=url, headers=headers)
    data = json.loads(response.content)
    if response.status_code == 200:
        return data
    elif response.status_code == 403:
        try:
            insert_updated_token_to_db(company_name=company_name)
            return get_autoload_last_completed_report(company_name=company_name)
        except Exception as exc:
            logger.info(msg=f'Ошибка: {exc}')


if __name__ == '__main__':
    pass
