#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""record_def_edit.py — ⟡tele-record-edit: MECHANICAL record-definition reparameterize generator (source-level).
Given a record def, classify each FIELD by codomain (`→ Set` ⇒ MUST-MOVE to a param; else STAY), emit the new
record header (orig params ++ moved-fields-as-params in field order) + the STAYED fields + a level with one
universe successor dropped. Complements reparameterize_record.py (which rewrites INSTANCES): this handles the
RECORD DEF. Reuses reparameterize_record.py's `_split_top` for depth-0 splitting.

Usage: record_def_edit.py <record.agda> <RecordName>   → prints the new header + moved/stayed/positions + level.
"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# the shared brace/depth-aware Agda-text kit (∩, lifted by the dedup machinery — dedups _strip_comment +
# breaks the record_def_edit ⇄ reparameterize_record import cycle that used to pull _split_top back here).
from telescope_text import _split_top, _strip_comment


def parse_record_def(src, name):
    """→ (orig_params_text, [(fname, ftype)], level_text, ctor_name). Fields in declaration order; `a b c : T`
    shorthand expanded; multi-line field types joined; interspersed `--` comment lines skipped."""
    HEAD = re.compile(r"(?ms)^record\s+" + re.escape(name) + r"\b(?P<hdr>.*?)\bwhere\b")
    m = HEAD.search(src)
    if not m:
        sys.exit(f"record {name} not found")
    # split the header at the DEPTH-0 ':' (the record's level annotation) — the ':' inside param
    # groups like `(G : Set ℓ)` / `{… : Set}` are at depth>0, so _split_top skips them.
    hparts = _split_top(m.group("hdr"), ":")
    orig_params = hparts[0].strip()
    level_text = ":".join(hparts[1:]).strip() if len(hparts) > 1 else ""
    after = src[m.end():]
    cm = re.search(r"(?m)^\s*constructor\s+(\S+)", after)
    ctor = cm.group(1) if cm else None
    fkw = re.search(r"(?m)^(\s*)field\b", after)
    if not fkw:
        return orig_params, [], level_text, ctor
    tail = after[fkw.end():]
    lines = tail.split("\n")
    # field-block: stop at first col-0 non-blank OR `open <name>`; skip full-line comments
    body = []
    for ln in lines[1:] if lines and not lines[0].strip() else lines:
        if re.match(r"\S", ln) or re.match(r"^\s*open\s+" + re.escape(name) + r"\b", ln):
            break
        body.append(ln)
    # field_col = indent of the first non-comment non-blank field line
    field_col = None
    for ln in body:
        s = ln.strip()
        if s and not s.startswith("--"):
            field_col = len(ln) - len(ln.lstrip())
            break
    fields, cur = [], ""

    def flush(entry):
        entry = entry.strip()
        if not entry:
            return
        parts = _split_top(entry, ":")
        if len(parts) < 2:
            return
        lhs, rhs = parts[0], ":".join(parts[1:]).strip()
        rhs = " ".join(rhs.split())
        for nm in lhs.split():
            fields.append((nm, rhs))

    for ln in body:
        raw = _strip_comment(ln)
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip())
        is_new = (indent == field_col) and (len(_split_top(raw, ":")) >= 2)
        if is_new:
            flush(cur)
            cur = raw
        else:
            cur += " " + raw.strip()
    flush(cur)
    return orig_params, fields, level_text, ctor


def codomain_is_set(ftype):
    """Peel top-level `→` to the codomain; unwrap a fully-parenthesized tail and re-peel (e.g. the
    `(G → Set ℓ)` in `Fin n → (G → Set ℓ)` — a curried predicate whose ultimate codomain is Set)."""
    tail = _split_top(ftype, "→")[-1].strip()
    while tail[:1] == "(" and tail[-1:] == ")" and len(_split_top(tail, "→")) == 1:
        tail = _split_top(tail[1:-1].strip(), "→")[-1].strip()
    head = tail.split()[0] if tail.split() else ""
    return head in {"Set", "Setω", "Set₁"} or tail.startswith("Set ")


def drop_one_universe(level_text):
    """→ (new_level, needs_review). Strip the SINGLE outermost lsuc/suc wrapping the whole level arg,
    KEEPING the inner's own parens (`Set (suc (ℓ⊔ℓ′))`→`Set (ℓ⊔ℓ′)`, NOT `Set ℓ⊔ℓ′`)."""
    if level_text == "Set₁":
        return "Set", False
    m = re.match(r"^Set\s*\((?P<inner>.*)\)\s*$", level_text)
    if m:
        inner = m.group("inner").strip()
        w = re.match(r"^(lsuc|suc)\s+(?P<rest>.*)$", inner)
        if w:
            rest = w.group("rest").strip()
            if re.search(r"\b(lsuc|suc)\b", rest) and "⊔" in rest:
                return level_text, True                      # multiple INDEPENDENT successors → HAND
            atomic = (" " not in rest and "⊔" not in rest)
            paren = rest[:1] == "(" and rest[-1:] == ")"
            return (f"Set {rest}" if (atomic or paren) else f"Set ({rest})"), False
        return level_text, True
    return level_text, True


def main():
    recfile, name = sys.argv[1], sys.argv[2]
    src = open(recfile).read()
    orig_params, fields, level_text, ctor = parse_record_def(src, name)
    moved = [(fn, ft) for fn, ft in fields if codomain_is_set(ft)]
    stayed = [(fn, ft) for fn, ft in fields if not codomain_is_set(ft)]
    moved_positions = [i for i, (fn, ft) in enumerate(fields) if codomain_is_set(ft)]
    new_level, review = drop_one_universe(level_text)

    print(f"# {name}: {len(fields)} fields → MOVE {len(moved)}, STAY {len(stayed)}")
    print(f"# moved_positions = {moved_positions}")
    print(f"# level: {level_text!r} → {new_level!r}" + ("   ⚠ REVIEW (multi-successor)" if review else ""))
    print(f"# CARRIERS (for reparameterize_record.py) = {','.join(fn for fn, _ in moved)}\n")
    np = (orig_params + " " if orig_params else "") + " ".join(f"({fn} : {ft})" for fn, ft in moved)
    print(f"record {name} {np} : {new_level} where")
    if ctor:
        print(f"  constructor {ctor}")
    print("  field")
    for fn, ft in stayed:
        print(f"    {fn} : {ft}")


if __name__ == "__main__":
    main()
