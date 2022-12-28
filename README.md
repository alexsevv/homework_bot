# Telegram bot для проверки статуса домашней работы на ЯндексПрактикуме.


- Telegram bot с помощью которого можно проверить статус домашней работы на ЯндексПрактикуме.
- Бот Каждые 10 минут дергает API ЯндексПрактикума и проверяет стутус домашней работы, отправленной на ревью.
- Если работу проверили, бот пришлет пользывателю в Telegram сообщение с результатот проверки.

Весь процесс работы логгируется с ошибками и исключениями.

## Технологии
- Python 3.7+
- Telegram Bot API
- Pytest


## Как запустить проект:

1. Kлонируем репозиторий:
```
git clone 
```
2. Cоздаем виртуальную среду:
```
python3 -m venv venv
```
3. Активируем виртуальную среду:
```
source venv/bin/activate
```
4. Устанавливаем зависимости:
```
pip install -r requirements.txt   #устанавливаем зависимости
```
5. Создаем файл .env в директории с проектом и указываем собственные токены:

```
PRACTICUM_TOKEN = токен Яндекс практикум.
TELEGRAM_TOKEN = токен вашего бота Telegram полученный от BotFather.
TELEGRAM_CHAT_ID = id вашего чата в Telegram.
```

### Как получить токены:

1. ```PRACTICUM_TOKEN``` - <a href="https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a" target="_blank">Получить токен</a>.
2. ```TELEGRAM_TOKEN``` - Зарегистрируйте бота в BotFather: <a href="https://t.me/BotFather" target="_blank">Регистрация бота и получение токена</a>.
3. ```TELEGRAM_CHAT_ID``` - Получите id своего чата у бота Userinfobot:<br>
<a href="https://t.me/userinfobot" target="_blank">Получить свой id</a>

### Автор
- [Александр Матияка](https://github.com/alexsevv)