#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.warrant_records` — the half that needs the engine installed.

⚑⚑⚑ THE IMPORT CASE IS THE ONE THAT PINS THE DEPENDENCY, AND IT IS AT MODULE SCOPE ON PURPOSE.
The code this replaces made the engine reachable by inserting a search path at call time; the
operator ruled that out, and the replacement declares paperkit instead. Importing it here, at the
top like any other dependency, is what turns "we declared it" into "it resolves" — and it is what
fails first if someone reverts to a path search or the install stops satisfying the declaration.

⚑⚑ AND THIS SUITE SPLIT FROM `warrant_bib_selftest` BECAUSE THE MODULE DID (gate-G209). A peer
measured that the whole `bibstruct` CLI was unreachable without a paperkit venv, because the
engine import sat three modules up a chain that runs at load. The module split so the dependency
is visible in the import graph; the suite splits the same way, so a consumer WITHOUT the engine
can still run the engine-free suite and get a real verdict rather than a collection error.

⚑⚑ AND THE PEER WHO OWNS THE ENGINE PREDICTED THE IMPORT WOULD FAIL. paperkit's session reported
that `import paperkit.bib` does not resolve outside their checkout (an internal flat import) and
advised not building against it yet. MEASURED HERE, against this venv: it resolves. The difference
is the install shape — an EDITABLE install writes a finder that maps the package into the
checkout, so its internal imports resolve normally. Their caveat is real for some shapes and does
not hold for this one, which is why this measures rather than trusts.

⚑ AN UNANCHORED FIGURE IS REFUSED, NOT DEFAULTED. A claim with no `[name=N]` marker gives a
witness nothing to compare against, and returning zero would let it check against a bound the
claim never made.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import paperkit.bib
from mikemol.witness.warrant_bib import WarrantError

from substrate import warrant_bib, warrant_records

# The figure the fixture claim anchors, named so the assertion and the fixture cannot drift.
_PROBE_TAG = 7

# A minimal warrant in the engine's own grammar — parsed by paperkit, never by a local regex.
_FIXTURE = f"""@misc{{PROBE,
  section = {{s}},
  claim   = {{a probe claim [probe={_PROBE_TAG}]}},
  check   = {{item:PROBE}},
  enables = {{OTHER}}
}}
"""

# The consumer field the fixture carries — a field the ENGINE does not know, which is the whole
# reason a project declares it.
_CONSUMER = "enables"

# A project config declaring that field, in the shape `paper.toml` uses.
_CONFIG = f"""[paper]
title = "a fixture"
consumer_fields = ["{_CONSUMER}"]
"""


def _bib(d: str) -> Path:
    """Write a fixture bib and return its path."""
    path = Path(d) / "warrants.bib"
    path.write_text(_FIXTURE, encoding="utf-8")
    return path


def _config(d: str, text: str = _CONFIG) -> Path:
    """Write a fixture project config and return its path."""
    path = Path(d) / "paper.toml"
    path.write_text(text, encoding="utf-8")
    return path


def the_engine_resolves(out: list[str]) -> int:
    """Check the declared dependency actually imports and exposes its parser.

    ⚑ THE DEPENDENCY, NOT THE SEARCH. If someone reinstates a `sys.path` insert this case still
    passes — but if the declaration stops being satisfied, this is what fails, which is the half
    a path search silently papered over.
    """
    if not hasattr(paperkit.bib, "parse"):
        out.append("selftest: paperkit.bib imported without a parse entry point")
        return 1
    return 0


def a_consumer_field_survives_the_parse(out: list[str]) -> int:
    """Check a declared non-engine field reaches the record — THE ITEM.

    ⚑⚑ THE CONFIG BEING READ IS NOT THE SAME AS THE FIELD ARRIVING. Reading a toml key proves
    only that a toml key was read; what the repair claims is that the engine now CARRIES the
    field, and only a parse that keeps it says so.
    """
    original = warrant_bib.CONFIG
    try:
        with tempfile.TemporaryDirectory() as d:
            warrant_bib.CONFIG = _config(d)
            rec = warrant_records.records(_bib(d)).get("PROBE", {})
    finally:
        warrant_bib.CONFIG = original

    if _CONSUMER not in rec:
        out.append(f"selftest: the consumer field was dropped: {sorted(rec)!r}")
        return 1
    return 0


def an_undeclared_field_is_still_dropped(out: list[str]) -> int:
    """Check the carry is the DECLARATION's doing, not the parser's default.

    ⚑⚑ THE POSITIVE CONTROL FOR THE ARM ABOVE. If the engine carried unknown fields regardless,
    that case would pass while proving nothing about the config — so an empty declaration must
    still drop the field.
    """
    original = warrant_bib.CONFIG
    try:
        with tempfile.TemporaryDirectory() as d:
            warrant_bib.CONFIG = _config(d, '[paper]\ntitle = "no consumer fields"\n')
            rec = warrant_records.records(_bib(d)).get("PROBE", {})
    finally:
        warrant_bib.CONFIG = original

    if _CONSUMER in rec:
        out.append("selftest: an undeclared field was carried — the config decides nothing")
        return 1
    return 0


def a_claim_is_read_from_the_bib(out: list[str]) -> int:
    """Check the claim prose comes back whitespace-collapsed."""
    with tempfile.TemporaryDirectory() as d:
        got = warrant_records.claim_of("PROBE", _bib(d))
    if got != f"a probe claim [probe={_PROBE_TAG}]":
        out.append(f"selftest: the claim read as {got!r}")
        return 1
    return 0


def a_tag_is_read_from_the_claim(out: list[str]) -> int:
    """Check the anchored integer is read out of the claim's own marker."""
    with tempfile.TemporaryDirectory() as d:
        got = warrant_records.tag("PROBE", "probe", _bib(d))
    if got != _PROBE_TAG:
        out.append(f"selftest: the tag read as {got!r}")
        return 1
    return 0


def an_unanchored_claim_is_refused(out: list[str]) -> int:
    """Check a missing `[name=N]` marker raises rather than defaulting.

    ⚑ A NUMBER NOBODY CAN AUDIT IS WORSE THAN A MISSING ONE. Defaulting to zero would let a
    witness compare against a bound the claim never stated, and report agreement.
    """
    with tempfile.TemporaryDirectory() as d:
        try:
            warrant_records.tag("PROBE", "absent", _bib(d))
        except WarrantError:
            return 0
    out.append("selftest: an unanchored claim returned a figure")
    return 1


def a_missing_warrant_is_refused(out: list[str]) -> int:
    """Check an absent key raises rather than reading as empty."""
    with tempfile.TemporaryDirectory() as d:
        try:
            warrant_records.claim_of("NOPE", _bib(d))
        except WarrantError:
            return 0
    out.append("selftest: a missing warrant returned a claim")
    return 1


def the_engine_error_is_not_an_exit(out: list[str]) -> int:
    """Check the engine-read refusal does not terminate the process.

    ⚑ THE ORIGINAL RAISED `SystemExit` FROM A LIBRARY FUNCTION, deciding the whole process's
    fate in a place that cannot know the caller's context. `WarrantError`'s half of this claim
    stays with the engine-free suite, since that is where the exception lives.
    """
    if issubclass(warrant_records.BibError, SystemExit):
        out.append("selftest: BibError is a SystemExit")
        return 1
    return 0


_ARMS = (
    the_engine_resolves,
    a_consumer_field_survives_the_parse,
    an_undeclared_field_is_still_dropped,
    a_claim_is_read_from_the_bib,
    a_tag_is_read_from_the_claim,
    an_unanchored_claim_is_refused,
    a_missing_warrant_is_refused,
    the_engine_error_is_not_an_exit,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"warrant-records selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"warrant-records selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
