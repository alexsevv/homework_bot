class GetAPIExceptionError(Exception):
    """Создаем свое исключение при сбое запроса к API."""
    pass

class BotNotSendError(Exception):
    """Создаем свое исключение при сбое отправки сообщения ботом."""
    pass

class NoHomeworkError(Exception):
    """Создаем свое исключение когда нет домашних работ на проверку."""
    pass
