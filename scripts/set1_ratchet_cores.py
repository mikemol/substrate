#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""set1_ratchet_cores.py — the Set₁ policy gate, a COLUMN READ over the interned SPPF (⟡gqs-ratchet-query).

⚑⚑⚑ THIS GATE IS BUILT ON A SUPERSEDED SPPF MODEL AND NEEDS A REWRITE, NOT A REPAIR
(operator, 2026-08-22: *"set1 needs to be rewritten; it was designed around an old sppf
model"*). Recorded here rather than patched, because every guard below is sound FOR THE
MODEL IT ASSUMES and none of them is what is wrong. ⟡set1-rewrite.

FOUR DEPENDENCIES ON THE OLD MODEL, each a distinct kind of staleness:

  1. IT READS `unit_obs.level`. The defmark tier was the SPPF's whole representation when
     this was written; today it is a small side table — MEASURED 2026-08-22: `unit_obs` holds
     14,779 rows (13,843 with a level) against a corpus of 2,833 cores and 443,169 interned
     `_node` rows. The structure moved to `_node`/`node_child`/`obs_node`; this gate did not.

  2. IT MEASURES BY RE-INGESTING. `_freshen` → `write_events(..., prune=True)` is a WRITE on
     what every other gate spells as a read-only `--quiet`. That is how a peer's two
     concurrent invocations deadlocked each other on `path_text` interning (measured: pids
     13932/15263, `RowExclusiveLock` vs `ShareLock`, opposite orders). **Asking the question
     is currently also a way to corrupt the answer.**

  3. IT COMPARES SCALARS, NOT KEY SETS. That is why it hand-rolled the baseline compare and
     so never inherited `ratchet.set_ratchet`'s write guard, its EMPTY-baseline reading, or
     its RELOCATED verdict — every one of which had to be re-derived here, and one of which
     (`parts[0]` on an empty file) crashed rather than stating a verdict.

  4. GUARD (3) REFUSES ON ANY CORE-COUNT CHANGE, so it is structurally red for the whole of a
     migration that adds files. `⟡ban-decompose` adds hundreds; the denominator guard makes
     the gate unusable exactly while the tree is moving most.

⚑⚑ THE REWRITE IS A PURE STRUCTURAL READ AND THE DATA IS ALREADY THERE. Agda 2.7+ unified
`Type/Prop/SSet` into `Univ :: Univ -> Level -> Sort'`, so a closed sort is `Univ _ (Max n [])`
— and that shape is interned as nodes. MEASURED on live:

    Univ 1,380 · Sort 261 · Max 1,381 · Plus 688 · FunSort 83 · PiSort 32 · Inf 1

and a `Max` node's children carry the level as a literal leaf:

    #Integer:0 -> 1,304   (Set₀)
    #Integer:1 ->   177   (Set₁)   ⟵ the debt, as a node count

So Set₁ debt is readable from `_node ⋈ node_child ⋈ terms` with NO ingest, NO write, NO
`unit_obs`, and NO denominator — and it becomes a KEY SET (which definition, at which site)
rather than a scalar, which is what lets it route through `set_ratchet` like its siblings and
inherit paydown, RELOCATED, and the empty-baseline reading for free.

⚑ NOT DONE HERE. The 177 is a CANDIDATE count, not a verdict: it counts `Max` nodes with a
nonzero level child, and mapping those to DEFINITIONS (the thing the policy is about) needs the
`unit_node`/`obs_node` join this note has not written. Quoting 177 as the debt would be the
scalar mistake one layer over.

⚑⚑ AND `set1_locate_census.py` IS **NOT** THE CLASSIFIER TO REUSE — IT READS THE SAME STALE
TIER. Run on live 2026-08-22 it reports `Set₁-inhabiting units: 0` over 3,183 cores (with 40
undecodable), and its degree table prints `reducible=0 floor=0 residue=0 of 0` while its own
header mentions 697. Two independent readers agreeing on zero is NOT corroboration when both
read `unit_obs`: it is one measurement counted twice.

⚑⚑ AND A FALSE DICHOTOMY I WROTE HERE AND AM RETRACTING. I recorded the zero-vs-node-tier gap
as *"either the level column stopped being populated, or those definitions are no longer
reachable — and the gate cannot tell the difference"*. There is a THIRD reading and it is the
likely one: **the two measure different things, and both may be right.**

    `_unit.level` / `unit_obs.level`  — the CODOMAIN sort of the definition's type.
                                        "does this definition INHABIT Set₁."
    a `Univ _ (Max 1 [])` node        — Set₁ MENTIONED anywhere in any term: a hypothesis,
                                        a parameter, a subterm.

A definition may take a `Set₁` argument and still inhabit `Set₀`. MEASURED: 2,112 of ~6,191
units have a level-1 `Max` in their support, while ZERO inhabit level ≥ 1 — and that spread is
exactly what "mentions vs inhabits" predicts. So the zero may be CORRECT, and my
"a green Set₁ gate is a fact about the tier it reads" was over-stated.

⚑ WHAT IS STILL MEASURED AND STILL ODD: `_unit.level` takes only two values corpus-wide —
0 (11,219 rows) and NULL (942). Never 1, never 2. A field with no variation is not evidence of
no debt; it is a field whose informativeness is unestablished. Guard (1) tests
`COUNT(level IS NOT NULL) == 0` to catch a level-blind shim, which 11,219 non-nulls passes:
**the guard checks PRESENCE, not VARIATION**, so a shim writing a constant reads as healthy.
That gap is real regardless of which reading of the zero is right.

⚑⚑⚑ THE ANSWER IS **BOTH**, AND THAT DISSOLVES THE QUESTION RATHER THAN CHOOSING A SIDE
(operator, 2026-08-22: *"Why not both?"* / *"Both will eventually be paid down to 0"*).

I had posed inhabits-vs-mentions as a policy fork to settle before writing a query. It is not a
fork: they are the SAME debt at two grades. `set1-is-grade-collapse` states it —
*"Set₁ IS grade-collapse/level-succession; construct across the grade (Set₀/step), never hold
the whole family"* — so a definition that INHABITS Set₁ has collapsed the grade, and one that
MENTIONS it is one step from collapsing. Same axis, different distance.

⚑ AND BOTH TARGETING ZERO IS WHAT MAKES THE DESIGN FALL OUT. If the mentions set were a
permanent frontier it would need a denominator and a policy about acceptable levels; at a
target of zero neither is needed, which is the same reasoning the EMPTY-baseline branch below
already uses (*"zero Set₁ is zero over any denominator"*). So:

    TWO CENSUSES, TWO BASELINES, BOTH PLAIN `ratchet.set_ratchet` KEY SETS.

      set1_inhabits   — the definition's CODOMAIN sort is Univ at level ≥ 1
      set1_mentions   — a `Univ _ (Max n [])`, n ≥ 1, anywhere in the unit's support

⚑ KEY SETS, NOT SCALARS, WHICH IS THE FIX FOR DEFECT 3 ABOVE. A key is the unit's identity
(`<relpath>::<qname>`), so the gate inherits `set_ratchet`'s write guard, its EMPTY reading,
its auto-lower, and its RELOCATED verdict — none of which the hand-rolled scalar compare has.
It also makes the report actionable: a count says "5 remain", a key set says WHICH five.

⚑ AND BOTH ARE PURE READS OVER `_node` / `node_child` / `unit_node` / `terms`, so `_freshen`
goes entirely (defect 2), the denominator guard goes with the scalar (defect 4), and
`unit_obs.level` stops being consulted (defect 1). The gate becomes safe to run concurrently
and outside the commit path, which is what `⟡set1-freshen-writes` was asking for.

⚑ MEASURED INPUTS FOR THE MENTIONS SIDE: 2,112 of ~6,191 units have a level-1 `Max` in their
support today; `Univ` is the parent of 238 such `Max` nodes. The inhabits side needs the
codomain-position restriction the shim's `codomainSort` already implements — the query must
reproduce "peel Πs, take the codomain, and if it is itself `Sort s` take that s", NOT merely
"a Univ appears". Getting that wrong turns inhabits into mentions and the two censuses collapse
into one.


USAGE
  ⚑ THIS BLOCK EXISTS BECAUSE ITS ABSENCE WAS ITSELF ONE OF THIS FILE'S FOUR OPT-OUTS from
  the shared layers (see `main`'s note: *"`toolmodes --find set1_ratchet_cores` returns ZERO
  hits, so it is absent from the mode census too"*). The divergence ratchet then read every
  dispatched flag here as UNDECLARED, which was correct.

  set1_ratchet_cores.py                  # the gate: census vs baseline, exit 1 on new Set₁ debt
  set1_ratchet_cores.py --quiet          # silent on success (hook form)
  set1_ratchet_cores.py --list           # ENUMERATE the census — WHICH units, not how many.
                                         # The point of defect 3's key-set fix: a count says
                                         # "5 remain", a key set says which five.
  set1_ratchet_cores.py --selftest       # the suite. Dispatches BEFORE the flag contract and
                                         # never reaches the census (which freshens the store).
  the tenant flags (`--sandbox` / `--live`)
                                         # ⚑ DELIBERATELY NOT WRITTEN AS A USAGE LINE HERE, and
                                         # that is the same rule the flags themselves follow.
                                         # ADMITTED VIA `needs_store=True` → `TENANT_FLAGS`,
                                         # never spelled here. This gate opens a connection in
                                         # `_freshen` AND `census_gate`, so which tenant it
                                         # reads is a real question; a bare run resolves LIVE,
                                         # which is how a corpus-scale scan happens by default.
  ⚑ `--halp` IS NOT A MODE. It appears as a literal in `_selftest` as the deliberately-bogus
  flag that asserts the refusal path fires. A census keying on argv-anchored literals reads it
  as a dispatched mode; it is a fixture, and documenting it would document a non-mode.

WHY NOT GREP (read before changing)
  The predecessor grepped `Set₁` in stripped source. That counts SOURCE TOKENS, not
  definitions: one `record R : Set₁` token yields ~4 Set₁ definitions in the core
  (the record, its constructor, and Agda's generated transp-/hcomp- helpers), and
  Set₁-TYPED FUNCTIONS carry no token at all. A sort is elaborated information; source
  text is elaboration's INPUT.

THE MEASURE
  A definition inhabits Set₁ iff the codomain sort of its type (Πs peeled; when the
  codomain is itself `Sort s`, that s) is `Type` at level >= 1. The shim emits this per
  defmark as {"sort":"Type","level":n}; write_events persists it as unit_obs.level, so the
  census is `set1_count` = COUNT(unit_obs WHERE level>=1) over catalog.db — NOT a ~94s
  per-core decode (this replaces the decode predecessor, ⟡gqs-ratchet-query). The pre-commit
  runs `make catalog` first (⟡gqs-precommit-reorder), so this queries a FRESH DB; standalone,
  it freshens catalog.db itself (INCREMENTAL — only mtime-advanced cores re-decode, via
  core_fp; auto-migrates a stale schema via write_events' version net).

THREE GUARDS (each preserved as a query — a silently-undercounting census is the exact
failure this gate exists to prevent; "cannot measure" is never "no debt"):
  (1) LEVEL POPULATED — unit_obs.level must carry values. A level-blind intern (a shim that
      emits no `level` — the repo's 2.8.0 shim predates the field, ⟡shim-upstream) makes
      every def look non-Set₁ and would silently lower the baseline to 0. The query-form of
      the old assert_shim_reports_sorts.
  (2) COMPLETENESS — every on-disk .agdai must be ingested (present in core_fp). An
      undecodable core is skipped by write_events → absent from core_fp → surfaced here.
      An incomplete census is not a low count.
  (3) DENOMINATOR — the core count must match the baseline's; a moving denominator is not a
      ratchet (a Set₁ count over a different core set is not comparable).

BASELINE  scripts/set1_baseline_cores.txt holds "<defs> <cores>". RATCHET: the count may only
  drop — it auto-lowers on a decrease, refuses on an increase, freezes at baseline.
  ⚑ A 1-FIELD BASELINE NOW REFUSES. It used to be "read with the denominator guard dormant",
  and the live file held the single token `0` — so Guard (3), whose own message says "a moving
  denominator is not a ratchet", NEVER RAN. A count without its denominator is not comparable;
  treating the absence as permission is how a guard becomes decoration.
  ⚑ WRITING IS OPT-IN via ratchet.may_write() / SUBSTRATE_RATCHET_WRITE, shared with the
  set-form gates. This gate hand-rolled its compare and so never received that guard: a plain
  `--quiet` run banked debt permanently, and it was the ONLY gate of which that was still true.

NO RAW SQL — every read is a named query_builders builder (⟡gqs-nolawsql): core_fp_ids,
  level_populated, set1_count. Only the incremental freshen (write_events) writes.
"""

import os, sys, glob, base64, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import sppf_db
import query_builders as QB
import schema as _schema  # rows/scalar: the named, backend-portable read contract
import store  # THE store authority — connections carry their backend

# ⚑⚑ A LATENT NameError, SURFACED BY JOINING THE ARG CONTRACT AND NOT INTRODUCED BY IT.
# `census_gate:137` already calls `ratchet.may_write()` and the module was NEVER IMPORTED —
# `pycodemod --importers ratchet` over this file returns 0 sites. So the write path raised
# `NameError: name 'ratchet' is not defined` on every run that reached it, which is every run
# that would have LOWERED the baseline. The paydown path of this gate has been dead.
#
# ⚑ AND IT WAS INVISIBLE FOR THE SAME REASON AS THE OTHER FOUR ABSENCES: the read path never
# reaches :137 when the baseline is unchanged, so the gate passes, and a gate that passes is
# not looked at. Adding `check_argv` — which calls into `ratchet` on the FIRST line of main —
# is what made the missing import raise immediately instead of only on a paydown.
import ratchet

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set1_baseline_cores.txt")


def baseline_verdict(parts, n, ncores):
    """(rc, kind) for a baseline's TOKENS against a measured (n, ncores) — no store, no I/O.

    ⚑ SPLIT OUT SO THE CONTRACT IS TESTABLE WITHOUT A CORPUS, exactly as
    `store._tenant_named` was split from `store.tenant` for the same reason: *"`tenant()`
    opens a connection, so a case driving it would need postgres up and would be asserting the
    connection rather than the DECISION."*  Here `census_gate` freshens catalog.db and scans
    ~3,600 cores, so a case driving IT would take ten minutes and assert the scan.  This is the
    decision alone — pure, total, and the thing the cases actually pin.

    `kind` names WHICH branch fired, because four of them return the same rc and a case
    asserting only the code cannot tell "refused for zero-tolerance" from "refused for a
    malformed baseline" — the distinction this gate's whole message text exists to draw.

      ()              → zero-tolerance: pass iff n == 0
      (n,)            → MALFORMED: a count with no denominator is not comparable
      (n, cores)      → compare, with the denominator guard
    """
    if not parts:
        return (0, "zero-tolerance-clean") if n == 0 else (1, "zero-tolerance-broken")
    if len(parts) < 2:
        return 1, "malformed"
    base_n, base_cores = int(parts[0]), int(parts[1])
    if base_cores != ncores:
        return 1, "denominator-moved"
    if n > base_n:
        return 1, "grown"
    if n < base_n:
        return 0, "paydown"
    return 0, "at-baseline"


def _freshen(cores, base):
    """Incremental event-tier freshen (no projection — the census reads unit_obs directly). A NO-OP after
    `make catalog` (core_fp all current); else re-decodes only mtime-advanced cores; auto-migrates a stale
    schema (write_events forces --full on a version mismatch)."""
    # ⚑ THE CONNECTION AND THE BACKEND MUST NOT DISAGREE, and this line made them.
    # It opened a raw `sqlite3.connect` while `SUBSTRATE_STORE` selected postgres, so
    # every helper downstream rendered postgres SQL (`%s`) against a sqlite cursor —
    # `sqlite3.OperationalError: near "%"`. A connection obtained anywhere but the
    # authority carries no backend, so the two can drift silently until a paramstyle
    # collides; routing through `store.connect` is what keeps them one fact.
    con = store.connect(mode="rw")
    sppf_db.write_events(cores, con, base, prune=True)
    con.commit()
    con.close()


def census_gate(cores, base, baseline_path, quiet=False, freshen=True):
    """The Set₁ ratchet as a query. Returns a process exit code (0 pass / 1 fail). `freshen=False` skips the
    incremental re-ingest (for testing an injected fault against a pre-built DB).

    ⚑ THE `catalog_db` PARAMETER IS GONE (⓺, 2026-08-11) AND IT WAS DEAD THROUGH TWO
    FRAMES. `main` passed `sppf_db.CATALOG_DB`; this function used it in exactly one
    place — handing it to `_freshen`, whose body never referenced it (see its ⚑ note:
    the connection comes from `store.connect`, which is the fix that made the path
    irrelevant). A value threaded through two call frames and dropped on the floor reads
    at every site as though the store were selectable there."""
    # ⚑⚑ COMPARED ON PATHS, NOT IDS (ⓝ P4) — AND UNDER SURROGATES THE OLD FORM WOULD HAVE
    # BLOCKED EVERY COMMIT. It built `on_disk` as `{_b64(relpath): path}` and subtracted the
    # store's `core_id` set. Once ids stopped being `_b64(relpath)` those two sets are DISJOINT
    # BY CONSTRUCTION, so `undec` becomes every core and this gate reports
    # "N of N cores UNDECODABLE — census incomplete" on a perfectly healthy store.
    #
    # ⚑ AND IT IS SIMPLER NOW, NOT MERELY DIFFERENT. The b64-reversibility trick existed to
    # recover a path from an id without a map; `core_fp.path` IS the map, so the gate compares
    # the thing that actually identifies a core on disk — its path — instead of comparing ids
    # and decoding one back to a path to report it.
    on_disk = {os.path.relpath(c, base): c for c in cores}
    if freshen:
        _freshen(cores, base)
    con = store.connect(mode="ro")  # was a raw sqlite3.connect — see _freshen's note

    # Guard (2) — COMPLETENESS: every on-disk core must be ingested; an undecodable one is absent from core_fp.
    # ⚑ THE PATH COMES FROM `terms`, WHERE THE ID INTERNED IT — there is no `core_fp.path`.
    # A core's `core_id` IS the term id of its relpath, so this join reads the path from its
    # single home rather than from a duplicate column.
    ingested = {
        r["text"]
        for r in _schema.rows(
            con, "SELECT t.text FROM core_fp f JOIN terms t ON t.term_id = f.core_id"
        )
    }
    undec = set(on_disk) - ingested
    if undec:
        print(
            f"set1-ratchet: {len(undec)} of {len(on_disk)} cores UNDECODABLE — census incomplete."
        )
        for rel in sorted(undec)[:3]:
            print("  " + rel)
        print(
            "  An incomplete census is not a low count. Rebuild cores (`make catalog`); do not certify."
        )
        con.close()
        return 1

    # Guard (1) — LEVEL POPULATED: a level-blind intern cannot certify Set₁ debt.
    # ⚑ `.fetchone()[0]` RAISES `KeyError: 0` ON PSYCOPG, and this gate is exactly where
    # that matters: its purpose is telling "zero Set₁ found" apart from "nothing was
    # measured", so a read that fails — or worse, one that returns a falsy value from an
    # empty store — turns the guard into the defect it exists to catch.
    if _schema.scalar(con, "SELECT COUNT(*) FROM unit_obs WHERE level IS NOT NULL") == 0:
        print(
            "set1-ratchet: unit_obs.level is empty — the shim emits no `level`, so Set₁ debt cannot be measured."
        )
        print(
            "  Rebuild a level-emitting shim (make -C jea/metalanguage shim), then `make catalog`."
        )
        con.close()
        return 1

    n = _schema.scalar(con, "SELECT COUNT(*) FROM unit_obs WHERE level >= 1")
    ncores = len(on_disk)
    con.close()

    # ── baseline compare / auto-lower (semantics identical to the decode version) ──
    #
    # ⚑ WRITING IS OPT-IN, via the SHARED resolver (`ratchet.may_write`).  This gate
    # hand-rolled its own census compare and therefore never received the write guard
    # `set_ratchet` grew after the read-mutates-state defect was MEASURED TWICE — so a
    # plain `--quiet` run of THIS gate, and only this one, banked debt permanently.
    # Audit IV named the class: the fix applied to the abstraction but not to the member
    # that opted out of it, invisible *because* the convention around it is articulate.
    # It also made the standing instruction "do not run the ratchet gates" true of one
    # gate and false of six, which trained avoidance of the wrong thing.
    write = ratchet.may_write()
    if os.path.exists(baseline_path):
        parts = open(baseline_path).read().split()
        # ⚑ EMPTY IS ZERO-TOLERANCE, AND IT IS THE STRONG SETTING — NOT A DEFECT.
        # An empty baseline file records NO EXCEPTIONS, so every offender is a new
        # offender and nothing is grandfathered; `check_baseline_health.py` states the
        # trichotomy (ABSENT = a free pass, REFUSED; EMPTY = zero tolerance, ACCEPTED).
        # Fourteen sibling baselines already read this way through `ratchet.set_ratchet`,
        # which parses an empty file to the empty key SET.  This gate compares SCALARS
        # over a denominator rather than key sets, so it never inherited that reading and
        # `parts[0]` raised IndexError on the very file shape the policy prefers — a
        # CRASH where the other gates state a verdict.  A non-pass that cannot say why is
        # not enforcement.
        #
        # ⚑ AND ZERO-TOLERANCE NEEDS NO DENOMINATOR.  Guard (3) exists because a COUNT is
        # incomparable across a changed core set (`5 Set₁ over 3000 cores` says nothing
        # about `5 over 3600`).  At a target of zero that reasoning does not apply: zero
        # Set₁ is zero over any denominator, so the guard is vacuous here rather than
        # skipped — which is why this branch may return before it runs.
        if not parts:
            if n == 0:
                if not quiet:
                    print(
                        f"set1-ratchet: ZERO-TOLERANCE baseline (empty) and {ncores} "
                        f"cores carry no Set₁-inhabiting definitions."
                    )
                return 0
            print(
                f"set1-ratchet: BROKEN — {n} Set₁-inhabiting definition(s) over "
                f"{ncores} cores, against a ZERO-TOLERANCE baseline (empty file = no "
                f"exceptions recorded, none allowed)."
            )
            print("  Set₁ is policy debt: do not FIELD a Set-valued carrier/relation —")
            print("  PARAMETERIZE it (set1-carrier-always-parameterize), or re-value into")
            print("  the Set₀ Tarski universe (Foundation.Universe's U/El; precedent")
            print("  Substrate.Category.Allegory.Power).  `scripts/set1_locate_census.py`")
            print("  classifies each offender and names the reducible ones.")
            print("  ⚑ Paying down means REMOVING Set₁, never re-recording a count here:")
            print("     an empty baseline cannot drift, which is why it is the strong one.")
            return 1
        base_n = int(parts[0])
        # ⚑ A MALFORMED BASELINE MUST REFUSE, NOT SILENTLY DISABLE THE GUARD.  The file
        # held the single token `0`, so `base_cores` parsed to None and Guard (3) — the
        # denominator guard, whose own message says "a moving denominator is not a
        # ratchet" — never ran.  The guard existed, was documented, was correct, and was
        # inert.  A missing denominator is not "no opinion"; it is an unusable baseline,
        # and treating it as permission is how a guard becomes decoration.
        if len(parts) < 2:
            print(
                f"set1-ratchet: MALFORMED BASELINE — {baseline_path!r} has no core "
                f"count, so the denominator guard cannot run."
            )
            print(
                f"  A count without its denominator is not comparable: {base_n} Set₁ "
                f"over an unknown number of cores says nothing about {n} over {ncores}."
            )
            print(
                f"  Re-baseline deliberately on the commit path "
                f"(SUBSTRATE_RATCHET_WRITE=1) once the tree is built."
            )
            return 1
        base_cores = int(parts[1])
    else:
        if not write:
            print(
                f"set1-ratchet: no baseline at {baseline_path} — would record {n} "
                f"Set₁ definitions over {ncores} cores (read-only; set "
                f"SUBSTRATE_RATCHET_WRITE=1)"
            )
            return 0
        import edit_snapshot as _es

        # ⚑ `intent="apply"` IS ENTAILED BY THE BRANCH: this line is reached only
        # past `if not write: return 0`, immediately above an unconditional write.
        # ⚑⚑ AND THE DECISION IS NOT IN ARGV AT ALL — `write` comes from the
        # ENVIRONMENT (`SUBSTRATE_RATCHET_WRITE=1`), so an argv-reading guard here
        # would refuse a run whose intent WAS stated, just not in the place argv can
        # see. `require_at_entry` cannot fix that either; the honest repair is for
        # this tool to spell the mutation pair on the command line, which changes a
        # gate's invocation contract and is the operator's call. Recorded.
        _es.guard("set1_ratchet_cores", [baseline_path], intent="apply")
        open(baseline_path, "w").write(f"{n} {ncores}\n")
        print(f"set1-ratchet: baseline recorded = {n} Set₁ definitions over {ncores} cores")
        return 0

    # Guard (3) — DENOMINATOR.
    if base_cores != ncores:
        print(f"set1-ratchet: CORE SET CHANGED — {ncores} cores now, baseline took {base_cores}.")
        print(
            f"  Set₁ count {n} is not comparable to baseline {base_n} over a different denominator."
        )
        print("  Rebuild the full tree, then re-baseline. (A moving denominator is not a ratchet.)")
        return 1

    if n > base_n:
        print(f"set1-ratchet: BROKEN — {n} > baseline {base_n} Set₁-inhabiting definitions.")
        print("  Set₁ is policy debt: do not FIELD a Set-valued carrier/relation — PARAMETERIZE it")
        print("  (see Substrate.Category.Lawvere's carrier-generic atoms).")
        return 1
    if n < base_n:
        # paydown is REPORTED either way; it only RECORDS on the commit path.
        if write:
            open(baseline_path, "w").write(f"{n} {ncores}\n")
            print(f"set1-ratchet: baseline LOWERED {base_n} -> {n} (debt paid down)")
        else:
            print(
                f"set1-ratchet: baseline would lower {base_n} -> {n} (debt paid down; "
                f"read-only, set SUBSTRATE_RATCHET_WRITE=1 to record)"
            )
    elif not quiet:
        print(f"set1-ratchet: at baseline {base_n} ({ncores} cores, legacy debt, frozen)")
    return 0


def _selftest():
    """⚑ THIS FILE HAD NO SUITE, AND THAT WAS THE FIFTH SHARED LAYER IT SAT OUTSIDE.

    Found by writing the fourth fix: I added the `--selftest` dispatch every sibling gate has,
    and `pycodemod --calls _selftest` reported "0 def(s), 1 call(s)" — the call being the one I
    had just written.  The other four absences: it hand-rolled its census compare (so it never
    received `may_write`), it was invisible to `check_baseline_health` until `ratchet_consumers`
    was re-keyed on baseline OWNERSHIP, it never called `check_argv`, and `toolmodes --find`
    returned zero hits.  Each was discovered separately, by tripping over it.

    ⚑ THE CASES DRIVE `baseline_verdict`, NOT `census_gate`.  The latter freshens catalog.db and
    scans ~3,600 cores; a suite that called it would take ten minutes and would be asserting the
    scan rather than the policy.  Same split, same reason, as `store._tenant_named`.
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    import rungs

    check = rungs.Cases(key="scripts/set1_ratchet_cores.py")

    # ── zero-tolerance: the EMPTY baseline, which is the STRONG setting ──────────────
    # ⚑ THIS BRANCH ONCE RAISED IndexError. `parts[0]` on an empty file crashed where every
    # sibling states a verdict — on the very file shape the operator's policy prefers.
    check(
        "empty baseline + zero offenders passes",
        baseline_verdict([], 0, 3600),
        (0, "zero-tolerance-clean"),
    )
    check(
        "empty baseline + any offender refuses",
        baseline_verdict([], 1, 3600),
        (1, "zero-tolerance-broken"),
    )
    # ⚑ AND IT NEEDS NO DENOMINATOR: zero Set₁ is zero over any core count, so the guard is
    # vacuous here rather than skipped.
    check(
        "...and the denominator is irrelevant at zero",
        baseline_verdict([], 0, 1),
        (0, "zero-tolerance-clean"),
    )

    # ── malformed: a count with no denominator ──────────────────────────────────────
    # ⚑ THE LIVE FILE HELD THE SINGLE TOKEN `0` FOR A MONTH, so Guard (3) — whose own message
    # says "a moving denominator is not a ratchet" — never ran. The guard existed, was
    # documented, was correct, and was inert.
    check(
        "a 1-token baseline is MALFORMED, not a zero",
        baseline_verdict(["0"], 5, 3600),
        (1, "malformed"),
    )
    check(
        "...and that is NOT the same verdict as zero-tolerance",
        baseline_verdict(["0"], 5, 3600)[1] == baseline_verdict([], 5, 3600)[1],
        False,
    )

    # ── the denominator guard ───────────────────────────────────────────────────────
    check(
        "a moved denominator refuses even when the count fell",
        baseline_verdict(["10", "3000"], 5, 3600),
        (1, "denominator-moved"),
    )
    check(
        "an equal denominator compares", baseline_verdict(["10", "3600"], 5, 3600), (0, "paydown")
    )
    check("growth refuses", baseline_verdict(["10", "3600"], 11, 3600), (1, "grown"))
    check(
        "unchanged is frozen at baseline",
        baseline_verdict(["10", "3600"], 10, 3600),
        (0, "at-baseline"),
    )

    # ── the arg contract, joined 2026-08-21 ─────────────────────────────────────────
    # ⚑ `--help` RAN THE FULL CENSUS before this. Measured: ten minutes, a catalog.db freshen
    # and a corpus scan, from a flag that should have printed usage.
    # ⚑ THE WITNESS IS `--halp`, NOT `--help`, AND THE SWAP IS NOT COSMETIC. `toolmodes`
    # derives a tool's dispatched modes from the flag literals in its source, so writing
    # `--help` here — even inside a refusal case — published it as a MODE THIS TOOL HAS. It
    # does not; the tool prints no usage. A census entry invented by its own test fixture is
    # the same class as a `--dead` verdict from a name-scoped scan: a fact about the METHOD
    # appearing as a fact about the substrate.
    check(
        "an unknown flag is refused",
        ratchet.check_argv(["s.py", "--halp"], {"--quiet", "--list"}, "t"),
        2,
    )
    check(
        "a known flag passes",
        ratchet.check_argv(["s.py", "--quiet"], {"--quiet", "--list"}, "t"),
        None,
    )
    # ⚑ `--dry-run` IS INHERITED FROM `UNIVERSAL_FLAGS` WITHOUT BEING DECLARED — the
    # authority-declares-its-own-vocabulary design, verified rather than assumed.
    check(
        "--dry-run is inherited, not declared",
        ratchet.check_argv(["s.py", "--dry-run"], {"--quiet"}, "t"),
        None,
    )
    return check.report()


def main():
    # ⚑⚑ THE SHARED ARG CONTRACT, JOINED AT LAST — and this gate was the ONE member outside it.
    # `ratchet.check_argv` has 21 call sites, every other ratchet gate among them; this file
    # read `"--quiet" in sys.argv` directly and validated nothing. Measured 2026-08-21 by
    # running it: `set1_ratchet_cores.py --help` DID NOT PRINT USAGE — it fell through to the
    # full census, freshened catalog.db, and scanned the corpus until it hit a ten-minute
    # timeout. An unknown flag on this gate costs ten minutes and a store write.
    #
    # ⚑ THAT IS EXACTLY THE INCIDENT `check_argv` EXISTS FOR, one severity higher than the one
    # it records. Its docstring: "a typo'd `--queit` silently degrades the gate to
    # verbose-but-passing — MEASURED across five gates, all exit 0 … harmless while they pass".
    # Here it is not harmless even while passing: the work runs.
    #
    # ⚑ AND THE PATTERN OF THIS FILE'S ABSENCES IS THE REAL FINDING. It hand-rolled its census
    # compare (so it never received `may_write`, and a plain `--quiet` banked debt permanently);
    # it was invisible to `check_baseline_health` until `ratchet_consumers` was re-keyed on
    # baseline OWNERSHIP; `toolmodes --find set1_ratchet_cores` returns ZERO hits, so it is
    # absent from the mode census too. Four shared layers, four opt-outs, each discovered
    # separately. `may_write`'s own note names the class: "the fix applied to the abstraction
    # but not to the one member that opted out of it."
    #
    # ⚑ `--selftest` DISPATCHES BEFORE THE CHECK, matching every sibling: a suite must be
    # runnable without satisfying the gate's own flag contract, and it must NOT reach the
    # census — which freshens catalog.db and scans the corpus.
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    # ⚑⚑ `needs_store=True` — THE FIRST ADOPTER, and for a measured reason. This gate opens a
    # connection in `_freshen` and again in `census_gate` (`store.connect(mode="rw"/"ro")`), so
    # which tenant it reads is a REAL question and it has never been asked: a bare run resolves
    # LIVE, which is how the corpus-scale scan happens by default. `store.tenant`'s advisory
    # fired into the void because nothing refused at the point of choice.
    #
    # ⚑ THIS ALSO ADMITS `--sandbox`/`--live` INTO THE KNOWN SET — via `TENANT_FLAGS`, not by
    # being listed here. A gate that did not declare `needs_store` would REFUSE those flags,
    # which is the opt-in asymmetry: a tool that opens no store has no business accepting a
    # tenant, and accepting one it cannot honour is the "looks like it ran" defect.
    rc = ratchet.check_argv(
        sys.argv, {"--quiet", "--list", "--selftest"}, "set1-ratchet", needs_store=True
    )
    if rc is not None:
        sys.exit(rc)
    quiet = "--quiet" in sys.argv
    base = sppf_db.substrate_core_root(os.path.join(ROOT, "agda"))
    cores = sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
    if not cores:
        print("set1-ratchet: NO CORES — cannot measure, so cannot certify.")
        print("  build the tree first (agda/Makefile / `make catalog`).")
        sys.exit(1)
    sys.exit(census_gate(cores, base, BASELINE, quiet=quiet))


# selftest-tenant: sandbox
# ⚑⚑ ⟡tenant-pragma, AND THE STAKES ARE HIGHEST HERE OF THE TWELVE. This tool has the recorded
# incident: `--quiet`, a gate that only COUNTS Set₁ debt, reached `_freshen` → `write_events(…,
# prune=True)`, ran ~1.5h, died on `DeadlockDetected`, and mid-run DESTROYED a live `--equiv`
# comparison window (3 cores comparable → 0). A read-shaped mode that writes is exactly the
# thing an unstated tenant makes unrecoverable, because the wrong store returns plausible rows
# nobody can distinguish (`sql-F2`).
# ⚑ `run_selftests._tenant` reads this and appends the flag; `store.tenant` exits 2 on an
# unstated tenant since ⟡tenant-mandatory (2026-08-24). SANDBOX is not a default here, it is
# the only admissible value: this suite must never reach the live corpus.
if __name__ == "__main__":
    main()
