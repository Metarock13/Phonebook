from dataclasses import dataclass
from typing import List, Dict, Optional
import re

from .exceptions import ValidationError, ContactNotFound


_PHONE_REGEX = re.compile(r"^[+\d][\d\- ()]{5,}$")


def _validate_name(name: str) -> str:
    """Проверка и нормализация имени контакта.

    Параметры:
    - name: исходное имя.

    Возвращает нормализованное имя.
    Бросает ValidationError, если имя пустое.
    """
    name_clean = (name or "").strip()
    if not name_clean:
        raise ValidationError("Имя не может быть пустым")
    return name_clean


def _validate_phone(phone: str) -> str:
    """Проверка и нормализация телефона.

    Параметры:
    - phone: исходная строка телефона.

    Допустимы: цифры, пробелы, дефисы, скобки и ведущий '+'.
    Возвращает нормализованную строку телефона.
    Бросает ValidationError при несоответствии.
    """
    phone_clean = (phone or "").strip()
    if not _PHONE_REGEX.match(phone_clean):
        raise ValidationError("Телефон некорректен. Разрешены цифры, пробелы, дефисы, скобки и ведущий '+'.")
    return phone_clean


@dataclass
class Contact:
    """Сущность контакта телефонного справочника."""

    id: int
    name: str
    phone: str
    comment: str = ""


class Phonebook:
    """Памятное (in-memory) хранилище контактов с авто-ID, валидацией и поиском."""

    def __init__(self) -> None:
        self._contacts: Dict[int, Contact] = {}
        self._next_id: int = 1
        self._dirty: bool = False

    @property
    def dirty(self) -> bool:
        """True — есть несохранённые изменения."""
        return self._dirty

    def mark_clean(self) -> None:
        """Пометить текущее состояние как сохранённое (чистое)."""
        self._dirty = False

    def _mark_dirty(self) -> None:
        """Пометить состояние как изменённое."""
        self._dirty = True

    def replace_all(self, contacts: List[Contact]) -> None:
        """Полностью заменить содержимое справочника переданным списком.

        Параметры:
        - contacts: список сущностей Contact, которыми заменить текущее содержимое.
        """
        self._contacts = {c.id: c for c in contacts}
        self._next_id = max(self._contacts.keys(), default=0) + 1
        self.mark_clean()

    def list(self) -> List[Contact]:
        """Вернуть все контакты, отсортированные по имени и id."""
        return sorted(self._contacts.values(), key=lambda c: (c.name.lower(), c.id))

    def add(self, name: str, phone: str, comment: str = "") -> Contact:
        """Создать и добавить контакт.

        Параметры:
        - name: имя контакта.
        - phone: телефон контакта.
        - comment: комментарий (необязательно).

        Возвращает созданную сущность Contact.
        """
        contact = Contact(
            id=self._next_id,
            name=_validate_name(name),
            phone=_validate_phone(phone),
            comment=(comment or "").strip(),
        )
        self._contacts[contact.id] = contact
        self._next_id += 1
        self._mark_dirty()
        return contact

    def get(self, contact_id: int) -> Contact:
        """Вернуть контакт по id или бросить ContactNotFound.

        Параметры:
        - contact_id: идентификатор контакта.
        """
        contact = self._contacts.get(int(contact_id))
        if not contact:
            raise ContactNotFound(f"Контакт с id={contact_id} не найден")
        return contact

    def update(self, contact_id: int, *, name: Optional[str] = None, phone: Optional[str] = None, comment: Optional[str] = None) -> Contact:
        """Обновить поля контакта. Пустые значения сохраняют прежние.

        Параметры:
        - contact_id: идентификатор обновляемого контакта.
        - name: новое имя (или None, чтобы не менять).
        - phone: новый телефон (или None, чтобы не менять).
        - comment: новый комментарий (или None, чтобы не менять).

        Возвращает обновлённую сущность Contact.
        """
        existing = self.get(contact_id)
        new_name = existing.name if name is None else _validate_name(name)
        new_phone = existing.phone if phone is None else _validate_phone(phone)
        new_comment = existing.comment if comment is None else (comment or "").strip()
        updated = Contact(id=existing.id, name=new_name, phone=new_phone, comment=new_comment)
        self._contacts[existing.id] = updated
        self._mark_dirty()
        return updated

    def delete(self, contact_id: int) -> None:
        """Удалить контакт по id или бросить ContactNotFound.

        Параметры:
        - contact_id: идентификатор удаляемого контакта.
        """
        cid = int(contact_id)
        if cid in self._contacts:
            del self._contacts[cid]
            self._mark_dirty()
        else:
            raise ContactNotFound(f"Контакт с id={contact_id} не найден")

    def search(self, query: str) -> List[Contact]:
        """Поиск по свободной строке (имя, телефон, комментарий).

        Параметры:
        - query: поисковая строка.
        """
        q = (query or "").strip().lower()
        if not q:
            return []
        return [c for c in self._contacts.values() if q in c.name.lower() or q in c.phone.lower() or q in c.comment.lower()]

    def search_by_fields(self, *, name: Optional[str] = None, phone: Optional[str] = None, comment: Optional[str] = None) -> List[Contact]:
        """Поиск с отдельными фильтрами по полям; пустые фильтры игнорируются.

        Параметры:
        - name: подстрока для фильтрации по имени.
        - phone: подстрока для фильтрации по телефону.
        - comment: подстрока для фильтрации по комментарию.
        """
        name_q = (name or "").strip().lower()
        phone_q = (phone or "").strip().lower()
        comment_q = (comment or "").strip().lower()
        def match(c: Contact) -> bool:
            ok = True
            if name_q:
                ok = ok and name_q in c.name.lower()
            if phone_q:
                ok = ok and phone_q in c.phone.lower()
            if comment_q:
                ok = ok and comment_q in c.comment.lower()
            return ok
        return [c for c in self._contacts.values() if match(c)]
