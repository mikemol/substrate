---
name: precommit-gates
description: >-
  Fire this BEFORE answering any question about this repo's pre-commit gates: what a gate
  checks, why one fired, what a ratchet baseline means, how to pay a gate down, which phase a
  gate runs in, whether a gate is blocking or advisory, or what a green verdict actually
  asserts — and the instant you catch yourself about to say a gate "passes", "is clean", "can
  be skipped", or that something "would need `--no-verify`". It routes to the `gate-oracle`
  agent, which re-derives every figure from the hook and each gate's own baseline. It exists
  because a green gate here is routinely a fact about the CENSUS rather than the tree: a ratchet
  whose baseline is ABSENT takes the "no baseline → record and pass" branch and exits 0
  REGARDLESS of what it measured, so `check_mypy_ratchet --quiet` once exited 0 while reporting
  116 unrecorded type errors. Anyone reading exit 0 as "this is fine" is reading the instrument.
  ⚑ ABSENT and EMPTY are OPPOSITE, and this description conflated them under "degraded" until
  2026-08-21: ABSENT is a free pass, EMPTY is ZERO-TOLERANCE (the empty set as baseline, so
  every offender is a NEW key and nothing is grandfathered). Ask the agent for the live split;
  do not quote a count from here.
---

# The pre-commit gate oracle

**Route the question; do not answer it from this file.** Dispatch the `gate-oracle` agent
(`Agent` tool, `subagent_type: "gate-oracle"`). It starts fresh, reads the generated census
below, and runs the owning tools against the tree as it is *now*. This file carries only what a
reader must not get wrong on the way there.

## When this fires

- **A gate fired and you want to know why** — what its census is, what its statistic is, what
  the refusal hint means, and what the paydown actually is.
- **Any question about a ratchet** — what a baseline holds, what auto-lower means, why paydown
  did not record, what `RELOCATED` is.
- **"Is the tree clean?" / "do the gates pass?"** — the question this skill exists for, because
  the honest answer requires knowing which baselines are healthy.
- **Which phase / blocking or advisory** — the hook has both, and the distinction is invisible
  in a name list.
- **Anything about `--no-verify` or `SUBSTRATE_RATCHET_WRITE`** — both are bypasses of the
  promotion gate and the repo has recorded incidents for each.
- **On your own tells:** *"that gate is green"*, *"the type gate passes"*, *"I'll add an
  exemption"*, *"just set SUBSTRATE_RATCHET_WRITE"*, *"commit with --no-verify"*, *"the ledger
  says this gate never fails"*, *"the census is empty so there's no debt"*.

## The four facts to not get wrong

**1. A green ratchet can mean its baseline is broken, and three distinct states look alike.**
`ok` — a real grandfathered set. `EMPTY` — the file exists and is zero bytes, so
`os.path.exists` is true, the baseline is the empty set, and **every census member reads as a
NEW key** (this is why the cap ratchet reports 11-of-11 as additions). `ABSENT` — no file at
all, so `set_ratchet` takes the *"no baseline → record and pass"* branch and **exits 0
regardless of what it measured**. `scripts/gate_census.py --baselines` is the only reader.

⚑⚑ **EMPTY IS THE STRONG SETTING, NOT A DEGRADED ONE, AND THIS SECTION SAID OTHERWISE FOR A
DAY.** It read *"7 of 15 degraded"* and lumped both states under that word. Only ABSENT is
degraded — it is a FREE PASS. EMPTY forgives nothing: `paid` is always empty, so the
`write and not added` guard can never quietly lower it, which makes it the one baseline state
that cannot drift. An operator who wants no grandfathering wants exactly this.
**Do not quote a figure from this paragraph — read the generated block below**, which is gated
and currently reports **0 ABSENT**. The count moved because five baselines were deliberately
touched from ABSENT to EMPTY, i.e. the tree got STRONGER while this prose read as an alarm.

**2. Paydown NEVER records while any addition is present, so huge progress can sit invisible.**
`set_ratchet` computes and prints paydown first, but the write is guarded on
`write and not added`. Live consequence: the ban ratchet is showing **8455 blocked paydown**
(15552→7465) and the private ratchet **166**. A red ratchet is not "no progress" — read the
paydown line before concluding anything.

**3. The outcome ledger is OBSERVED, never DECLARED, and it currently inverts reality.** It has
38 rows from a single day covering 13 of 31 gates, prints no recency, and ranks `def/proof
separation` at 0% failure while that gate is **red right now**. Six currently-red gates have
never appeared in it at all. Cross-check the declared roster with `build_census.py --gates`
before believing any coverage or ranking figure, and treat a gate's *absence* from the ranking
as unmeasured rather than as passing.

**4. Four words are overloaded here, and each has produced a real error.**
- **"ratchet"** — `check_import_shape` is called one by the hook and has no baseline and never
  calls `set_ratchet`; it is a pure 0-tolerance violation gate that happens to be at 0.
- **"public"** — `check_public_ratchet`'s docstring says it counts *wholesale* re-exports (no
  `using`/`hiding`/`renaming`); its `census()` counts **every** `open … public`, narrowed or
  not, per a 2026-07-27 policy change the header never absorbed.
- **"violation"** — `check_carrier_locality` prints 22 off-home operators *informationally* and
  separately ratchets the sanctioned **exemption set** (baseline 5). Its exit 1 came from 2 new
  exemptions, not from the 22.
- **"advisory"** — `--quiet` on `check_def_proof_separation.sh` prints nothing **on failure**,
  and the hook wraps it in `|| true` plus a verbose re-run. It is BLOCKING; the `|| true` sits
  outside `run`, which has already set `fail`.

## Absence claims need a witness

This surface is where "the gate passes" is most often a fact about the METHOD. Live examples:

- **`check_mypy_ratchet.py --quiet` exits 0 and prints "would record 116 type errors."** There
  is no baseline. "The type gate is green" means the ratchet has never been baselined.
- **`set1_ratchet_cores.py` and `run_selftests.py --quiet` have both been measured exceeding
  10–15 minutes with no output.** Under `--quiet`, silence is indistinguishable from success. A
  timeout is neither a pass nor a fail — report it as unmeasured.
- **`⚑rederive:` does not clear the rederive gate** — the annotation is COUNTED, not exempted.
  Adding it to silence the gate leaves it red.

Report presence with witnesses; say "no mode by that spelling", never "the gate cannot do that".

## The census — GENERATED, do not edit

`python3 scripts/gate_census.py --sync` rewrites everything between the markers; `--check` is
the pre-commit drift gate on the **structural** block. Every figure is derived from the hook's
own call sites and each gate's own baseline declaration.

⚑ **This does NOT restate `build_census.py --gates`.** That owns the gate name+phase roster; a
second authority for one figure is the shape this toolkit retires. This owns what that cannot
see: blocking-vs-advisory, kind, and baseline health.

⚑ **THE CENSUS MEASURES ITS OWN GATE.** Adding or renaming a gate moves this block, and this
block is itself checked by a gate. A `--check` failure right after a hook edit is the
instrument working: re-sync.

--- BEGIN gate-census ---
⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 scripts/gate_census.py --sync`
rewrites everything between the markers; `--check` is a pre-commit gate that
refuses drift. Derived from the hook's own call sites and each gate's own
`BASELINE` declaration — no figure below is typed by a human.

⚑ **This does NOT restate `build_census.py --gates`** (the name+phase roster).
It owns what that cannot see: blocking-vs-advisory, kind, and baseline HEALTH.

```
── BLOCKING vs ADVISORY  (⚑ the distinction the name list cannot show)
   38 BLOCKING gate(s) — routed through the hook's `run()`, which sets `fail`
   2 ADVISORY  — a bare invocation with `|| true`, DELIBERATELY outside `run()`
     · collapse_check.py                  scripts/collapse_check.py
     · reuse_sweep.py                     scripts/reuse_sweep.py
   ⚑ Advisory gates are invisible to the outcome ledger BY CONSTRUCTION — the
     ledger records inside `run()`, which they bypass. Their absence from a
     ranking is not evidence they pass.

── KIND — 17 ratchet(s), derived from callers of `ratchet.set_ratchet`
     · scripts/check_ban_ratchet.py
     · scripts/check_cap_ratchet.py
     · scripts/check_carrier_locality.py
     · scripts/check_claims.py
     · scripts/check_clause_audit.py
     · scripts/check_discharge_ratchet.py
     · scripts/check_divergence_ratchet.py
     · scripts/check_mode_contracts.py
     · scripts/check_mypy_ratchet.py
     · scripts/check_public_ratchet.py
     · scripts/check_rederive_ratchet.py
     · scripts/check_snapshot_guard.py
     · scripts/check_sorted_order.py
     · scripts/check_sumtype_ratchet.py
     · scripts/ratchet_legacy.py
     · scripts/run_selftests.py
     · scripts/set1_ratchet_cores.py
   ⚑ Not all of these are hook gates, and not all hook gates are ratchets.
     Ratchet semantics: the census is a SET of opaque keys; a NEW key REFUSES,
     removals auto-lower. A bare count would let one offender swap for another.

── ⚑⚑ BASELINE HEALTH — the reading that has no other home
   gate                                   baseline                           state   keys
   scripts/check_ban_ratchet.py           ban_ratchet_baseline.txt           ok      15552
   scripts/check_cap_ratchet.py           cap_ratchet_baseline.txt           EMPTY   0   ⚑
   scripts/check_carrier_locality.py      carrier_locality_baseline.txt      ok      5
   scripts/check_claims.py                claims_baseline.txt                ok      14
   scripts/check_clause_audit.py          clause_unused_baseline.txt         EMPTY   0   ⚑
   scripts/check_discharge_ratchet.py     discharge_baseline.txt             ok      28
   scripts/check_divergence_ratchet.py    divergence_ratchet_baseline.txt    EMPTY   0   ⚑
   scripts/check_mode_contracts.py        mode_contracts_baseline.txt        EMPTY   0   ⚑
   scripts/check_mypy_ratchet.py          mypy_ratchet_baseline.txt          EMPTY   0   ⚑
   scripts/check_public_ratchet.py        public_ratchet_baseline.txt        ok      552
   scripts/check_rederive_ratchet.py      rederive_baseline.txt              ok      133
   scripts/check_snapshot_guard.py        snapshot_guard_baseline.txt        EMPTY   0   ⚑
   scripts/check_snapshot_guard.py        mutation_intent_baseline.txt       EMPTY   0   ⚑
   scripts/check_snapshot_guard.py        snapshot_split_baseline.txt        EMPTY   0   ⚑
   scripts/check_sorted_order.py          sorted_order_baseline.txt          EMPTY   0   ⚑
   scripts/check_sumtype_ratchet.py       sumtype_ratchet_baseline.txt       ok      48
   scripts/ratchet_legacy.py              (no baseline literal found)        UNREAD  0   ⚑
   scripts/run_selftests.py               selftest_contract_baseline.txt     EMPTY   0   ⚑
   scripts/set1_ratchet_cores.py          set1_baseline_cores.txt            EMPTY   0   ⚑

   ABSENT → the gate takes the `no baseline → record and pass` branch and exits
            0 REGARDLESS of what it measured. A green verdict here is a fact
            about the census, not about the tree.
   EMPTY  → the file EXISTS and is zero bytes, so `os.path.exists` is true and
            the empty set is the baseline: EVERY census member reads as a NEW
            key. Not the same condition as ABSENT, and not a grandfathered set.

── CONDITIONAL TRIGGERS — STAGED paths only (a dirty tree never fires these)
     ^(jea|el-atlas)/
     ^[+-][[:space:]]*(open import|import |module |public|renaming)
     ^[+-][^[:space:]+-].*[[:space:]]:([[:space:]]|$)
     ^jea/(metalanguage/.*|jea_oneforest|jea_omml_domain)\.py$
     ^jea/jea_.*\.py$

── CHECK → SYNC COUNTERPART
   scripts/gen_build_makefiles.py --check               scripts/gen_build_makefiles.py
   scripts/gen_build_makefiles.py --check-census        scripts/gen_build_makefiles.py --sync-census
   scripts/gate_census.py --check                       scripts/gate_census.py --sync
   jea/metalanguage/query_defs.py --check               jea/metalanguage/query_defs.py --compile
   scratch/toolmodes.py --check                         scratch/toolmodes.py --sync
   jea/metalanguage/sql_lift.py --check-census          jea/metalanguage/sql_lift.py --sync-census
   scripts/worklist.py --check                          (none — integrity check, not diff-vs-generated)
   scripts/sppf_node_index.py --check                   (none — integrity check, not diff-vs-generated)
   scripts/law_motif_apex.py --check                    (none — integrity check, not diff-vs-generated)
```
--- END gate-census ---

## The measured figures — DERIVED, NOT GATED

⚑ These read local, volatile state — baseline contents, the outcome ledger, a locally-built
`catalog.db`. Gating them would fail on every machine and after every commit.

--- BEGIN gate-observations ---
⚑ **DERIVED, NOT TYPED — AND NOT GATED.** These read local, volatile state
(baseline contents, the outcome ledger, a locally-built catalog.db). On another
machine they differ, and that is correct. **Re-run before asserting any.**

```
── HOW TO READ A GATE'S CURRENT STATE
   Ratchets:      python3 scripts/<gate>.py --quiet     (exit 1 = new key)
   Census/sync:   the --check mode in the table above
   Whole roster:  python3 scripts/build_census.py --gates
   ⚑ There is NO whole-pipeline read mode — see `Growing this`.

── THE OUTCOME LEDGER (last written 2026-08-25 09:03)
   scripts/gate_ledger.py --order / --report
   ⚑ OBSERVED, NEVER DECLARED, and it prints no recency — so a stale, partial
     ledger reads as a complete current ranking. Cross-check the declared
     population with `build_census.py --gates` before believing a coverage
     figure, and treat a gate's ABSENCE from the ranking as unmeasured.

── ⚑ TWO GATES RUN LONG ENOUGH THAT `--quiet` IS AMBIGUOUS
   `set1_ratchet_cores.py` and `run_selftests.py` have both been measured
   exceeding 10-15 minutes with NO output under --quiet. Silence there is
   indistinguishable from success. Give them a generous timeout and do not
   read a timeout as a failure — or as a pass.
```
--- END gate-observations ---

## Growing this

A missing mode is WORK, not a finding.

1. **`gate_ledger.py --coverage`** — which declared gates have zero rows. Named in its own
   docstring; today 18 of 31 are invisible. `build_census.py --gates` holds the population.
2. **`gate_ledger.py --staleness`** — newest-row age. Without it a three-week-old ranking reads
   as current.
3. **A whole-pipeline read mode** — there is no `--all` that runs every gate's read path and
   prints a verdict table; auditing the surface means ~25 individual invocations.
4. **A bounded or progress-reporting mode for the two long gates**, so `--quiet` silence stops
   being ambiguous between hung and passing.
5. **`check_def_proof_separation.sh --quiet` should emit a one-line verdict on failure.** The
   hook's `|| true` + verbose re-run workaround exists only because it does not.
6. **The hook's Δ-G2 comment says `scripts/jea_*.py`; the code matches `^jea/jea_.*\.py$`.** A
   prose-vs-code mismatch in a trigger path — the census now derives the regexes, so the
   comment is the thing to fix.
7. **Seven degraded baselines are the standing debt this census exists to surface.** Minting
   one is a `git commit` (the promotion gate), never `SUBSTRATE_RATCHET_WRITE=1` by hand.
