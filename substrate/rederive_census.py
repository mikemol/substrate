# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Census the sites that RE-DERIVE an authority the tree already owns.

⚑⚑⚑ THE DRAIN THIS BEGINS WAS CHOSEN AFTER A SURVEY INVERTED THE ARC'S FRAMING (gate-F81).
Asking both readiness axes across six gates found every one NOT SWAPPABLE for the SAME reason —
the per-file gate refuses the edit at 127, 190, 300, 585 findings. Import packaging was never the
binding constraint, and the one gate that swapped did so because it happened to be editable. So
the work is draining a consumer, and this file is the cheapest one's first unit.

⚑⚑ EVERY MOTIF HERE IS A GUARD THAT FAILED ON THE INSTANCE IT WAS WRITTEN FROM, and the origin
records five rounds of it. *A guard written from the instance passes on everything except the
instance.* The measured cases:

  * `importname` was written as a FIXED PREFIX and missed four live survivors, because they
    write an alternation between the keyword and the capture. The identical defect in the
    sibling unit test let it pass while all four stood.
  * `declscan` matched the non-capturing spelling — the one that had just been fixed — and
    missed the capturing form, which six of nine live files use.
  * The `wordbound` and `renameclause` patterns were first written through nested shell
    escaping and never run against a real line, missing every live instance. They were rebuilt
    against five live witnesses, and that validation is what the suite keeps.

⚑⚑⚑ THE KEY IS ORDINAL, NOT LINE-NUMBERED, AND THAT WAS A MEASURED DEFECT. Keying on
`<relpath>:<line>` makes any edit ABOVE a site read as retire-plus-add: adding lines to one file
moved a byte-identical site down and the gate refused, reporting one NEW derivation that was the
same site. *A gate that fires on every unrelated edit trains reflexive re-baselining, which is
precisely how a ratchet becomes worthless.* The per-motif per-file ordinal is stable under edits
elsewhere, still separates multiple sites in one file, and still moves when a site is genuinely
added or removed.

⚑⚑ AND `os.walk` IS MATCHED CONTEXTUALLY, NEVER BY THE CALL ALONE. A walk is not an Agda
enumeration — tools here walk for timing ledgers, for `.py` files, for a subdirectory. Censusing
those measures the wrong thing, and *a false positive banked into a paydown-only baseline is debt
that can never legitimately be paid.*

⚑ THE WALK IS THE CALLER'S. This takes `(relpath, source)` pairs, so the census is a pure
function of text and a case can drive it without a tree — the same boundary `ban_census` draws,
for the same reason.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

#: The modules that ARE the derivation, so they cannot re-derive it.
CANONICAL = frozenset(
    {"agda_lex.py", "agda_defs.py", "agda_imports.py", "_agdatext.py", "gate_keys.py", "ratchet.py"}
)

#: How far a `⚑rederive:` marker reaches past its own line — a site the marker introduces.
MARKER_SPAN = 40

#: How near the top a marker must be to count as living in the module docstring.
DOCSTRING_HEAD = 60

#: How many lines around an `os.walk` are searched for the filter that makes it an Agda walk.
WALK_CONTEXT = 3

# ⚑ QUOTING IS NOT UNIFORM BELOW AND CANNOT BE. A pattern that must match a double quote in the
# source it scans has to be written in single quotes, so the house style yields to the subject:
# these patterns are ABOUT quoting, and respelling one changes what it matches.
MOTIFS: dict[str, re.Pattern[str]] = {
    "mask": re.compile(r're\.sub\(\s*r?["\']\\\{-|\.partition\(["\']--["\']\)'),
    "span": re.compile(
        r'startswith\(\(?["\'] ["\']\)?\)\s*and\s+\w+\[?\w*\]?\.strip\(\)'
        r"|\(\?:\\n\[ \\t\]\+|\(\\n\\s\+\[\^\\n\]\*\)\*"
    ),
    "modname": re.compile(r'r["\']\^\\s\*module\\s|r["\']\^module\\s'),
    # ⚑ MATCH THE CLASS, NOT A SPELLING — see the module docstring for what each of these
    # missed when it was written from the instance in hand.
    "importname": re.compile(r"import[^\n]{0,40}\[A-Za-z0-9[^\]]*\]\+"),
    "declscan": re.compile(r'r["\'][^"\']{0,12}\(\??:?\s*data\|record\)'),
    "enumerate": re.compile(r'glob\.glob\([^)]*\*\*[^)]*\.agda|rglob\(["\']\*\.agda'),
    "enumerate_walk": re.compile(r"os\.walk\("),
    "public": re.compile(r"\\bpublic\\b"),
    "wordbound": re.compile(
        r'r"\\b"\s*\+\s*re\.escape'
        r'|re\.escape\([^)]*\)\s*\+\s*r"\\b"'
    ),
    "renameclause": re.compile(r'r"renaming\\s\*\\\('),
}

DECLARED = re.compile(r"⚑rederive:")


def declared_lines(src: str) -> set[int] | None:
    """Return the line numbers a `⚑rederive:` marker covers, or None for the whole file.

    ⚑⚑ A DOCSTRING MARKER DECLARES THE WHOLE FILE, and that is the honest shape for a tool
    predating the authorities entirely — the measured case is a ~2600-line module carrying one
    declaration. Returning None rather than a huge set says *file-level* explicitly, so a caller
    cannot mistake exhaustive coverage for a coincidence of ranges.

    ⚑ A MARKER ALSO COVERS WHAT FOLLOWS IT, because the site it introduces sits below it. The
    span is fixed rather than parsed: a declaration is a human statement about a region, and
    inferring the region from syntax would make the marker mean different things in different
    files.
    """
    lines = src.split("\n")
    covered: set[int] = set()
    for i, line in enumerate(lines, 1):
        if not DECLARED.search(line):
            continue
        # ⚑ INSIDE THE MODULE DOCSTRING means an ODD number of triple quotes precede it near the
        # top of the file — which is what distinguishes a file-level declaration from a marker
        # that merely happens to appear early.
        if i < DOCSTRING_HEAD and src[: src.find(line)].count('"""') % 2 == 1:
            return None
        covered |= set(range(i, i + MARKER_SPAN + 1))
    return covered


def _is_agda_walk(lines: list[str], at: int) -> bool:
    """Report whether the `os.walk` at line `at` is enumerating Agda sources.

    ⚑⚑ CONTEXTUAL, BECAUSE THE CALL ALONE PROVES NOTHING. Tools here walk for timing ledgers,
    for `.py` files, for a subdirectory — censusing those measures the wrong thing, and a false
    positive banked into a paydown-only baseline is debt nobody can ever legitimately pay.
    """
    ctx = "\n".join(lines[max(0, at - WALK_CONTEXT) : at + WALK_CONTEXT + 1])
    return ".agda" in ctx


def keys_for(rel: str, src: str) -> set[str]:
    """Return every `<motif>::<relpath>#<ordinal>[::declared]` key one source carries.

    ⚑⚑⚑ THE ORDINAL IS PER MOTIF PER FILE, and that is what makes the key stable under edits
    elsewhere in the file — the defect that once made a byte-identical site read as newly added
    because lines were inserted above it.

    ⚑ A DECLARED SITE STILL GETS A KEY, marked. Dropping it would make a declaration erase the
    site from the census, so removing the declaration would read as a NEW derivation rather than
    as the withdrawal of a claim.
    """
    lines = src.split("\n")
    covered = declared_lines(src)
    ordinal: dict[str, int] = {}
    keys: set[str] = set()
    for motif, pattern in MOTIFS.items():
        for found in pattern.finditer(src):
            at = src[: found.start()].count("\n") + 1
            name = motif
            if name == "enumerate_walk":
                if not _is_agda_walk(lines, at):
                    continue
                # ⚑ A QUALIFYING WALK IS AN `enumerate`, so the two spellings share one key
                # space — otherwise the same derivation would be counted under two motifs.
                name = "enumerate"
            marked = covered is None or at in covered
            nth = ordinal.get(name, 0)
            ordinal[name] = nth + 1
            keys.add(f"{name}::{rel}#{nth}" + ("::declared" if marked else ""))
    return keys


def relevant(name: str, src: str) -> bool:
    """Report whether a source is worth censusing at all.

    ⚑ THE CANONICAL MODULES ARE EXCLUDED BY NAME because they ARE the derivation — censusing
    them would key the authority as its own re-derivation, which is the one shape the gate must
    never refuse.

    ⚑ AND A FILE MENTIONING NEITHER `.agda` NOR `module` cannot be re-deriving an Agda reader.
    This is a cheap pre-filter, not a claim: a file it drops carries no motif anyway, and the
    keys are identical with or without it.
    """
    return name not in CANONICAL and (".agda" in src or "module" in src)


def census(sources: Iterable[tuple[str, str]]) -> set[str]:
    """Return the re-derivation census over `(relpath, source_text)` pairs.

    ⚑ THE WALK IS THE CALLER'S, which keeps this a pure function of text so a case can drive it
    without a tree. The filesystem root, the directory roster and the exclusions belong to the
    application — the same boundary drawn for the ban census and the naming authority.
    """
    keys: set[str] = set()
    for rel, text in sources:
        name = rel.rsplit("/", 1)[-1]
        if relevant(name, text):
            keys |= keys_for(rel, text)
    return keys
