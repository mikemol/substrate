#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""check_rederive_ratchet.py — a site that RE-DERIVES an authority is counted, not exempted.

THE POLICY. Fifteen tools re-derived the Agda span rule instead of calling the module that owns
it, and each copy drifted its own way. So an independent derivation of something the tree already
has an authority for is DEBT, censused as a paydown-only ratchet: a new site is REFUSED, a removed
one auto-lowers the baseline, and the target is 0.

⚑ DECLARING A SITE DOES NOT CLEAR IT. A `⚑rederive:` marker makes the key read `::declared` so
the debt is visible and re-readable — it is COUNTED, never exempted. That is the whole difference
from an allow-list: a declaration records why a derivation exists, it does not make it free.

⚑⚑⚑ THE CENSUS, THE WALK AND THE CASES NOW COME FROM THE PACKAGE, and every one was differenced
against this file BEFORE the swap (gate-F83, gate-F85). Three things were verified rather than
assumed:

  * `substrate.rederive_census` reproduces this gate's key set EXACTLY over the whole tree —
    set equality, with a positive control that the census is non-empty so agreement cannot be
    vacuous.
  * `substrate.tool_walk` enumerates the same population, carrying each exclusion for its own
    recorded incident: `tests/` holds the broken forms as regression witnesses, `.edit-snapshots`
    once produced two keys for THIS file seconds after a guard run, and `jea`/`el-atlas` are
    absent from the ROOTS rather than excluded because a policy gate bars them from adopting the
    authorities at all.
  * The four cases this file's own `_selftest` held are all in the drained suite. One was NOT,
    until it was read: *a marker does not cover the line BEFORE it.* No key differential could
    have caught that, because a file with no marker yields identical keys under either coverage
    rule — the drain would have shipped a silent coverage loss with six green arms.

⚑⚑ SO THE DIFFERENTIAL EXPIRES HERE, DELIBERATELY. This gate now CALLS the census it was
differenced against, so that arm is a function agreeing with itself from this commit forward
(gate-F75). What remains independent is the committed baseline, which no code path here produces.

⚑ WHAT STAYS: the baseline path, the argv contract, the tally, and the refusal text. Those are
the application — where the census is a pure function of text and the walk of a repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts import ratchet
from substrate import rederive_census, rederive_census_selftest, tool_walk

ROOT = Path(__file__).resolve().parent.parent

# ⚑ A `str`, NOT A `Path`, AND THAT IS AN INTERFACE RATHER THAN A STYLE (gate-F76). Readers that
# census this gate narrow the attribute with `isinstance(declared, str)` and report a non-string
# as NO baseline — so a `Path` here leaves the gate correct while blinding every reader of it,
# rendering the whole census as newly added.
BASELINE = str(ROOT / "scripts" / "rederive_baseline.txt")


def census() -> set[str]:
    """Return the set of `<motif>::<relpath>#<ordinal>[::declared]` keys over this repo's tools."""
    return rederive_census.census(tool_walk.sources(ROOT))


def main() -> int:
    """Run the ratchet over the re-derivation census."""
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list", "--selftest"}, "check_rederive_ratchet")
    if rc is not None:
        return int(rc)
    if "--selftest" in sys.argv:
        # ⚑ DELEGATED TO THE DRAINED SUITE, which holds this file's four original cases plus the
        # arms the drain added. Keeping a second copy here would be two rosters of one fact —
        # and the copy that drifts is always the one nobody runs.
        return 0 if rederive_census_selftest.selftest() else 1

    keys = census()
    # ⚑ THE TALLY IS A SUMMARY, NOT A RENDERING, so it rides `summary=` rather than a per-key
    # hook — a tally rendered per key would repeat itself once per row.
    declared = sum(1 for k in keys if k.endswith("::declared"))
    return int(
        ratchet.set_ratchet(
            keys,
            BASELINE,
            "rederive-ratchet",
            "--quiet" in sys.argv,
            list_keys="--list" in sys.argv,
            summary=f"{declared} declared, {len(keys) - declared} undeclared",
            noun="independent derivation site(s)",
            refuse_hint=(
                "Call the authority instead: substrate.agda_mask.mask_comments / "
                "substrate.agda_naming.{module_path,module_file,module_name_of} / "
                "substrate.agda_statements.{statements,span_end} / "
                "substrate.agda_telescope.{telescope_span,telescope_groups,head_span} / "
                "substrate.agda_tokens.{word,body_tokens,mixfix_delims} / "
                "substrate.agda_walk.agda_files.\n"
                "  ⚑ DECLARING THE SITE DOES NOT CLEAR THIS GATE. `⚑rederive: <reason>` is "
                "COUNTED, not exempted — it marks the key `::declared` so the debt is visible "
                "and re-readable, but it is still a NEW key and the census still grew. A "
                "genuinely new independent derivation is a deliberate act: make it, declare "
                "it, and let `git commit` bank the baseline — the commit path IS the promotion "
                "gate, and it arms the write itself. That is the same discipline every other "
                "ratchet here follows.\n"
                "  ⚑ DO NOT SET THE WRITE VARIABLE BY HAND. `check_baseline_health` states the "
                "rule this hint must not contradict: setting it by hand 'banks a census against "
                "a tree nothing has approved (the `--no-verify` shape)'. This hint used to name "
                "that variable in parentheses right after saying 'on the commit path', and a "
                "reader audited it as a gate RECOMMENDING the bypass its own authority forbids — "
                "the parenthetical read as the mechanism to invoke rather than as the thing the "
                "commit path does for you."
            ),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
