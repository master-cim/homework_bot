import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import random
import os
import logging
import time

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
updater = Updater(token=TELEGRAM_TOKEN)

RETRY_TIME = 600
TEST_TIME = 2629743 # один месяц
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    if 'current_date' in response:
        current_timestamp = response['current_date']
    ...


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp-TEST_TIME}
    # Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)

    # Печатаем ответ API в формате JSON
    print(homework_statuses.text)
    
    # Возвращаем ответ в формате JSON привести к типам данных Python
    return(homework_statuses.json())


def check_response(response):

    pass


def parse_status(homework):
    """Извлечение статуса домашней работы.""" 
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status') 
    if 'homework_name' not in homework:
        raise NoHwNameError('Отсутствует ключ homework_name')
    if 'status' not in homework:
        raise NoHwStatusError[(['Отсутствует ключ homework_status'])
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise HwStatusError('Недокументированный статус')
    elif homework_status == 'approved':
        verdict = HOMEWORK_STATUSES.get('approved')
    elif homework_status == 'reviewing':
        verdict = HOMEWORK_STATUSES.get('reviewing')
    elif homework_status == 'rejected':
        verdict = HOMEWORK_STATUSES.get('rejected')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ...


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
