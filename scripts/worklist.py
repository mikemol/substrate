#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""worklist.py — mechanically-maintained thread status (registry-as-regenerator).

The open-threads worklist kept going STALE: done arcs stayed listed as "open" because their
status was a HAND-EDITED value, and a regrounding then re-dispatched completed work. The
discipline this tree already holds says: don't store the answer, COMPUTE it from the evidence of
the moment. So status is never written down — it is derived from the tree on every run.

⚑⚑⚑ THIS FILE IS NOW A SHIM, AND THAT IS THE WHOLE POINT OF THE CHANGE. It held the roster, the
predicate evaluator, the renderer and the ledger writer in one module carrying findings well past
the per-file gate's threshold, so a ONE-TOKEN path repair to a single item was refused exactly as
any other edit would be (gate-G217). Seven items pointed at artifacts the ban-decompose pipeline
had moved, and none of them could be repaired in place.

⚑⚑ THE GATE JUDGES NEW CONTENT, WHICH IS THE PROPERTY THAT MAKES A SWAP LAND WHERE A PATCH
CANNOT. The same route retired `scratch/bibstruct.py`: a dirty monolith cannot be edited, and can
be REPLACED. Each responsibility now has a clean home — `worklist_manifest` the roster,
`worklist_status` the verdicts, `worklist_render` the rows and the ledger block — and this file
does argv and nothing else.

⚑⚑ AND THE FIRST CUT REACHED FOR A `sys.path` BOOTSTRAP, WHICH THE GATE REFUSED AND THE TREE DID
NOT NEED. mypy proved the guard's second operand unreachable, and `scripts/roster_span.py` already
imports the package with no bootstrap at all — the repo is installed, so the insert was solving a
problem that does not exist while violating the standing rule against path modification.

⚑ THE MODES ARE UNCHANGED, DELIBERATELY. `.githooks/pre-commit` runs `--check` on every commit and
the ledger's generated block is written by `--update`, so a swap that altered either would be a
rewrite wearing a refactor's clothes. The rendered `--md` output is byte-compared against a
pre-swap capture rather than assumed equal.

    scripts/worklist.py            # the live status table (DONE / OPEN / MANUAL)
    scripts/worklist.py --open     # only the not-done items (what to actually dispatch)
    scripts/worklist.py --md       # a markdown block (never hand-edit the rendered result)
    scripts/worklist.py --update   # REGENERATE the status block in the open_threads ledger
    scripts/worklist.py --check    # counts (a gate runs this)

⚑ `--check` REPORTS AND EXITS 0 BY DESIGN. An OPEN item with a live artifact predicate is the
ordinary state of a work list, so refusing on merely-open would refuse every commit. The narrower
class — an item whose predicate no longer RESOLVES — is `check_worklist_predicates.py`'s subject,
and that gate refuses.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import worklist_manifest, worklist_render

#: The repo root, and the Agda tree `defines` predicates resolve against.
ROOT = Path(__file__).resolve().parent.parent
AGDA = ROOT / "agda"

#: The hand-authored ledger whose generated block `--update` replaces.
LEDGER = Path(
    "~/.claude/projects/-home-mikemol-github-substrate/memory/project_open_threads.md"
).expanduser()


def render() -> list[worklist_render.Row]:
    """Return every roster row, each predicate evaluated exactly once."""
    return worklist_render.rows(worklist_manifest.WORKLIST, root=ROOT, agda=AGDA)


def update_ledger(path: Path, rendered: list[worklist_render.Row]) -> str:
    """Replace the generated block in `path`, returning what happened.

    ⚑⚑ THE SNAPSHOT IS ARMED BEFORE THE WRITE AND NEVER BLOCKS IT. `edit_snapshot` exists because
    a rewrite once left 33 files unrecoverable, and `git stash create` cannot hold untracked files
    — so the guard copies them aside. A guard that can abort the tool it protects converts an
    unrecoverable edit into a failed commit, so this is best-effort and says so when it cannot run.

    ⚑ AND THE FIRST ARMING OF THE ORIGIN WAS INERT, CAUGHT BY RUNNING IT RATHER THAN READING IT:
    `edit_snapshot` lives in `scratch/`, off this file's import path, so the import raised while
    the write proceeded — and the contract gate would have counted the file ARMED, because it
    checks that the module is MENTIONED. A census verifies PRESENCE, never BEHAVIOUR.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return f"ledger not found: {path}"

    try:
        sys.path.insert(0, str(ROOT / "scratch"))
        import edit_snapshot  # noqa: PLC0415 - reachable only on the write path

        edit_snapshot.guard("worklist", [str(path)], intent="apply")
    except (ImportError, OSError, RuntimeError) as exc:
        print(f"  ⚠ snapshot unavailable ({exc}) — writing anyway")  # noqa: T201

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(worklist_render.splice(text, rendered), encoding="utf-8")
    tmp.replace(path)
    return f"regenerated worklist status block in {path.name}"


def report(rendered: list[worklist_render.Row], *, only_open: bool, as_md: bool) -> None:
    """Print the status table in either the plain or the markdown shape."""
    shown = [r for r in rendered if not (only_open and r.label == "DONE")]
    if as_md:
        for line in worklist_render.table(shown):
            print(line)  # noqa: T201
    else:
        for row in shown:
            mark = worklist_render.MARKS.get(row.label, "?")
            print(f"  {mark} {row.label:<6} {row.sym:<16} {row.desc}")  # noqa: T201


def main(argv: list[str]) -> int:
    """Dispatch one mode. Nothing here decides a verdict — it only selects a view."""
    if "--update" in argv:
        index = argv.index("--update")
        after = argv[index + 1] if index + 1 < len(argv) else ""
        path = Path(after) if after and not after.startswith("-") else LEDGER
        print(update_ledger(path, render()))  # noqa: T201
        return 0

    rendered = render()
    counted = worklist_render.tally(rendered)

    if "--check" in argv:
        print(
            f"worklist: {counted.done} done, {counted.open_} open, "  # noqa: T201
            f"{counted.manual} manual (status derived from tree)"
        )
        return 0

    report(rendered, only_open="--open" in argv, as_md="--md" in argv)
    print(f"\n  {counted.why()}  (DERIVED from the tree — never hand-edited)")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
