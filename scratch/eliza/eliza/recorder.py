"""Eliza.Recorder — SQLite-backed persistence.

Per the Agda contract: opaque Database, monotone counter increments,
session start/end lifecycle, cross-session persistence.

WAL mode keeps writes sequential (small per-statement appends to the
journal). The schema is fixed at SCHEMA_VERSION = 1.

Two classes:

  * `Store`: low-level SQLite access. One per process.
  * `SessionRecorder`: per-session in-memory caches synchronised with
    the store. Started/ended around each conversation.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from eliza.alphabets import Chamber, Gen


SCHEMA_VERSION = 1
DEFAULT_DB = "state.db"


@dataclass
class Turn:
    """The structural payload of one per-char event the Recorder persists."""
    n: int
    user_input: str
    generator: Gen
    chamber_from: str        # canonical word
    chamber_to: str
    bruhat: int
    fiedler: float
    turbulence: float
    holonomy_closes: bool
    holonomy_target: str
    curvature: float
    curvature_band: str
    surprise: Optional[float]


class Store:
    """Single-process SQLite handle. Owns schema + migrations."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._ensure_schema()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    # --- Schema -----------------------------------------------------------

    def _ensure_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                n INTEGER,
                ts TEXT,
                user_input TEXT,
                generator TEXT,
                chamber_from TEXT,
                chamber_to TEXT,
                bruhat INTEGER,
                fiedler REAL,
                turbulence REAL,
                holonomy_closes INTEGER,
                holonomy_target TEXT,
                curvature REAL,
                curvature_band TEXT,
                surprise REAL
            );
            CREATE INDEX IF NOT EXISTS turns_session_idx ON turns(session_id);
            CREATE TABLE IF NOT EXISTS chamber_visits (
                chamber TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS edge_traversals (
                from_chamber TEXT NOT NULL,
                generator TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (from_chamber, generator)
            );
            CREATE TABLE IF NOT EXISTS trigrams (
                c1 TEXT NOT NULL,
                c2 TEXT NOT NULL,
                c3 TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (c1, c2, c3)
            );
            """
        )
        cur.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        self.conn.commit()

    # --- Session lifecycle -----------------------------------------------

    def start_session(self, ts: str) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO sessions(started_at) VALUES (?)", (ts,))
        self.conn.commit()
        return int(cur.lastrowid)

    def end_session(self, session_id: int, ts: str) -> None:
        self.conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?", (ts, session_id)
        )
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES ('last_session_ended', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (ts,),
        )
        self.conn.commit()

    def session_count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        return int(cur.fetchone()[0])

    def turn_count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM turns")
        return int(cur.fetchone()[0])

    # --- Per-turn write ---------------------------------------------------

    def record_turn(self, session_id: int, turn: Turn) -> None:
        self.conn.execute(
            """
            INSERT INTO turns(session_id, n, ts, user_input, generator,
                              chamber_from, chamber_to, bruhat,
                              fiedler, turbulence, holonomy_closes,
                              holonomy_target, curvature, curvature_band, surprise)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                turn.n,
                time.strftime("%Y-%m-%dT%H:%M:%S"),
                turn.user_input,
                turn.generator.name,
                turn.chamber_from,
                turn.chamber_to,
                turn.bruhat,
                turn.fiedler,
                turn.turbulence,
                1 if turn.holonomy_closes else 0,
                turn.holonomy_target,
                turn.curvature,
                turn.curvature_band,
                turn.surprise,
            ),
        )

    def increment_chamber_visit(self, chamber_word: str, by: int = 1) -> None:
        self.conn.execute(
            "INSERT INTO chamber_visits(chamber, count) VALUES (?, ?) "
            "ON CONFLICT(chamber) DO UPDATE SET count = count + excluded.count",
            (chamber_word, by),
        )

    def increment_edge(self, from_word: str, generator: Gen, by: int = 1) -> None:
        self.conn.execute(
            "INSERT INTO edge_traversals(from_chamber, generator, count) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(from_chamber, generator) DO UPDATE "
            "SET count = count + excluded.count",
            (from_word, generator.name, by),
        )

    def increment_holonomy(self, closes: bool) -> None:
        key = "holonomy_closes" if closes else "holonomy_drifts"
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, '1') "
            "ON CONFLICT(key) DO UPDATE SET value = "
            "CAST(CAST(value AS INTEGER) + 1 AS TEXT)",
            (key,),
        )

    def set_last_chamber(self, chamber_word: str) -> None:
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES ('last_chamber', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (chamber_word,),
        )

    def increment_trigram(self, c1: str, c2: str, c3: str, by: int = 1) -> None:
        self.conn.execute(
            "INSERT INTO trigrams(c1, c2, c3, count) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(c1, c2, c3) DO UPDATE SET count = count + excluded.count",
            (c1, c2, c3, by),
        )

    def commit(self) -> None:
        self.conn.commit()

    # --- Reads ------------------------------------------------------------

    def get_visits(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        cur.execute("SELECT chamber, count FROM chamber_visits")
        return dict(cur.fetchall())

    def get_edges(self) -> Dict[str, Dict[str, int]]:
        cur = self.conn.cursor()
        cur.execute("SELECT from_chamber, generator, count FROM edge_traversals")
        out: Dict[str, Dict[str, int]] = {}
        for from_c, gen_name, count in cur.fetchall():
            out.setdefault(from_c, {})[gen_name] = count
        return out

    def get_meta(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

    def get_holonomy_counts(self) -> Tuple[int, int]:
        return (
            int(self.get_meta("holonomy_closes") or "0"),
            int(self.get_meta("holonomy_drifts") or "0"),
        )

    def load_trigrams(self) -> Dict[Tuple[str, str], Dict[str, int]]:
        cur = self.conn.cursor()
        cur.execute("SELECT c1, c2, c3, count FROM trigrams")
        out: Dict[Tuple[str, str], Dict[str, int]] = {}
        for c1, c2, c3, count in cur.fetchall():
            out.setdefault((c1, c2), {})[c3] = count
        return out


class SessionRecorder:
    """In-memory aggregates synchronised to a Store."""

    def __init__(self, store: Store) -> None:
        self.store = store
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.session_id = store.start_session(ts)
        self.started_at = ts
        self.aggregate: Dict[str, object] = {
            "session_count": store.session_count(),
            "turn_count": store.turn_count(),
            "chamber_visits": store.get_visits(),
            "edge_traversals": store.get_edges(),
            "holonomy_closes": store.get_holonomy_counts()[0],
            "holonomy_drifts": store.get_holonomy_counts()[1],
            "last_chamber": store.get_meta("last_chamber"),
            "last_session_ended": store.get_meta("last_session_ended"),
        }
        self._n = 0

    def session_start_visit(self, chamber_word: str) -> None:
        visits = self.aggregate["chamber_visits"]
        assert isinstance(visits, dict)
        visits[chamber_word] = visits.get(chamber_word, 0) + 1
        self.store.increment_chamber_visit(chamber_word)
        self.store.commit()

    def record_turn(self, turn: Turn) -> None:
        self._n += 1
        turn = Turn(
            n=self._n,
            user_input=turn.user_input,
            generator=turn.generator,
            chamber_from=turn.chamber_from,
            chamber_to=turn.chamber_to,
            bruhat=turn.bruhat,
            fiedler=turn.fiedler,
            turbulence=turn.turbulence,
            holonomy_closes=turn.holonomy_closes,
            holonomy_target=turn.holonomy_target,
            curvature=turn.curvature,
            curvature_band=turn.curvature_band,
            surprise=turn.surprise,
        )
        # In-memory aggregate.
        agg = self.aggregate
        agg["turn_count"] = int(agg.get("turn_count", 0)) + 1  # type: ignore[arg-type]
        visits = agg["chamber_visits"]
        assert isinstance(visits, dict)
        visits[turn.chamber_to] = visits.get(turn.chamber_to, 0) + 1
        edges = agg["edge_traversals"]
        assert isinstance(edges, dict)
        edges.setdefault(turn.chamber_from, {})
        edges[turn.chamber_from][turn.generator.name] = (
            edges[turn.chamber_from].get(turn.generator.name, 0) + 1
        )
        if turn.holonomy_closes:
            agg["holonomy_closes"] = int(agg.get("holonomy_closes", 0)) + 1  # type: ignore[arg-type]
        else:
            agg["holonomy_drifts"] = int(agg.get("holonomy_drifts", 0)) + 1  # type: ignore[arg-type]
        agg["last_chamber"] = turn.chamber_to
        # Persist.
        self.store.record_turn(self.session_id, turn)
        self.store.increment_chamber_visit(turn.chamber_to)
        self.store.increment_edge(turn.chamber_from, turn.generator)
        self.store.increment_holonomy(turn.holonomy_closes)
        self.store.set_last_chamber(turn.chamber_to)
        self.store.commit()

    def record_trigram(self, c1: str, c2: str, c3: str) -> None:
        if c1 and c2:
            self.store.increment_trigram(c1, c2, c3)

    def session_end(self) -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.aggregate["last_session_ended"] = ts
        self.store.end_session(self.session_id, ts)
