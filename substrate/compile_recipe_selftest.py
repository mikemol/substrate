#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.compile_recipe` — the filter must cut what the parser reads.

⚑⚑⚑ THE ANCHOR CASES ARE THE ITEM, BECAUSE THE RETIRED SHIM'S FILTER SILENTLY MATCHED NOTHING.
It cut on `/^Statistics for /`, a header THIS AGDA DOES NOT EMIT, so the profile block survived
into every per-module log and was removed only when the GHC block happened to follow it.
MEASURED in a committed artefact: `Substrate/Cardinality.agdai.log` carries six leaked lines. A
`sed` that deletes nothing still exits 0, so nothing anywhere reported it.

⚑⚑ SO THE ARMS BELOW ASSERT AGAINST REAL CAPTURED OUTPUT, not against the regexes' own shape. A
case that re-spelled the anchor would agree with the module by construction and re-create the
defect one layer down — the same trap the `#row` separator bug set, where reader and writer each
held a private copy of one contract.

⚑ AND THE PARSER IS THE OTHER HALF. `proofcost._parse` anchors on the profile's `Total` line;
this module cuts from that same line. One arm drives BOTH so a future edit to either is caught by
the disagreement rather than by a build log going noisy.
"""

from __future__ import annotations

import re
import sys
from typing import Protocol, cast

from substrate import compile_recipe
from substrate.gate_module import gate_module


class Parses(Protocol):
    """The one thing this suite needs of `proofcost` — its profile parser.

    ⚑ A PROTOCOL, NOT `getattr`. The loader hands back an untyped module and `getattr` returns
    `Any`, which carries into every read downstream — the untyped-boundary defect this repo
    narrows AT the seam. Declaring the shape also states exactly what this suite depends on, so a
    rename of `_parse` becomes a visible break rather than a silent None.
    """

    def _parse(self, out: str) -> dict[str, object]:
        """Pull the SLIs out of one captured profile block."""
        ...


# Real `agda --profile=all ... +RTS -s` output, captured 2026-09-01 from
# `Substrate/Foundation/Nat/Nat.agda`. ⚑ VERBATIM, INCLUDING THE ABSENCE OF A `Statistics for`
# HEADER — that absence IS the defect under test, so a tidied fixture would erase it.
_CAPTURED = """Total         10ms
Miscellaneous 10ms
      27,014,752 bytes allocated in the heap
       1,558,648 bytes copied during GC
         370,072 bytes maximum residency (2 sample(s))
  Gen  0         4 colls,     0 par    0.001s   0.001s     0.0003s    0.0005s
  Productivity  51.4% of total user, 46.8% of total elapsed
"""

# A module's real diagnostic output, which must SURVIVE the cut.
_REAL = "Substrate/Foundation/Nat/Nat.agda:12,1-9: warning\n"

# The GHC block alone — `--profile=all` absent, `-s` present.
_RTS_ONLY = "      27,014,752 bytes allocated in the heap\n  Productivity  51.4%\n"

# The agda block alone — `--profile=all` present, `-s` absent.
_PROFILE_ONLY = "Total         10ms \nDeserialization            232ms (268ms)\n"

# What a leaked block would look like in a log, by the words that must not survive.
_LEAKS = ("Total", "Miscellaneous", "bytes allocated", "Productivity")

# The profile-cost tool, which owns the OTHER half of the block boundary.
#
# ⚑ `scripts/` IS PACKAGED (`pyproject.toml` declares `substrate` and `scripts`) and `gate_module`
# is its loader. A first cut reached for `scratch_module` — the loader for `scratch/` — and this
# arm failed honestly with "proofcost is unreachable", which is the loader reporting that the file
# is not where IT looked, never that the capability is absent. Three unpackaged directories, three
# loaders; picking by habit rather than by location is how a present tool reads as missing.
_PROFILER = "proofcost.py"


def _cut(text: str) -> str:
    """Apply the module's two anchors the way the emitted `sed` does: first line to EOF."""
    out = text
    for pattern in (compile_recipe.PROFILE_HEAD, compile_recipe.RTS_HEAD):
        found = re.compile(pattern, re.MULTILINE).search(out)
        if found:
            head = out[: found.start()]
            out = head[: head.rfind("\n") + 1] if "\n" in head else ""
    return out


def _parsed_total(text: str) -> int | None:
    """Return `proofcost._parse`'s total_ms for one captured block, or None when unreachable."""
    module, _why = gate_module(_PROFILER)
    if module is None or not hasattr(module, "_parse"):
        return None
    got = cast("Parses", module)._parse(text)  # noqa: SLF001 — the parse boundary is under test
    total = got.get("total_ms")
    return total if isinstance(total, int) else None


def the_profile_anchor_matches_real_output(out: list[str]) -> int:
    """Check the agda anchor matches captured output — THE ARM THE SHIM FAILED.

    ⚑⚑⚑ THE RETIRED FILTER'S ANCHOR MATCHED NOTHING. This asserts against text agda actually
    produced, so an anchor that stops matching a future agda fails HERE rather than in a build
    log nobody reads.
    """
    if not re.compile(compile_recipe.PROFILE_HEAD, re.MULTILINE).search(_CAPTURED):
        out.append(
            f"selftest: the profile anchor {compile_recipe.PROFILE_HEAD!r} "
            "matches nothing in real agda output"
        )
        return 1
    return 0


def the_rts_anchor_matches_real_output(out: list[str]) -> int:
    """Check the GHC anchor matches captured output."""
    if not re.compile(compile_recipe.RTS_HEAD, re.MULTILINE).search(_CAPTURED):
        out.append(
            f"selftest: the RTS anchor {compile_recipe.RTS_HEAD!r} "
            "matches nothing in real agda output"
        )
        return 1
    return 0


def the_cut_removes_both_blocks(out: list[str]) -> int:
    """Check nothing from either report survives.

    ⚑ THIS IS THE PROPERTY THE SHIM CLAIMED AND DID NOT HOLD: "build output stays clean". Six
    lines per module survived, in the logs the cap-ratchet reads.
    """
    got = _cut(_REAL + _CAPTURED)
    for leaked in _LEAKS:
        if leaked in got:
            out.append(f"selftest: {leaked!r} survived the cut: {got!r}")
            return 1
    return 0


def a_real_diagnostic_survives(out: list[str]) -> int:
    """Check the cut does not eat the module's own output.

    ⚑ THE POSITIVE CONTROL. A filter that removed everything would pass the arm above while
    destroying the warnings and errors the log exists to carry.
    """
    if _REAL not in _cut(_REAL + _CAPTURED):
        out.append("selftest: the module's own diagnostic was cut away")
        return 1
    return 0


def either_block_alone_is_cut(out: list[str]) -> int:
    """Check a run carrying only one report still cuts cleanly — WHY THERE ARE TWO ANCHORS.

    ⚑⚑ NOT BELT-AND-BRACES. `--profile=all` and `+RTS -s` are separate flags, so one-without-the-
    other is a reachable state, and anchoring on a single block would leak the other. That is
    exactly how the shim leaked: it had two anchors and one of them was dead.
    """
    if "bytes allocated" in _cut(_REAL + _RTS_ONLY):
        out.append("selftest: the RTS block survived when the profile block was absent")
        return 1
    if "Deserialization" in _cut(_REAL + _PROFILE_ONLY):
        out.append("selftest: the profile block survived when the RTS block was absent")
        return 1
    return 0


def the_parser_reads_what_the_filter_cuts(out: list[str]) -> int:
    """Check the cut boundary and the parse boundary are the SAME line.

    ⚑⚑⚑ ONE BLOCK, TWO CONSUMERS. `proofcost._parse` anchors on the profile's `Total` line to
    READ it; this module anchors on the same line to STRIP it. If they ever disagree, either the
    ledger loses its samples or the logs go noisy — and both failures are silent. Driving both
    from one fixture is what makes a divergence loud.
    """
    total = _parsed_total(_CAPTURED)
    if total is None:
        out.append(
            "selftest: proofcost is unreachable — the shared boundary is UNMEASURED, not agreed"
        )
        return 1
    if total <= 0:
        out.append(f"selftest: the parser read {total} from the block the filter cuts")
        return 1
    return 0


def the_lease_label_is_per_module(out: list[str]) -> int:
    """Check the recipe labels the lease by module, not by tool — ⟡claim-label-identity.

    ⚑⚑ THE SHIM HARDCODED `agda`, so every compile in the tree shared ONE ledger row and
    `membudget peaks` could only report a fleet-wide figure. A per-module label is what makes
    `auto` size from THIS module's history.
    """
    line = compile_recipe.compile_line("Substrate/Foundation/Nat/Nat.agda")
    if f"run {compile_recipe.LEASE} agda " in line:
        out.append("selftest: the lease is labelled `agda` — one row for the whole tree")
        return 1
    if "$(@F)" not in line:
        out.append(f"selftest: the label is not derived from the target: {line!r}")
        return 1
    return 0


def the_exit_code_survives(out: list[str]) -> int:
    """Check agda's exit code is re-raised rather than masked.

    ⚑ 251 IS THE RTS HEAP-CAP KILL THE CAP-RATCHET KEYS ON. Masking it to 1 erases the signal the
    gate exists to read.
    """
    for line in (
        compile_recipe.compile_line("X.agda"),
        compile_recipe.profiled_compile_line("X.agda"),
    ):
        if "exit $$rc" not in line:
            out.append(f"selftest: the exit code is not re-raised: {line!r}")
            return 1
    return 0


def the_retry_is_declared_at_the_call_site(out: list[str]) -> int:
    """Check the recipe declares idempotent-retry rather than inheriting it.

    ⚑ THE SHIM SET `MEMBUDGET_RETRY_OOM` AND NOTHING ELSE DID — which is why `Selftest.mk`'s
    suites had no retry ladder at all. Declaring it in the recipe makes the property readable
    where the command is.
    """
    if "MEMBUDGET_RETRY_OOM=1" not in compile_recipe.compile_line("X.agda"):
        out.append("selftest: the compile does not declare retry-on-OOM")
        return 1
    return 0


def the_stamp_is_its_own_line(out: list[str]) -> int:
    """Check a failed compile writes no stamp.

    ⚑ make ABORTS AT THE FIRST NON-ZERO LINE, so `touch` on its own line is what makes a stamp
    mean "this compile succeeded". Folded onto the compile it would stamp failures.
    """
    got = compile_recipe.recipe("$(BUILD)/X.agdai", "X.agda", "$(BUILD)/Y.agdai")
    if got[-1].strip() != "@touch $@":
        out.append(f"selftest: the stamp is not the last line on its own: {got!r}")
        return 1
    return 0


_ARMS = (
    the_profile_anchor_matches_real_output,
    the_rts_anchor_matches_real_output,
    the_cut_removes_both_blocks,
    a_real_diagnostic_survives,
    either_block_alone_is_cut,
    the_parser_reads_what_the_filter_cuts,
    the_lease_label_is_per_module,
    the_exit_code_survives,
    the_retry_is_declared_at_the_call_site,
    the_stamp_is_its_own_line,
)

_CASE_COUNT = 1 + 1 + 4 + 1 + 2 + 1 + 2 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"compile-recipe selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"compile-recipe selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
