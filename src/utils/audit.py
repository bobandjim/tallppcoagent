"""
Append-only SQLite audit trail.

Schema: audit_log(id, audit_trail_id, lead_id, event_type, timestamp, payload_json)

Event types:
  LEAD_CREATED, LEAD_UPDATED, EMAIL_SENT, REPLY_RECEIVED,
  OPT_OUT, BOUNCE, MEETING_BOOKED, SHOW_BOOKED, DEDUP

Usage:
    from src.utils.audit import AuditLog
    audit = AuditLog("data/audit.db")
    audit.log("EMAIL_SENT", lead_id=42, audit_trail_id="uuid-...", payload={"step": 1})
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


VALID_EVENT_TYPES = frozenset({
    "LEAD_CREATED",
    "LEAD_UPDATED",
    "EMAIL_SENT",
    "REPLY_RECEIVED",
    "OPT_OUT",
    "BOUNCE",
    "MEETING_BOOKED",
    "SHOW_BOOKED",
    "DEDUP",
    "SUPPRESSED",
    "IMPORT",
})

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_trail_id  TEXT NOT NULL,
    lead_id         INTEGER,
    event_type      TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    payload_json    TEXT
);
"""

INSERT_SQL = """
INSERT INTO audit_log (audit_trail_id, lead_id, event_type, timestamp, payload_json)
VALUES (?, ?, ?, ?, ?);
"""


class AuditLog:
    """Thread-safe, append-only audit log backed by SQLite."""

    def __init__(self, db_path: str | Path = "data/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(CREATE_TABLE_SQL)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def log(
        self,
        event_type: str,
        lead_id: Optional[int] = None,
        audit_trail_id: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Write one audit event. Returns the audit_trail_id used.
        Raises ValueError for unknown event types.
        """
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type!r}. Valid: {sorted(VALID_EVENT_TYPES)}")
        trail_id = audit_trail_id or str(uuid.uuid4())
        ts = datetime.now(timezone.utc).isoformat()
        payload_json = json.dumps(payload or {}, default=str)
        with self._conn() as conn:
            conn.execute(INSERT_SQL, (trail_id, lead_id, event_type, ts, payload_json))
        return trail_id

    def get_events(
        self,
        lead_id: Optional[int] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Query audit events. Useful for reporting and debugging."""
        clauses = []
        params: list[Any] = []
        if lead_id is not None:
            clauses.append("lead_id = ?")
            params.append(lead_id)
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        sql = f"SELECT * FROM audit_log {where} ORDER BY timestamp DESC LIMIT ?"
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def event_count(self, event_type: Optional[str] = None) -> int:
        where = "WHERE event_type = ?" if event_type else ""
        params = [event_type] if event_type else []
        sql = f"SELECT COUNT(*) FROM audit_log {where}"
        with self._conn() as conn:
            return conn.execute(sql, params).fetchone()[0]
