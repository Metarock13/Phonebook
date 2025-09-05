from pathlib import Path
from typing import List, Dict, Any


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def load_contacts_txt(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        return []
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    contacts: List[Dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            parts = parts + [""] * (4 - len(parts))
        cid_str, name, phone, comment = parts[:4]
        try:
            cid = int(cid_str)
        except ValueError:
            continue
        contacts.append({"id": cid, "name": name.strip(), "phone": phone.strip(), "comment": comment.strip()})
    return contacts


def save_contacts_txt(file_path: Path, contacts: List[Dict[str, Any]]) -> None:
    ensure_parent_dir(file_path)
    lines = []
    for c in contacts:
        cid = int(c.get("id", 0))
        name = str(c.get("name", ""))
        phone = str(c.get("phone", ""))
        comment = str(c.get("comment", ""))
        name = name.replace("\n", " ")
        phone = phone.replace("\n", " ")
        comment = comment.replace("\n", " ")
        lines.append(f"{cid}\t{name}\t{phone}\t{comment}")
    text = "\n".join(lines) + ("\n" if lines else "")
    tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(file_path)
