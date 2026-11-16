#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""telescope_lib.py — the LIFTED shared skeleton of the telescope-threading migrators, extracted by the
dedup machinery (jea_pysim --clusters found `import_span` identical + the binder-rewrite/variable-block core
81.4%-shared between scratch/telescope_migrate.py [UPArrow] and scratch/telescope_migrate_gen.py [generalized]).
Single-source for the common part; each migrator keeps only its record-specific tail.

A CARRIER SPEC is (suffix, type_template): the per-binder fresh carrier is `{suffix}{v}`, typed by
type_template with `{v}` substituted (may reference earlier carriers of the same binder — e.g. UPArrow's
W = `S{v} → T{v} → Set`)."""
import re


def import_span(lines):
    """indices of the last line belonging to any (multi-line) import block."""
    end, i = -1, 0
    while i < len(lines):
        if lines[i].startswith("open import") or lines[i].startswith("import "):
            j = i
            while j + 1 < len(lines) and lines[j + 1][:1] in (" ", "\t") and lines[j + 1].strip():
                j += 1
            end = j; i = j + 1
        else:
            i += 1
    return end


def thread_binders(src, record, carriers, new_record=None):
    """Thread `{v… : record}` / `(v… : record)` binders → `{v : new_record C1{v} C2{v}…}` and emit a
    `private variable` block (after the import section) declaring every fresh carrier at its type.
    `new_record` defaults to `record` (the new records keep their name + gain params); pass a distinct name
    for the UPArrow case where the reparameterized record is renamed (UPArrow → UPArrowP).
    Returns (new_src, vars_seen) — vars_seen lets a caller add record-specific tails keyed on the binders."""
    new_record = new_record or record
    lines = src.split("\n")
    vars_seen = []
    # ⟡tele-binder-applied: the record may appear BARE (`{v : UPArrow}`) or APPLIED (`(b : Brick T)`).
    # Group 3 captures any existing applied args between the record name and the close bracket — a
    # non-bracket run (`\b[^{}()]*?`), which is "" for the bare form and " T" for `Brick T`. (A binder whose
    # applied args THEMSELVES contain a bracket, e.g. `Brick (f x)`, won't match — SAFE under-match, left as-is.)
    binder_re = re.compile(r'([{(])\s*([A-Za-zα-ω][^:{}()]*?)\s*:\s*' + re.escape(record) + r'\b([^{}()]*?)\s*([)}])')

    def repl_binder(m):
        ob, names, existing, cb = m.group(1), m.group(2).split(), m.group(3).strip(), m.group(4)
        head = f"{new_record} {existing}" if existing else new_record   # keep existing applied args, then append carriers
        parts = []
        for v in names:
            if v not in vars_seen:
                vars_seen.append(v)
            args = " ".join(f"{suf}{v}" for suf, _ in carriers)
            parts.append(f"{v} : {head} {args}")
        sep = "} {" if ob == "{" else ") ("
        return ob + sep.join(parts) + cb

    lines = binder_re.sub(repl_binder, "\n".join(lines)).split("\n")

    if vars_seen:
        end = import_span(lines)
        block = ["", f"-- ⟡set1-rp: telescope carriers for {record} (auto).", "private variable"]
        for suf, tmpl in carriers:
            if "{v}" in tmpl:
                for v in vars_seen:
                    block.append(f"  {suf}{v} : " + tmpl.replace("{v}", v))
            else:
                block.append("  " + " ".join(f"{suf}{v}" for v in vars_seen) + f" : {tmpl}")
        lines[end + 1:end + 1] = block

    return "\n".join(lines), vars_seen
