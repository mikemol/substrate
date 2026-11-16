#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡typeengine-false-export: every name a stub RE-EXPORTS must resolve at runtime.

⚑⚑⚑ THIS IS THE FIFTH `DEFINED-IN` vs `EXPORTED-FROM` INSTANCE IN THIS ARC, AND THE FIRST FOUND
ON A RE-EXPORT LIST RATHER THAN IN A DECLARATION. The prior four — `Dialect` (invented),
`PGDialect` (defined at `base.py:3240` and not exported), `PGDialect_psycopg2` (wrong package),
`Column` (wrong module) — were each a name a stub CLAIMED to declare. This one is a name a stub
claimed to FORWARD: `stubs/sqlalchemy/__init__.pyi` spelled `TypeEngine as TypeEngine` and two
siblings while the runtime `sqlalchemy` exports none of the three. Every one type-checked green,
and `from sqlalchemy import TypeEngine` raised `ImportError`.

⚑⚑⚑ AND THE STUB'S OWN DOCSTRING NAMED ALL THREE AS NOT-RE-EXPORTED, three lines above the block
that re-exported them. The prose was correct and the code contradicted it, in one file, from the
file's first commit. A declaration is not an enforcement; this module is the enforcement.

⚑⚑⚑ `stubtest` STRUCTURALLY CANNOT CATCH IT, WHICH IS THE FINDING RATHER THAN A DETAIL. stubtest
walks RUNTIME to STUB: it enumerates the runtime module's attributes and asks what the stub says
about each one. A name present in the STUB and absent from the RUNTIME is not in the population
it iterates, so nothing ever asks about it. MEASURED 2026-09-03: a fabricated `GhostExport`
re-export was added to the sqlalchemy stub and `check_stub_authority.py` reported clean on every
one of its stubs. On a bare run over the same stub, all sixteen findings read `is not present in
stub`; not one reads `not present at runtime`. `--ignore-missing-stub` is NOT the cause — it
silences the direction stubtest DOES check, and the uncovered direction is the other one.

⚑⚑ SO THIS IS NOT A RATCHET AND NOT A SECOND STUBTEST — IT IS THE MISSING DIRECTION. The gate
that owns stub authority keeps its population and its verdict; this closes the half of the
correspondence that gate cannot reach. `check_stub_authority` answers *does the stub agree about
what the runtime has*; this answers *does the runtime have what the stub forwards*.

⚑⚑ THE INSTRUMENT IS AN ATTRIBUTE PROBE ON THE IMPORTED MODULE, AND NOTHING WEAKER SETTLES IT. A
typecheck reads the stub, so it agrees with the stub by construction — that is what made four
prior instances ship. `--binding` answers DEFINED-IN, which is a different question and the one
that misled instance three: `PGDialect` genuinely IS defined where the reader found it, and is
still not importable from where the stub said. Only an import of the live module answers
EXPORTED-FROM.

⚑ THE POPULATION IS THE `X as X` FORM ONLY, and that is the whole discriminator. PEP 484 makes
`from m import X as X` a re-export and a plain `from m import X` a private reference; a stub
legitimately imports names it merely ANNOTATES with. Flagging the plain form would refuse the
sqlalchemy stub's honest use of `ReadOnlyColumnCollection` in `Table.c`'s return type, which is
not a claim about `sqlalchemy`'s exports at all. The repair for a false re-export is therefore to
DROP the `as X`, not to drop the import.

⚑ AN UNIMPORTABLE MODULE IS REPORTED, NEVER FAILED. A stub whose runtime is absent from this
machine is the `absent-dep` state `check_stub_authority` already discriminates, and failing on it
would fail a clean checkout for a reason its author cannot fix. Reported as `unverified`.

Exit 0 = every re-export resolves, 1 = at least one does not.
"""

from __future__ import annotations

import ast
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).absolute().parent.parent
STUBS = ROOT / "stubs"

# The states a stub file can end in. `ok` and `unverified` pass; `false-export` fails.
OK = "ok"
FALSE_EXPORT = "false-export"
UNVERIFIED = "unverified"

# ⚑ FAILING IS DECLARED AS A SET, NOT RE-DERIVED AT EACH READER — the shape
# `check_stub_authority._FAILING` sets, so a newly-added state cannot be silently admitted as
# passing by whichever reader nobody updated.
_FAILING = frozenset({FALSE_EXPORT})


@dataclass(frozen=True, slots=True)
class Verdict:
    """One stub file's result: what it claimed, and which claims the runtime denied."""

    module: str
    state: str
    missing: tuple[str, ...]
    detail: str

    @property
    def failed(self) -> bool:
        """True when this verdict must abort the commit."""
        return self.state in _FAILING


def reexports(path: Path) -> tuple[str, ...]:
    """Return the names a `.pyi` re-exports via the `X as X` form.

    ⚑ THE `as` MUST MATCH THE NAME. `from m import X as Y` binds a different name and forwards
    nothing under PEP 484's rule; only the redundant-looking spelling is the export marker, which
    is exactly why it is easy to write by habit and hard to notice on review.

    ⚑ A DOTTED `import a.b as a.b` CANNOT OCCUR, so the plain-`Import` arm only ever contributes
    bare names — but it is read anyway, because a stub CAN re-export a submodule and leaving the
    arm out would make this reader's zero a fact about the arm rather than the file.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ImportFrom, ast.Import)):
            out += [a.name for a in node.names if a.asname == a.name and a.name not in out]
    return tuple(out)


def stub_modules() -> tuple[tuple[str, Path], ...]:
    """Return every stub file paired with the runtime module name it describes.

    ⚑ A PACKAGE'S SUBMODULES EACH MAKE THEIR OWN CLAIMS, so the population is per FILE rather
    than per unit — the inverse of `check_stub_authority.stubs()`, and deliberately so. That gate
    asks a question stubtest answers once per package; this one asks about a re-export list, and
    every `.pyi` has a distinct one. `stubs/sqlalchemy/dialects/postgresql/__init__.pyi` forwards
    names from `sqlalchemy.dialects.postgresql`, not from `sqlalchemy`.
    """
    if not STUBS.is_dir():
        return ()
    out: list[tuple[str, Path]] = []
    for p in sorted(STUBS.rglob("*.pyi")):
        rel = p.relative_to(STUBS)
        parts = list(rel.parts[:-1]) if rel.stem == "__init__" else [*rel.parts[:-1], rel.stem]
        if parts:
            out.append((".".join(parts), p))
    return tuple(out)


def check(module: str, path: Path) -> Verdict:
    """Import the runtime module and ask whether each re-exported name resolves on it.

    ⚑ `hasattr`, NOT `getattr(..., None)`. Only the boolean is wanted, and reaching for the VALUE
    in order to test for it drags in an unchecked type this file's own gate refuses — the reason
    `ratchet_suites.suite` records for the same choice.
    """
    claimed = reexports(path)
    if not claimed:
        return Verdict(module, OK, (), "")
    try:
        mod = importlib.import_module(module)
    except ImportError as exc:
        return Verdict(module, UNVERIFIED, (), f"{type(exc).__name__}: {exc}")
    missing = tuple(n for n in claimed if not hasattr(mod, n))
    if missing:
        return Verdict(module, FALSE_EXPORT, missing, "")
    return Verdict(module, OK, (), "")


def verdicts() -> tuple[Verdict, ...]:
    """Check every stub file's re-export list against its runtime module."""
    return tuple(check(m, p) for m, p in stub_modules())


def _render(found: tuple[Verdict, ...]) -> None:
    """Print the false re-exports, each as the import line that would raise."""
    bad = [v for v in found if v.failed]
    sys.stdout.write(
        f"stub-reexport: BROKEN — {len(bad)} of {len(found)} stub file(s) forward a name their "
        f"runtime does not export:\n"
    )
    for v in bad:
        sys.stdout.writelines(
            f"    ✗ from {v.module} import {n} — resolves at TYPE-CHECK, "
            f"raises ImportError at RUNTIME\n"
            for n in v.missing
        )
    sys.stdout.write(
        "  ⚑ stubtest cannot see this: it walks RUNTIME to STUB, and a stub-only name is not in\n"
        "  the population it iterates. NEXT: drop the `as X` (keeping the plain import if the\n"
        "  stub annotates with the name), or import it from the module that does export it.\n"
    )


def _render_clean(found: tuple[Verdict, ...], *, quiet: bool) -> None:
    """Print the passing verdict, naming what could not be verified on this machine."""
    unverified = [v for v in found if v.state == UNVERIFIED]
    if quiet and not unverified:
        return
    ok = [v for v in found if v.state == OK]
    sys.stdout.write(
        f"stub-reexport: clean ({len(ok)} of {len(found)} stub file(s) forward only real "
        f"exports).\n"
    )
    sys.stdout.writelines(f"    ? {v.module} NOT VERIFIED: {v.detail}\n" for v in unverified)


def main(argv: list[str]) -> int:
    """Check every stub's re-export list; 1 when the runtime denies one."""
    found = verdicts()
    if not found:
        sys.stdout.write(
            "stub-reexport: no stubs in stubs/ — nothing to verify (a fact about the "
            "POPULATION, not a pass)\n"
        )
        return 0
    if any(v.failed for v in found):
        _render(found)
        return 1
    _render_clean(found, quiet="--quiet" in argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
