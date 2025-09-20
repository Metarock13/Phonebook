from pathlib import Path

import pytest

from phonebook.model import Contact
from phonebook.storage import TxtStorage
from phonebook.exceptions import StorageError


def test_load_nonexistent_returns_empty(tmp_path: Path) -> None:
    """Если файл отсутствует — вернуть пустой список без ошибок."""
    path = tmp_path / "book.txt"
    storage = TxtStorage(path)
    assert storage.load() == []


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    """Проверить, что после сохранения можно корректно загрузить те же контакты."""
    path = tmp_path / "book.txt"
    storage = TxtStorage(path)
    contacts = [
        Contact(id=1, name="Иван", phone="+7 (999) 123-45-67", comment="A"),
        Contact(id=2, name="Пётр", phone="8 800 555-35-35", comment="B"),
    ]
    storage.save(contacts)

    loaded = storage.load()
    assert len(loaded) == 2
    assert loaded[0].name == "Иван"
    assert loaded[1].phone.startswith("8 800")


def test_load_bad_file_raises(tmp_path: Path) -> None:
    """Невалидная строка (id не число) должна приводить к StorageError при загрузке."""
    path = tmp_path / "book.txt"
    path.write_text("abc\tName\t+7 999\tComment\n", encoding="utf-8")
    storage = TxtStorage(path)
    with pytest.raises(StorageError):
        storage.load()
