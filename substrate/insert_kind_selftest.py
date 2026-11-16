# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.insert_kind` — the install-versus-drain split.

⚑ THE LOAD-BEARING CASE IS THE FALSE GREEN. If the repo root stays on the search path,
every own-tree module resolves and the whole drain population reports as INSTALL — a
clean-looking answer that says the work is already done. A case pins that the root is
dropped, so a regression there fails loudly instead of emptying the queue.

⚑⚑ AND THE SECOND IS DECLARED-BEATS-PROBED. The first cut of this reader misfiled every
declared-but-absent dependency as DRAIN, because a probe cannot tell an uninstalled
third-party package from an own-tree module. The case below asserts the manifest is
consulted BEFORE the probe, which is the whole of that repair.

⚑ THE PATH IS RESTORED WHETHER OR NOT THE PROBE RAISES. `kind_of` mutates `sys.path` to
ask its question — the very construct this arc exists to remove, admissible only because
it is scoped to one call and undone in a `finally`. A reader that leaked its own path
surgery would be the defect wearing the instrument's clothes.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import insert_kind

_ROOT = Path(__file__).resolve().parent.parent


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the three kinds ──────────────────────────────────────────────────────
    check(
        "a stdlib name is neither install nor drain",
        passed=insert_kind.kind_of("json", _ROOT) == insert_kind.STDLIB,
    )
    check(
        "a name nothing provides and nothing declares is a DRAIN problem",
        passed=insert_kind.kind_of("no_such_module_anywhere_xyzzy", _ROOT) == insert_kind.DRAIN,
    )

    # ── DECLARED BEATS PROBED — the misfiling this reader was repaired for ───
    # ⚑ A declared dependency reports INSTALL even when the probe would fail, because
    # the fix is the same whether or not it happens to be installed on this machine.
    fake = frozenset({"not_installed_but_declared"})
    check(
        "a DECLARED name is INSTALL even though nothing resolves it",
        passed=insert_kind.kind_of("not_installed_but_declared", _ROOT, fake)
        == insert_kind.INSTALL,
    )
    check(
        "an UNDECLARED name with the same absence is still DRAIN",
        passed=insert_kind.kind_of("not_installed_but_declared", _ROOT, frozenset())
        == insert_kind.DRAIN,
    )

    # ⚑ And stdlib still wins over a declaration — a manifest naming `json` would not
    # make it an install chore.
    check(
        "stdlib is decided before the manifest is consulted",
        passed=insert_kind.kind_of("json", _ROOT, frozenset({"json"})) == insert_kind.STDLIB,
    )

    # ── the manifest reader ──────────────────────────────────────────────────
    known = insert_kind.declared_imports(_ROOT)
    check("the manifest yields at least one declared import name", passed=bool(known))
    # ⚑ Normalisation: `psycopg-binary` is declared, `psycopg` is imported.
    check(
        "a distribution whose import name differs is mapped",
        passed="psycopg" in known or "psycopg-binary" not in known,
    )

    # ── THE FALSE GREEN: the repo's own directories must come off the path ───
    dropped = insert_kind.clean_path(_ROOT)
    check("the repo root is not on the clean path", passed=str(_ROOT) not in dropped)
    check("the empty entry is not on the clean path", passed="" not in dropped)
    for name in insert_kind.REPO_DIRS:
        check(
            f"the repo's {name}/ is not on the clean path", passed=str(_ROOT / name) not in dropped
        )

    # ⚑ An own-tree scratch tool is importable ONLY under an insert, so it is drain
    # population — and it is not declared, so neither discriminator rescues it.
    check(
        "an own-tree scratch tool is DRAIN, not INSTALL",
        passed=insert_kind.kind_of("agda_lex", _ROOT) == insert_kind.DRAIN,
    )

    # ── the reader must not leak its own path surgery ────────────────────────
    before = sys.path[:]
    insert_kind.kind_of("json", _ROOT)
    insert_kind.kind_of("no_such_module_anywhere_xyzzy", _ROOT)
    check("sys.path is restored after probing", passed=sys.path == before)

    # ── the partition covers every name exactly once ─────────────────────────
    names = ["json", "agda_lex", "no_such_module_anywhere_xyzzy"]
    grouped = insert_kind.partition(names, _ROOT)
    total = sum(len(v) for v in grouped.values())
    check("every name lands in exactly one group", passed=total == len(names))
    check("the partition keeps stdlib apart", passed=grouped[insert_kind.STDLIB] == ["json"])

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
