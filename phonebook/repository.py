from typing import List, Dict, Optional, Iterable, Any
import re


_PHONE_REGEX = re.compile(r"^[+\d][\d\- ()]{5,}$")


def _is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    return bool(_PHONE_REGEX.match(phone))


def _make_contact(contact_id: int, name: str, phone: str, comment: str = "") -> Dict[str, Any]:
    name_clean = (name or "").strip()
    if not name_clean:
        raise ValueError("Name must not be empty")
    phone_str = (phone or "").strip()
    if not _is_valid_phone(phone_str):
        raise ValueError("Phone is invalid. Allowed: digits, spaces, dashes, parentheses, optional leading '+'.")
    comment_clean = (comment or "").strip()
    return {"id": int(contact_id), "name": name_clean, "phone": phone_str, "comment": comment_clean}


_state: Dict[str, Any] = {
    "contacts": {},
    "next_id": 1,
    "dirty": False,
    "opened_file": None,
}


def get_opened_file() -> Optional[str]:
    return _state["opened_file"]


def bind_file(path: Optional[str]) -> None:
    _state["opened_file"] = path


def is_dirty() -> bool:
    return bool(_state["dirty"])


def _mark_dirty() -> None:
    _state["dirty"] = True


def mark_clean() -> None:
    _state["dirty"] = False


def _update_next_id_from_existing() -> None:
    contacts: Dict[int, Dict[str, Any]] = _state["contacts"]
    if contacts:
        _state["next_id"] = max(contacts.keys()) + 1
    else:
        _state["next_id"] = 1


def load_all(contacts: Iterable[Dict[str, Any]]) -> None:
    contacts_by_id: Dict[int, Dict[str, Any]] = {}
    for c in contacts:
        cid = int(c["id"])
        name = str(c.get("name", ""))
        phone = str(c.get("phone", ""))
        comment = str(c.get("comment", ""))
        contacts_by_id[cid] = _make_contact(cid, name=name, phone=phone, comment=comment)
    _state["contacts"] = contacts_by_id
    _update_next_id_from_existing()
    mark_clean()


def list_contacts() -> List[Dict[str, Any]]:
    contacts: Dict[int, Dict[str, Any]] = _state["contacts"]
    return sorted(contacts.values(), key=lambda c: (str(c["name"]).lower(), int(c["id"])))


def add_contact(name: str, phone: str, comment: str = "") -> Dict[str, Any]:
    cid = int(_state["next_id"])
    contact = _make_contact(cid, name=name, phone=phone, comment=comment)
    _state["contacts"][cid] = contact
    _state["next_id"] = cid + 1
    _mark_dirty()
    return contact


def get(contact_id: int) -> Optional[Dict[str, Any]]:
    return _state["contacts"].get(int(contact_id))


def update_contact(contact_id: int, *, name: Optional[str] = None, phone: Optional[str] = None, comment: Optional[str] = None) -> Optional[Dict[str, Any]]:
    existing = _state["contacts"].get(int(contact_id))
    if not existing:
        return None
    new_name = existing["name"] if name is None else name
    new_phone = existing["phone"] if phone is None else phone
    new_comment = existing["comment"] if comment is None else comment
    updated = _make_contact(int(existing["id"]), name=new_name, phone=new_phone, comment=new_comment)
    _state["contacts"][int(contact_id)] = updated
    _mark_dirty()
    return updated


def delete_contact(contact_id: int) -> bool:
    cid = int(contact_id)
    if cid in _state["contacts"]:
        del _state["contacts"][cid]
        _mark_dirty()
        return True
    return False


def search(query: str) -> List[Dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return []
    results: List[Dict[str, Any]] = []
    for c in _state["contacts"].values():
        if q in str(c["name"]).lower() or q in str(c["phone"]).lower() or q in str(c["comment"]).lower():
            results.append(c)
    return sorted(results, key=lambda c: (str(c["name"]).lower(), int(c["id"])))


def search_by_fields(*, name: Optional[str] = None, phone: Optional[str] = None, comment: Optional[str] = None) -> List[Dict[str, Any]]:
    name_q = (name or "").strip().lower()
    phone_q = (phone or "").strip().lower()
    comment_q = (comment or "").strip().lower()

    def match(c: Dict[str, Any]) -> bool:
        ok = True
        if name_q:
            ok = ok and name_q in str(c["name"]).lower()
        if phone_q:
            ok = ok and phone_q in str(c["phone"]).lower()
        if comment_q:
            ok = ok and comment_q in str(c["comment"]).lower()
        return ok

    return sorted([c for c in _state["contacts"].values() if match(c)], key=lambda c: (str(c["name"]).lower(), int(c["id"])))
