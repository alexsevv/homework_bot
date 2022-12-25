import json
import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()
PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str  = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: int =  os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


# Здесь задана глобальная конфигурация для всех логгеров
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens() -> bool:
    """Проверяет обязательное наличие переменных окружения."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.critical(
            'Проверить наличие переменных PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID')
        return False
    logger.info('Все переменные окружение импортированы без ошибок')
    return True


def get_api_answer(current_timestamp) -> dict:
    """Запрос к АПИ Яндекспрактикума для получения информации о домашней работе"""
    params = {'from_date': current_timestamp}
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if homework.status_code == HTTPStatus.OK:
            logger.info('Статус 200')
            return homework.json()
    except requests.RequestException as error:
        logger.error(f'Ошибка урла {error}')
    except json.decoder.JSONDecodeError as error:
        logger.error(f'Проблемы с Json форматом {error}')
    if homework.status_code != HTTPStatus.OK:
        logger.error('Сервер не отвечает')
        raise Exception('Сервер не отвечает')


def check_response(response):
    """Вызывается из def main(). Проверяет АПИ на корректность."""
    if not isinstance(response, dict):
        logger.warning('Тип должен быть dict')
        raise TypeError('Тип должен быть dict')
    if 'homeworks' not in response:
        logger.warning('Ключ homeworks не найден')
        raise KeyError('Ключ homeworks не найден')
    if not isinstance(response['homeworks'], list):
        logger.warning('Список не получили')
        raise TypeError('Список не получили')
    if len(response) > 0 or len(response) == 0:
        logger.info('Список работ получили')
        return response['homeworks'][0]
        

def parse_status(homework):
    """Парсинг ответа на запрос."""
    if 'status' not in homework or type(homework) is str:
        logger.error('Ключ status отсутствует в homework')
        raise KeyError('Ключ status отсутствует в homework')
    if 'homework_name' not in homework:
        logger.error('Ключ homework_name отсутствует в homework')
        raise KeyError('Ключ homework_name отсутствует в homework')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS.keys():
        raise ValueError('Значение не соответствует справочнику статусов')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    

def send_message(bot, message):
    """Телеграмм бот отправляет сообщение в конкретный телеграмм уккаунт"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Бот отправил сообщение')
    except Exception as error:
        logger.error(f'Бот сообщение не отправил. Проверь TELEGRAM_CHAT_ID и TELEGRAM_TOKEN. Ошибка {error}')



def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    #current_timestamp = 1669951537 # для отладки Fri Dec 02 2022 03:25:37 GMT+0000
    while True:
        try:
            if check_tokens():
                response = get_api_answer(current_timestamp)
                check_key_homeworks = check_response(response)
                parse_homeworks = parse_status(check_key_homeworks)
                send_message(bot, parse_homeworks)
                time.sleep(RETRY_PERIOD)   
        except Exception as error:
            logger.error(f'Что-то не так: {error}')
            time.sleep(RETRY_PERIOD)
        else:
            break

if __name__ == '__main__':
    main()
