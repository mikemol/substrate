#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which Agda types are load-bearing, and which are not.

For every top-level `data`/`record` type in `agda/Substrate`, count how many OTHER
modules reference it (comments stripped), classifying each as:

  DEAD   — referenced nowhere outside its own declaration (not load-bearing).
  LOCAL  — used only inside its defining module (load-bearing to that module's proofs,
           but not part of the cross-module surface).
  BORNE  — used in N other modules (load-bearing; N is its degree). If those uses are
           ONLY in re-export/catalog modules, it is flagged catalog-only.

Usage: `scripts/audit_type_load_bearing.py [--full]` — the default prints the DEAD,
catalog-only and duplicate lists plus a degree summary; `--full` also prints the
load-bearing degree for every type.

⚑ THE WORK MOVED OUT OF MODULE SCOPE, AND THAT IS A BEHAVIOUR FIX RATHER THAN TIDYING.
Every stage ran at import: `import audit_type_load_bearing` walked the whole Agda tree,
read several thousand files twice, and PRINTED THE REPORT. A module that cannot be
imported without doing its work cannot be reused, tested, or read by a tool — and the
`T201` findings at module level were the tell.

⚑ `absolute()`, NEVER `resolve()`: `PTH100` recommends `Path.resolve()` as
`os.path.abspath`'s replacement and it is NOT one — `resolve()` follows symlinks.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).absolute().parent.parent / "agda" / "Substrate"

# Re-export catalogs: a reference from one of these is not proof-load-bearing.
# ⚑ MATCHED ON THE FILE NAME, NOT THE PATH TAIL. The previous form tested
# `p.endswith(("Generators.agda",))` against a FULL PATH, which happens to work for a
# basename and silently would not for any entry naming a directory — the same class as
# a census keyed on one spelling. A set of names says what is meant.
CATALOG_NAMES = frozenset({"Generators.agda"})

_BLOCK_COMMENT = re.compile(r"\{-.*?-\}", re.DOTALL)
_LINE_COMMENT = re.compile(r"--[^\n]*")
_DECL = re.compile(r"^(?:data|record)\s+(\S+)", re.MULTILINE)
_TOKEN_SPLIT = re.compile(r"[\s()\[\]{};,.\"]+")

_TOP_N = 15


def strip_comments(s: str) -> str:
    """Return `s` with Agda block and line comments replaced by spaces."""
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", s))


def read_tree() -> dict[Path, str]:
    """Return every `.agda` under ROOT mapped to its comment-stripped text.

    ⚑ READ ONCE, NOT TWICE. The previous shape read every file for its tokens and then
    read every file AGAIN for its declarations, stripping comments both times — the
    whole tree, twice, at import.
    """
    return {p: strip_comments(p.read_text(encoding="utf-8")) for p in ROOT.rglob("*.agda")}


def tokens_of(text: str) -> set[str]:
    """Return the identifier-ish tokens of comment-stripped Agda source."""
    return set(_TOKEN_SPLIT.split(text))


def declarations(texts: dict[Path, str]) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    """Return (name -> first defining path, name -> every defining path)."""
    decls: dict[str, Path] = {}
    dups: dict[str, list[Path]] = collections.defaultdict(list)
    for p, text in texts.items():
        for m in _DECL.finditer(text):
            # ⚑ `re.Match.group()` IS `str | Any`, so it is narrowed once here rather
            # than read repeatedly — the third distinct `Any`-at-a-boundary this
            # migration has hit, after `argparse.Namespace` and `collections.namedtuple`.
            name = str(m.group(1))
            if name == "where":  # a `record X where` head with no name captured
                continue
            dups[name].append(p)
            decls.setdefault(name, p)
    return decls, dict(dups)


class Audit(NamedTuple):
    """The classification, as one value rather than six parallel lists.

    ⚑⚑ `typing.NamedTuple`, NOT `collections.namedtuple` — and the difference is 76
    findings, not a style preference. The `collections` form is UNTYPED: every field
    access returns `Any`, so `a.decls`, `a.dead` and every expression reading them
    became an unchecked expression, and the report builder inherited the `Any` on each
    of its lines. ONE untyped container at the boundary poisons everything downstream
    of it, which is why `PYI024` is worth taking rather than silencing.
    """

    decls: dict[str, Path]
    dups: dict[str, list[Path]]
    dead: list[str]
    local: list[str]
    catalog_only: list[tuple[str, int]]
    borne: list[tuple[str, int]]


def classify(texts: dict[Path, str]) -> Audit:
    """Classify every declared type by how many other modules reference it."""
    toks = {p: tokens_of(t) for p, t in texts.items()}
    decls, dups = declarations(texts)

    dead: list[str] = []
    local: list[str] = []
    catalog_only: list[tuple[str, int]] = []
    borne: list[tuple[str, int]] = []

    for name, home in decls.items():
        ext = [p for p in toks if p != home and name in toks[p]]
        if not ext:
            # ⚑ ONE TEST, TWO ARMS. The previous form was
            # `local.append(name) if name in own else None` — a conditional EXPRESSION
            # evaluated as a statement, whose else-branch produced a discarded `None`,
            # immediately followed by an `if name not in own` re-testing the same thing.
            # Two spellings of one branch; the second could drift from the first.
            (local if name in toks[home] else dead).append(name)
            continue
        non_catalog = [p for p in ext if p.name not in CATALOG_NAMES]
        if non_catalog:
            borne.append((name, len(non_catalog)))
        else:
            catalog_only.append((name, len(ext)))

    # ⚑ A TYPED KEY. `lambda x: -x[1]` leaves `x` inferred as `Any`, so the sort key is
    # `Callable[[Any], Any]` and the bar refuses it — the same one-untyped-thing-poisons
    # -the-expression shape as the namedtuple above, at the size of one line.
    def _degree(item: tuple[str, int]) -> int:
        return -item[1]

    borne.sort(key=_degree)
    return Audit(decls, dups, dead, local, catalog_only, borne)


def _rel(p: Path) -> str:
    """Return `p` relative to the Agda source root."""
    return str(p.relative_to(ROOT))


def render(a: Audit, *, full: bool) -> str:
    """Render the audit as one ordered report."""
    out: list[str] = [
        f"== type load-bearing audit: {len(a.decls)} types ==",
        f"DEAD (referenced nowhere outside declaration): {len(a.dead)}",
        *(f"    {n:30s}  {_rel(a.decls[n])}" for n in sorted(a.dead)),
        f"\nCATALOG-ONLY (only re-exported, no proof depends): {len(a.catalog_only)}",
        *(f"    {n:30s}  {_rel(a.decls[n])}" for n, _ in sorted(a.catalog_only)),
    ]
    multi = {n: ps for n, ps in a.dups.items() if len(ps) > 1}
    out.append(f"\nDUPLICATE NAMES (same name, multiple decls — uniqueness check): {len(multi)}")
    out.extend(
        f"    {n:24s}  " + " | ".join(_rel(p) for p in ps) for n, ps in sorted(multi.items())
    )
    out.append(f"\nLOAD-BEARING: {len(a.borne)} types; module-local only: ~{len(a.local)}")
    out.append(f"  top {_TOP_N} by degree (modules depending on it):")
    out.extend(f"    {d:4d}  {n}" for n, d in a.borne[:_TOP_N])
    if full:
        out.append("\n  full degree list:")
        out.extend(f"    {d:4d}  {n:30s}  {_rel(a.decls[n])}" for n, d in a.borne)
    return "\n".join(out)


def main(argv: list[str]) -> int:
    """Run the audit over the Agda tree and print the report."""
    a = classify(read_tree())
    sys.stdout.write(render(a, full="--full" in argv) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
