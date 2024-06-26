# Exhibition TG bot

## Описание

Данный бот был создан для автоматизации работы с автозагрузкой на Авито. Он помогает быстро
парсить данные из нужного вам Google Sheet, чтобы создать из него XML-файл, который будет храниться на сервере.
Без аккаунта на Авито с оплаченным тарифом бот не сможет получать статистику за определенный период.
Кроме того, так как проект был написан после того, как был написан сервер, то для работы с Авито необходимо использовать
еще и сервер (его я не выкладывал на гитхаб).

По этим причинам данного бота нельзя использовать автономно, он нужен для оценки моего кода и знаний, и
подходит лишь для ознакомления. Поэтому все тонкости и нюансы по установке опущены, но оставлены общие настройки.

## Настройка

### Google Cloud API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/).
2. Создайте новый проект, если у вас его ещё не было.
3. Войдите в проект и нажмите "IAM & Admin", затем выберите "Service accounts".
4. Создайте новую учетную запись службы и даёте ей подходящие разрешения для вашего бота.
5. Перейдите на вкладку "Keys", затем добавьте новый ключ, выберите тип ключа "JSON".
6. Скачайте json и сохраните его в [google_drive_api](google_drive_api).

### Настройка .env файла

Создайте файл с именем `.env` в корне вашего проекта. Заполните файл следующим образом:

```
BOT_TOKEN = 'ваш токен бота'
URL= 'HOST:PORT сервера с реализованным функционалом'
TARGET_FOLDER_NAME='ID папки с вашими гугл листами'
```

### Установка зависимостей

Выполните pip install requirements.txt 
Это не обязательно, если вы будете использовать докер.


### Инициализация базы данных

В первую очередь вам потребуется инициализировать вашу базу данных, добавив пользователя с Telegram ID. 
Инициализация произойдет при первом запуске, однако, так как база пустая, то вас не пропустит в 
административную часть. Поэтому после первого запуска бота нужно подключиться к вашей бд
(она будет лежать в модуле [database](database)), и внести себя в таблицу админов. Потребуется ваш Telegram ID и имя.
После внесения изменений можно запускать бота.


## Запуск бота

Убедитесь, что все переменные конфигурации и зависимости установлены правильно. Затем запустите бота, используя следующую команду: `python3 bot.py`,
или можете использовать докер (для этого написан [Dockerfile](Dockerfile))

