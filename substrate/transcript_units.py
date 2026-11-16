# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A transcript split into the four streams the tmi probes read, on mtools' transcript reader.

⚑ ONE SPELLING OF A PRELUDE FIVE PROBES EACH RE-TYPED (2026-09-24). Every `scratch/tmi_probe*.py`
opened with the same loop over `scratch/transcriptstruct.py`: collect the human turns, the
assistant prose, the tool calls and the tool results, each tagged with its line. The scratch
reader is retired to mtools' `mikemol-transcriptstruct` (handed over 2026-09-23), so the prelude
moves here once, onto the package, and the probes import it.

⚑ THE MAPPING IS mtools' OWN, NOT INFERRED (mtools-91, 2026-09-24):
  * `T.stream`           → `records.read_path`; a record carries its 1-based `.line`.
  * `T.human_text`       → `provenance.classify(r).text` WHEN `.kind == "human"`. Filter on the
                           KIND, never on non-empty text: every other kind carries its own text.
  * `T.envelope_role`    → `classify(r).kind`, a richer vocabulary than the raw role.
  * `T.blocks`           → `blocks.blocks(r)`, whose text is WHOLE — the old 20k/4k caps are gone,
                           so a count over tool text can be larger than the scratch reader's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from mikemol.transcriptstruct import blocks, provenance, records

if TYPE_CHECKING:
    from pathlib import Path

#: One unit: the record's 1-based line and its text.
type Unit = tuple[int, str]


@dataclass(slots=True)
class Units:
    """The four streams, each in file order."""

    human: list[Unit] = field(default_factory=list)
    assistant: list[Unit] = field(default_factory=list)
    tool_use: list[Unit] = field(default_factory=list)
    tool_result: list[Unit] = field(default_factory=list)


def split(path: Path) -> Units:
    """Read a transcript and sort its content into the four streams.

    ⚑ ASSISTANT PROSE IS ONE UNIT PER TEXT BLOCK, and tool calls and results are taken from
    EVERY record, whatever its speaker — the scratch probes did both, and a port that changed
    either would change what they count.
    """
    out = Units()
    for record in records.read_path(path):
        who = provenance.classify(record)
        if who.kind == "human" and who.text:
            out.human.append((record.line, who.text))
        for block in blocks.blocks(record):
            if block.kind == "text" and who.kind == "assistant" and block.text.strip():
                out.assistant.append((record.line, block.text))
            elif block.kind == "tool_use":
                out.tool_use.append((record.line, block.text))
            elif block.kind == "tool_result":
                out.tool_result.append((record.line, block.text))
    return out


def record_texts(path: Path) -> list[tuple[int, str, str]]:
    """Return `(line, speaker kind, joined text blocks)` for every record, whatever its speaker.

    ⚑ tmi_probe3's duplicate-envelope census reads EVERY role's text, not only assistant prose —
    the hazard it measures is the same body arriving under different envelopes.
    """
    out: list[tuple[int, str, str]] = []
    for record in records.read_path(path):
        text = "\n".join(b.text for b in blocks.blocks(record) if b.kind == "text")
        out.append((record.line, provenance.classify(record).kind, text))
    return out


def assistant_turns(units: Units) -> list[Unit]:
    """Return one unit per assistant RECORD, its text blocks newline-joined.

    ⚑ tmi_probe/2/3 joined a record's text blocks before testing emptiness, where tmi_probe4/5
    kept one unit per block. Both shapes are offered so neither probe's counts move in the port.
    """
    joined: dict[int, list[str]] = {}
    for line, text in units.assistant:
        joined.setdefault(line, []).append(text)
    return [(line, "\n".join(parts)) for line, parts in joined.items()]
