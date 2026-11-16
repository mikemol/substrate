#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Mechanize routine stdlib to substrate migrations, one Agda file at a time.

For trivial single-symbol migrations (`Data.List` to `Foundation.List`,
`Data.Maybe` to `Foundation.Maybe`, `Data.Empty` to `Foundation.Empty`,
`Data.Unit` to `Foundation.Unit`) this performs import rewriting and identifier
renaming by regex.

NOT a full Agda parser. It does not decompose multi-lemma files. The caller still
decomposes where required.

⚑⚑ `--verify` NOW DISPATCHES TO `make`, AND THE CONTRACT IS UNCHANGED. It always meant
"verify the migration"; that it invoked `agda --safe` ONCE PER FILE was an
implementation detail a caller could only observe as slowness. The per-file form was a
second build system, worse than `make` on four axes at once - no parallelism, no
dependency order (each invocation re-elaborated shared upstreams in-process), no
incrementality, and no memory discipline (a bare `agda` on PATH, outside `membudget`).
`scripts/agda_build.py` owns the one build path and has all four for free.

⚑ SO THIS FILE NOW HOLDS NO SUBPROCESS BOUNDARY AT ALL, and needs no `S603` exemption.
Extracting the build was the answer to "is this the fifth per-file override, or a
responsibility that wants its own module?"

⚑ `absolute()`, NEVER `resolve()`, AND THIS FILE CARRIED `resolve()` TWICE. `resolve()`
FOLLOWS SYMLINKS; `absolute()` is `os.path.abspath`'s real counterpart. A resolved
`__file__` derives the SYMLINK TARGET's root rather than the invoking checkout's - the
substitution that shipped to five repos on 2026-08-30 and was caught by a peer's routes
slice, never by anything in this tree. ⚑⚑ Ruff recommends the wrong one: `PTH100`
offers `Path.resolve()` as `abspath`'s replacement, and it fires only on the `os.path`
spelling, so an existing `resolve()` is INVISIBLE to the linter.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from scripts.agda_build import build
except ImportError as _e:  # pragma: no cover - adoption-shaped, not reachable in-repo
    sys.stderr.write(f"agda_stdlib_migrator: cannot import a sibling ({_e}).\n")
    sys.exit(0)

REPO_ROOT = _ROOT
AGDA_DIR = REPO_ROOT / "agda"

_PATTERN_LABEL_CHARS = 60

# ⚑⚑ THE AGDA GLYPH IS THE SUBJECT, NOT A CONFUSABLE, AND THE CURE IS TO NAME THE
# CODEPOINT. `RUF001` reads DOWN TACK as a lookalike for `T` - correct advice for prose
# and exactly backwards for a tool whose job is rewriting Agda import lines that NAME
# that identifier. Substituting an ASCII letter would silently stop the rule matching
# any real file.
#
# ⚑ A CONSTANT HOLDING THE LITERAL DOES NOT HELP - it relocates the glyph, and the rule
# scans the literal wherever it sits (measured: a first cut of this fix moved them to
# module constants and RUF001 followed). The `\N{...}` escape is the honest spelling:
# the checker sees ASCII, the reader sees the character's OFFICIAL NAME rather than a
# glyph they must recognise by eye, and the value is byte-identical.
#
# ⚑ ONLY DOWN TACK NEEDS THIS. Measured: UP TACK and the cons operator are flagged by
# nothing, because ruff's confusable table is keyed on RESEMBLANCE TO ASCII, not on
# being non-ASCII. Escaping them too would be cargo-cult - the surrounding patterns keep
# their literal glyphs deliberately.
_TOP = "\N{DOWN TACK}"

# (regex_to_match, replacement) for the import line.
# `Foundation.List` is universe-polymorphic and preferred over `Coxeter.Word` for the
# generic List-of-A use, since `Coxeter.Word` is mono-universe.
_LIST_LENGTH_REPL = (
    "open import Substrate.Foundation.List using (List; []; _∷_)\n"
    "open import Substrate.Foundation.List.Length using (length)"
)

RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; length\)$", re.MULTILINE),
        _LIST_LENGTH_REPL,
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; foldl\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_; foldl)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; foldr\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_; foldr)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List)",
    ),
    # Data.Maybe (mono).
    (
        re.compile(r"^open import Data\.Maybe using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Maybe using (\1)",
    ),
    # Inline Data.Empty / Data.Unit (used inside where-clauses).
    (
        re.compile(r"^(\s*)open import Data\.Empty using \(⊥\)$", re.MULTILINE),
        r"\1open import Substrate.Foundation.Empty using (⊥)",
    ),
    (
        re.compile(rf"^(\s*)open import Data\.Unit using \({_TOP}(?:; tt)?\)$", re.MULTILINE),
        rf"\1open import Substrate.Foundation.Unit using ({_TOP}; tt)",
    ),
    # Polymorphic Unit / Empty (used in higher-universe code).
    (
        re.compile(r"^open import Data\.Unit\.Polymorphic using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Unit.Polymorphic using (\1)",
    ),
    (
        re.compile(r"^open import Data\.Empty\.Polymorphic using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Empty.Polymorphic using (\1)",
    ),
    # Level - substrate's Foundation.Level re-exports Agda.Primitive with
    # `suc to lsuc` renames. Backwards-compatible for all common patterns.
    (
        re.compile(r"^open import Level using \((.*?)\)(\s+renaming \(.*?\))?$", re.MULTILINE),
        r"open import Substrate.Foundation.Level using (\1)\2",
    ),
]

# No identifier renames needed: Foundation.List exposes the same names
# (List / [] / _∷_) as stdlib's Data.List.
ID_RENAMES: list[tuple[re.Pattern[str], str]] = []


class Outcome(NamedTuple):
    """What one file's migration did.

    ⚑ A RECORD, NOT A `dict`. The previous shape returned an untyped mapping whose keys
    were spelled at every read site, so a reader could not tell an ABSENT verdict from a
    FAILED one without knowing which keys the writer happened to set - the tristate
    collapse this repo files most often, one layer down.
    """

    path: str
    applied: list[str]
    changed: bool


def migrate_text(text: str) -> tuple[str, list[str]]:
    """Apply RULES then ID_RENAMES, returning the new text and what fired."""
    applied: list[str] = []
    new = text
    list_was_imported = "Data.List" in new
    for rx, repl in RULES:
        prev = new
        new = rx.sub(repl, new)
        if new != prev:
            applied.append(rx.pattern[:_PATTERN_LABEL_CHARS])
    # Only rename `List` to `Word` if Data.List was the source.
    if list_was_imported:
        for rx, repl in ID_RENAMES:
            prev = new
            new = rx.sub(repl, new)
            if new != prev:
                applied.append(f"id-rename {rx.pattern}")
    return new, applied


def process_file(path: Path, *, write: bool) -> Outcome:
    """Migrate one file, writing it only when `write`."""
    text = path.read_text(encoding="utf-8")
    new, applied = migrate_text(text)
    changed = new != text
    if applied and write:
        path.write_text(new, encoding="utf-8")
    return Outcome(path=str(path), applied=applied, changed=changed)


def _report(results: list[Outcome], *, quiet: bool) -> None:
    """Write each outcome to stdout, skipping unchanged files when `quiet`."""
    for r in results:
        if quiet and not r.changed:
            continue
        applied = ", ".join(r.applied) if r.applied else "no-change"
        sys.stdout.write(f"{r.path}: {applied}\n")


def main(argv: list[str]) -> int:
    """Migrate every named Agda file; dry-run unless `--write`."""
    ap = argparse.ArgumentParser(description="Migrate stdlib imports to substrate.")
    ap.add_argument("paths", nargs="+", help="Agda files to migrate.")
    ap.add_argument("--write", action="store_true", help="Write changes (default: dry-run).")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="After writing, run the repo's build (make -C agda -j) ONCE.",
    )
    ap.add_argument("--quiet", action="store_true", help="Only print files that changed.")
    args = ap.parse_args(argv)

    # ⚑ NARROWED AT THE BOUNDARY. `argparse.Namespace` attributes are `Any`, so every
    # read through `args.` is an unchecked expression under this bar; `object` is the
    # honest type of an untrusted value and this is where it becomes a checked one.
    opts: dict[str, object] = vars(args)
    write = opts.get("write") is True
    verify = opts.get("verify") is True
    quiet = opts.get("quiet") is True
    raw = opts.get("paths")
    raw_paths: list[str] = [str(x) for x in raw] if isinstance(raw, list) else []

    results: list[Outcome] = []
    for item in raw_paths:
        p = Path(item)
        if not p.exists():
            sys.stderr.write(f"WARN: missing {p}\n")
            continue
        results.append(process_file(p, write=write))

    _report(results, quiet=quiet)

    # ⚑ ONCE, AFTER THE WHOLE BATCH - not per file. That is the point of dispatching to
    # `make`: it orders and parallelises the work itself, so a build per migrated file
    # would serialise exactly what the build system exists to overlap.
    if verify and write and any(r.changed for r in results):
        ok, tail = build()
        sys.stdout.write(f"verify: {'green' if ok else 'FAILED'}\n")
        if tail:
            sys.stdout.write(f"{tail}\n")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
