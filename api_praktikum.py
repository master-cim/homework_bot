import requests
import os

from dotenv import load_dotenv

load_dotenv()
secret_token = os.getenv('TOKEN')

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {secret_token}'}
payload = {'from_date': 1639054614-(2629743*2)}

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)

# Печатаем ответ API в формате JSON
print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
# print(homework_statuses.json())
