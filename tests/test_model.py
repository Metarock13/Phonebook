import pytest

from phonebook.model import Phonebook, Contact
from phonebook.exceptions import ValidationError, ContactNotFound


@pytest.fixture()
def pb() -> Phonebook:
    """Создать новый пустой справочник для каждого теста."""
    return Phonebook()


def test_add_contact_success(pb: Phonebook) -> None:
    """Успешное добавление контакта и пометка справочника как изменённого."""
    c = pb.add(name="Иван", phone="+7 (999) 123-45-67", comment="Коллега")
    assert c.id == 1
    assert c.name == "Иван"
    assert pb.dirty is True


def test_add_contact_invalid_name(pb: Phonebook) -> None:
    """Проверка ValidationError при пустом имени."""
    with pytest.raises(ValidationError):
        pb.add(name="   ", phone="+7 999 123-45-67")


def test_add_contact_invalid_phone(pb: Phonebook) -> None:
    """Проверка ValidationError при некорректном номере телефона."""
    with pytest.raises(ValidationError):
        pb.add(name="Иван", phone="abc")


def test_get_update_delete_flow(pb: Phonebook) -> None:
    """Сценарий: добавление -> чтение -> обновление -> удаление -> проверка ошибок."""
    c = pb.add(name="Пётр", phone="8 800 555-35-35")
    got = pb.get(c.id)
    assert got.name == "Пётр"

    updated = pb.update(c.id, name="Пётр Петров", phone="+7 812 555-00-00", comment="Сервис")
    assert updated.name == "Пётр Петров"
    assert updated.phone.startswith("+7")

    pb.delete(c.id)
    with pytest.raises(ContactNotFound):
        pb.get(c.id)


def test_delete_not_found(pb: Phonebook) -> None:
    """Удаление несуществующего контакта вызывает ContactNotFound."""
    with pytest.raises(ContactNotFound):
        pb.delete(123)


def test_search_free_text(pb: Phonebook) -> None:
    """Свободный поиск по подстроке по всем полям (имя/телефон/комментарий)."""
    pb.add(name="Иван Иванов", phone="+7 999 111-11-11", comment="A")
    pb.add(name="Пётр", phone="+7 999 222-22-22", comment="B")
    pb.add(name="Мария", phone="+7 999 333-33-33", comment="Иван")

    r1 = pb.search("иван")
    assert len(r1) == 2

    r2 = pb.search("+7 999 222")
    assert len(r2) == 1
    assert r2[0].name == "Пётр"


def test_search_by_fields(pb: Phonebook) -> None:
    """Поиск с фильтрами по полям (имя + комментарий)."""
    pb.add(name="Иван Иванов", phone="+7 999 111-11-11", comment="Отдел продаж")
    pb.add(name="Иван Петров", phone="+7 999 222-22-22", comment="Отдел закупок")
    r = pb.search_by_fields(name="Иван", comment="прод")
    assert len(r) == 1
    assert r[0].comment == "Отдел продаж"


@pytest.mark.parametrize(
    "name,phone",
    [
        ("Alex", "+1 (415) 555-0133"),
        ("Мария", "+380 (44) 123-4567"),
        ("Павел", "8 999 000-00-00"),
    ],
)
def test_parametrized_add(pb: Phonebook, name: str, phone: str) -> None:
    """Параметризованный тест успешного добавления контактов с разными номерами."""
    c = pb.add(name=name, phone=phone)
    assert c.id >= 1
    assert c.name == name


@pytest.mark.parametrize(
    "bad_phone",
    ["", " ", "abc", "+", "()", "1234"],
)
def test_parametrized_bad_phone(pb: Phonebook, bad_phone: str) -> None:
    """Параметризованный тест ошибок валидации для разных некорректных телефонов."""
    with pytest.raises(ValidationError):
        pb.add(name="Тест", phone=bad_phone)
