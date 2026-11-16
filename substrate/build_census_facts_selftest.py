# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_census_facts`: the readers' own contracts, on fixtures.

⚑ THE REAL-TREE FIGURES ARE `build_census_selftest`'s. These pin what a fixture tree can: the
order of a ranking, the loud refusals, and that the roster is data a gate can assert against.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import build_census_facts as facts


def _refusal(root: Path) -> str:
    """Return the message `gate_census` refuses `root` with, or `""` when it did not refuse."""
    try:
        facts.gate_census(root)
    except RuntimeError as exc:
        return str(exc)
    return ""


# The rows `mikemol-membudget describe` printed on 2026-10-10 (mtools 7ff52eb), measured, not typed
# from memory: two figures, then one `verb` row per verb from the client's dispatch table.
_DESCRIBE = (
    "default_mb 192\nmax_mb 384\nverb describe\nverb capabilities\nverb run\nverb hold\n"
    "verb init\nverb status\nverb lease\nverb deadline\nverb peaks\n"
)


def _describe_refusal(text: str) -> str:
    """Return the message `membudget_from_describe` refuses `text` with, or `""` when it parses."""
    try:
        facts.membudget_from_describe(text)
    except RuntimeError as exc:
        return str(exc)
    return ""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    roster = facts.readers_census()
    paths = [rel for rel, _ in roster]
    parsed = facts.membudget_from_describe(_DESCRIBE)
    out = [
        ("the roster names each tool once", len(paths) == len(set(paths))),
        ("every roster row carries its question", all(what for _, what in roster)),
        (
            "the phase anchors are the full build, then the reorder marker",
            [name[:7] for _, name in facts.PHASE_ANCHORS] == ["Phase B", "Phase C"],
        ),
        (
            "describe rows parse to the same shape the bash arm returns",
            (parsed["default_mb"], parsed["max_mb"]) == (192, 384)
            and parsed["commands"] == sorted(parsed["commands"])
            and "run" in parsed["commands"]
            and len(parsed["commands"]) == _DESCRIBE.count("verb "),
        ),
        (
            "a repeated verb is one verb",
            facts.membudget_from_describe(_DESCRIBE + "verb run\n")["commands"]
            == parsed["commands"],
        ),
        (
            "a missing max_mb refuses and names it",
            "max_mb" in _describe_refusal("default_mb 1\nverb run\n"),
        ),
        (
            "a repeated figure refuses rather than picking one",
            "twice" in _describe_refusal(_DESCRIBE + "default_mb 5\n"),
        ),
        (
            "a non-integer figure is an unrecognised row",
            "unrecognised" in _describe_refusal("default_mb x\nmax_mb 1\nverb run\n"),
        ),
        (
            "no verb row refuses",
            "no verb rows" in _describe_refusal("default_mb 1\nmax_mb 2\n"),
        ),
        (
            "an unseen row kind refuses so a changed format is reviewed",
            "format changed" in _describe_refusal(_DESCRIBE + "flavour mint\n"),
        ),
        ("empty output refuses", bool(_describe_refusal(""))),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        hook = root / ".githooks" / "pre-commit"
        hook.parent.mkdir()
        hook.write_text('make -C "$ROOT/agda" -j\n# ⟡gqs-precommit-reorder\n', encoding="utf-8")
        out.append(
            (
                "anchors without a `run` call site refuse instead of reporting zero gates",
                _refusal(root).startswith('build_census: no `run "..."` gate call sites'),
            )
        )
        missing = facts.PHASE_ANCHORS[1][0]
        hook.write_text(f'run "g" x\n{facts.PHASE_ANCHORS[0][0]}\n', encoding="utf-8")
        out.append(("a missing anchor names itself in the refusal", missing in _refusal(root)))
        try:
            facts.load_script(root, "absent")
        except (FileNotFoundError, ImportError):
            out.append(("loading an absent script raises", True))
        else:
            out.append(("loading an absent script raises", False))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-census-facts selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
