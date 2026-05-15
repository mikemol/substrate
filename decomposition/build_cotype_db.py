#!/usr/bin/env python3
"""Build a section-by-section semantic triple database for cotype markdown.

This script parses markdown headings into a section tree and extracts
semantic triples with precise line anchors.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
AXIS_RE = re.compile(r"^\*\*Axis-signature\*\*:\s*(.+)$")
KEYVAL_RE = re.compile(r"^\*\*([^*]+)\*\*:\s*(.+)$")
BULLET_KEYVAL_RE = re.compile(r"^[-*]\s+\*\*([^*]+)\*\*:\s*(.+)$")
ROW_RE = re.compile(r"^\|(.+)\|$")
MOVE_SPLIT_RE = re.compile(r"^(Move\s+[^-\u2014]+)[\u2014-]\s*(.+)$")


def strip_md(text: str) -> str:
    text = text.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@dataclass
class Section:
    section_index: int
    level: int
    title: str
    path: str
    parent_index: int | None
    heading_line: int
    content_start_line: int
    start_line: int
    end_line: int


@dataclass
class Triple:
    section_index: int
    subject: str
    predicate: str
    object: str
    line_start: int
    line_end: int
    evidence_text: str
    method: str
    confidence: float


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def parse_sections(lines: list[str]) -> list[Section]:
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines, start=1):
        m = HEADING_RE.match(line)
        if m:
            headings.append((i, len(m.group(1)), strip_md(m.group(2))))

    sections: list[Section] = []
    stack: list[tuple[int, int, str]] = []

    for idx, (line_no, level, title) in enumerate(headings, start=1):
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_index = stack[-1][1] if stack else None
        parent_path = stack[-1][2] if stack else ""
        path = f"{parent_path} > {title}" if parent_path else title

        end_line = len(lines)
        for nxt_line, _nxt_level, _nxt_title in headings[idx:]:
            if nxt_line > line_no:
                end_line = nxt_line - 1
                break

        section = Section(
            section_index=idx,
            level=level,
            title=title,
            path=path,
            parent_index=parent_index,
            heading_line=line_no,
            content_start_line=min(line_no + 1, len(lines)),
            start_line=line_no,
            end_line=end_line,
        )
        sections.append(section)
        stack.append((level, idx, path))

    return sections


def first_content_line(lines: list[str], section: Section) -> tuple[int, str] | None:
    for i in range(section.content_start_line, section.end_line + 1):
        raw = lines[i - 1].strip()
        if not raw:
            continue
        if raw.startswith("#"):
            continue
        if raw.startswith("|"):
            continue
        if raw.startswith("---"):
            continue
        if raw.startswith("- ") or raw.startswith("* "):
            continue
        if re.match(r"^\d+\.\s+", raw):
            continue
        text = strip_md(raw)
        if text:
            return i, text
    return None


def classify_section(title: str) -> str:
    t = title.lower()
    if t.startswith("move "):
        return "move"
    if "probe state" in t:
        return "probe_state"
    if "shadows" in t:
        return "shadow_catalog"
    if "context" in t:
        return "context"
    if "cumulative status" in t:
        return "status"
    if "result" in t:
        return "result"
    if "verification" in t:
        return "verification"
    return "section"


def iter_table_rows(lines: list[str], section: Section) -> Iterable[tuple[int, list[str]]]:
    for i in range(section.content_start_line, section.end_line + 1):
        raw = lines[i - 1].strip()
        if not raw.startswith("|"):
            continue
        if set(raw.replace("|", "").strip()) <= {"-", ":"}:
            continue
        m = ROW_RE.match(raw)
        if not m:
            continue
        cells = [strip_md(c) for c in m.group(1).split("|")]
        yield i, cells


def extract_triples(lines: list[str], sections: list[Section]) -> list[Triple]:
    triples: list[Triple] = []

    for s in sections:
        section_subject = s.title

        triples.append(
            Triple(
                section_index=s.section_index,
                subject=section_subject,
                predicate="section_kind",
                object=classify_section(s.title),
                line_start=s.heading_line,
                line_end=s.heading_line,
                evidence_text=lines[s.heading_line - 1],
                method="heading_classifier",
                confidence=0.99,
            )
        )

        move_match = MOVE_SPLIT_RE.match(s.title)
        if move_match:
            triples.append(
                Triple(
                    section_index=s.section_index,
                    subject=strip_md(move_match.group(1)),
                    predicate="focuses_on",
                    object=strip_md(move_match.group(2)),
                    line_start=s.heading_line,
                    line_end=s.heading_line,
                    evidence_text=lines[s.heading_line - 1],
                    method="move_title_split",
                    confidence=0.98,
                )
            )

        lead = first_content_line(lines, s)
        if lead:
            lead_line, lead_text = lead
            triples.append(
                Triple(
                    section_index=s.section_index,
                    subject=section_subject,
                    predicate="states",
                    object=lead_text,
                    line_start=lead_line,
                    line_end=lead_line,
                    evidence_text=lines[lead_line - 1],
                    method="lead_sentence",
                    confidence=0.8,
                )
            )

        for i in range(s.content_start_line, s.end_line + 1):
            raw = lines[i - 1].strip()
            if not raw:
                continue

            m_axis = AXIS_RE.match(raw)
            if m_axis:
                triples.append(
                    Triple(
                        section_index=s.section_index,
                        subject=section_subject,
                        predicate="has_axis_signature",
                        object=strip_md(m_axis.group(1)),
                        line_start=i,
                        line_end=i,
                        evidence_text=lines[i - 1],
                        method="axis_signature",
                        confidence=1.0,
                    )
                )
                continue

            m_keyval = KEYVAL_RE.match(raw)
            if m_keyval:
                key = strip_md(m_keyval.group(1)).lower().replace(" ", "_")
                val = strip_md(m_keyval.group(2))
                triples.append(
                    Triple(
                        section_index=s.section_index,
                        subject=section_subject,
                        predicate=f"has_{key}",
                        object=val,
                        line_start=i,
                        line_end=i,
                        evidence_text=lines[i - 1],
                        method="inline_keyval",
                        confidence=0.96,
                    )
                )
                continue

            m_bkeyval = BULLET_KEYVAL_RE.match(raw)
            if m_bkeyval:
                key = strip_md(m_bkeyval.group(1)).lower().replace(" ", "_")
                val = strip_md(m_bkeyval.group(2))
                triples.append(
                    Triple(
                        section_index=s.section_index,
                        subject=section_subject,
                        predicate=f"bullet_{key}",
                        object=val,
                        line_start=i,
                        line_end=i,
                        evidence_text=lines[i - 1],
                        method="bullet_keyval",
                        confidence=0.95,
                    )
                )

        rows = list(iter_table_rows(lines, s))
        if rows:
            header_cells = rows[0][1]
            header_norm = [c.lower().replace(" ", "_") for c in header_cells]
            for row_line, cells in rows[1:]:
                if len(cells) != len(header_cells):
                    continue
                if all(not c for c in cells):
                    continue
                row_subject = cells[0] if cells and cells[0] else section_subject
                for col_name, col_val in zip(header_norm[1:], cells[1:]):
                    if not col_val:
                        continue
                    predicate = f"table_{col_name}"
                    triples.append(
                        Triple(
                            section_index=s.section_index,
                            subject=row_subject,
                            predicate=predicate,
                            object=col_val,
                            line_start=row_line,
                            line_end=row_line,
                            evidence_text=lines[row_line - 1],
                            method="table_row",
                            confidence=0.9,
                        )
                    )

    return triples


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS sources (
            source_id INTEGER PRIMARY KEY,
            source_path TEXT NOT NULL UNIQUE,
            source_sha256 TEXT NOT NULL,
            line_count INTEGER NOT NULL,
            generated_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sections (
            section_id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            section_index INTEGER NOT NULL,
            level INTEGER NOT NULL,
            title TEXT NOT NULL,
            path TEXT NOT NULL,
            parent_index INTEGER,
            heading_line INTEGER NOT NULL,
            content_start_line INTEGER NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );

        CREATE TABLE IF NOT EXISTS triples (
            triple_id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            section_index INTEGER NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            evidence_line_start INTEGER NOT NULL,
            evidence_line_end INTEGER NOT NULL,
            evidence_text TEXT NOT NULL,
            method TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );

        CREATE INDEX IF NOT EXISTS idx_sections_source ON sections(source_id);
        CREATE INDEX IF NOT EXISTS idx_sections_path ON sections(path);
        CREATE INDEX IF NOT EXISTS idx_triples_source ON triples(source_id);
        CREATE INDEX IF NOT EXISTS idx_triples_section ON triples(source_id, section_index);
        CREATE INDEX IF NOT EXISTS idx_triples_spo ON triples(subject, predicate, object);
        """
    )


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def upsert_source(conn: sqlite3.Connection, source_path: Path, line_count: int) -> int:
    source_sha = compute_sha256(source_path)
    conn.execute(
        """
        INSERT INTO sources (source_path, source_sha256, line_count)
        VALUES (?, ?, ?)
        ON CONFLICT(source_path)
        DO UPDATE SET source_sha256=excluded.source_sha256,
                      line_count=excluded.line_count,
                      generated_at_utc=datetime('now')
        """,
        (str(source_path), source_sha, line_count),
    )
    source_id = conn.execute(
        "SELECT source_id FROM sources WHERE source_path = ?",
        (str(source_path),),
    ).fetchone()[0]
    return int(source_id)


def replace_decomposition(
    conn: sqlite3.Connection,
    source_id: int,
    sections: list[Section],
    triples: list[Triple],
) -> None:
    conn.execute("DELETE FROM sections WHERE source_id = ?", (source_id,))
    conn.execute("DELETE FROM triples WHERE source_id = ?", (source_id,))

    conn.executemany(
        """
        INSERT INTO sections (
            source_id, section_index, level, title, path, parent_index,
            heading_line, content_start_line, start_line, end_line
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                source_id,
                s.section_index,
                s.level,
                s.title,
                s.path,
                s.parent_index,
                s.heading_line,
                s.content_start_line,
                s.start_line,
                s.end_line,
            )
            for s in sections
        ],
    )

    conn.executemany(
        """
        INSERT INTO triples (
            source_id, section_index, subject, predicate, object,
            evidence_line_start, evidence_line_end, evidence_text,
            method, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                source_id,
                t.section_index,
                t.subject,
                t.predicate,
                t.object,
                t.line_start,
                t.line_end,
                t.evidence_text,
                t.method,
                t.confidence,
            )
            for t in triples
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="cotype-free-self-extending-grammar.md",
        help="Path to markdown source file",
    )
    parser.add_argument(
        "--db",
        default="decomposition/cotype_decomposition.sqlite",
        help="Output sqlite database path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.source).resolve()
    db_path = Path(args.db).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    lines = read_lines(source_path)
    sections = parse_sections(lines)
    triples = extract_triples(lines, sections)

    with sqlite3.connect(db_path) as conn:
        ensure_schema(conn)
        source_id = upsert_source(conn, source_path, len(lines))
        replace_decomposition(conn, source_id, sections, triples)
        conn.commit()

        section_count = conn.execute(
            "SELECT COUNT(*) FROM sections WHERE source_id = ?", (source_id,)
        ).fetchone()[0]
        triple_count = conn.execute(
            "SELECT COUNT(*) FROM triples WHERE source_id = ?", (source_id,)
        ).fetchone()[0]

    print(f"source: {source_path}")
    print(f"db: {db_path}")
    print(f"lines: {len(lines)}")
    print(f"sections: {section_count}")
    print(f"triples: {triple_count}")


if __name__ == "__main__":
    main()
