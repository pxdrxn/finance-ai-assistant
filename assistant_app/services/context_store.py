import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class JSONContextStore:
    """
    Persistência simples em JSON para manter contexto e histórico entre execuções.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save({"sessions": {}})

    def get_session(self, session_id: str) -> Dict[str, Any]:
        payload = self._load()
        session = payload["sessions"].get(session_id)
        if session:
            return session

        session = {
            "name": None,
            "last_amount": None,
            "messages": [],
        }
        payload["sessions"][session_id] = session
        self._save(payload)
        return session

    def update_context(
        self,
        session_id: str,
        *,
        name: Optional[str] = None,
        last_amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        payload = self._load()
        session = payload["sessions"].setdefault(
            session_id,
            {"name": None, "last_amount": None, "messages": []},
        )

        if name is not None:
            session["name"] = name
        if last_amount is not None:
            session["last_amount"] = last_amount

        self._save(payload)
        return session

    def append_message(self, session_id: str, role: str, content: str) -> None:
        payload = self._load()
        session = payload["sessions"].setdefault(
            session_id,
            {"name": None, "last_amount": None, "messages": []},
        )
        messages: List[Dict[str, str]] = session["messages"]
        messages.append({"role": role, "content": content})
        session["messages"] = messages[-12:]
        self._save(payload)

    def _load(self) -> Dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, payload: Dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
