#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""telescope_text.py — the LIFTED shared skeleton (∩) of the record-reparameterize tools, extracted by the
dedup machinery (jea_pysim --clusters flagged `_strip_comment` IDENTICAL across record_def_edit.py and
reparameterize_record.py; `_split_top` was already shared BY REFERENCE — the very import that made the two
tools circular). This is the brace/paren/depth-aware Agda-surface-text kit both consume; single-sourcing it
here breaks the record_def_edit ⇄ reparameterize_record cycle BY CONSTRUCTION.

RESIDUE kept in each tool (the symmetric-difference halves, NOT merged here):
  • reparameterize_record.py — `transform` (the `= record{}` + positional-ctor rewrite branches), `_block_end`
    (positional-application span scan), the codemod CLI.
  • record_def_edit.py — `parse_record_def`, `codomain_is_set`, `drop_one_universe`, its record-def CLI.
"""
import re

OPEN, CLOSE = "([{", ")]}"


def _match_brace(s, i):
    """s[i] == '{'; return index of the matching '}'."""
    depth = 0
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _depth_iter(s):
    """the shared paren-depth primitive of _split_top / _parse_field (the size-8 subtree the sweep
    enumerated in BOTH — lifted, not dismissed as floor): yield (i, ch, depth) where depth is the
    bracket-nesting AFTER applying ch (a CLOSE reports the level it drops to, an OPEN the level it enters).
    Separator chars (`;`/`→`/`:`/`=`/space) are never brackets, so they carry the running depth verbatim."""
    depth = 0
    for i, ch in enumerate(s):
        if ch in OPEN:
            depth += 1
        elif ch in CLOSE:
            depth -= 1
        yield i, ch, depth


def _split_top(s, sep):
    """split s on `sep` at bracket-depth 0."""
    out, cur = [], ""
    for _, ch, depth in _depth_iter(s):
        if ch == sep and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def _parse_field(f):
    """`name = value` split on the first depth-0 '='."""
    for i, ch, depth in _depth_iter(f):
        if ch == "=" and depth == 0:
            return f[:i].strip(), f[i + 1:].strip()
    return f.strip(), None


def _arg(v):
    """paren-wrap a carrier VALUE for use as a type argument if it isn't atomic."""
    v = v.strip()
    if v and (" " in v or "→" in v) and not (v[0] in "([{" and v[-1] in ")]}"):
        return f"({v})"
    return v


def _strip_comment(line):
    """drop an inline `--…` Agda comment (naive: first ` --`/leading `--`; block comments not handled)."""
    m = re.search(r"(?:^|\s)--", line)
    return line[:m.start()] if m else line
