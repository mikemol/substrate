# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The pre-commit hook's gate ROSTER — which gates it wires, and how each is invoked.

⚑⚑ EXTRACTED FROM `commit_refusal` TO CUT THE ONE LIVE IMPORT CYCLE (2026-09-24, mtools N-c).
`commit_refusal` imports `sync_verdict` to fold census-sync rows into its survey, and
`sync_verdict` needed `commit_refusal.hook_gates()` for the roster — so each imported the other,
function-locally on both sides. The roster is a reader of the HOOK, not a verdict about it, so it
belongs to neither: both now import this module, and the cycle is gone rather than hidden.

Everything below moved verbatim; `commit_refusal` re-exports these names so its existing callers
and suite see no change.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from substrate import gate_module

# The script path a hook `run` line names, e.g. `$ROOT/scripts/check_claims.py`.
_SCRIPT = re.compile(r"\$ROOT/([\w/.\-]+\.py)")


@dataclass(frozen=True, slots=True)
class Gate:
    """One hook-wired gate, as the hook itself declares it."""

    name: str
    script: str
    blocking: bool
    conditional: bool
    # ⚑⚑ THE INVOCATION, NOT JUST THE FILE — and its absence produced a bogus row for three
    # ticks (gate-G26, gate-G28). `scratch/toolmodes.py` holds TWO gate mechanisms: an unwired
    # `--nearmiss` ratchet and the `--check` census-sync the hook actually runs. Keyed on the
    # script alone, the censusing reader found the ratchet's key set and rendered its arithmetic
    # under the wired gate's name. `gate_status.gates()` has always yielded this field;
    # `hook_gates` matched the path out of it and dropped the rest.
    # ⚑ DEFAULTED, because an ADVISORY gate has no `run` argv to carry — and an empty argv is
    # correctly not a sync gate, so that half of the roster keeps today's behaviour exactly.
    argv: str = ""


def authority(name: str) -> object | None:
    """Load one census authority from `scripts/`, or return None when it will not import.

    ⚑ THROUGH `gate_module`, NOT `sys.path`. Path mutation is refused in this tree and would be
    the wrong fix regardless: it makes an import work by rearranging global interpreter state
    instead of by naming where the file is, and it leaks into every unrelated import in the run.
    """
    module, _why = gate_module.gate_module(name)
    return module


def call_rows(mod: object | None, attr: str) -> list[object]:
    """Call an authority's reader and return its rows, or nothing when it cannot be called.

    ⚑ THE ONLY CROSSING OF THE UNTYPED BOUNDARY, and it returns `list[object]` so nothing
    downstream inherits `Any`. An authority that does not expose the reader yields NO rows,
    which every caller renders as "could not read" rather than as "nothing found" — the
    method-vs-substrate collapse, refused at the one place it could enter.
    """
    reader: object = getattr(mod, attr, None)
    if not callable(reader):
        return []
    got: object = reader()
    if not isinstance(got, (list, tuple, set)):
        return []
    out: list[object] = []
    out.extend(got)
    return out


def field(row: object, index: int) -> object:
    """Return one field of a sequence row, or None when the row is not one that long."""
    if isinstance(row, (list, tuple)) and index < len(row):
        return row[index]
    return None


def entry(row: object, key: str) -> str:
    """Return one field of a mapping row as text, or the empty string when absent.

    ⚑ A ROW IS A MAPPING OR A SEQUENCE DEPENDING ON THE AUTHORITY, and both spellings are
    narrowed here rather than at call sites that would each invent their own guard.
    """
    if isinstance(row, dict):
        got: object = row.get(key)
        return "" if got is None else str(got)
    return ""


def advisory_gates() -> list[Gate]:
    """Return the gates the hook invokes bare with `|| true` — they print, they cannot refuse."""
    kinds = call_rows(authority("gate_census"), "gate_kinds")
    rows = kinds[1] if len(kinds) > 1 else None
    if not isinstance(rows, (list, tuple)):
        return []
    out: list[Gate] = []
    for row in rows:
        script = entry(row, "script")
        if script:
            out.append(
                Gate(
                    name=entry(row, "name") or script,
                    script=script,
                    blocking=False,
                    conditional=False,
                )
            )
    return out


def hook_gates() -> list[Gate]:
    """Return every gate the hook wires, with how it is invoked.

    ⚑ THE ROSTER IS PARSED FROM THE HOOK, NEVER RESTATED. A hand-kept copy is a derived view
    that diverges silently — the defect this repo has paid for repeatedly. `gate_status.gates`
    owns the parse (including its refusal on a hook that does not parse as shell, so a truncated
    census is an error rather than a short list) and `gate_census.gate_kinds` owns
    blocking-vs-advisory, which it classifies by TWO independent readings because getting it
    backwards is that census's worst failure. Both are imported; neither is re-derived.
    """
    advisory = advisory_gates()
    advisory_scripts = {g.script for g in advisory}

    out: list[Gate] = []
    for row in call_rows(authority("gate_status"), "gates"):
        name, argv, cond = field(row, 0), field(row, 1), field(row, 2)
        if name is None:
            continue
        found = _SCRIPT.search(str(argv))
        script = found.group(1) if found else "(inline)"
        out.append(
            Gate(
                name=str(name),
                script=script,
                argv=str(argv),
                blocking=script not in advisory_scripts,
                conditional=cond is True,
            )
        )

    # ⚑ AN ADVISORY GATE MAY NOT APPEAR AS A `run` LINE AT ALL, so the two rosters are UNIONED
    # rather than intersected. `gate_status.gates()` parses only `run "..."` call sites; a bare
    # `… || true` invocation is invisible to it. Reporting the intersection would silently drop
    # exactly the gates whose distinguishing property is that they sit outside `run` — the
    # ADVISORY half of the distinction, dropped by the reader built to preserve it.
    seen = {g.script for g in out}
    out.extend(g for g in advisory if g.script not in seen)
    return out
