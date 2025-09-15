from pathlib import Path
from typing import Optional

from .exceptions import PhonebookError, ContactNotFound, ValidationError
from .model import Phonebook
from .storage import TxtStorage
from .view import ConsoleView


class PhonebookController:
    """Контроллер приложения, связывающий представление, модель и хранилище.

    Управляет меню, обрабатывает ошибки и координирует загрузку/сохранение.
    """

    def __init__(self, view: ConsoleView, model: Phonebook) -> None:
        """Инициализация контроллера.

        Параметры:
        - view: экземпляр представления для ввода/вывода.
        - model: экземпляр модели (справочника).
        """
        self._view = view
        self._model = model
        self._opened_path: Optional[Path] = None

    def _open(self) -> None:
        """Открыть .txt-файл и загрузить контакты в модель."""
        path_str = self._view.input_text("Введите путь к файлу (.txt): ")
        path = Path(path_str).expanduser().resolve()
        if path.suffix.lower() != ".txt":
            self._view.error("Поддерживается только .txt")
            return
        storage = TxtStorage(path)
        try:
            contacts = storage.load()
            self._model.replace_all(contacts)
            self._opened_path = path
            self._view.notify(f"Загружено контактов: {len(contacts)} из '{path}'.")
        except PhonebookError as e:
            self._view.error(str(e))

    def _save(self) -> None:
        """Сохранить модель в .txt-файл (спросит путь при первом сохранении)."""
        if not self._opened_path:
            path_str = self._view.input_text("Введите путь для сохранения (.txt): ")
            self._opened_path = Path(path_str).expanduser().resolve()
        if self._opened_path.suffix.lower() != ".txt":
            self._view.error("Поддерживается только .txt")
            return
        storage = TxtStorage(self._opened_path)
        try:
            storage.save(self._model.list())
            self._model.mark_clean()
            self._view.notify(f"Сохранено в '{self._opened_path}'.")
        except PhonebookError as e:
            self._view.error(str(e))

    def _list(self) -> None:
        """Показать все контакты."""
        self._view.show_contacts(self._model.list())

    def _create(self) -> None:
        """Создать новый контакт на основе ввода пользователя.

        Запрашивает имя, телефон и комментарий, валидирует и добавляет в модель.
        """
        name = self._view.input_text("Имя: ").strip()
        phone = self._view.input_text("Телефон: ").strip()
        comment = self._view.input_text("Комментарий: ").strip()
        try:
            contact = self._model.add(name=name, phone=phone, comment=comment)
            self._view.notify(f"Добавлен контакт [{contact.id}].")
        except ValidationError as e:
            self._view.error(str(e))

    def _ask_id(self) -> Optional[int]:
        """Запросить у пользователя id контакта.

        Возвращает: целочисленный id или None при неверном вводе.
        """
        raw = self._view.input_text("Введите ID контакта: ").strip()
        if not raw.isdigit():
            self._view.error("Некорректный ID.")
            return None
        return int(raw)

    def _find(self) -> None:
        """Выполнить поиск: по свободной строке или по фильтрам полей.

        Запрашивает один общий запрос или отдельные подстроки для полей.
        """
        self._view.notify("Поиск: можно ввести либо общий запрос, либо оставить пустым и указать поля.")
        q = self._view.input_text("Общий запрос (Enter чтобы пропустить): ").strip()
        if q:
            results = self._model.search(q)
        else:
            name = self._view.input_text("Имя содержит (Enter чтобы пропустить): ").strip()
            phone = self._view.input_text("Телефон содержит (Enter чтобы пропустить): ").strip()
            comment = self._view.input_text("Комментарий содержит (Enter чтобы пропустить): ").strip()
            results = self._model.search_by_fields(name=name, phone=phone, comment=comment)
        if not results:
            self._view.notify("Ничего не найдено.")
            return
        self._view.show_contacts(results)

    def _edit(self) -> None:
        """Изменить поля существующего контакта по вводу пользователя."""
        cid = self._ask_id()
        if cid is None:
            return
        try:
            existing = self._model.get(cid)
        except ContactNotFound as e:
            self._view.error(str(e))
            return
        self._view.notify(f"Оставьте поле пустым, чтобы оставить: {existing.name} | {existing.phone} | {existing.comment}")
        name = self._view.input_text("Имя: ").strip()
        phone = self._view.input_text("Телефон: ").strip()
        comment = self._view.input_text("Комментарий: ").strip()
        try:
            self._model.update(cid, name=None if name == "" else name, phone=None if phone == "" else phone, comment=None if comment == "" else comment)
            self._view.notify("Контакт обновлён.")
        except PhonebookError as e:
            self._view.error(str(e))

    def _delete(self) -> None:
        """Удалить контакт по id."""
        cid = self._ask_id()
        if cid is None:
            return
        try:
            self._model.delete(cid)
            self._view.notify("Контакт удалён.")
        except ContactNotFound as e:
            self._view.error(str(e))

    def _maybe_prompt_save(self) -> bool:
        """Спросить о сохранении при наличии несохранённых изменений.

        Возвращает: True — можно выходить; False — остаться в приложении.
        """
        if not self._model.dirty:
            return True
        ans = self._view.input_text("Есть несохранённые изменения. Сохранить? (y/n): ").strip().lower()
        if ans in ("y", "yes", "д", "да"):
            self._save()
            return True
        if ans in ("n", "no", "н", "нет"):
            return True
        return False

    def run(self) -> None:
        """Главный цикл приложения с условием выхода."""
        actions = {
            "1": self._open,
            "2": self._save,
            "3": self._list,
            "4": self._create,
            "5": self._find,
            "6": self._edit,
            "7": self._delete,
            "8": None,
        }
        choice: Optional[str] = None
        while choice != "8":
            self._view.print_line()
            self._view.print_line("Телефонный справочник")
            self._view.print_line("1. Открыть файл")
            self._view.print_line("2. Сохранить файл")
            self._view.print_line("3. Показать все контакты")
            self._view.print_line("4. Создать контакт")
            self._view.print_line("5. Найти контакт")
            self._view.print_line("6. Изменить контакт")
            self._view.print_line("7. Удалить контакт")
            self._view.print_line("8. Выход")
            choice = self._view.input_text("Выберите пункт меню: ").strip()
            if choice == "8":
                if self._maybe_prompt_save():
                    self._view.notify("До свидания!")
                    break
                choice = None
                continue
            action = actions.get(choice)
            if action is None:
                self._view.error("Неизвестный пункт меню. Повторите ввод.")
                continue
            try:
                action()
            except PhonebookError as e:
                self._view.error(str(e))
            except KeyboardInterrupt:
                self._view.print_line("\nОперация отменена пользователем.")
