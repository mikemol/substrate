# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The findings ledger's witness CLI, reading the BIBS — the cleanroom of `findings.py <KEY>` (W40).

⚑⚑ ONCE EVERY BIB `check` IS ITS WITNESS, THE ROSTER IS THE BIBS. `findings.py` answered `<KEY>`
from a 7,000-line `WITNESSES` literal that no edit may touch (the per-file gate refuses the file).
After the convergence (`ledger_converge`, `--versus` 850 agrees), the same witness lives in each
entry's `check`, so answering a key is: find the entry across the project's warrant bibs, then run
its check through `witness_run.verdict` — the verdict the paperkit verbs already produce.

⚑ THE BIBS COME FROM THE PROJECT'S `warrants`, never a typed list: a second roster of file names
is the drift this whole arc has been removing.

⚑⚑ THE UNKNOWN-KEY REFUSAL KEEPS ITS WORDING, BECAUSE A CONSUMER READS IT. `witness_resolves`
tells "no such key" from "an honest gap" (both exit 2) by the message beside the code, and it
matches `no witness registered for`. Changing the words would turn every refused key into a
resolved one there — the three-senders-on-exit-2 class, reintroduced by a rephrase.

    python -m substrate.ledger_cli --root <tree> <KEY>       the key's verdict, as its exit code
    python -m substrate.ledger_cli --root <tree> --kinds     the census of check kinds
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from mikemol.ledger import finding_kinds

from substrate import bib_parse, witness_run

# The ledger project, relative to the tree.
PROJECT = (".claude", "agents")

# The phrase `witness_resolves` reads to tell an unknown key from an honest gap.
UNKNOWN = "no witness registered for"

# The argv shape: the flag, the tree, the key.
_ARGC = 3


def warrant_bibs(project: Path) -> list[Path]:
    """Return the warrant bibs the project's paper.toml declares, in declaration order.

    ⚑ THE `Any` FROM `tomllib` IS NARROWED AT THE SEAM (the `dep_addressing.declared` shape).
    """
    parsed: object = tomllib.loads(project.joinpath("paper.toml").read_text(encoding="utf-8"))
    paper: object = parsed.get("paper") if isinstance(parsed, dict) else None
    warrants: object = paper.get("warrants") if isinstance(paper, dict) else None
    if not isinstance(warrants, list):
        return []
    return [project / name for name in warrants if isinstance(name, str)]


def checks(project: Path) -> dict[str, str]:
    """Return `{key: check}` for every entry across the project's warrant bibs."""
    out: dict[str, str] = {}
    for bib in warrant_bibs(project):
        for key, fields in bib_parse.parse(bib.read_text(encoding="utf-8")).items():
            out[key] = fields.get("check", "")
    return out


def resolve(asked: str, known: dict[str, str]) -> tuple[str | None, str]:
    """Return `(key, "")` for an exact or unique-prefix match, else `(None, refusal)`."""
    if asked in known:
        return asked, ""
    hits = sorted(key for key in known if key.startswith(asked))
    if len(hits) == 1:
        return hits[0], ""
    if not hits:
        return None, f"{UNKNOWN} {asked!r}, and no key begins with it"
    return None, f"{UNKNOWN} {asked!r} exactly; it is a prefix of {len(hits)}: {', '.join(hits)}"


def verdict(asked: str, root: Path) -> finding_kinds.Verdict:
    """Return the verdict for the ledger key `asked`, in the tree at `root`."""
    known = checks(root.joinpath(*PROJECT))
    key, refusal = resolve(asked, known)
    if key is None:
        return finding_kinds.UNRUNNABLE, refusal
    return witness_run.verdict(known[key], root)


# What each check kind asserts, in the order `--kinds` reports them. ⚑ `standing` is marked
# VACUOUS in-band because no change to the code can flip it — the bound travels with the count.
GLOSS = {
    "selftest": "behavioural, holds on exit 0",
    "refuses": "behavioural, holds on NON-zero",
    "excludes": "behavioural, holds while a corpus stays narrow",
    "agda-field": "behavioural, holds while a record lacks a field",
    "agda-grep": "behavioural, holds while a census stays blind",
    "mode": "documentation, roster-vs-dispatch",
    "unwitnessed": "honest gap, always 2",
    "standing": "⚑ VACUOUS — passes unconditionally",
}

# The kinds a code change can flip.
BEHAVIOURAL = ("selftest", "refuses", "excludes", "agda-field", "agda-grep")


def kind_of(check: str) -> str:
    """Return a converged check's kind: the text before its first `:`."""
    return check.partition(":")[0]


def kinds(project: Path) -> dict[str, int]:
    """Return `{kind: count}` over every entry's check across the project's warrant bibs."""
    out: dict[str, int] = {}
    for check in checks(project).values():
        out[kind_of(check)] = out.get(kind_of(check), 0) + 1
    return out


def render_kinds(counts: dict[str, int]) -> str:
    """Render the kind census with each kind's gloss and the behavioural/vacuous summary."""
    order = [*GLOSS, *sorted(k for k in counts if k not in GLOSS)]
    lines = [
        f"── {kind + ':':<12} {GLOSS.get(kind, '⚑ UNKNOWN KIND'):<48} {counts[kind]:>4}"
        for kind in order
        if kind in counts
    ]
    total = sum(counts.values())
    moving = sum(counts.get(k, 0) for k in BEHAVIOURAL)
    lines.append(
        f"\n{moving} of {total} witnesses are BEHAVIOURAL; {counts.get('standing', 0)} are "
        "`standing`, which no change to the code can flip."
    )
    return "\n".join(lines) + "\n"


# The `--list` tag for each verdict code, as the origin prints it.
TAG = {
    finding_kinds.CLOSED: "holding",
    finding_kinds.OPEN: "OPEN",
    finding_kinds.UNRUNNABLE: "unwitnessed",
}

# How much of a verdict's note one `--list` row carries.
_NOTE_WIDTH = 96


def listing(root: Path) -> tuple[list[tuple[str, str, str]], dict[int, int]]:
    """Return `(rows, counts)`: `(tag, key, note)` per entry by key, and the count per code.

    ⚑ `--list` REPORTS, IT DOES NOT GATE (the origin's contract, kept): an UNWITNESSED finding is a
    named gap in the instrument, not a failure of this run.
    """
    rows: list[tuple[str, str, str]] = []
    counts = dict.fromkeys(TAG, 0)
    for key, check in sorted(checks(root.joinpath(*PROJECT)).items()):
        code, note = witness_run.verdict(check, root)
        counts[code] = counts.get(code, 0) + 1
        rows.append((TAG.get(code, "?"), key, note[:_NOTE_WIDTH]))
    return rows, counts


def render_listing(rows: list[tuple[str, str, str]], counts: dict[int, int]) -> str:
    """Render the listing the way the origin does: tag, key, note, then the totals."""
    wide = max((len(key) for _, key, _ in rows), default=0)
    lines = [f"  {tag:<11} {key:<{wide}}  {note}" for tag, key, note in rows]
    lines.append(
        f"\n{counts.get(finding_kinds.CLOSED, 0)} holding · {counts.get(finding_kinds.OPEN, 0)} "
        f"OPEN · {counts.get(finding_kinds.UNRUNNABLE, 0)} UNWITNESSED, over {len(rows)} finding(s)"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Answer one key (exit = its verdict), or census the kinds / list every verdict."""
    args = argv[1:]
    if len(args) != _ARGC or args[0] != "--root":
        sys.stderr.write(__doc__ or "")
        return finding_kinds.UNRUNNABLE
    root = Path(args[1])
    if args[2] == "--kinds":
        sys.stdout.write(render_kinds(kinds(root.joinpath(*PROJECT))))
        return 0
    if args[2] == "--list":
        sys.stdout.write(render_listing(*listing(root)))
        return 0
    known = checks(root.joinpath(*PROJECT))
    key, refusal = resolve(args[2], known)
    if key is None:
        sys.stdout.write(f"{refusal}\n")
        return finding_kinds.UNRUNNABLE
    code, note = witness_run.verdict(known[key], root)
    # ⚑ `key: note`, as the origin prints it — the resolved key, so a prefix shows what it hit.
    sys.stdout.write(f"{key}: {note}\n")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
