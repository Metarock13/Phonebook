from pathlib import Path
from typing import Optional

from . import repository as repo
from .storage import load_contacts_txt, save_contacts_txt


def _input(prompt: str) -> str:
    return input(prompt)


def _print(text: str = "") -> None:
    print(text)


def cmd_open() -> None:
    path_str = _input("Введите путь к файлу (.txt): ")
    path = Path(path_str).expanduser().resolve()
    try:
        if path.suffix.lower() != ".txt":
            _print("Поддерживается только .txt")
            return
        contacts = load_contacts_txt(path)
    except Exception as e:
        _print(f"Ошибка загрузки: {e}")
        return
    repo.load_all(contacts)
    repo.bind_file(str(path))
    _print(f"Загружено контактов: {len(contacts)} из '{path}'.")


def cmd_save() -> None:
    if not repo.get_opened_file():
        path_str = _input("Введите путь для сохранения (.txt): ")
        repo.bind_file(str(Path(path_str).expanduser().resolve()))
    path = Path(repo.get_opened_file() or "")
    if not str(path):
        _print("Путь для сохранения не задан.")
        return
    if path.suffix.lower() != ".txt":
        _print("Поддерживается только .txt")
        return
    try:
        save_contacts_txt(path, repo.list_contacts())
        repo.mark_clean()
        _print(f"Сохранено в '{path}'.")
    except Exception as e:
        _print(f"Ошибка сохранения: {e}")


def cmd_list() -> None:
    contacts = repo.list_contacts()
    if not contacts:
        _print("Справочник пуст.")
        return
    _print("Все контакты:")
    for c in contacts:
        _print(f"[{c['id']}] {c['name']} | {c['phone']} | {c['comment']}")


def cmd_create() -> None:
    name = _input("Имя: ").strip()
    phone = _input("Телефон: ").strip()
    comment = _input("Комментарий: ").strip()
    try:
        c = repo.add_contact(name=name, phone=phone, comment=comment)
        _print(f"Добавлен контакт [{c['id']}].")
    except Exception as e:
        _print(f"Ошибка создания: {e}")


def cmd_find() -> None:
    _print("Поиск: можно ввести либо общий запрос, либо оставить пустым и указать поля.")
    q = _input("Общий запрос (Enter чтобы пропустить): ").strip()
    if q:
        results = repo.search(q)
    else:
        name = _input("Имя содержит (Enter чтобы пропустить): ").strip()
        phone = _input("Телефон содержит (Enter чтобы пропустить): ").strip()
        comment = _input("Комментарий содержит (Enter чтобы пропустить): ").strip()
        results = repo.search_by_fields(name=name, phone=phone, comment=comment)
    if not results:
        _print("Ничего не найдено.")
        return
    for c in results:
        _print(f"[{c['id']}] {c['name']} | {c['phone']} | {c['comment']}")


def _ask_contact_id() -> Optional[int]:
    raw = _input("Введите ID контакта: ").strip()
    if not raw.isdigit():
        _print("Некорректный ID.")
        return None
    return int(raw)


def cmd_edit() -> None:
    cid = _ask_contact_id()
    if cid is None:
        return
    existing = repo.get(cid)
    if not existing:
        _print("Контакт не найден.")
        return
    _print(f"Оставьте поле пустым, чтобы оставить: {existing['name']} | {existing['phone']} | {existing['comment']}")
    name = _input("Имя: ").strip()
    phone = _input("Телефон: ").strip()
    comment = _input("Комментарий: ").strip()
    try:
        updated = repo.update_contact(
            cid,
            name=None if name == "" else name,
            phone=None if phone == "" else phone,
            comment=None if comment == "" else comment,
        )
        if updated:
            _print("Контакт обновлён.")
        else:
            _print("Контакт не найден.")
    except Exception as e:
        _print(f"Ошибка обновления: {e}")


def cmd_delete() -> None:
    cid = _ask_contact_id()
    if cid is None:
        return
    if repo.delete_contact(cid):
        _print("Контакт удалён.")
    else:
        _print("Контакт не найден.")


def _maybe_prompt_save() -> bool:
    """Return True if we should proceed to exit, False to continue program."""
    if not repo.is_dirty():
        return True
    ans = _input("Есть несохранённые изменения. Сохранить? (y/n): ").strip().lower()
    if ans in ("y", "yes", "д", "да"):
        cmd_save()
        return True
    if ans in ("n", "no", "н", "нет"):
        return True
    return False


def run() -> None:
    actions = {
        "1": cmd_open,
        "2": cmd_save,
        "3": cmd_list,
        "4": cmd_create,
        "5": cmd_find,
        "6": cmd_edit,
        "7": cmd_delete,
        "8": None,
    }
    while True:
        _print()
        _print("Телефонный справочник")
        _print("1. Открыть файл")
        _print("2. Сохранить файл")
        _print("3. Показать все контакты")
        _print("4. Создать контакт")
        _print("5. Найти контакт")
        _print("6. Изменить контакт")
        _print("7. Удалить контакт")
        _print("8. Выход")
        choice = _input("Выберите пункт меню: ").strip()
        if choice == "8":
            if _maybe_prompt_save():
                _print("До свидания!")
                break
            else:
                continue
        action = actions.get(choice)
        if action is None:
            _print("Неизвестный пункт меню. Повторите ввод.")
            continue
        try:
            action()
        except KeyboardInterrupt:
            _print("\nОперация отменена пользователем.")
        except Exception as e:
            _print(f"Ошибка: {e}")
