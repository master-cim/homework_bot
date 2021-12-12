import requests
import telegram
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import os
import sys
import time

from dotenv import load_dotenv

import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000,
                              backupCount=5, encoding = "UTF-8")
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)

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
    list_messages = message
    chat_id = TELEGRAM_CHAT_ID
    for text in list_messages:
        bot.send_message(chat_id, text)
        logger.info(f'Бот отправил сообщение: {text}.')


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
        raise TypeError('Не получен словарь от API-сервиса: %s')
    logging.raiseExceptions = True
    if not 'homeworks':
        raise KeyError('Нет ключа homeworks в словаре')
    logging.raiseExceptions =True
    if type(response['homeworks']) is not list:
        raise TypeError('Зачения ключа homeworks приходят не списком')
    logging.raiseExceptions =True
    return(response)


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней
        работе статус этой работы."""
    list_w = homework['homeworks']
    list_change = []
    for homework in list_w:
        list_hw = homework.get("date_updated")
        update_hw = int(time.mktime(
            time.strptime(list_hw, '%Y-%m-%dT%H:%M:%SZ')))
        if update_hw > 1637107200:
            list_name_hw = homework.get("homework_name")
            list_status_hw = homework.get("status")
            verdict = HOMEWORK_STATUSES.get(list_status_hw)
            list_change.append(
                f'Изменился статус проверки работы "{list_name_hw}".'
                f'{verdict}')
    return list_change


def check_tokens():
    """Проверяем доступность переменных окружения, 
    которые необходимы для работы программы."""
    key_value = ('TELEGRAM_TOKEN',
                 'PRACTICUM_TOKEN',
                 'TELEGRAM_CHAT_ID')
    for key in key_value:
        try:
            os.environ[key]
            logger.info(f'Переменная окружения {key} установлена.')
        except NameError:
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {key}. '
                'Программа принудительно остановлена.'
            )
            sys.exit(1)


def main():
    """Основная логика работы бота."""
# подключим токен бота
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    # updater = Updater(token=TELEGRAM_TOKEN)
    while True:
        try:
            check_tokens()
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            send_message(bot, parse_status(homework))
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)
            time.sleep(RETRY_TIME)
        else:
            break
#     updater.dispatcher.add_handler(CommandHandler('start', wake_up))
#     updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
#     updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
#     # Метод start_polling() запускает процесс polling, 
#     # приложение начнёт отправлять регулярные запросы для получения обновлений.
#     updater.start_polling(poll_interval=RETRY_TIME)
#     # Бот будет работать до тех пор, пока не нажмете Ctrl-C
#     updater.idle() 
#     pass

if __name__ == '__main__':
    main()
