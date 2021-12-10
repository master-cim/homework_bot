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
    """Отправляет сообщение в Telegram чат."""
    i = len(message)
    print(i)
    k = 0
    while k < i:
        print(message[k])
        k += 1
    pass


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp - TEST_TIME}
    # Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    # Печатаем ответ API в формате JSON
    # print(homework_statuses.text)
    # Возвращаем ответ в формате JSON привести к типам данных Python
    return(homework_statuses.json())


def check_response(response):
    """Проверяем ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError('Не получен словарь от API-сервиса')
    if not 'homeworks':
        raise KeyError('Нет ключа homeworks в словаре')
    if type(response['homeworks']) is not list:
        raise TypeError('Зачения ключа homeworks приходят не списком')
    # print(response.get('homeworks'))
    return(response)


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней
        работе статус этой работы."""
    list_w = homework
    i = len(list_w['homeworks'])
    print(i)
    k = 0
    list_change = []
    while k < i:
        list_hw = list_w["homeworks"][k].get("date_updated")
        update_hw = int(time.mktime(
            time.strptime(list_hw, '%Y-%m-%dT%H:%M:%SZ')))
        if update_hw > 1637107200:
            list_name_hw = list_w["homeworks"][k].get("homework_name")
            list_status_hw = list_w["homeworks"][k].get("status")
            verdict = HOMEWORK_STATUSES.get(list_status_hw)
            list_change.append(f'Изменился статус проверки работы "{list_name_hw}".'
                               f'{verdict}')
        k += 1
    return list_change


def check_tokens():
    """Проверяем доступность переменных окружения, 
    которые необходимы для работы программы."""



def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer(current_timestamp)
            for homework in check_response(response):
                send_message(bot, parse_status(homework))
            # if 'current_date' in response:
            #     current_timestamp = response['current_date']
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)
            time.sleep(RETRY_TIME)
        else:
            ...


# if __name__ == '__main__':
#     main()
check_tokens(parse_status(check_response(get_api_answer(1639054614))))
