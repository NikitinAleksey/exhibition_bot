import os.path
import sqlite3
from typing import List, Optional, Dict

from log_settings.logger_init import logger


PATH_TO_DB = os.path.join(os.path.dirname(__file__), 'levbov.db')

CREATE_TOKENS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tokens (
    avito_id INTEGER PRIMARY KEY,
       token TEXT,
 FOREIGN KEY (avito_id) REFERENCES customers(avito_id)
)
"""

CREATE_COMMON_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS customers (
                  avito_id INTEGER PRIMARY KEY,
                     title VARCHAR(50) NOT NULL,
                 client_id VARCHAR(50),
             client_secret VARCHAR(50),
     chat_with_client_link VARCHAR(255),
    chat_about_client_link VARCHAR(255),
           google_doc_link VARCHAR(255)
)
"""

CREATE_ADMINS_ID_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY,
  admin_name VARCHAR(100) NOT NULL,
   in_charge BOOL NOT NULL
)
"""

CREATE_OR_UPDATE_TOKEN = """
INSERT OR REPLACE INTO tokens (avito_id, token) VALUES (?, ?)
"""

DELETE_ADMIN_SQL = """
DELETE FROM admins
      WHERE admin_id = ?
"""

DELETE_ADMIN_WITH_NAME_SQL = """
DELETE FROM admins
      WHERE admin_name = ?
        AND in_charge = FALSE
"""

DELETE_COMPANY_SQL = """
DELETE FROM customers
      WHERE title = ?
"""

DELETE_RECORD_FROM_CUSTOMERS_SQL = """
DELETE FROM customers
 WHERE (title = ? AND avito_id = ?) 
    OR (avito_id = ? AND client_id = ?)
    OR (client_id = ? AND title = ?)
"""

INSERT_ADMIN_SQL = """
INSERT INTO admins (admin_id, admin_name, in_charge)
     VALUES (?, ?, ?)
"""

INSERT_RECORD_TO_COMMON_SQL = """
INSERT INTO customers (
            title,
            avito_id,
            client_id,
            client_secret,
            chat_with_client_link,
            chat_about_client_link,
            google_doc_link
            )
     VALUES (?, ?, ?, ?, ?, ?, ?)
"""

INSERT_RECORD_TO_TOKEN_SQL = """
INSERT INTO tokens (
            avito_id,
            token
            )
     VALUES (?, ?)
"""

GET_AVITO_ID_SQL = """
SELECT avito_id
  FROM customers
 WHERE title = ?
"""

GET_COMPANIES_LIST_SQL = """
SELECT title
  FROM customers
"""

GET_INFO_FOR_STATS_SQL = """
SELECT avito_id, client_id, client_secret
  FROM customers
 WHERE title = ?
"""

GET_LINKS_TO_CHATS_AND_DOC_SQL = """
SELECT chat_with_client_link, chat_about_client_link, google_doc_link
  FROM customers
 WHERE title = ?
"""

GET_TOKEN_SQL = """
SELECT token
  FROM tokens
 WHERE avito_id = ?
"""

GET_AVITO_ID_BY_COMPANY_NAME = """
SELECT avito_id
  FROM customers
 WHERE title = ?
"""

GET_ALL_COMPANY_INFO_SQL = """
SELECT * 
  FROM customers
 WHERE title = ?
"""

GET_ADMIN_IDS_LIST = """
SELECT admin_id FROM admins
"""

GET_ADMIN_NAMES_LIST_SQL = """
SELECT admin_name
  FROM admins
"""

GET_IN_CHARGE_ADMIN_IDS_LIST_SQL = """
SELECT admin_id
  FROM admins
 WHERE in_charge = TRUE
"""


def create_table(sql: str):
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)


def insert_record_to_common_table(company_name: str, avito_id: int, client_id: str = None, client_secret: str = None,
                                  chat_with_client: str = None, chat_about_client: str = None,
                                  google_doc_link: str = None) -> None:
    with sqlite3.connect(PATH_TO_DB) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(
            INSERT_RECORD_TO_COMMON_SQL,
            (company_name, avito_id, client_id, client_secret, chat_with_client, chat_about_client,
             google_doc_link))


def insert_record_to_tokens_table(avito_id: int, token: str) -> None:
    with sqlite3.connect(PATH_TO_DB) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(CREATE_OR_UPDATE_TOKEN, (avito_id, token))


def get_avito_id(company_name: str) -> int:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_AVITO_ID_SQL, (company_name,))

    result, *_ = cursor.fetchone()
    return result


def get_info_for_stats(company_name: str) -> tuple:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_INFO_FOR_STATS_SQL, (company_name, ))

    result = cursor.fetchone()
    return result


def get_companies_titles_list() -> List[str]:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_COMPANIES_LIST_SQL)

    result = cursor.fetchall()

    return [company[0] for company in result]


def get_token_from_tokens_table(company_name: str) -> Optional[str]:
    try:
        with sqlite3.connect(PATH_TO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(GET_AVITO_ID_BY_COMPANY_NAME, (company_name, ))
            avito_id, *_ = cursor.fetchone()
            cursor.execute(GET_TOKEN_SQL, (avito_id, ))
        result, *_ = cursor.fetchone()
        return result
    except TypeError as exc:
        logger.warning(msg=f'Ошибка при получении токена из таблицы: {exc}')


def insert_admin(admin_id: int, admin_name: str, in_charge: bool = False) -> None:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(INSERT_ADMIN_SQL, (admin_id, admin_name, in_charge))


def get_admin_names() -> List[str]:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_ADMIN_NAMES_LIST_SQL)
    result = cursor.fetchall()

    return [admin[0] for admin in result]


def delete_company(company_name: str) -> None:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(DELETE_COMPANY_SQL, (company_name, ))


def delete_admin_with_id(admin_id: int) -> None:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(DELETE_ADMIN_SQL, (admin_id, ))


def delete_admin_with_name(admin_name: str) -> bool:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(DELETE_ADMIN_WITH_NAME_SQL, (admin_name, ))
        rows_deleted = cursor.rowcount
        if rows_deleted > 0:
            return True
        return False


def delete_record_from_customers_with_condition(title: str, avito_id: str, client_id) -> bool:
    values_tuple: tuple = (title, avito_id, avito_id, client_id, client_id, title)
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(DELETE_RECORD_FROM_CUSTOMERS_SQL, values_tuple)

    if cursor.rowcount > 0:
        return True
    return False


def get_admin_ids() -> List[int]:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_ADMIN_IDS_LIST)
    result = cursor.fetchall()
    return [admin_id[0] for admin_id in result]


def get_in_charge_admin_ids() -> List[int]:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_IN_CHARGE_ADMIN_IDS_LIST_SQL)
    result = cursor.fetchall()
    return [admin_id[0] for admin_id in result]


def get_all_info_about_company(title: str) -> Optional[Dict]:
    with sqlite3.connect(PATH_TO_DB) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(GET_ALL_COMPANY_INFO_SQL, (title, ))

    result = cursor.fetchone()
    if result:
        try:
            data = dict(result)
            return data
        except Exception as exc:
            logger.warning(msg=f'Ошибка при получении информации о компании из таблицы: {exc}')
            return None


def get_links_to_chats(title: str) -> List:
    with sqlite3.connect(PATH_TO_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(GET_LINKS_TO_CHATS_AND_DOC_SQL, (title,))

    result = list(cursor.fetchone())
    return result


if __name__ == '__main__':
    pass
