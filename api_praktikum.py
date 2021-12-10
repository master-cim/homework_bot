import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import random
import os
import logging
import time
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# updater = Updater(token=TELEGRAM_TOKEN)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}



def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp-(2629743*2)}


    # Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)

    # Печатаем ответ API в формате JSON
    # print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
    list_w = homework_statuses.json()
    i = len(list_w['homeworks'])
    print(i)
    k = 0
    li = []
    while k < i:
        list_hw = list_w["homeworks"][k].get("date_updated")
        update_hw = int(time.mktime(time.strptime(list_hw, '%Y-%m-%dT%H:%M:%SZ')))
        if update_hw > 1637107200:
            list_name_hw = list_w["homeworks"][k].get("homework_name")
            list_status_hw = list_w["homeworks"][k].get("status")
            list_name_hw = dict(homework_name=f'{list_name_hw}', status=f'{list_status_hw}')
            # superhero_dict = {list_name_hw: list_status_hw}
            # dict(right_hand='sword', left_hand='shield')
            li.append(list_name_hw)
        k += 1        
    print(li)
    # datetime_string = '2021-11-28T16:12:29Z'
    # datetime_obj = int(time.mktime(time.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ')))
    # print(datetime_obj)



# def check_response(response):
#     for index in response:
#         list_hw = response["homeworks"][index].get("homework_name")
#     print(list_hw)



get_api_answer(1639054614)