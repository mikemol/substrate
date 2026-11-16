# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Plan a ledger bib's convergence onto its witnesses — the roster cleanroom's two passes (W40).

⚑⚑ BOTH PASSES HAVE RUN, AND THE CLI THAT READ THE ROSTER IS RETIRED. The operator's rulings,
mechanised here: *"Converge `check`; roster wins"* — every entry's `check` became exactly the
spelling of its roster witness — and *"move losslessly, then structure"* — every roster note the
bibs did not hold was appended verbatim under a provenance marker. Results, recorded in the
paths-forward ledger: 808 checks rewritten (850 agree, 0 differ); 845 notes moved plus 1 with a
declared brace spelling (846 of 846 carried). Re-running either pass was a no-op, and the roster
is retiring into the bibs, so the CLI now REFUSES and names those results.

⚑ THE PLANNERS STAY, because they are pure: `plan` and `plan_notes` take a bib's text and the
spellings/notes as data, and neither reads the roster. Their fixture suite still pins every
bucket, the note/claim predicate shared with the census, and idempotence.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from substrate import bib_edit, bib_parse, ledger_checks

# The field `plan` rewrites.
CHECK = "check"

# The marker a moved roster note is appended under — provenance travels with the text.
NOTE_MARK = "⚑ WITNESS NOTE, moved verbatim from findings.py WITNESSES (2026-09-26):"

# What the retired CLI refuses with.
RETIRED = (
    "ledger_converge: the CLI is RETIRED — both passes have run and re-running either was a "
    "no-op. Recorded in .claude/paths-forward.ledger: 808 checks rewritten (850 agree, 0 differ); "
    "845 notes moved + 1 brace-spelled (846 of 846 carried). The roster it read is retiring into "
    "the bibs; edit a bib's check or note with `bibstruct --set`.\n"
)


@dataclass
class Plan:
    """What converging one bib would do: the new text, and every entry by what happened to it."""

    text: str
    rewritten: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    no_roster: list[str] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)


def _write(out: Plan, key: str, fields: dict[str, str], edit: tuple[str, str, str]) -> str | None:
    """Apply one field write to `out`, bucketing the key; return a refusal message, or None."""
    entries = bib_parse.parse(out.text)
    if edit[1] in fields:
        new = bib_edit.set_field(out.text, edit, entries, bib_parse.GRAMMAR)
        bucket = out.rewritten
    else:
        new = bib_edit.add_field(out.text, edit, entries, bib_parse.GRAMMAR)
        bucket = out.added
    if isinstance(new, bib_edit.Refusal):
        return new.message
    out.text = new
    bucket.append(key)
    return None


def plan(text: str, spelled: dict[str, str], refused: dict[str, str]) -> Plan | bib_edit.Refusal:
    """Return the converged text for one bib, or the first edit that refused."""
    out = Plan(text=text)
    for key, fields in bib_parse.parse(text).items():
        if key in refused:
            out.refused.append(key)
            continue
        want = spelled.get(key)
        if want is None:
            out.no_roster.append(key)
            continue
        if fields.get(CHECK) == want:
            out.unchanged.append(key)
            continue
        why = _write(out, key, fields, (key, CHECK, want))
        if why is not None:
            return bib_edit.Refusal(why)
    return out


def plan_notes(text: str, notes: dict[str, str]) -> Plan | bib_edit.Refusal:
    """Return the text with every not-yet-held note appended verbatim to its entry's `note`.

    ⚑ "ALREADY HELD" IS THE CENSUS'S PREDICATE (note or claim, verbatim or in the declared brace
    spelling from `ledger_checks`) — a first cut read `note` alone and would have double-appended
    three notes the claim carried. An unbalanced-brace note is moved with the declared, reversible
    substitution, stated in its marker, because the one-level field grammar cannot hold it.
    """
    out = Plan(text=text)
    for key, fields in bib_parse.parse(text).items():
        note = notes.get(key)
        if note is None:
            out.no_roster.append(key)
            continue
        have = " ".join(fields.get("note", "").split())
        claim = " ".join(fields.get("claim", "").split())
        held = f"{have} {claim}"
        if note in held or ledger_checks.spelled(note) in held:
            out.unchanged.append(key)
            continue
        mark = NOTE_MARK
        if note.count("{") != note.count("}"):
            note = ledger_checks.spelled(note)
            mark = f"{NOTE_MARK} [braces spelled {ledger_checks.LBRACE} / {ledger_checks.RBRACE}]"
        why = _write(out, key, fields, (key, "note", f"{have} {mark} {note}".strip()))
        if why is not None:
            return bib_edit.Refusal(why)
    return out


def main(argv: list[str]) -> int:
    """Refuse: both passes have run, and the roster the CLI read is retiring."""
    del argv
    sys.stderr.write(RETIRED)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
