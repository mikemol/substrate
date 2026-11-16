#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Rewrite one section of a markdown document — a LINE SPLICE, addressed structurally.

⚑⚑⚑ THE AST ANSWERS *WHERE*, RAW LINES CARRY *WHAT*. An AST render is admissible here — a
first argument against it (that round-tripping reports 1,215 changed lines on one SKILL.md) was
a figure from ONE instrument quoted as a fact about ANOTHER: round-trip measures drift under a
DEFAULT writer, fixpoint measures convergence under the CONFIGURED one, and both those files are
already fixpoints. The operator's reading was that a rewritten file is *"compliant-by-
construction"*, which is true.

⚑⚑ SO THE SPLICE IS CHOSEN FOR BLAST RADIUS, NOT CORRECTNESS. A whole-document render turns a
five-line edit into a whole-file diff no reviewer can read, and silently bundles a not-yet-
converged file's migration into an unrelated change. A splice touches the lines it means to. The
normalization is worth having and is a SEPARATE, REVIEWABLE migration.

⚑⚑ THE HEADING LINE IS NEVER TOUCHED. It is the anchor every other reader resolves against, so
rewriting it would silently orphan the references pointing at it. Body only — a rename is a
different verb, and this module does not have it.

⚑⚑ AND APPEND IS THE BOUNDED FORM OF WHAT `>>` DOES UNBOUNDED. A shell append lands at
end-of-file, which for a sectioned document is almost never where the content belongs — it
silently migrates under whatever heading happens to be last. This lands it in a NAMED section and
fails if that place is gone. The structural-query hook refuses `cat >>` and, before this mode
existed, could only name a READER, which made a correct refusal look like a bug (reported by
cassian-observability). **A refusal that names an owning tool with no write mode is a gate that
blocks without routing.**

⚑ THESE FUNCTIONS RETURN TEXT; THEY DO NOT WRITE. The caller decides, so a dry run and an apply
share one derivation rather than being two code paths that can disagree.

⚑ EXTRACTED FROM `scratch/mdstruct.py` (⟡mdstruct-n-split), file-per-mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.mdstruct import spans as md_spans

if TYPE_CHECKING:
    from pathlib import Path


def replace_section(
    path: Path,
    needle: str,
    body: str,
    *,
    exact: bool = False,
) -> tuple[str, md_spans.Span]:
    """Return the document with ONE section's body replaced, and the span it targeted.

    ⚑ THE SPAN IS RETURNED SO THE CALLER CAN REPORT WHAT IT HIT. A write that says only
    "done" leaves a reader to re-derive which section moved.

    ⚑ `exact` FORWARDS TO THE MATCHER, for a heading wholly contained in another — see
    `md_spans.find_section`. A write path that cannot address every section has sections
    it can only refuse.
    """
    span = md_spans.find_section(path, needle, exact=exact)
    lines = path.read_text(encoding="utf-8").split("\n")
    new = lines[: span.start] + body.rstrip("\n").split("\n") + lines[span.end - 1 :]
    return "\n".join(new), span


def append_to_section(
    path: Path,
    needle: str,
    body: str,
    *,
    exact: bool = False,
) -> tuple[str, md_spans.Span]:
    """Return the document with `body` appended INSIDE one section, before the next heading.

    ⚑ TRAILING BLANK LINES ARE PRESERVED BENEATH THE INSERTION, not swallowed. Markdown block
    separation is load-bearing, and an append that eats the blank line before the next heading
    produces a document that renders differently from the one the author reviewed.

    ⚑ `exact` FORWARDS TO THE MATCHER — see `replace_section`.
    """
    span = md_spans.find_section(path, needle, exact=exact)
    lines = path.read_text(encoding="utf-8").split("\n")
    body_lines = lines[span.start : span.end - 1]

    tail = 0
    while tail < len(body_lines) and not body_lines[len(body_lines) - 1 - tail].strip():
        tail += 1
    keep = body_lines[: len(body_lines) - tail] if tail else body_lines
    blanks = body_lines[len(body_lines) - tail :] if tail else []

    new = (
        lines[: span.start]
        + keep
        + [""]
        + body.rstrip("\n").split("\n")
        + blanks
        + lines[span.end - 1 :]
    )
    return "\n".join(new), span
