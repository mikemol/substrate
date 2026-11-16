#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Render the per-module Agda compile recipe — an EXPLICIT lease, never a PATH interception.

⚑⚑⚑ THE PATH-INTERCEPTING agda SHIM IS RETIRED BY ITS OWN JUSTIFICATION (⟡retire-shim). The
generator used to prepend `scripts/agda-shim` to `make`'s PATH so a bare `agda` in a recipe
resolved to a wrapper. The comment defending that arrangement explained why BOTH mechanisms
existed: the shim budgets `agda` by intercepting a binary NAME, and that *"cannot reach a
`python3 sppf_db.py` recipe, which resolves straight past it — so every pg-touching recipe names
MEMBUDGET explicitly."* **Both halves are true, and together they say interception is
unnecessary here:** it is for call sites you do not control, and these recipes are GENERATED. The
call site was always ours.

⚑⚑ AND A DOWNSTREAM CONSUMER REACHED THE SAME FORM INDEPENDENTLY.
`scratch/estate/mat260/tools/jea_gate.py` builds `[membudget, "run", "auto", <label>, "--",
"agda"] + args` — explicit, per-module label, no PATH interception, on modules heavier than
substrate's. Corroboration from a separate implementation, not a design derived here.

⚑⚑⚑ THE SHIM WAS ALSO LEAKING ITS PROFILE BLOCK, MEASURED, INTO THE ARTEFACT ITS CONTRACT IS
ABOUT. Its filter was `sed -e '/^Statistics for /,$d' -e '/bytes allocated in the heap$/,$d'`,
and THIS AGDA EMITS NO `Statistics for` HEADER — `--profile=all` opens directly with
`Total <n>ms`. The first expression matched nothing, so the profile block survived and was
stripped only incidentally when the GHC `-s` block happened to follow it. MEASURED in a
committed log: `agda/_build/2.8.0/agda/Substrate/Cardinality.agdai.log` carries SIX leaked lines
(Total / Miscellaneous / Deserialization / Deserialization.Compaction / Parsing / Import), on one
module, in the logs the cap-ratchet and every log-driven codemod read. The shim's own comment
warned *"sed deleting nothing is still exit 0"* — about the OTHER expression.

⚑ SO THE BLOCK IS CUT BY ITS REAL BOUNDARY. `proofcost._parse` anchors on `^Total\s+…ms` and
`^Deserialization\s+…ms`: the filter and the parser want the SAME block, one to strip and one to
read. That makes the boundary a shared fact rather than two regexes that can disagree.

⚑ THE LABEL IS THE MODULE, WHICH THE SHIM COULD NOT DO. It hardcoded `agda`, so every compile in
the tree shared ONE row in the label ledger and `membudget peaks` could only ever report a
fleet-wide figure — the per-key sizing defect `_auto_mb`'s own comment describes
(*"per-label is the right key for a gate that runs once; per-module is the right key for work
that runs per core"*). A compile is the second kind.

⚑ EXTRACTED RATHER THAN EDITED INTO `gen_build_makefiles.py`, WHICH CARRIES 290 FINDINGS and is
refused whole by the per-file gate. That gate's own guidance is to extract the one concern into a
new module written clean in one pass; this is that module. This will _require_ _fully_
    splitting the monolith into smaller, independently clean modules; the monolith
    will not be editable until it can be wholly replaced.
"""

from __future__ import annotations

# The make variables a recipe assumes, defined once by the generator's preamble.
AGDA = "$(AGDA)"
FLAGS = "$(AGDA_FLAGS)"
CAP = "$(MEM_CAP)"
ROOT = "$(AGDA_ROOT)"
MEMBUDGET = "$(MEMBUDGET)"
PROOFCOST = "$(PROOFCOST)"

# ⚑ THE TWO REPORT BLOCKS, KEYED ON THEIR FIRST LINES — the only honest anchors, because neither
# carries a header. Agda's `--profile=all` opens at `Total <n>ms`; GHC's `+RTS -s` opens at
# `<n> bytes allocated in the heap`. Each is cut from its first line to end-of-file.
PROFILE_HEAD = r"^Total  *[0-9,]*ms"
RTS_HEAD = "bytes allocated in the heap$"

# The lease size. `auto` makes membudget size it from this module's own recorded peaks.
LEASE = "auto"


def compile_line(source: str) -> str:
    """Return the recipe line that typechecks one module under a lease.

    ⚑⚑ THE LOG IS WRITTEN FIRST AND REPLAYED ON FAILURE, WHICH IS THE PRE-EXISTING CONTRACT AND
    IS PRESERVED EXACTLY. A `make -j` console interleaves jobs, so a log-driven codemod reading
    the console would absorb one job's warnings into another's. One log per module is
    interleave-proof by construction.

    ⚑ AND AGDA'S EXIT CODE SURVIVES. `exit $$rc` re-raises it rather than masking to 1, because
    251 is the RTS heap-cap kill that the cap-ratchet keys on — collapsing it would erase the
    signal the gate exists to read.

    ⚑ `MEMBUDGET_RETRY_OOM=1` IS DECLARED AT THE CALL SITE, not inherited from a wrapper. An agda
    compile is idempotent, so a too-tight auto-sized lease self-corrects: the cgroup kill releases
    and membudget re-enters at the next power-of-two bucket. Declaring it here is what makes the
    property visible to a reader of the recipe.
    """
    agda = f"{AGDA} {FLAGS} +RTS -M{CAP} -RTS -i {ROOT} {ROOT}/{source}"
    return (
        f"\t@MEMBUDGET_RETRY_OOM=1 {MEMBUDGET} run {LEASE} $(basename $(@F)) -- {agda}"
        " > $@.log 2>&1 || { rc=$$?; cat $@.log >&2; exit $$rc; }"
    )


def profiled_compile_line(source: str) -> str:
    """Return the compile line with proof-cost capture — the always-on profiling path.

    ⚑⚑ THE PROFILE IS PARSED FROM THE LOG, THEN CUT FROM IT. Both steps read the same file, so
    there is no second capture and no temp file to leak: the log is the one artefact. `--parse`
    is best-effort by its own contract and must never alter the compile's exit code, so it is
    guarded with `|| true`.

    ⚑ THE CUT USES BOTH ANCHORS, AND THAT IS NOT BELT-AND-BRACES. Agda's block appears whenever
    `--profile=all` is passed; GHC's only when `-s` reaches the RTS. A run carrying one and not
    the other is a real state (`MEMBUDGET_NOPROFILE` half-applied, an agda without `-s` support),
    and anchoring on a single block would leak the other — which is precisely how the retired
    shim leaked six lines per module.
    """
    agda = f"{AGDA} --profile=all {FLAGS} +RTS -M{CAP} -s -RTS -i {ROOT} {ROOT}/{source}"
    return (
        f"\t@MEMBUDGET_RETRY_OOM=1 {MEMBUDGET} run {LEASE} $(basename $(@F)) -- {agda}"
        " > $@.log 2>&1 || { rc=$$?; cat $@.log >&2; exit $$rc; }; "
        f"{PROOFCOST} --parse $@.log {ROOT}/{source} > /dev/null 2>&1 || true; "
        f"sed -i -e '/{PROFILE_HEAD}/,$$d' -e '/{RTS_HEAD}/,$$d' $@.log 2>/dev/null || true"
    )


def recipe(target: str, source: str, prerequisites: str, *, profile: bool = True) -> list[str]:
    """Render the whole target: dependencies, mkdir, compile, stamp.

    ⚑ `touch $@` STAYS ON ITS OWN LINE. make aborts a recipe at the first non-zero line, so a
    failed compile writes no stamp and the module is retried next build. A stamp is only ever
    created by a compile that actually succeeded.
    """
    body = profiled_compile_line(source) if profile else compile_line(source)
    return [
        f"{target}: {ROOT}/{source} {prerequisites}".rstrip(),
        "\t@mkdir -p $(@D)",
        body,
        "\t@touch $@",
    ]
