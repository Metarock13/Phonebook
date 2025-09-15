from pathlib import Path
from typing import List

from .exceptions import StorageError
from .model import Contact


class TxtStorage:
    """TXT-хранилище на базе табличного файла.

    Формат строки: id<TAB>name<TAB>phone<TAB>comment
    """

    def __init__(self, path: Path) -> None:
        """Создать хранилище, привязанное к конкретному пути файла.

        Параметры:
        - path: путь к .txt файлу.
        """
        self._path = Path(path).expanduser().resolve()

    @property
    def path(self) -> Path:
        """Вернуть привязанный абсолютный путь."""
        return self._path

    def _ensure_parent(self) -> None:
        parent = self._path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Contact]:
        """Загрузить контакты из TXT-файла.

        Возвращает: список Contact (пустой, если файл отсутствует).
        Бросает: StorageError — если путь не файл или при ошибках парсинга/ввода-вывода.
        """
        if not self._path.exists():
            return []
        if not self._path.is_file():
            raise StorageError(f"Путь не является файлом: {self._path}")
        contacts: List[Contact] = []
        try:
            for line in self._path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) < 4:
                    parts = parts + [""] * (4 - len(parts))
                cid_str, name, phone, comment = parts[:4]
                cid = int(cid_str)
                contacts.append(Contact(id=cid, name=name.strip(), phone=phone.strip(), comment=comment.strip()))
        except ValueError as e:
            raise StorageError(f"Ошибка парсинга файла: {e}") from e
        except OSError as e:
            raise StorageError(f"Ошибка чтения файла: {e}") from e
        return contacts

    def save(self, contacts: List[Contact]) -> None:
        """Сохранить список контактов в TXT-файл атомарно.

        Параметры:
        - contacts: список Contact для записи.
        Бросает: StorageError — при ошибках записи.
        """
        self._ensure_parent()
        lines = []
        for c in contacts:
            name = c.name.replace("\n", " ")
            phone = c.phone.replace("\n", " ")
            comment = c.comment.replace("\n", " ")
            lines.append(f"{c.id}\t{name}\t{phone}\t{comment}")
        text = "\n".join(lines) + ("\n" if lines else "")
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            tmp_path.write_text(text, encoding="utf-8")
            tmp_path.replace(self._path)
        except OSError as e:
            raise StorageError(f"Ошибка записи файла: {e}") from e
