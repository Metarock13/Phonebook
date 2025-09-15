from typing import Optional, Iterable

from .model import Contact


class ConsoleView:
    """Консольное представление: взаимодействие через stdin/stdout."""

    def input_text(self, prompt: str) -> str:
        """Запросить ввод у пользователя и вернуть строку.

        Параметры:
        - prompt: подсказка пользователю.
        """
        return input(prompt)

    def print_line(self, text: str = "") -> None:
        """Вывести одну строку в stdout.

        Параметры:
        - text: текст строки (по умолчанию пустая строка).
        """
        if text:
            print(f"\033[32m{text}\033[0m")
        else:
            print("")

    def show_contacts(self, contacts: Iterable[Contact]) -> None:
        """Вывести список контактов; если нет данных — сообщение о пустом списке.

        Параметры:
        - contacts: итерируемая коллекция объектов Contact.
        """
        has_any = False
        for c in contacts:
            self.print_line(f"[{c.id}] {c.name} | {c.phone} | {c.comment}")
            has_any = True
        if not has_any:
            self.print_line("Справочник пуст.")

    def notify(self, message: str) -> None:
        """Вывести нейтральное уведомление.

        Параметры:
        - message: текст уведомления.
        """
        self.print_line(message)

    def error(self, message: str) -> None:
        """Вывести сообщение об ошибке.

        Параметры:
        - message: текст ошибки.
        """
        self.print_line(f"Ошибка: {message}")
