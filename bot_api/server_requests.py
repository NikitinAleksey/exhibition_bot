from typing import List, Dict, Union, Optional

import requests
import json

from bot_api.settings import url


class Request:
    url: str = url
    headers_for_xml: Dict = {'Content-Type': 'application/xml'}
    headers_for_json: Dict = {'Content-type': 'application/json'}

    @classmethod
    def get_files_list(cls, resource: str = 'all_files') -> List:
        needed_url = cls.url + resource
        response = requests.get(url=needed_url)
        file_list = json.loads(response.content)
        return file_list

    @classmethod
    def get_url_to_feed(cls, company_name: str) -> str:
        if not company_name.endswith('xml'):
            company_name += '.xml'
        url = cls.url + company_name
        response = requests.get(url=url)
        if response.status_code == 200:
            return url
        else:
            return f'Файл {company_name} не найден.'

    @classmethod
    def update_feed(cls, company_name: str, data: bytes) -> Optional[str]:
        url = cls.url + company_name
        response = requests.post(url=url, data=data, headers=cls.headers_for_json)
        if response.status_code == 200:
            return f'Файл {company_name} успешно обновлен.'
        else:
            return (f'Обновление не прошло.\n'
                    f'Код ошибки: {response.status_code}')

    @classmethod
    def delete_file(cls, company_name: str):
        if not company_name.endswith('xml'):
            company_name += '.xml'
        data = json.dumps({'company_name': company_name})
        response = requests.delete(url=cls.url, data=data)
        return response.content.decode(encoding='utf-8')


if __name__ == '__main__':
    pass
