#!/usr/bin/env python3
"""Interpret the conversation decomposition database retrospectively.

Materialises:
  - retrospective_conversation         : summary row per conversation
  - retrospective_move_intro           : earliest-turn-mention per M-move
  - retrospective_turn_summary         : per-turn reference density

And writes a markdown report linking turn -> move and move -> turn.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


M_MOVE_RE = re.compile(r"\bM(\d+)(?:\s*v(\d+(?:\.\d+)?))?\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="decomposition/cotype_decomposition.sqlite")
    parser.add_argument("--out", default="decomposition/conversation_retrospective.md")
    parser.add_argument("--top-turns", type=int, default=20,
                        help="How many highest-density turns to surface in the report")
    parser.add_argument("--top-verifiers", type=int, default=15)
    return parser.parse_args()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_retro_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS retrospective_conversation (
            retro_conv_id    INTEGER PRIMARY KEY,
            conversation_id  INTEGER NOT NULL UNIQUE,
            turn_count       INTEGER NOT NULL,
            user_turn_count  INTEGER NOT NULL,
            assistant_turn_count INTEGER NOT NULL,
            total_refs       INTEGER NOT NULL,
            distinct_moves   INTEGER NOT NULL,
            distinct_verifiers INTEGER NOT NULL,
            distinct_files   INTEGER NOT NULL,
            generated_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS retrospective_move_intro (
            retro_intro_id   INTEGER PRIMARY KEY,
            conversation_id  INTEGER NOT NULL,
            m_token          TEXT NOT NULL,
            first_turn       INTEGER NOT NULL,
            first_turn_role  TEXT NOT NULL,
            mention_count    INTEGER NOT NULL,
            UNIQUE(conversation_id, m_token)
        );

        CREATE TABLE IF NOT EXISTS retrospective_turn_summary (
            retro_turn_summary_id INTEGER PRIMARY KEY,
            conversation_id  INTEGER NOT NULL,
            ordinal          INTEGER NOT NULL,
            role             TEXT NOT NULL,
            m_move_count     INTEGER NOT NULL,
            verifier_count   INTEGER NOT NULL,
            file_count       INTEGER NOT NULL,
            total_refs       INTEGER NOT NULL,
            moves_referenced TEXT,
            verifiers_referenced TEXT,
            files_referenced TEXT,
            UNIQUE(conversation_id, ordinal)
        );

        CREATE INDEX IF NOT EXISTS idx_retro_intro ON retrospective_move_intro(conversation_id, first_turn);
        CREATE INDEX IF NOT EXISTS idx_retro_turn ON retrospective_turn_summary(conversation_id, ordinal);
    """)


def normalize_m_token(raw: str) -> str:
    """Canonicalise tokens like 'M22 v6', 'M22v6', 'M22  v6.0' to 'M22 v6'."""
    m = M_MOVE_RE.match(raw)
    if not m:
        return raw
    token = f"M{m.group(1)}"
    if m.group(2):
        token += f" v{m.group(2)}"
    return token


def populate_retro_tables(conn: sqlite3.Connection, conversation_id: int) -> None:
    # Wipe prior retro rows for this conversation
    for tbl in ("retrospective_conversation",
                "retrospective_move_intro",
                "retrospective_turn_summary"):
        conn.execute(f"DELETE FROM {tbl} WHERE conversation_id = ?", (conversation_id,))

    # Summary numbers
    summary = conn.execute("""
        SELECT
          (SELECT COUNT(*) FROM turns WHERE conversation_id = ?) AS turn_count,
          (SELECT COUNT(*) FROM turns WHERE conversation_id = ? AND role='user') AS user_count,
          (SELECT COUNT(*) FROM turns WHERE conversation_id = ? AND role='assistant') AS asst_count,
          (SELECT COUNT(*) FROM turn_references WHERE turn_id IN (SELECT turn_id FROM turns WHERE conversation_id = ?)) AS ref_count
    """, (conversation_id,)*4).fetchone()

    distinct_moves = conn.execute("""
        SELECT COUNT(DISTINCT ref_target) FROM turn_references
        WHERE ref_type='m_move' AND turn_id IN (SELECT turn_id FROM turns WHERE conversation_id = ?)
    """, (conversation_id,)).fetchone()[0]
    distinct_verifiers = conn.execute("""
        SELECT COUNT(DISTINCT ref_target) FROM turn_references
        WHERE ref_type='verifier' AND turn_id IN (SELECT turn_id FROM turns WHERE conversation_id = ?)
    """, (conversation_id,)).fetchone()[0]
    distinct_files = conn.execute("""
        SELECT COUNT(DISTINCT ref_target) FROM turn_references
        WHERE ref_type='file_path' AND turn_id IN (SELECT turn_id FROM turns WHERE conversation_id = ?)
    """, (conversation_id,)).fetchone()[0]

    conn.execute("""
        INSERT INTO retrospective_conversation
          (conversation_id, turn_count, user_turn_count, assistant_turn_count,
           total_refs, distinct_moves, distinct_verifiers, distinct_files)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (conversation_id, summary["turn_count"], summary["user_count"],
          summary["asst_count"], summary["ref_count"],
          distinct_moves, distinct_verifiers, distinct_files))

    # Earliest M-move mention per token
    move_rows = conn.execute("""
        SELECT tr.ref_target AS token, t.ordinal AS turn, t.role AS role
        FROM turn_references tr
        JOIN turns t ON tr.turn_id = t.turn_id
        WHERE t.conversation_id = ? AND tr.ref_type='m_move'
        ORDER BY t.ordinal ASC
    """, (conversation_id,)).fetchall()

    first_seen: Dict[str, Tuple[int, str]] = {}
    mention_count: Dict[str, int] = defaultdict(int)
    for r in move_rows:
        tok = normalize_m_token(r["token"])
        mention_count[tok] += 1
        if tok not in first_seen:
            first_seen[tok] = (r["turn"], r["role"])

    for tok, (first_turn, first_role) in first_seen.items():
        conn.execute("""
            INSERT INTO retrospective_move_intro
              (conversation_id, m_token, first_turn, first_turn_role, mention_count)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, tok, first_turn, first_role, mention_count[tok]))

    # Per-turn summary
    turn_rows = conn.execute("""
        SELECT t.ordinal AS ordinal, t.role AS role, tr.ref_type AS ref_type,
               tr.ref_target AS ref_target
        FROM turns t
        LEFT JOIN turn_references tr ON tr.turn_id = t.turn_id
        WHERE t.conversation_id = ?
        ORDER BY t.ordinal ASC
    """, (conversation_id,)).fetchall()

    per_turn: Dict[int, Dict[str, object]] = defaultdict(
        lambda: {"role": "", "m_move": [], "verifier": [], "file_path": [],
                 "concept": [], "claim": [], "line_anchor": [], "all": 0}
    )
    for r in turn_rows:
        ord_ = r["ordinal"]
        per_turn[ord_]["role"] = r["role"]
        if r["ref_type"]:
            bucket = per_turn[ord_].setdefault(r["ref_type"], [])  # type: ignore
            bucket.append(r["ref_target"])  # type: ignore
            per_turn[ord_]["all"] += 1  # type: ignore

    for ord_, data in per_turn.items():
        moves_unique = sorted(set(normalize_m_token(m) for m in data["m_move"]))  # type: ignore
        verifiers_unique = sorted(set(data["verifier"]))  # type: ignore
        files_unique = sorted(set(data["file_path"]))  # type: ignore
        conn.execute("""
            INSERT INTO retrospective_turn_summary
              (conversation_id, ordinal, role, m_move_count, verifier_count,
               file_count, total_refs, moves_referenced, verifiers_referenced,
               files_referenced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (conversation_id, ord_, data["role"],
              len(data["m_move"]), len(data["verifier"]), len(data["file_path"]),  # type: ignore
              data["all"],
              "; ".join(moves_unique),
              "; ".join(verifiers_unique),
              "; ".join(files_unique)))


def write_report(
    conn: sqlite3.Connection,
    conversation_id: int,
    out_path: Path,
    top_turns: int,
    top_verifiers: int,
) -> None:
    conv = conn.execute("""
        SELECT c.source_uri, c.mhtml_path, c.snapshot_date, c.transcript_path,
               c.turn_count, rc.user_turn_count, rc.assistant_turn_count,
               rc.total_refs, rc.distinct_moves, rc.distinct_verifiers, rc.distinct_files
        FROM conversations c
        LEFT JOIN retrospective_conversation rc USING (conversation_id)
        WHERE c.conversation_id = ?
    """, (conversation_id,)).fetchone()

    intros = conn.execute("""
        SELECT m_token, first_turn, first_turn_role, mention_count
        FROM retrospective_move_intro
        WHERE conversation_id = ?
        ORDER BY first_turn ASC, m_token ASC
    """, (conversation_id,)).fetchall()

    top_density_turns = conn.execute("""
        SELECT ordinal, role, total_refs, m_move_count, verifier_count, file_count,
               moves_referenced, verifiers_referenced
        FROM retrospective_turn_summary
        WHERE conversation_id = ? AND total_refs > 0
        ORDER BY total_refs DESC, ordinal ASC
        LIMIT ?
    """, (conversation_id, top_turns)).fetchall()

    top_verifier_rows = conn.execute("""
        SELECT ref_target, COUNT(*) AS hits, MIN(t.ordinal) AS first_turn
        FROM turn_references tr
        JOIN turns t ON tr.turn_id = t.turn_id
        WHERE t.conversation_id = ? AND tr.ref_type='verifier'
        GROUP BY ref_target
        ORDER BY hits DESC, ref_target ASC
        LIMIT ?
    """, (conversation_id, top_verifiers)).fetchall()

    top_files = conn.execute("""
        SELECT ref_target, COUNT(*) AS hits, MIN(t.ordinal) AS first_turn
        FROM turn_references tr
        JOIN turns t ON tr.turn_id = t.turn_id
        WHERE t.conversation_id = ? AND tr.ref_type='file_path'
        GROUP BY ref_target
        ORDER BY hits DESC, ref_target ASC
        LIMIT 15
    """, (conversation_id,)).fetchall()

    lines: List[str] = []
    lines.append("# Conversation Retrospective")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    lines.append(f"- Source: {conv['source_uri']}")
    lines.append(f"- MHTML: {conv['mhtml_path']}")
    lines.append(f"- Transcript: {conv['transcript_path']}")
    lines.append(f"- Turn count: {conv['turn_count']} ({conv['user_turn_count']} user + {conv['assistant_turn_count']} assistant)")
    lines.append(f"- Total references: {conv['total_refs']}")
    lines.append(f"- Distinct M-tokens: {conv['distinct_moves']}; verifiers: {conv['distinct_verifiers']}; files: {conv['distinct_files']}")
    lines.append("")

    lines.append("## Interpretation Lens")
    lines.append("")
    lines.append(
        "This retrospective treats the conversation transcript as a time-ordered "
        "sequence of turns and surfaces (a) when each M-move was first introduced, "
        "(b) the most-cited verifiers and files across the conversation, and "
        "(c) the densest-reference turns. Cross-reference targets resolve against "
        "[catalog/](../catalog/) and [cotype_decomposition.sqlite](cotype_decomposition.sqlite)."
    )
    lines.append("")

    lines.append("## M-move introduction timeline")
    lines.append("")
    lines.append("Each M-move's first conversational mention. Comparison to "
                 "[cotype_retrospective.md](cotype_retrospective.md) shows which moves "
                 "the narrative documents that the conversation also names.")
    lines.append("")
    lines.append("| First turn | Role | M-token | Mentions in conversation |")
    lines.append("|------------|------|---------|--------------------------|")
    for r in intros:
        lines.append(f"| {r['first_turn']} | {r['first_turn_role']} | {r['m_token']} | {r['mention_count']} |")
    lines.append("")

    lines.append("## Most-referenced verifiers")
    lines.append("")
    lines.append("| Verifier | Hits | First turn |")
    lines.append("|----------|------|------------|")
    for r in top_verifier_rows:
        lines.append(f"| `{r['ref_target']}` | {r['hits']} | {r['first_turn']} |")
    lines.append("")

    lines.append("## Most-referenced files")
    lines.append("")
    lines.append("| File | Hits | First turn |")
    lines.append("|------|------|------------|")
    for r in top_files:
        lines.append(f"| `{r['ref_target']}` | {r['hits']} | {r['first_turn']} |")
    lines.append("")

    lines.append(f"## Densest-reference turns (top {top_turns})")
    lines.append("")
    lines.append("| Turn | Role | Total refs | M | Verifiers | Files | Moves mentioned |")
    lines.append("|------|------|------------|---|-----------|-------|------------------|")
    for r in top_density_turns:
        moves = r["moves_referenced"][:80] + ("…" if len(r["moves_referenced"]) > 80 else "")
        lines.append(
            f"| {r['ordinal']} | {r['role']} | {r['total_refs']} | "
            f"{r['m_move_count']} | {r['verifier_count']} | {r['file_count']} | "
            f"{moves} |"
        )
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).resolve()
    out_path = Path(args.out).resolve()

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT conversation_id FROM conversations "
            "ORDER BY generated_at_utc DESC, conversation_id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            raise RuntimeError("No conversations found. Run build_conversation_db.py first.")
        conversation_id = int(row["conversation_id"])

        ensure_retro_schema(conn)
        populate_retro_tables(conn, conversation_id)
        write_report(conn, conversation_id, out_path, args.top_turns, args.top_verifiers)
        conn.commit()

        counts = conn.execute("""
            SELECT
              (SELECT COUNT(*) FROM retrospective_move_intro WHERE conversation_id = ?) AS intros,
              (SELECT COUNT(*) FROM retrospective_turn_summary WHERE conversation_id = ?) AS turn_summaries
        """, (conversation_id, conversation_id)).fetchone()

    print(f"db: {db_path}")
    print(f"report: {out_path}")
    print(f"move intros: {counts['intros']}")
    print(f"turn summaries: {counts['turn_summaries']}")


if __name__ == "__main__":
    main()
