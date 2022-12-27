class GetAPIException(Exception):
    """Создаем свое исключение при сбое запроса к API."""
    pass

class BotNotSend(Exception):
    """Создаем свое исключение при сбое отправки сообщения ботом."""
    pass

class NoHomework(Exception):
    """Создаем свое исключение когда нет домашних работ на проверку."""
    pass