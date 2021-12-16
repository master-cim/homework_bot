import requests
import telegram
import os
import time


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
TELEGRAM_RETRY_TIME = 86400

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Бот отправил сообщение: {message}.')
    except telegram.error.BadRequest as e:
       if e.result.status_code == 403 or e.result.status_code == 400:
           logger.critical('Telegram не может правильно обработать запрос.'
                           f'Ошибка: {e}.')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or time.time()
    last_timestamp = timestamp
    params = {'from_date': last_timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS,
                                     params=params)
    if homework_statuses.status_code != 200:
        raise Exception('API возвращает код, отличный от 200')
    logger.exception
    return(homework_statuses.json())


def check_response(response):
    """Проверяем ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError(f'Не получен словарь от API-сервиса: %s')
    if not 'homeworks':
        raise KeyError('Нет ключа homeworks в словаре')
    if type(response['homeworks']) is not list:
        raise TypeError('Зачения ключа homeworks приходят не списком')
    return(response['homeworks'])


def parse_status(homework):
    """Извлекаем статус домашней работы."""
    work = homework
    name_hw = work["homework_name"]
    status_hw = work["status"]
    if status_hw in HOMEWORK_STATUSES.keys():
        verdict = HOMEWORK_STATUSES.get(status_hw)
        change = f'Изменился статус проверки работы "{name_hw}".{verdict}'
    else:
        message = f'Неизвестный статус работы - {status_hw}'
        logger.error(message)
        raise TypeError(message)
    return change


def check_tokens():
    """Проверяем доступность переменных окружения."""
    if (TELEGRAM_TOKEN is not None
            and TELEGRAM_CHAT_ID is not None
            and PRACTICUM_TOKEN is not None):
        logger.info('Переменные окружения установлены.')
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - TELEGRAM_RETRY_TIME
    check_tokens()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if not homework:
                logger.debug('Нет обновлений')
            else:
                for work in homework:
                    update_hw = int(time.mktime(
                        time.strptime(work["date_updated"],
                                      '%Y-%m-%dT%H:%M:%SZ')))
                    if update_hw > current_timestamp:
                        send_message(bot, parse_status(work))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)
            time.sleep(TELEGRAM_RETRY_TIME)
        else:
            time.sleep(TELEGRAM_RETRY_TIME)


if __name__ == '__main__':
    main()
