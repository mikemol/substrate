# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Report which of a red ratchet's new keys are decomposition churn, and which are debt.

The runnable half of the churn classifier: read a gate's baseline, obtain its live census
from the gate's own code, and print the partition.

⚑⚑⚑ THIS IS THE TOOL A DRAIN NEEDS AND THE REASON THE DRAIN STALLS WITHOUT IT. Decomposing
a monolith retires old census keys and mints new ones for byte-identical lines, so the gate
reads growth — and because a set ratchet returns on `added` BEFORE its paydown branch, the
churn also blocks the paydown that drain earned from recording. Without a way to say *these
N additions are the SAME violations at new paths*, an operator sees only a red gate.

⚑⚑ THE CENSUS COMES FROM THE GATE'S OWN CODE, NEVER RE-IMPLEMENTED. A second
implementation of a gate's predicate is exactly the drift this exists to prevent, so each
gate is loaded and its own census function called. The loader works by file location rather
than by putting a directory on the import path, which is what lets this live in the package.

⚑ AND A GATE THAT CANNOT BE MEASURED IS REPORTED, NOT SKIPPED. The origin's dispatch raised
for an unknown gate and carried a hand-written branch per known one, so a gate absent from
that dispatch was invisible rather than unmeasured. Here every reason is carried through,
because *"could not measure"* and *"clean"* must never render alike.
"""

from __future__ import annotations

import sys

from substrate import (
    baseline_io,
    census_call,
    corpus,
    gate_module,
    ratchet_churn,
    ratchet_key,
)

# The gate script each schema entry's census lives in, by gate name.
GATE_SCRIPT: dict[str, str] = {
    "public": "check_public_ratchet.py",
    "sumtype": "check_sumtype_ratchet.py",
    "ban": "check_ban_ratchet.py",
    "claims": "check_claims.py",
    "discharge": "check_discharge_ratchet.py",
    "carrier-locality": "check_carrier_locality.py",
}

# ⚑⚑⚑ THE MIGRATED CENSUSES, AND THEY NEED A SECOND MAP RATHER THAN AN ENTRY IN THE FIRST.
# `gate_module` resolves against `GATE_DIR` (`scripts/`) by construction — that is what lets it
# arm `sibling_finder` for a directory of scripts that is not a package. A package module
# resolves by ordinary import and needs none of that, so putting `substrate/private_census.py`
# in the map above would send the loader looking for `scripts/substrate/private_census.py`.
#
# ⚑⚑ TWO MAPS BECAUSE THERE ARE GENUINELY TWO HOMES, not because one is a special case. The
# same widening `gate_population.GATE_HOMES` records: a census that MIGRATED must not leave the
# reader that consumes it, and the fix is to name the second home rather than to teach one
# loader both layouts.
PACKAGE_CENSUS: dict[str, str] = {
    "private": "substrate.private_census",
}

# ⚑ THE GATE THAT HAS NO `census()`. Its census is the LIVE-EXEMPTION set — a field of the
# verdict `judge(*scan())` returns — and those two functions were carved out of its `main`
# precisely so a pre-flight could reuse the exact extraction. Declaring the chain here is
# what keeps this reader from re-implementing the gate's own predicate.
#
# ⚑⚑ PUBLIC BECAUSE IT IS A DECLARATION A CALLER MAY READ. A case asserting the adapter
# exists had to reach past a leading underscore to do it, which the per-file gate refuses —
# correctly, since a name a test must read is part of the surface, not an internal.
CHAINED: dict[str, tuple[str, str, int]] = {
    "carrier-locality": ("scan", "judge", 4),
}

_USAGE = """\
usage: churn_report.py [<gate>] [--strict]

Partition a red ratchet's NEW keys into decomposition churn and genuine debt.

  <gate>     one of the declared gates; omit to report every gate with a baseline
  --strict   report a one-old-to-many-new fan-out as SUSPECT rather than churn

⚑ CHURN IS NEVER AUTO-ABSOLVED. This reports a pairing an operator reads; it does not
  rewrite a baseline, because a paydown-only baseline rewritten by a tool is an
  absolution nobody reviewed.
"""


def baseline_path(gate: str) -> str:
    """Return where `gate` keeps its baseline.

    ⚑ THE SCHEMA CARRIES THE FILENAME AND THIS CARRIES THE DIRECTORY. Baking the repo
    layout into the schema would make a parsing module depend on where this checkout sits.
    """
    return str(corpus.ROOT / "scripts" / ratchet_key.SCHEMA[gate].baseline)


def _package_census(dotted: str) -> tuple[set[str], str | None]:
    """Return the census of a migrated, package-resident module.

    ⚑ ORDINARY IMPORT, NOT `gate_module`. A package module needs no location fallback and no
    sibling finder — reaching for the gate loader here would resolve it against `scripts/` and
    report a present census as absent, which is the wrong-loader defect `argument_consumed`
    already records at its own call site.

    ⚑⚑ AND IT GOES THROUGH `census_call.census_of` LIKE EVERY OTHER ARM. That narrows the
    untyped module boundary and turns a raising census into a REASON: an empty census and a
    census that could not run render identically as a number, and the second banked into a
    paydown-only baseline would absolve every existing violation permanently.
    """
    import importlib  # noqa: PLC0415 — kept local so importing this module costs nothing

    try:
        module = importlib.import_module(dotted)
    except BaseException as exc:  # noqa: BLE001 — a census may exit or raise anything
        return set(), f"{type(exc).__name__}: {exc}"
    return census_call.census_of(module, dotted)


def live_census(gate: str) -> tuple[set[str], str | None]:
    """Return `(census, None)` from the gate's own code, or `(set(), why)`.

    ⚑ THE MIGRATED HOME IS TRIED FIRST. A gate whose census moved into the package has no
    entry in `GATE_SCRIPT` at all, so consulting that map first would report it as undeclared —
    a retirement reading as a missing gate.
    """
    dotted = PACKAGE_CENSUS.get(gate)
    if dotted is not None:
        return _package_census(dotted)
    script = GATE_SCRIPT.get(gate)
    if script is None:
        return set(), f"no gate script declared for {gate!r}"
    module, why = gate_module.gate_module(script)
    if module is None:
        return set(), why or f"could not load {script}"
    chain = CHAINED.get(gate)
    if chain is not None:
        first, second, field = chain
        return census_call.chained_census(module, first, second, field, script)
    return census_call.census_of(module, script)


def report(verdict: ratchet_churn.Verdict) -> str:
    """Render one gate's partition."""
    head = f"=== {verdict.gate}: {len(verdict.added)} added, {len(verdict.paid)} paid"
    out = [head]
    if verdict.churn:
        # ⚑⚑ BOTH NUMBERS, ALWAYS. Churn answers "is this the same violation relocated";
        # creditable answers "may a baseline absolve it". MEASURED on ban: 198 and 20. An
        # operator shown only the first reads the gate as nearly clean and the ratchet as
        # broken, which is what a fan-out does — one retirement licenses one move.
        out.append(
            f"  CHURN {len(verdict.churn)} — the same violation at a new path, "
            f"of which {len(verdict.creditable)} creditable as a 1:1 move:"
        )
        out.extend(
            f"    {k}\n        was: {', '.join(olds)}" for k, olds in sorted(verdict.churn.items())
        )
    if verdict.suspect:
        out.append(f"  SUSPECT {len(verdict.suspect)} — a fan-out, so at most one is the move:")
        out.extend(f"    {k}" for k in sorted(verdict.suspect))
    if verdict.genuinely_new:
        out.append(f"  GENUINELY NEW {verdict.queue} — real debt:")
        out.extend(f"    {k}" for k in verdict.genuinely_new)
    if verdict.unpaired:
        out.append(
            f"  ⚑ {len(verdict.unpaired)} paid key(s) paired with nothing — a "
            f"retirement this reader could not evidence as a move."
        )
    return "\n".join(out)


def one(gate: str, *, strict: bool = False) -> tuple[str, int]:
    """Return `(rendered, queue)` for one gate."""
    path = baseline_path(gate)
    if not _exists(path):
        return f"=== {gate}: no baseline at {path} — skipped", 0
    cur, why = live_census(gate)
    if why is not None:
        return f"=== {gate}: UNMEASURED — {why}", 0
    verdict = ratchet_churn.classify(gate, baseline_io.read_baseline(path), cur, strict=strict)
    return report(verdict), verdict.queue


def _exists(path: str) -> bool:
    """Report whether an absolute baseline path is present."""
    from pathlib import Path  # noqa: PLC0415 — kept local to keep the import graph thin

    return Path(path).exists()


def main(argv: list[str]) -> int:
    """Report the churn partition for one gate or for all with a baseline."""
    if "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0
    strict = "--strict" in argv
    named = [a for a in argv if not a.startswith("--")]
    if len(named) > 1:
        sys.stderr.write(f"churn_report: one gate at a time, got {named}\n")
        return 2
    if named and named[0] not in ratchet_key.SCHEMA:
        sys.stderr.write(
            f"churn_report: {named[0]!r} is not a declared gate; "
            f"have {', '.join(ratchet_key.GATES)}\n"
        )
        return 2

    gates = named or [g for g in ratchet_key.GATES if _exists(baseline_path(g))]
    queue = 0
    for gate in gates:
        rendered, count = one(gate, strict=strict)
        sys.stdout.write(rendered + "\n")
        queue += count

    sys.stdout.write(
        f"\nWORK QUEUE: {queue} item(s) of genuinely-new debt across {len(gates)} gate(s).\n"
    )
    return 1 if queue else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
