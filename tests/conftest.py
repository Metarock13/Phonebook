"""Общие настройки тестов (pytest): настраивает PYTHONPATH для импорта пакета phonebook."""

import sys
from pathlib import Path


def _ensure_project_on_path() -> None:
    """Добавить корень проекта (где находится пакет phonebook) в sys.path, если его там нет."""
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


_ensure_project_on_path()
