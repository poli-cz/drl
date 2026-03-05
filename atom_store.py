from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Iterable
from datetime import datetime

@dataclass
class Atom:
    atom: str
    value: Any
    from_: str
    note: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {"atom": self.atom, "value": self.value, "from": self.from_, "note": self.note}

class AtomDefinitionStore:
    """Loads atom definitions (registry) for governance & validation."""

    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self._registry: Dict[str, Any] = {}

    def load(self) -> "AtomDefinitionStore":
        with open(self.registry_path, "r", encoding="utf-8") as f:
            self._registry = json.load(f)
        return self

    @property
    def atoms(self) -> List[Dict[str, Any]]:
        return self._registry.get("atoms", [])

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        for a in self.atoms:
            if a.get("name") == name:
                return a
        return None

    def validate_atom(self, atom: Atom) -> None:
        """Lightweight validation: atom must exist in registry (optional in early prototyping)."""
        # You can loosen this during development if needed.
        if self.get(atom.atom) is None:
            raise ValueError(f"Atom '{atom.atom}' is not registered in atoms_registry.json")

class AtomValueStore:
    """SQLite cache for computed atoms per domain and provider_key (provider_id@version)."""

    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._init_db()

    def _init_db(self) -> None:
        con = sqlite3.connect(self.sqlite_path)
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS atom_values (
                domain TEXT NOT NULL,
                provider_key TEXT NOT NULL,
                ts TEXT NOT NULL,
                atom TEXT NOT NULL,
                value_json TEXT NOT NULL,
                note TEXT,
                PRIMARY KEY (domain, provider_key, atom)
            );
            """
        )
        con.commit()
        con.close()

    def upsert(self, domain: str, provider_key: str, atoms: Iterable[Dict[str, Any]]) -> None:
        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        con = sqlite3.connect(self.sqlite_path)
        cur = con.cursor()
        for a in atoms:
            atom = a["atom"]
            value_json = json.dumps(a.get("value"))
            note = a.get("note", "")
            cur.execute(
                """
                INSERT INTO atom_values(domain, provider_key, ts, atom, value_json, note)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(domain, provider_key, atom)
                DO UPDATE SET ts=excluded.ts, value_json=excluded.value_json, note=excluded.note;
                """,
                (domain, provider_key, ts, atom, value_json, note),
            )
        con.commit()
        con.close()

    def fetch(self, domain: str, provider_key: Optional[str] = None) -> List[Dict[str, Any]]:
        con = sqlite3.connect(self.sqlite_path)
        cur = con.cursor()
        if provider_key is None:
            cur.execute(
                """SELECT provider_key, atom, value_json, note FROM atom_values WHERE domain=?""",
                (domain,),
            )
        else:
            cur.execute(
                """SELECT provider_key, atom, value_json, note FROM atom_values WHERE domain=? AND provider_key=?""",
                (domain, provider_key),
            )
        rows = cur.fetchall()
        con.close()

        out = []
        for pk, atom, value_json, note in rows:
            out.append({
                "atom": atom,
                "value": json.loads(value_json),
                "from": f"learned:{pk}",
                "note": note or ""
            })
        return out
