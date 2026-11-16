#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ledger_cli` — key resolution, the live ledger, `--kinds`, `--list`.

⚑⚑ THE LIVE CASES ARE PROPERTIES OF THE BIBS, NOT A DIFFERENTIAL AGAINST `findings.py`. This suite
once ran `findings.py <KEY>` beside `ledger_cli` for one key of every non-command kind, and both
agreed (recorded in the paths-forward ledger). Once `findings.py` is a shim over this module that
comparison would test a thing against itself, so what is owed instead: resolving a key yields the
same verdict as running its check directly, and the census covers every entry.

⚑⚑ THE UNKNOWN-KEY REFUSAL IS CASED ON ITS WORDS, not only its code: `witness_resolves` reads
`no witness registered for` beside exit 2 to tell an unknown key from an honest gap. A match on
the exit code alone would pass a rephrase that breaks that consumer.

⚑ `--list` is cased on a FIXTURE tree: the live listing runs 232 real suites, and what is owed
here is its shape and counts. The tree is the working directory, resolved at this CLI entry.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.ledger import finding_kinds

from substrate import ledger_cli, witness_run

# The kinds whose witness is not a command, so running them is cheap.
_CHEAP = ("standing", "unwitnessed", "mode", "excludes", "agda-field", "agda-grep")

# A key no ledger will ever hold.
_NO_SUCH = "zz-no-such-finding-anywhere"

_KNOWN = {"alpha-one": "standing", "alpha-two": "standing", "beta": "unwitnessed"}

_FIXTURE_BIB = """@misc{a-holds,
  check    = {standing}
}

@misc{b-open,
  check    = {selftest:false}
}

@misc{c-gap,
  check    = {unwitnessed}
}

@misc{d-holds,
  check    = {selftest:true}
}
"""


def _resolve_cases() -> list[tuple[str, bool]]:
    """Return the cases for `resolve` over a fixture key set."""
    exact, _ = ledger_cli.resolve("beta", _KNOWN)
    prefix, _ = ledger_cli.resolve("bet", _KNOWN)
    ambiguous, why_amb = ledger_cli.resolve("alpha", _KNOWN)
    missing, why_none = ledger_cli.resolve("gamma", _KNOWN)
    return [
        ("an exact key resolves", exact == "beta"),
        ("a unique prefix resolves", prefix == "beta"),
        ("an ambiguous prefix is refused", ambiguous is None),
        ("the ambiguity refusal names both keys", "alpha-two" in why_amb),
        ("an unknown key is refused", missing is None),
        ("the refusal carries the phrase witness_resolves reads", ledger_cli.UNKNOWN in why_none),
    ]


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return the live cases: one key per cheap kind resolves to its check's own verdict."""
    checks = ledger_cli.checks(root.joinpath(*ledger_cli.PROJECT))
    picked: dict[str, str] = {}
    for key, check in sorted(checks.items()):
        kind = ledger_cli.kind_of(check)
        if kind in _CHEAP and kind not in picked:
            picked[kind] = key
    cases = [("every cheap kind has a live key", set(picked) == set(_CHEAP))]
    for kind, key in sorted(picked.items()):
        by_key = ledger_cli.verdict(key, root)[0]
        by_check = witness_run.verdict(checks[key], root)[0]
        sys.stdout.write(f"  {kind:<12} {key[:52]}: by key={by_key} by check={by_check}\n")
        cases.append((f"{kind}: resolving the key == running its check", by_key == by_check))
    code, note = ledger_cli.verdict(_NO_SUCH, root)
    cases.append(("an unknown key is UNRUNNABLE", code == finding_kinds.UNRUNNABLE))
    cases.append(("and says the phrase witness_resolves reads", ledger_cli.UNKNOWN in note))
    return cases


def _kinds_cases(root: Path) -> list[tuple[str, bool]]:
    """Return the `--kinds` cases over the live bibs: the census covers every entry."""
    project = root.joinpath(*ledger_cli.PROJECT)
    counts = ledger_cli.kinds(project)
    rendered = ledger_cli.render_kinds(counts)
    return [
        ("the census covers every entry", sum(counts.values()) == len(ledger_cli.checks(project))),
        ("every live kind has a gloss", all(kind in ledger_cli.GLOSS for kind in counts)),
        ("the render carries the vacuous bound in-band", "VACUOUS" in rendered),
    ]


def _listing_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the `--list` cases over a fixture tree holding one entry per verdict."""
    project = tmp.joinpath(*ledger_cli.PROJECT)
    project.mkdir(parents=True)
    project.joinpath("paper.toml").write_text('[paper]\nwarrants = ["w.bib"]\n', encoding="utf-8")
    project.joinpath("w.bib").write_text(_FIXTURE_BIB, encoding="utf-8")
    rows, counts = ledger_cli.listing(tmp)
    rendered = ledger_cli.render_listing(rows, counts)
    tags = {key: tag for tag, key, _ in rows}
    exit_code = ledger_cli.main(["lc", "--root", str(tmp), "--list"])
    return [
        ("every entry is listed, sorted by key", [key for _, key, _ in rows] == sorted(tags)),
        ("a holding check tags holding", tags.get("a-holds") == tags.get("d-holds") == "holding"),
        ("a failing check tags OPEN", tags.get("b-open") == "OPEN"),
        ("an honest gap tags unwitnessed", tags.get("c-gap") == "unwitnessed"),
        ("the totals line counts each verdict", "2 holding · 1 OPEN · 1 UNWITNESSED" in rendered),
        ("--list reports, it does not gate", exit_code == finding_kinds.CLOSED),
    ]


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        listed = _listing_cases(Path(tmp))
    cases = _resolve_cases() + _live_cases(root) + _kinds_cases(root) + listed
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"ledger-cli selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"ledger-cli selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
