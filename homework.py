import requests
import telegram
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import os
import sys
import time
from http import HTTPStatus
from os import environ


from dotenv import load_dotenv

import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000,
                              backupCount=5, encoding="UTF-8")
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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
    """Отправляет сообщение в Telegram чат."""
    list_messages = message
    chat_id = TELEGRAM_CHAT_ID
    for text in list_messages:
        bot.send_message(chat_id, text)
        logger.info(f'Бот отправил сообщение: {text}.')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or time.time()
    last_timestamp = timestamp
    params = {'from_date': last_timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if homework_statuses.status_code != 200:
        raise Exception('API возвращает код, отличный от 200')
    logger.exception
    return(homework_statuses.json())


def check_response(response):
    """Проверяем ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError('Не получен словарь от API-сервиса: %s')
    if not 'homeworks':
        raise KeyError('Нет ключа homeworks в словаре')
    if type(response['homeworks']) is not list:
        raise TypeError('Зачения ключа homeworks приходят не списком')
    return(response)


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней
        работе статус этой работы."""
    list_w = homework.get('homeworks')
    list_change = []
    last_timestamp = int(time.time()) - RETRY_TIME
    for work in list_w:
        list_hw = work.get("date_updated")
        update_hw = int(time.mktime(
            time.strptime(list_hw, '%Y-%m-%dT%H:%M:%SZ')))
        if update_hw > last_timestamp:
            list_name_hw = work.get("homework_name")
            list_status_hw = work.get("status")
            if list_status_hw in HOMEWORK_STATUSES.keys():
                verdict = HOMEWORK_STATUSES.get(list_status_hw)
                list_change.append(
                    f'Изменился статус проверки работы "{list_name_hw}".'
                    f'{verdict}')
            else:
                message = f'Неизвестный статус работы - {list_status_hw}'
                logger.error(message)
    return list_change


def check_tokens():
    """Проверяем доступность переменных окружения, 
    которые необходимы для работы программы."""
    key_value = ('TELEGRAM_TOKEN',
                 'PRACTICUM_TOKEN',
                 'TELEGRAM_CHAT_ID')
    for key in key_value:
        if environ.get('key') is not None:
            logger.info(f'Переменная окружения {key} установлена.')
        else:
            Exception(
                f'Отсутствует обязательная переменная окружения: {key}'
                ' Программа принудительно остановлена')
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {key}. '
                'Программа принудительно остановлена.'
            )
            SystemExit: 1


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    empty_list = []
    while True:
        try:
            check_tokens()
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            print(homework)
            if homework['homeworks'] == empty_list:
                logger.debug('Нет обновлений')
            else:
                send_message(bot, parse_status(homework))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
