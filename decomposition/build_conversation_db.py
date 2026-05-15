#!/usr/bin/env python3
"""Build conversation decomposition database from MHTML transcript.

Pipeline (per the design in mhtml_conversation_decomposition_design.md):
  S1: MHTML -> decoded HTML -> markdown transcript
  S2: HTML -> turns (role + markdown content + char anchors in transcript)
  S3: per-turn reference extraction
  S4: SQLite persistence (extends cotype_decomposition.sqlite)
"""

from __future__ import annotations

import argparse
import email
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from email import policy
from pathlib import Path
from typing import List, Tuple

from bs4 import BeautifulSoup, Tag
import html2text


# Selectors derived from the Claude.ai DOM (Chrome MHTML export, 2026-05-15).
USER_CLASS_MARKER = "!font-user-message"
ASSISTANT_CLASS_MARKER = "font-claude-response"
ASSISTANT_INNER_MARKER = "font-claude-response-body"


# Reference patterns (S3). See design doc § 4.
M_MOVE_RE = re.compile(r"\bM(\d+)(?:\s*v(\d+(?:\.\d+)?))?\b")
CONCEPT_SLUG_RE = re.compile(r"\bC-[a-z][a-z0-9-]+\b")
CLAIM_SLUG_RE = re.compile(r"\bK-[a-z][a-z0-9-]+\b")
VERIFIER_NAME_RE = re.compile(r"\b(verify_[a-z][a-z0-9_]+)\b")
FILE_PATH_RE = re.compile(
    r"\b([\w][\w/.-]*\.(?:py|md|sqlite|mhtml|txt|sql))(?::(\d+)(?:-(\d+))?)?\b"
)


@dataclass
class Turn:
    ordinal: int
    role: str            # 'user' or 'assistant'
    char_start: int      # in transcript output
    char_end: int
    content_md: str


@dataclass
class Reference:
    turn_ordinal: int
    ref_type: str        # 'm_move' | 'concept' | 'claim' | 'verifier' | 'file_path' | 'line_anchor'
    ref_target: str
    char_offset: int     # within the turn's content_md
    confidence: float


def decode_mhtml(path: Path) -> str:
    """S1: extract the text/html part from MHTML and decode quoted-printable.

    Uses raw payload + explicit UTF-8 decode because the MHTML's Content-Type
    omits charset; ``get_content()`` defaults to ASCII/latin-1 in that case
    and corrupts non-ASCII (em-dash, subscripts, →, etc.) as U+FFFD.
    """
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_payload(decode=True).decode("utf-8", errors="replace")
    raise ValueError(f"No text/html part found in {path}")


def _html_to_markdown(elem: Tag) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = True
    h.protect_links = True
    h.unicode_snob = True
    h.bypass_tables = False
    md = h.handle(str(elem)).strip()
    # Collapse runs of >2 blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def is_user_turn(elem: Tag) -> bool:
    cls = elem.get("class") or []
    return USER_CLASS_MARKER in " ".join(cls)


def is_assistant_turn_outer(elem: Tag) -> bool:
    cls = elem.get("class") or []
    cls_text = " ".join(cls)
    return ASSISTANT_CLASS_MARKER in cls_text and ASSISTANT_INNER_MARKER not in cls_text


def extract_turn_elements(html: str) -> List[Tuple[str, Tag]]:
    """S2 (locator): scan doc-order for turn outer elements."""
    soup = BeautifulSoup(html, "html.parser")
    turns: List[Tuple[str, Tag]] = []
    for elem in soup.find_all(True):
        if is_user_turn(elem):
            turns.append(("user", elem))
        elif is_assistant_turn_outer(elem):
            turns.append(("assistant", elem))
    return turns


def build_transcript_and_turns(html: str) -> Tuple[str, List[Turn]]:
    """S1+S2 (output): produce transcript markdown and Turn records with anchors."""
    turn_elems = extract_turn_elements(html)
    parts: List[str] = []
    turns: List[Turn] = []
    cursor = 0
    for ordinal, (role, elem) in enumerate(turn_elems, start=1):
        content_md = _html_to_markdown(elem)
        if not content_md:
            continue
        header = f"\n\n## Turn {ordinal} — {role}\n\n"
        body = content_md + "\n"
        block = header + body
        char_start = cursor + len(header)
        char_end = char_start + len(body)
        parts.append(block)
        cursor += len(block)
        turns.append(Turn(
            ordinal=ordinal,
            role=role,
            char_start=char_start,
            char_end=char_end,
            content_md=content_md,
        ))
    preamble = "# Conversation transcript\n\nGenerated from MHTML export.\n"
    # Re-anchor cursor positions to account for preamble offset
    offset = len(preamble)
    for t in turns:
        t.char_start += offset
        t.char_end += offset
    transcript = preamble + "".join(parts)
    return transcript, turns


def extract_references(turns: List[Turn]) -> List[Reference]:
    """S3: detect cross-references inside each turn's markdown."""
    refs: List[Reference] = []
    for t in turns:
        md = t.content_md
        # M-move tokens
        for m in M_MOVE_RE.finditer(md):
            target = f"M{m.group(1)}"
            if m.group(2):
                target += f" v{m.group(2)}"
            refs.append(Reference(
                turn_ordinal=t.ordinal,
                ref_type="m_move",
                ref_target=target,
                char_offset=m.start(),
                confidence=0.95,
            ))
        # Concept slugs
        for m in CONCEPT_SLUG_RE.finditer(md):
            refs.append(Reference(
                turn_ordinal=t.ordinal,
                ref_type="concept",
                ref_target=m.group(0),
                char_offset=m.start(),
                confidence=0.9,
            ))
        # Claim slugs
        for m in CLAIM_SLUG_RE.finditer(md):
            refs.append(Reference(
                turn_ordinal=t.ordinal,
                ref_type="claim",
                ref_target=m.group(0),
                char_offset=m.start(),
                confidence=0.9,
            ))
        # Verifier names
        for m in VERIFIER_NAME_RE.finditer(md):
            refs.append(Reference(
                turn_ordinal=t.ordinal,
                ref_type="verifier",
                ref_target=m.group(1),
                char_offset=m.start(),
                confidence=0.85,
            ))
        # File paths + line anchors
        for m in FILE_PATH_RE.finditer(md):
            path = m.group(1)
            refs.append(Reference(
                turn_ordinal=t.ordinal,
                ref_type="file_path",
                ref_target=path,
                char_offset=m.start(),
                confidence=0.8,
            ))
            if m.group(2):
                line_target = path + ":" + m.group(2)
                if m.group(3):
                    line_target += "-" + m.group(3)
                refs.append(Reference(
                    turn_ordinal=t.ordinal,
                    ref_type="line_anchor",
                    ref_target=line_target,
                    char_offset=m.start(),
                    confidence=0.85,
                ))
    return refs


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id  INTEGER PRIMARY KEY,
            source_uri       TEXT NOT NULL UNIQUE,
            mhtml_path       TEXT NOT NULL,
            mhtml_sha256     TEXT NOT NULL,
            snapshot_date    TEXT NOT NULL,
            transcript_path  TEXT,
            turn_count       INTEGER NOT NULL,
            generated_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS turns (
            turn_id          INTEGER PRIMARY KEY,
            conversation_id  INTEGER NOT NULL,
            ordinal          INTEGER NOT NULL,
            role             TEXT NOT NULL,
            char_start       INTEGER NOT NULL,
            char_end         INTEGER NOT NULL,
            content_md       TEXT NOT NULL,
            content_sha256   TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
        );

        CREATE TABLE IF NOT EXISTS turn_references (
            reference_id     INTEGER PRIMARY KEY,
            turn_id          INTEGER NOT NULL,
            ref_type         TEXT NOT NULL,
            ref_target       TEXT NOT NULL,
            char_offset      INTEGER NOT NULL,
            confidence       REAL NOT NULL DEFAULT 1.0,
            FOREIGN KEY (turn_id) REFERENCES turns(turn_id)
        );

        CREATE INDEX IF NOT EXISTS idx_turns_conv ON turns(conversation_id, ordinal);
        CREATE INDEX IF NOT EXISTS idx_refs_turn ON turn_references(turn_id);
        CREATE INDEX IF NOT EXISTS idx_refs_target ON turn_references(ref_type, ref_target);
    """)


def extract_metadata(html: str) -> Tuple[str, str]:
    """Extract source_uri and snapshot date hints from HTML / MHTML envelope."""
    m = re.search(r"claude\.ai/chat/[a-f0-9-]+", html)
    source_uri = "https://" + m.group(0) if m else ""
    return source_uri, ""


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def upsert_conversation(
    conn: sqlite3.Connection,
    source_uri: str,
    mhtml_path: Path,
    snapshot_date: str,
    transcript_path: Path,
    turn_count: int,
) -> int:
    sha = compute_sha256(mhtml_path)
    conn.execute("""
        INSERT INTO conversations (source_uri, mhtml_path, mhtml_sha256,
                                   snapshot_date, transcript_path, turn_count)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_uri) DO UPDATE SET
            mhtml_path=excluded.mhtml_path,
            mhtml_sha256=excluded.mhtml_sha256,
            snapshot_date=excluded.snapshot_date,
            transcript_path=excluded.transcript_path,
            turn_count=excluded.turn_count,
            generated_at_utc=datetime('now')
    """, (source_uri, str(mhtml_path), sha, snapshot_date, str(transcript_path), turn_count))
    row = conn.execute(
        "SELECT conversation_id FROM conversations WHERE source_uri = ?",
        (source_uri,),
    ).fetchone()
    return int(row[0])


def replace_turns_and_refs(
    conn: sqlite3.Connection,
    conversation_id: int,
    turns: List[Turn],
    refs: List[Reference],
) -> None:
    conn.execute("""
        DELETE FROM turn_references WHERE turn_id IN
            (SELECT turn_id FROM turns WHERE conversation_id = ?)
    """, (conversation_id,))
    conn.execute("DELETE FROM turns WHERE conversation_id = ?", (conversation_id,))

    ordinal_to_turn_id = {}
    for t in turns:
        content_sha = hashlib.sha256(t.content_md.encode("utf-8")).hexdigest()
        cur = conn.execute("""
            INSERT INTO turns (conversation_id, ordinal, role, char_start, char_end,
                               content_md, content_sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (conversation_id, t.ordinal, t.role, t.char_start, t.char_end,
              t.content_md, content_sha))
        ordinal_to_turn_id[t.ordinal] = cur.lastrowid

    conn.executemany("""
        INSERT INTO turn_references (turn_id, ref_type, ref_target, char_offset, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, [(ordinal_to_turn_id[r.turn_ordinal], r.ref_type, r.ref_target,
           r.char_offset, r.confidence) for r in refs])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mhtml", default="scratch/Numpy-backed SPPF datastructure design - Claude.mhtml")
    parser.add_argument("--transcript", default="decomposition/conversation_transcript.md")
    parser.add_argument("--db", default="decomposition/cotype_decomposition.sqlite")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mhtml_path = Path(args.mhtml).resolve()
    transcript_path = Path(args.transcript).resolve()
    db_path = Path(args.db).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    html = decode_mhtml(mhtml_path)
    transcript, turns = build_transcript_and_turns(html)
    refs = extract_references(turns)

    transcript_path.write_text(transcript, encoding="utf-8")

    source_uri, snapshot_date = extract_metadata(html)
    if not source_uri:
        source_uri = f"file://{mhtml_path}"

    with sqlite3.connect(db_path) as conn:
        ensure_schema(conn)
        conv_id = upsert_conversation(
            conn, source_uri, mhtml_path, snapshot_date, transcript_path, len(turns),
        )
        replace_turns_and_refs(conn, conv_id, turns, refs)
        conn.commit()

        ref_counts = conn.execute("""
            SELECT ref_type, COUNT(*) FROM turn_references
            WHERE turn_id IN (SELECT turn_id FROM turns WHERE conversation_id = ?)
            GROUP BY ref_type ORDER BY 2 DESC
        """, (conv_id,)).fetchall()

    print(f"mhtml: {mhtml_path}")
    print(f"transcript: {transcript_path}")
    print(f"db: {db_path}")
    print(f"source_uri: {source_uri}")
    print(f"turns: {len(turns)}  ({sum(1 for t in turns if t.role == 'user')} user, "
          f"{sum(1 for t in turns if t.role == 'assistant')} assistant)")
    print(f"references: {len(refs)}")
    for rtype, n in ref_counts:
        print(f"  {rtype}: {n}")


if __name__ == "__main__":
    main()
