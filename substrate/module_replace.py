#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Replace one named top-level definition with new text — the ADDITIVE half of `module_trim`.

⚑⚑⚑ THE NON-CONTIGUOUS WALL HAS A MECHANICAL ANSWER FOR REMOVALS AND NONE FOR ADDITIONS. Under the
zero-tolerance per-file gate a change spanning several regions cannot pass through any intermediate
state — add the parameter and its use is undefined, add the use and the parameter is unknown — and
every partial `Edit` is refused, each refusal reverting the last. `module_trim` dissolves that for
an EXCISION by staging a whole prospective file through `record_migrate`'s check-then-write
pipeline. Its transform only removes named definitions, so threading a new parameter through a
signature, a helper and a call site had no path but a hand `Write` over unread lines (gate-G338).

⚑⚑ SO THE UNIT HERE IS A NAMED DEFINITION AND ITS REPLACEMENT TEXT. The caller supplies what the
def should BECOME; this locates the current one by name over `Module.body` — the same partition
`module_trim` uses, for the same reason its docstring gives: a method sharing the name is a
DIFFERENT definition, and a visitor matching on the name alone would take it.

⚑⚑⚑ AND THE CONSERVATION GUARD CANNOT BE REUSED AS-IS, WHICH IS THE DESIGN POINT RATHER THAN A
GAP. `module_trim` asserts every original line lands in one of two partitions — a claim that is
FALSE BY CONSTRUCTION here, because a replacement legitimately introduces lines the original never
held and drops lines it did. What survives is the half that still discriminates: every line OUTSIDE
the replaced span must be untouched, so a transform that corrupted an unrelated region is still
caught. The replaced span itself is the caller's claim, checked by the gate rather than by this.

⚑⚑ THE CHECK-THEN-WRITE LATTICE IS `record_migrate`'s, CALLED AND NEVER REIMPLEMENTED — staging,
`ruff --fix`, the house checker and the three-state verdict. This module contributes the TRANSFORM
and the OUTSIDE-THE-SPAN guard. A second write path would be the rival-authority defect, and the
verdict vocabulary would drift the first time either moved.

    module_replace.py --dry-run <file> <name> <new-text-file>
    module_replace.py --apply   <file> <name> <new-text-file>
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import libcst as cst

from substrate import corpus, module_trim, record_migrate

#: What a replacement carries when the named definition is not there to replace.
NOT_FOUND = "no top-level definition named"

#: The verdict a replacement carries when the guard refused it.
UNSAFE = module_trim.UNSAFE

#: What a bare or unusable invocation exits with — usage, not a verdict about the tree.
USAGE_EXIT = 2


@dataclass(frozen=True, slots=True)
class Replacement:
    """One module's prospective replacement: what it would become, and whether it may land."""

    relpath: str
    verdict: str
    name: str
    report: str
    source: str

    @property
    def writable(self) -> bool:
        """Report whether this replacement may be committed to disk.

        ⚑ ONLY `CLEAN` IS WRITABLE, and the lattice is `record_migrate`'s rather than restated.
        UNSAFE and UNKNOWN are refused on the same footing as FINDINGS: a guard that refused and a
        checker that could not run have both established nothing.
        """
        return self.verdict == record_migrate.CLEAN


def outside_span(source: str, replaced: str, name: str) -> tuple[str, ...]:
    """Return the reasons a replacement disturbed a line it had no business touching.

    ⚑⚑⚑ THE HALF OF THE CONSERVATION GUARD THAT STILL DISCRIMINATES. `module_trim` can assert that
    every original line survives into one of two partitions; a replacement cannot, because
    introducing and dropping lines inside the named span is the whole operation. What remains
    checkable is everything ELSE: a transform that corrupted an unrelated region, dropped a
    neighbouring def, or duplicated the module header is still caught here.

    ⚑⚑ BOTH DIRECTIONS, FOR `module_trim`'s OWN REASON. Absent-outside catches a deletion; gained-
    outside catches a transform that REWROTE a line while leaving it in place — the failure a line
    count cannot see. An import may move in either direction, because `ruff --fix` legitimately
    re-sorts and re-narrows the block and treating its output as invented content makes the
    pipeline accuse itself (gate-G333).
    """
    before = _body_outside(source, name)
    after = _body_outside(replaced, name)
    reasons: list[str] = []
    for line in sorted(set(before)):
        lost = before.count(line) - after.count(line)
        if lost > 0 and not module_trim._is_import(line):  # noqa: SLF001 — the shared predicate
            reasons.append(f"{lost} occurrence(s) of {line!r} vanished from outside {name}")
    for line in sorted(set(after)):
        gained = after.count(line) - before.count(line)
        if gained > 0 and not module_trim._is_import(line):  # noqa: SLF001 — same predicate
            reasons.append(f"{gained} occurrence(s) of {line!r} appeared outside {name}")
    return tuple(reasons)


def _body_outside(source: str, name: str) -> list[str]:
    """Return the module's code lines with the named definition's own span removed."""
    try:
        module = cst.parse_module(source)
    except cst.ParserSyntaxError:
        return []
    kept = [s for s in module.body if module_trim._defined_name(s) != name]  # noqa: SLF001 — the shared partition
    return module_trim._body(module.with_changes(body=kept).code)  # noqa: SLF001 — same unit


def consider(path: Path, name: str, new_text: str) -> Replacement:
    """Return what replacing `name` in `path` would produce, without writing anything.

    ⚑ A NAME THAT IS NOT THERE IS A REFUSAL, NOT A NO-OP. Silently writing a file in which nothing
    was replaced is the plausible-and-wrong output this whole pipeline exists to refuse — and the
    caller would read CLEAN as *the change landed*.
    """
    relpath = str(path.relative_to(corpus.ROOT))
    source = path.read_text(encoding="utf-8")
    module = cst.parse_module(source)
    swapped: list[cst.BaseStatement] = []
    found = False
    for statement in module.body:
        if module_trim._defined_name(statement) == name:  # noqa: SLF001 — the shared partition
            swapped.extend(cst.parse_module(new_text).body)
            found = True
        else:
            swapped.append(statement)
    if not found:
        return Replacement(
            relpath=relpath, verdict=UNSAFE, name=name, report=f"{NOT_FOUND}: {name}", source=source
        )

    replaced = module.with_changes(body=swapped).code
    reasons = outside_span(source, replaced, name)
    if reasons:
        return Replacement(
            relpath=relpath,
            verdict=UNSAFE,
            name=name,
            report="outside-span guard REFUSED:\n" + "\n".join(reasons),
            source=replaced,
        )

    report = record_migrate._check(replaced)  # noqa: SLF001 — the house checker, called not rebuilt
    verdict = record_migrate._verdict(report)  # noqa: SLF001 — the shared three-state lattice
    fixed = record_migrate._fixed(replaced) if verdict == record_migrate.CLEAN else replaced  # noqa: SLF001
    return Replacement(relpath=relpath, verdict=verdict, name=name, report=report, source=fixed)


def render(found: Replacement, *, applied: bool) -> list[str]:
    """Render one replacement's outcome, with its report bounded so it cannot bury the verdict."""
    out = [f"\n{found.verdict:<9} {found.relpath}  (replacing {found.name})"]
    if found.report.strip():
        out.extend(
            f"     {line}" for line in found.report.splitlines()[: record_migrate.REPORT_LINES]
        )
    if found.verdict == UNSAFE:
        out.append(
            "   ⚑ UNSAFE means a GUARD refused — the name was absent, or content outside "
            "the replaced span moved. Nothing about the checker is claimed."
        )
    if found.verdict == record_migrate.UNKNOWN:
        out.append(
            "   ⚑ UNKNOWN means the CHECKER could not run — a fact about this "
            "environment, never a clean bill."
        )
    out.append(f"   ✓ WROTE {found.relpath}" if applied else "   (nothing written)")
    return out


def run(argv: list[str]) -> int:
    """Replace one named definition, writing only if the result passes clean."""
    apply = "--apply" in argv
    if not apply and "--dry-run" not in argv:
        # ⚑ INTENT IS STATED, NEVER DEFAULTED — the house contract for a mutating tool.
        print(__doc__)  # noqa: T201 - the usage, for a bare or unusable invocation
        return USAGE_EXIT
    operands = [a for a in argv if not a.startswith("-")]
    if len(operands) != _OPERANDS:
        sys.stderr.write("module_replace: name a file, a definition, and a file of new text\n")
        return USAGE_EXIT

    target, name, text_at = operands
    found = consider(Path(target).resolve(), name, Path(text_at).read_text(encoding="utf-8"))
    written = apply and found.writable
    if written:
        (corpus.ROOT / found.relpath).write_text(found.source, encoding="utf-8")
    for line in render(found, applied=written):
        sys.stdout.write(line + "\n")
    return 0 if found.writable or not apply else 1


#: How many positional operands the CLI takes — the file, the name, and the new text's file.
_OPERANDS = 3


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
