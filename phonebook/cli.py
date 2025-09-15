"""Запуск (bootstrap) MVC-приложения телефонного справочника."""

from .controller import PhonebookController
from .model import Phonebook
from .view import ConsoleView


def run() -> None:
    """Собрать компоненты MVC и запустить цикл контроллера."""
    controller = PhonebookController(view=ConsoleView(), model=Phonebook())
    controller.run()
