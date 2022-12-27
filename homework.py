import json
import logging
import os
import sys
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from urllib.error import HTTPError

import requests
import telegram

from dotenv import load_dotenv
from exceptions import GetAPIException, BotNotSend, NoHomework


load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
)
streamHandler.setFormatter(formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(streamHandler)


def check_tokens() -> bool:
    """Проверяет обязательное наличие переменных окружения."""
    logger.info('Все переменные окружение импортированы без ошибок')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def get_api_answer(current_timestamp):
    """Запрос к АПИ Яндекспрактикума."""
    params = {'from_date': current_timestamp}
    logger.info('Начало запроса к API')
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException as error:
        raise GetAPIException(f'Сервер не отвечает : {error}')
    try:
        if homework.status_code != HTTPStatus.OK:
            raise GetAPIException(f'Ответ на запрос к API: {homework.status_code}')
        return homework.json()
    except json.decoder.JSONDecodeError as error:
        raise GetAPIException(f'Проблемы с Json форматом {error}')


def check_response(response):
    """Вызывается из def main(). Проверяет АПИ на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Тип должен быть dict')
    if 'homeworks' not in response:
        raise KeyError('Ключ homeworks не найден')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Список не получили')
    if len(response['homeworks']) > 0:
        logger.info('Список работ получили')
        return response['homeworks'][0]
    else:
        raise NoHomework('Сейчас нет работ на проверке')


def parse_status(homework):
    """Парсинг ответа на запрос."""
    if not isinstance(homework, dict):
        raise TypeError('Тип должен быть dict')
    if len(homework) > 0:
        logger.info('Получили домашнее задание')
    if 'status' not in homework or type(homework) is str:
        raise KeyError('Ключ status отсутствует в homework')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует в homework')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS.keys():
        raise ValueError('Значение не соответствует справочнику статусов')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Телеграмм бот отправляет сообщение в конкретный телеграмм уккаунт."""
    try:
        logger.info('Начало отправки сообщения ботом')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Бот отправил сообщение')
    except Exception as error:
        logger.error(f'Бот сообщение не отправил. Ошибка {error}')
        raise BotNotSend(f'Бот сообщение не отправил. Ошибка {error}')


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    while True:
        try:
            logger.debug('Начало новой иттерации----------------------------------------------')
            if check_tokens():
                bot = telegram.Bot(token=TELEGRAM_TOKEN)
                response = get_api_answer(current_timestamp)
                check_key_homeworks = check_response(response)
                parse_homeworks = parse_status(check_key_homeworks)
                send_message(bot, parse_homeworks)
                current_timestamp = int(time.time())
                time.sleep(RETRY_PERIOD)
            else:
                message = 'Проверить токены. Бот остановлен!'
                logger.critical(message)
                sys.exit(message)
        except Exception as error:
            logger.error(f'Ошибка: {error}')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
