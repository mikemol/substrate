#!/usr/bin/env python3
"""Interpret cotype decomposition database retrospectively.

This script reads the section/triple decomposition DB, derives move-level
retrospective structures, stores them back into the DB, and writes a
human-readable report.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


MOVE_TOKEN_RE = re.compile(r"\b(M\d+(?:\s*v\d+(?:\.\d+)?)?)\b", re.IGNORECASE)
AXIS_RE = re.compile(r"\b([01]{3})\b")


@dataclass
class MoveRow:
    source_id: int
    section_index: int
    title: str
    path: str
    start_line: int
    end_line: int
    token: str | None


@dataclass
class AxisEvidence:
    axis: str
    evidence_line: int
    raw_object: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        default="decomposition/cotype_decomposition.sqlite",
        help="Path to decomposition sqlite database",
    )
    parser.add_argument(
        "--out",
        default="decomposition/cotype_retrospective.md",
        help="Path to retrospective markdown report",
    )
    parser.add_argument(
        "--top-themes",
        type=int,
        default=5,
        help="Number of top predicates to keep per move",
    )
    return parser.parse_args()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def grammar_source_id(conn: sqlite3.Connection) -> int:
    # The move-retrospective is specific to the grammar arc (its `Move M*` sections + axis
    # signatures). Target the grammar source BY PATH — not "latest" — because the DB now holds
    # many ledger sources (Λ6, build_cotype_db --all) and "latest" would mis-select another arc.
    row = conn.execute(
        """
        SELECT source_id
        FROM sources
        WHERE source_path LIKE '%cotype-free-self-extending-grammar.md'
        ORDER BY source_id DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise RuntimeError(
            "Grammar source not found. Run build_cotype_db.py (grammar is the default --source)."
        )
    return int(row["source_id"])


def fetch_moves(conn: sqlite3.Connection, source_id: int) -> list[MoveRow]:
    rows = conn.execute(
        """
        SELECT source_id, section_index, title, path, start_line, end_line
        FROM sections
        WHERE source_id = ?
          AND lower(title) LIKE 'move %'
        ORDER BY start_line ASC
        """,
        (source_id,),
    ).fetchall()

    out: list[MoveRow] = []
    for r in rows:
        title = str(r["title"])
        m = MOVE_TOKEN_RE.search(title)
        out.append(
            MoveRow(
                source_id=int(r["source_id"]),
                section_index=int(r["section_index"]),
                title=title,
                path=str(r["path"]),
                start_line=int(r["start_line"]),
                end_line=int(r["end_line"]),
                token=m.group(1).upper().replace("  ", " ") if m else None,
            )
        )
    return out


def move_section_indices(conn: sqlite3.Connection, source_id: int, move: MoveRow) -> list[int]:
    rows = conn.execute(
        """
        SELECT section_index
        FROM sections
        WHERE source_id = ?
          AND start_line >= ?
          AND start_line <= ?
        ORDER BY start_line ASC
        """,
        (source_id, move.start_line, move.end_line),
    ).fetchall()
    return [int(r["section_index"]) for r in rows]


def fetch_axis_evidence(
    conn: sqlite3.Connection,
    source_id: int,
    section_indices: list[int],
) -> list[AxisEvidence]:
    if not section_indices:
        return []

    placeholders = ",".join(["?"] * len(section_indices))
    sql = f"""
        SELECT object, evidence_line_start
        FROM triples
        WHERE source_id = ?
          AND predicate = 'has_axis_signature'
          AND section_index IN ({placeholders})
        ORDER BY evidence_line_start ASC
    """
    params: list[object] = [source_id, *section_indices]
    rows = conn.execute(sql, params).fetchall()

    result: list[AxisEvidence] = []
    for r in rows:
        raw_obj = str(r["object"])
        m = AXIS_RE.search(raw_obj)
        if m:
            result.append(
                AxisEvidence(
                    axis=m.group(1),
                    evidence_line=int(r["evidence_line_start"]),
                    raw_object=raw_obj,
                )
            )
    return result


def fetch_focus(conn: sqlite3.Connection, source_id: int, move: MoveRow) -> str | None:
    row = conn.execute(
        """
        SELECT object
        FROM triples
        WHERE source_id = ?
          AND section_index = ?
          AND predicate = 'focuses_on'
        ORDER BY evidence_line_start ASC
        LIMIT 1
        """,
        (source_id, move.section_index),
    ).fetchone()
    if row:
        return str(row["object"])

    row = conn.execute(
        """
        SELECT object
        FROM triples
        WHERE source_id = ?
          AND section_index = ?
          AND predicate = 'states'
        ORDER BY evidence_line_start ASC
        LIMIT 1
        """,
        (source_id, move.section_index),
    ).fetchone()
    return str(row["object"]) if row else None


def fetch_themes(
    conn: sqlite3.Connection,
    source_id: int,
    section_indices: list[int],
    top_n: int,
) -> list[tuple[str, int]]:
    if not section_indices:
        return []

    placeholders = ",".join(["?"] * len(section_indices))
    sql = f"""
        SELECT predicate, COUNT(*) AS c
        FROM triples
        WHERE source_id = ?
          AND section_index IN ({placeholders})
          AND predicate NOT IN ('section_kind', 'states', 'has_axis_signature')
        GROUP BY predicate
        ORDER BY c DESC, predicate ASC
        LIMIT ?
    """
    params: list[object] = [source_id, *section_indices, top_n]
    rows = conn.execute(sql, params).fetchall()
    return [(str(r["predicate"]), int(r["c"])) for r in rows]


def fetch_probe_sections(
    conn: sqlite3.Connection,
    source_id: int,
    move: MoveRow,
) -> list[tuple[str, int, int]]:
    rows = conn.execute(
        """
        SELECT title, start_line, end_line
        FROM sections
        WHERE source_id = ?
          AND start_line >= ?
          AND start_line <= ?
          AND lower(title) LIKE 'probe state%'
        ORDER BY start_line ASC
        """,
        (source_id, move.start_line, move.end_line),
    ).fetchall()
    return [(str(r["title"]), int(r["start_line"]), int(r["end_line"])) for r in rows]


def ensure_retro_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS retrospective_moves (
            retro_move_id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            ordinal INTEGER NOT NULL,
            section_index INTEGER NOT NULL,
            move_title TEXT NOT NULL,
            move_token TEXT,
            section_path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            primary_axis TEXT,
            all_axes TEXT,
            focus_text TEXT,
            probe_sections TEXT,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );

        CREATE TABLE IF NOT EXISTS retrospective_move_themes (
            retro_theme_id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            ordinal INTEGER NOT NULL,
            move_title TEXT NOT NULL,
            predicate TEXT NOT NULL,
            weight INTEGER NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );

        CREATE TABLE IF NOT EXISTS retrospective_axis_transitions (
            retro_transition_id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            from_ordinal INTEGER NOT NULL,
            to_ordinal INTEGER NOT NULL,
            from_move_title TEXT NOT NULL,
            to_move_title TEXT NOT NULL,
            from_axis TEXT,
            to_axis TEXT,
            from_line INTEGER NOT NULL,
            to_line INTEGER NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );

        CREATE INDEX IF NOT EXISTS idx_retromoves_source ON retrospective_moves(source_id);
        CREATE INDEX IF NOT EXISTS idx_retrothemes_source ON retrospective_move_themes(source_id);
        CREATE INDEX IF NOT EXISTS idx_retrotrans_source ON retrospective_axis_transitions(source_id);
        """
    )


def replace_retro_rows(
    conn: sqlite3.Connection,
    source_id: int,
    moves: list[MoveRow],
    top_themes: int,
) -> None:
    conn.execute("DELETE FROM retrospective_moves WHERE source_id = ?", (source_id,))
    conn.execute("DELETE FROM retrospective_move_themes WHERE source_id = ?", (source_id,))
    conn.execute("DELETE FROM retrospective_axis_transitions WHERE source_id = ?", (source_id,))

    enriched: list[dict[str, object]] = []

    for ordinal, move in enumerate(moves, start=1):
        section_indices = move_section_indices(conn, source_id, move)
        axis_evidence = fetch_axis_evidence(conn, source_id, section_indices)
        axis_values = [a.axis for a in axis_evidence]
        axis_unique = []
        for a in axis_values:
            if a not in axis_unique:
                axis_unique.append(a)

        primary_axis = axis_unique[0] if axis_unique else None
        all_axes = ",".join(axis_unique) if axis_unique else None

        focus = fetch_focus(conn, source_id, move)
        probes = fetch_probe_sections(conn, source_id, move)
        probe_blob = "; ".join(
            f"{title} [{start}-{end}]" for title, start, end in probes
        ) if probes else None

        conn.execute(
            """
            INSERT INTO retrospective_moves (
                source_id, ordinal, section_index, move_title, move_token,
                section_path, start_line, end_line, primary_axis, all_axes,
                focus_text, probe_sections
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                ordinal,
                move.section_index,
                move.title,
                move.token,
                move.path,
                move.start_line,
                move.end_line,
                primary_axis,
                all_axes,
                focus,
                probe_blob,
            ),
        )

        themes = fetch_themes(conn, source_id, section_indices, top_themes)
        for predicate, weight in themes:
            conn.execute(
                """
                INSERT INTO retrospective_move_themes (
                    source_id, ordinal, move_title, predicate, weight
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (source_id, ordinal, move.title, predicate, weight),
            )

        enriched.append(
            {
                "ordinal": ordinal,
                "move_title": move.title,
                "primary_axis": primary_axis,
                "start_line": move.start_line,
            }
        )

    for idx in range(len(enriched) - 1):
        a = enriched[idx]
        b = enriched[idx + 1]
        conn.execute(
            """
            INSERT INTO retrospective_axis_transitions (
                source_id, from_ordinal, to_ordinal, from_move_title,
                to_move_title, from_axis, to_axis, from_line, to_line
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                a["ordinal"],
                b["ordinal"],
                a["move_title"],
                b["move_title"],
                a["primary_axis"],
                b["primary_axis"],
                a["start_line"],
                b["start_line"],
            ),
        )


def write_report(conn: sqlite3.Connection, source_id: int, out_path: Path) -> None:
    source = conn.execute(
        """
        SELECT source_path, source_sha256, line_count, generated_at_utc
        FROM sources
        WHERE source_id = ?
        """,
        (source_id,),
    ).fetchone()

    move_rows = conn.execute(
        """
        SELECT ordinal, move_title, move_token, start_line, end_line,
               primary_axis, all_axes, focus_text, probe_sections
        FROM retrospective_moves
        WHERE source_id = ?
        ORDER BY ordinal ASC
        """,
        (source_id,),
    ).fetchall()

    transition_rows = conn.execute(
        """
        SELECT from_axis, to_axis, COUNT(*) AS c
        FROM retrospective_axis_transitions
        WHERE source_id = ?
          AND from_axis IS NOT NULL
          AND to_axis IS NOT NULL
        GROUP BY from_axis, to_axis
        ORDER BY c DESC, from_axis, to_axis
        """,
        (source_id,),
    ).fetchall()

    global_themes = conn.execute(
        """
        SELECT predicate, SUM(weight) AS score
        FROM retrospective_move_themes
        WHERE source_id = ?
        GROUP BY predicate
        ORDER BY score DESC, predicate ASC
        LIMIT 15
        """,
        (source_id,),
    ).fetchall()

    lines: list[str] = []
    lines.append("# Retrospective Interpretation of the Cotype")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.utcnow().isoformat()}Z")
    lines.append(f"- Source: {source['source_path']}")
    lines.append(f"- Source SHA-256: {source['source_sha256']}")
    lines.append(f"- Line count: {source['line_count']}")
    lines.append(f"- Source decomposed at: {source['generated_at_utc']}")
    lines.append("")

    lines.append("## Interpretation Lens")
    lines.append("")
    lines.append(
        "This retrospective interprets the cotype as a time-indexed sequence of "
        "moves, each carrying axis-signatures, thematic predicates, and probe "
        "state anchors with exact source-line positions."
    )
    lines.append("")

    lines.append("## Chronology")
    lines.append("")
    lines.append("| # | Move | Lines | Primary axis | All axes |")
    lines.append("|---|------|-------|--------------|----------|")
    for r in move_rows:
        lines.append(
            "| {o} | {t} | {s}-{e} | {p} | {a} |".format(
                o=r["ordinal"],
                t=str(r["move_title"]).replace("|", "\\|"),
                s=r["start_line"],
                e=r["end_line"],
                p=r["primary_axis"] or "-",
                a=r["all_axes"] or "-",
            )
        )
    lines.append("")

    lines.append("## Axis Transition Dynamics")
    lines.append("")
    lines.append("| From | To | Count |")
    lines.append("|------|----|-------|")
    for r in transition_rows:
        lines.append(f"| {r['from_axis']} | {r['to_axis']} | {r['c']} |")
    if not transition_rows:
        lines.append("| - | - | 0 |")
    lines.append("")

    lines.append("## Dominant Thematic Predicates")
    lines.append("")
    lines.append("| Predicate | Score |")
    lines.append("|-----------|-------|")
    for r in global_themes:
        lines.append(f"| {r['predicate']} | {r['score']} |")
    if not global_themes:
        lines.append("| - | 0 |")
    lines.append("")

    lines.append("## Move-Level Retrospective Notes")
    lines.append("")
    for r in move_rows:
        title = str(r["move_title"])
        lines.append(f"### {r['ordinal']}. {title}")
        lines.append("")
        lines.append(f"- Lines: {r['start_line']}-{r['end_line']}")
        lines.append(f"- Axis profile: {r['all_axes'] or '-'}")
        if r["focus_text"]:
            lines.append(f"- Focus: {r['focus_text']}")
        if r["probe_sections"]:
            lines.append(f"- Probe anchors: {r['probe_sections']}")

        themes = conn.execute(
            """
            SELECT predicate, weight
            FROM retrospective_move_themes
            WHERE source_id = ? AND ordinal = ?
            ORDER BY weight DESC, predicate ASC
            """,
            (source_id, r["ordinal"]),
        ).fetchall()
        if themes:
            theme_blob = ", ".join(f"{t['predicate']}({t['weight']})" for t in themes)
            lines.append(f"- Theme signals: {theme_blob}")

        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).resolve()
    out_path = Path(args.out).resolve()

    with connect(db_path) as conn:
        source_id = grammar_source_id(conn)
        moves = fetch_moves(conn, source_id)
        if not moves:
            raise RuntimeError("No move sections found (title LIKE 'Move %').")

        ensure_retro_schema(conn)
        replace_retro_rows(conn, source_id, moves, top_themes=args.top_themes)
        write_report(conn, source_id, out_path)
        conn.commit()

        counts = conn.execute(
            """
            SELECT
              (SELECT COUNT(*) FROM retrospective_moves WHERE source_id = ?) AS move_count,
              (SELECT COUNT(*) FROM retrospective_move_themes WHERE source_id = ?) AS theme_count,
              (SELECT COUNT(*) FROM retrospective_axis_transitions WHERE source_id = ?) AS transition_count
            """,
            (source_id, source_id, source_id),
        ).fetchone()

    print(f"db: {db_path}")
    print(f"report: {out_path}")
    print(f"moves: {counts['move_count']}")
    print(f"themes: {counts['theme_count']}")
    print(f"transitions: {counts['transition_count']}")


if __name__ == "__main__":
    main()
