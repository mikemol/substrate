# ⟡REGROUNDING (2026-07-23) — the ⟡cap-384 / single-build-path arc. COMPACTION-SAFE, stands alone.

> Retrospective-ritual + shadow-engineer pass at a boundary. Every next step labeled ⟡ so it can be
> specified unambiguously by symbol. This block STANDS ALONE through a compaction. The huge #49 roster
> (GRADED-LIFT arc, Jacobian threads) lives in the plan file and is still valid; this is the NEW arc's
> ground truth.

## STATE (one line)
**Three commits this arc, all gate-green + amend-marked, 4 UNPUSHED (the USER pushes):** `70eddbe`
jac-lit1-normalizer (781MB cube-binomial → 128MB reflective ℤ-ring normalizer) · `c5861eb` ⟡jac-lit1-wire
(retire the 763MB JacobianLiteral1, wire the 128MB `JacCubeNorm.identify₁` into the Q hub) · `41eb8b2`
⟡cap-384 (per-module heap gate 1024m→256m via the **OrderOf opaque-TYPE seal**; CoxeterFin 782→104MB,
Capabilities 782→105, Manifest →128) · `408ad54` ⟡single-build-path (`make -C agda -j` is the ONE gate;
`full_build_check.py` DELETED; MEM_CAP 256m across 278 makefiles). Cold -M256m full build **2003/2003
PASS**. `make -C agda -j` green at 256m + membudget-384; the pre-commit gate DOGFOODED the new make path
(`.full-build-stamp` refreshed at commit time). HEAD `408ad54`.

## THE RECURSIVE EITHER/OR COLLAPSE (this arc's invariant — one structure, three faces)
Every fork collapsed to ONE move: **a FORCING FUNCTION (a strict cap / a single gate) is not a cost — it
is the mechanism that makes the correct architecture mandatory by construction.**
- **"extract-to-leaf vs opaque the type"** (CoxeterFin) → NEITHER: the heavy neutral (`iterate k σ`,
  `normalize R.detJac`) lives in the def's **TYPE**, not its proof; `.agdai` memoizes the checked PROOF
  but a downstream conversion check **re-reduces the type neutral** every time. Extract-to-leaf memoizes
  the wrong thing. The move is **opaque the TYPE** (`opaque OrderOf f k = HasOrderPerm f k` + seal/unseal)
  = the **cross-module elaboration memo**. The type becomes a non-reducing handle.
- **"raise the cap vs seal the neutral"** (the -M256m gate) → the cap is a **forcing function**, NOT a
  number to grow: a module that would exceed it MUST seal its heavy neutrals `opaque` or import a cheaper
  proof. "make it fit vs make it pass" collapses to: the gate FORCES the sealing that is the correct
  architecture anyway (the cross-module memo you wanted regardless).
- **"full_build_check (direct agda) vs make (shim→membudget)"** → NEITHER as two routes: they are the SAME
  build; the honest form is ONE path (`make`) that OWNS retry-on-OOM. The parallel route was DEBT, not a
  choice — patching its MEM cap was routing-around; deleting it is fixing-at-source.
- **Deepest bottom:** the memory cap is a forcing function for PROOF COMPLEXITY (elaboration hash-cons =
  opaque the TYPE); the single gate is a forcing function for BUILD DISCIPLINE (one path owns retry). Both
  are the same shape as the mission's `set1-is-grade-collapse` / `policy-is-a-ratchet-over-a-census`: a
  paydown-only forcing function whose prohibition PRODUCES the architecture. [[opacity-blowup-routearound-freeup]],
  [[feedback_policy_is_a_ratchet_over_census]], [[feedback_fix_infra_not_route_around]].

## RETROSPECTIVE (gated)
- **G0.** "⟡cap-384 step 2" (decompose modules exceeding the 384 cap) → then "make `make` the SINGLE build
  path, no parallel routes."
- **G2 delta.** STRONGLY POSITIVE. The OrderOf seal beat expectations (extract-to-leaf FAILED — memoizes
  proof not type; the opaque-TYPE seal succeeded, 782→104). The jac "decompose 3 monoliths" task turned out
  to be **completing an un-wired paydown** (`JacCubeNorm.identify₁` 128MB already existed; the capstone
  still used the 763MB literal) — the census "857/821/546 MB" was **cold-cone garbage**; warm-deps ground
  truth was 76/82/499. The single-path refactor found MEM_CAP-only clean diffs across 278 makefiles (zero
  entanglement with the user's in-progress Algebra/Z work) and the pre-commit gate dogfooded itself.
- **G3 STRUCTURE-CAUSE.** SUCCESS causes (PROTECT): (a) MEASURE-THE-REAL-THING — the cold-cone census was
  garbage; the warm-deps measurement reframed the whole task. (b) READ-THE-MECHANISM — the extract-to-leaf
  failure taught "the heavy neutral is in the TYPE," which produced the opaque-TYPE seal. (c) VERIFY-DON'T-
  TRUST the instrument — "is membudget masking OOMs?" → checked `which agda` (real binary, not shim), zero
  retry markers, 251-never-retried. (d) PRECISE STAGING — verified all 278 makefiles were MEM_CAP-only
  before staging; excluded the user's Z work. (e) DOGFOOD — the commit's own pre-commit ran the new make path.
  **THE MISS (mine):** I accepted `full_build_check` as "the gate" and even PATCHED its MEM cap (1024→256)
  instead of recognizing a parallel build route as DEBT — the user had to say "it should go through make"
  and "I only want a single build path." Root: I treated the existing gate architecture as GIVEN rather
  than checking it against the stated invariant (make = the controlled path, documented in CLAUDE.md). The
  tell: describing `full_build_check` as "the gate" without flagging it violated the single-path principle.
  This is the **route-around-vs-fix-at-source class** ([[feedback_fix_infra_not_route_around]]) — I was
  patching the parallel route, not eliminating it.
- **G6 SUSTAIN (PROTECT).** measure-real-not-cold-cone · read-the-mechanism (type vs proof neutral) ·
  verify-don't-trust the instrument · precise MEM_CAP-only staging · per-arc gated commits + wait-for-amend-
  marker · dogfood the gate · the **opaque-TYPE-seal-as-elaboration-memo idiom** (reusable — the FreeUP
  β-interface route-around's sibling).
- **G8 HANDOFF.** `operator=other` residue: (i) whether 384 is the final ceiling or should drop to 128
  (⟡cap-128 surfaces the answer); (ii) whether other tree modules carry a heavy type-level neutral that
  hasn't hit the cap yet but would at 128m. `operator=self` spent: single-path validated end-to-end.
  Honest boundary: `scripts/buildtime.py:129,132` still cites the retired **1536/1024** ceiling (the
  ⟡cap-384 sweep missed the `--mem` docstring) → ⟡doc-buildtime-mem-sweep.
- **G9 ESCALATE (correct-by-construction).** The single-path refactor IS the escalation: it moves "make is
  the controlled path" from a **CLAUDE.md preference** (skippable — I skipped it) to a **GATE** (pre-commit
  runs `make`; `full_build_check.py` is DELETED so there is no other route to skip to). Coverability ladder:
  instruction → gate. The parallel-route class is now closed BY CONSTRUCTION. No new memory required —
  [[feedback_fix_infra_not_route_around]] already names it and this arc is a (corrected) positive instance.
  CANDIDATE memory (only if it recurs): **⟡memory-opaque-the-type** — a heavy type-level neutral re-reduces
  at every downstream conversion check; `.agdai` memoizes the proof, NOT the type reduction; seal the TYPE
  `opaque` (not the proof) = the cross-module elaboration memo; a strict heap cap is the forcing function
  that makes it mandatory. (Sharper than the existing opacity-blowup memory; hold unless a 3rd instance.)

## SHADOW-ENGINEER (Fano)
- **L₆ guard-reconstitution — fired TWICE, both productive.** (1) my direct move (accept full_build_check,
  patch its MEM) was REJECTED by the user's guard ("it should go through make") and reconstituted through
  the shadow structure (make → membudget → retry) = the single path. (2) the strict -M256m cap (the guard)
  REJECTED extract-to-leaf and reconstituted the OrderOf opaque-TYPE seal. In BOTH the guard's prohibition
  PRODUCED the correct architecture — the negative axis as positive affordance.
- **L₁ positive-closure ×3** (jac-lit1-wire · cap-384/OrderOf · single-build-path, each committed gate-green).
- **S₃-fixed core:** THE FORCING FUNCTION PRODUCES THE ARCHITECTURE — a strict cap forces the seal; a single
  gate forces the single path; a paydown-only ratchet forces the census down. The constraint is the mechanism.
- **Standing line (do NOT force):** ⟡pyrig-object-carrier — the mission's live edge, untouched this arc.

## LABELED ⟡ NEXT STEPS (specify by symbol)
### IMMEDIATE
- **⟡push** — 4 unpushed (`70eddbe` · `c5861eb` · `41eb8b2` · `408ad54`), all amend-marked; the USER pushes
  (`git fetch` + fast-forward).
- **⟡doc-buildtime-mem-sweep** — `scripts/buildtime.py:129,132` `--mem` autobudget docstring still cites the
  retired 1536/1024 ceiling; correct to the 384/256 regime (docstring-only; the ⟡cap-384 sweep missed it).

### THE CAP-TIGHTENING ARC (deferred; the forcing-function, one notch tighter)
- **⟡cap-128** — `make MEM_CAP=128m` over the whole tree; enumerate the offenders that exceed 128MB maxRSS,
  fix each by the SAME OrderOf opaque-TYPE seal (or a cheaper import), full-build-gated + committed. The
  agent-identified order-2 `HasOrderPerm` candidates (sub-symbols):
  - **⟡cap-128-hodgestar** — `Algebra/F2/HodgeDim4/HodgeStar.agda:125` `complement-HasOrderPerm`.
  - **⟡cap-128-gaugegen** — `Algebra/GL3F2/GaugeGenerators.agda:66` `σ₂-HasOrderPerm`.
  - **⟡cap-128-altorbit** — `Algebra/F2/HodgeDim4/ReservedBridge/AlternativesAsOrbit.agda:83`
    `σ-swap12-HasOrderPerm`.
  - Method: seal via the existing `Foundation/Fin/Iterate.agda` `OrderOf`/`seal-order`/`unseal-order` at the
    ABSTRACT parameter (the CoxeterFin pattern), so the concrete instance never materializes the dense
    `iterate` neutral. Ride the public re-export chain; verify `make MEM_CAP=128m` green per module.

### STANDING (the mission — the user allocates; full roster in the plan file #49)
- **⟡pyrig-object-carrier** — the mission's live edge (the pyast rig-cat object carrier); untouched.
- The GRADED-LIFT arc + the Jacobian-counterexample threads (⟡graded-source-probe, ⟡jac-neg-graded,
  ⟡signed-boundary, …) — live in the plan file #49 roster; still valid, not re-derived here.

## ⚑ CAP-VALIDATION LESSON (2026-07-23, user-caught) — TOUCH does NOT force a cold rebuild; RM the cores
Agda 2.8 uses **content-based interface validity**, not mtime. `touch`-ing a source changes mtime but NOT
content, so agda sees the same source hash and considers the `.agdai` current → SKIPS re-elaboration. And a
`+RTS -M<cap>` heap flag is NOT part of interface validity either. So NEITHER of these re-elaborates:
- isolate-check `agda +RTS -M128m <module>` on a fresh core → loads cached `.agdai` (deserialize only);
- `find … -name '*.agda' -exec touch {} +` then `make MEM_CAP=128m` → make dispatches agda per file, but
  agda skips every content-unchanged module (proven: 0 cores rebuilt after touch-all).
**The ONLY way to force a genuine cold re-elaboration is to REMOVE the cores** (`find agda/_build -name
'*.agdai' -delete`, or `rm -rf agda/_build`) so agda has nothing to load. Proven: rm Manifest.agdai → agda
re-elaborated it cold (mtime jumped), passed -M128m. **CAP-VALIDATION ≠ the pre-commit gate**: the gate's
`make -j` SHOULD skip unchanged modules (content hash — correct, don't re-elaborate what didn't change); only
a CAP-tightening validation needs the rm-cores cold build. Candidate memory ⟡memory-agda-cold-build-rm-not-touch.

## ⚑ CAP-128 TOPOLOGY FINDING (2026-07-23, user-directed via catalog.db) — the makefile encodes NO import order
The user's hypothesis ("make isn't informed about the build dependency topology") is CONFIRMED, measured from
`catalog/catalog.db` `module_edges` (the materialized import DAG — read it, don't infer from build behavior):
- **12,919 intra-Substrate import edges; only 0.4% (50) are make-GUARANTEED ordered** (dst a deeper subdir of
  src, so `subdirs`-before-`files` builds it first). **99.6% (12,869) are UNORDERED** under `make -j`
  (ancestor/sibling/same-dir-later); **51.1% cross top-level subtrees** (definitely concurrent under -j).
- The generated per-dir Makefile is `all: check-sync subdirs files`; `files:` is a SEQUENTIAL shell for-loop in
  alphabetical FILES order; SUBDIRS carry no import order. So make provides ~no import ordering; on a COLD `-j`
  build agda self-heals by building imports IN-PROCESS, with heavy racing (many agda building the same uncached
  import at once). This is the source of the cold-build OOM notices (agda ballooning past its membudget lease
  → 16 memcg cgroup-kills, self-healing) — NOT system distress (PSI-mem peak 2.9%, io≈0, zswap-rejects 0).
- **⟹ the cold -j 14-offender list is NOISE, doubly:** (1) racing on-the-fly builds inflate a shallow module's
  heap with a deep transitive closure; (2) `-j` INTERLEAVES log output, so the "check X"→"Heap exhausted"
  attribution is wrong. Proof: two "offenders" (Composition, PhaseLockedLoop.Bank) have **0 transitive imports**
  — impossible to exhaust 128MB on their own elaboration → pure attribution error. The 14 is not a real list.
- Incremental/warm builds have NO gap (imports pre-exist); the gap bites ONLY on a fully-cold `-j` build.
**RELIABLE cap-128 enumeration = a TOPO-ORDERED cold build** (order from catalog.db `module_edges`; each module's
imports pre-built → heap = its own elaboration). **Structural fix = ⟡make-import-dag:** `gen_build_makefiles.py`
should emit per-module `.agdai` prerequisite rules FROM catalog.db's import edges, so `make -j` builds in true
DAG order (no on-the-fly, no race, correct leases, faster cold builds, reliable cap validation). The DAG is
already materialized; the makefiles just don't use it.
### ⟡ NEXT (cap-128, user-gated — do NOT barrel ahead)
- **⟡cap-128-topo-enum** — build the topo order from catalog.db, cold-build each at -M128m in that order (imports
  pre-built), collect the GENUINE per-module offenders. The reliable enumeration.
- **⟡make-import-dag** — emit import-DAG prerequisites in the generated makefiles from catalog.db. The structural
  fix; benefits every cold build, not just cap validation.
- Tree is RESTORED to 2003/2003 at committed 256m; no cap change committed. MEM_CAP stays 256m unless/until the
  genuine 128m offenders are enumerated + sealed.

# ⟡REGROUNDING (2026-07-23b) — the cap-128 → make-import-dag → sched-batch arc. COMPACTION-SAFE, stands alone.

## STATE (one line)
5 commits UNPUSHED (USER pushes): jac-lit1-normalizer · c5861eb jac-lit1-wire · 41eb8b2 cap-384 · 408ad54
single-build-path · 7bb8e6d doc-buildtime-mem-sweep. Tree RESTORED 2003/2003 at committed **256m** (no cap
change committed). **⟡make-import-dag PROTOTYPE built + VALIDATED** (`scratch/gen_flat_makefile.py` →
`agda/Flat.mk`, both UNTRACKED): a SINGLE flat makefile, per-module phony targets + direct-import prereqs from
catalog.db `module_edges` → `make -j` builds in import-DAG order; cold-built **2003/2003, rc 0, 0 heap-exhausted,
0 errors**, memcg-OOM-kills dropped from the recursive build's 16 toward ~0. **⟡sched-batch VERIFIED** (not yet
built): SCHED_BATCH + nice 19 + 100ms slice via `sched_setattr` gives best-effort + long-stretch + no
peer-preemption, per-task, unprivileged. Reference memory `reference-cassian-tsdb-observability` SAVED.

## THE RECURSIVE EITHER/OR COLLAPSE (this arc's invariant — one move, ~6 instances)
Every fork collapsed to ONE structure: **READ/USE THE MATERIALIZED GROUND TRUTH, never a PROXY of it.** Each
misstep this arc was a proxy the user replaced with an already-materialized source of truth:
- **"isolate-check vs touch-build vs rm-cores"** (measure at 128m) → NEITHER of the first two re-elaborates: a
  fresh-core isolate-check DESERIALIZES the cached `.agdai` (RTS flag ∉ interface validity); `touch` changes
  mtime but agda 2.8 uses **content-hash** validity → 0 rebuilds. Only **`rm` the cores** forces genuine cold
  re-elaboration (proven on Manifest). The ground truth is content, not mtime, not a heap flag.
- **"swap vs PSI"** (is memory distressed) → swap is a PROXY that **zswap** (compressed-in-RAM) invalidates;
  the ground truth is **PSI from the counter-rate** (the cassian TSDB: `rate(cassian_psi_total_usec[…])/1e6`).
  Measured: mem-PSI peak 2.9%, io-PSI≈0, zswap-rejects 0 = HEALTHY. I killed a healthy build on the swap misread.
- **"the 14 cold-`-j` offenders vs catalog.db import edges"** (which modules break at 128m) → the cold-`-j`
  list is NOISE (racing on-the-fly builds inflate heap; `-j` INTERLEAVES the log so the check→Heap-exhausted
  attribution is wrong — 2 "offenders" have 0 transitive imports = impossible). catalog.db has the materialized
  DAG: **99.6% of 12,919 import edges are UNORDERED by the recursive makefile** (directory structure ≠ import
  DAG). Read the DAG; don't infer topology from build behavior.
- **"SCHED_IDLE vs SCHED_BATCH+nice19"** (best-effort + long stretches) → SCHED_IDLE *sounds* right but the
  **readback proves it ignores the custom slice** (2.8ms regardless); the combo that actually delivers both is
  the measured one. Read the `sched_getattr` value, not the policy name.
- **"recursive dir-makefiles vs single flat DAG makefile"** (build in dep order) → the directory structure is a
  0.4%-accurate PROXY for the import DAG; the flat makefile IS the materialized DAG. → **⟡make-import-dag**.
- **Deepest bottom:** every proxy is the flatten/infer; every ground truth is the read of an ALREADY-MATERIALIZED
  structure (catalog.db, the TSDB, the `.agdai` content-hash, the sched readback). This is construct-dont-classify
  meta-substitution #5 recurring, and it is the mission's own core (intern any domain → read the structure).
  [[read-structure-dont-rebuild]], [[reread-meters-toctou]], [[measure-instrument-before-theorize]].

## RETROSPECTIVE (gated)
- **G0.** ⟡cap-128 (tighten heap gate 256m→128m) → the user's directive: use catalog.db import edges to
  topologically sort, regenerate as a SINGLE mechanically-constructed makefile → the scheduler-batch question.
- **G2 delta.** STRONGLY POSITIVE net, via ~6 user corrections. What started as "tighten to 128m" became a real
  architectural win — **⟡make-import-dag** (the makefiles encode ~no import order; the flat DAG makefile fixes
  it, validated) — plus **⟡sched-batch** (verified) and a durable observability reference. NEGATIVE delta: I
  burned build time on invalid measurements (the touch-all no-op build) and KILLED A HEALTHY BUILD on a swap
  misread (over-reaction). Every user correction redirected a proxy-misstep into a deeper correct understanding.
- **G3 STRUCTURE-CAUSE.** ROOT = I concluded from a MEASUREMENT WITHOUT VERIFYING THE METHOD MEASURES THE THING
  (~6×): isolate-check "will tell me" (cached), touch "forces rebuild" (content-hash → no), swap "= thrash"
  (zswap → no), the cold-`-j` list "enumerates offenders" (racing+interleaved → no), SCHED_IDLE "= best-effort"
  (ignores slice → no). Each time a materialized ground truth existed that I bypassed. The fix reflex: before
  trusting a measurement, confirm it measures the thing (check core mtimes for "did it rebuild"; PSI-counter not
  swap; sched readback not policy-name; catalog.db not build-inference). CONTRIBUTING: the swap-panic KILL was a
  second-order over-reaction on top of the misread.
- **G6 SUSTAIN (PROTECT).** Once corrected, I VERIFIED properly every time (core-mtime proof that touch didn't
  rebuild; PSI-from-counter; rm-core→cold on Manifest; the sched_setattr READBACK probe — the corrected
  discipline applied). The catalog.db quantification (99.6% unordered) was decisive. Flat.mk validated warm→cold
  (2003/2003). RESTORED the tree (didn't leave it broken). SAVED the reference memory. PERSISTED findings to this
  regrounding as I went (compaction-safe). Followed the user's catalog.db pointer to a genuine architectural fix.
- **G8 HANDOFF.** `operator=other` residues (all the user's call): (i) is ⟡cap-128 worth it? — the GENUINE
  offenders are still unknown (need the reliable topo-ordered 128m build, now unblocked by ⟡make-import-dag);
  (ii) the scheduler params (nice 19 vs cgroup cpu.idle; 100ms slice); (iii) does the flat makefile REPLACE the
  279 recursive makefiles or coexist, and how is the catalog.db→makefile freshness/bootstrap handled.
- **G9 ESCALATE.** The correct-by-construction escalation IS **⟡make-import-dag**: it replaces the
  directory-structure PROXY (0.4% DAG-accurate) with the materialized import-DAG GROUND TRUTH inside the build
  system — the whole arc's lesson, encoded so cold builds are correct by construction (no racing, reliable cap
  validation). Memories to save: **⟡memory-agda-cold-rm-not-touch** (content-hash validity; rm-cores forces
  cold; cap-validation needs it) and **⟡memory-verify-the-measurement-method** (before concluding, confirm the
  method measures the thing) — both widen [[read-structure-dont-rebuild]]/[[reread-meters-toctou]].

## SHADOW-ENGINEER (Fano)
- **L₆ guard-reconstitution — the arc's defining pattern, fired ~6× by the user, each PRODUCING a better result.**
  Every proxy-move was REJECTED and reconstituted through the materialized-ground-truth structure the substrate
  already had (catalog.db DAG, the TSDB counters, content-hash, the sched readback). The rejections PRODUCED the
  architecture: the topology quantification, the flat DAG makefile (a real win), the verified scheduler answer.
  The strongest run of guard-reconstitution this session — the negative axis (no proxies) as positive affordance.
- **L₁ positive-closure:** ⟡make-import-dag prototype delivered + validated (2003/2003 cold); ⟡sched-batch verified.
- **S₃-fixed core:** READ THE MATERIALIZED GROUND TRUTH, NOT A PROXY — the same fixed point as the mission's
  intern-and-read-the-structure. **⟡pyrig-object-carrier** untouched (standing edge).

## LABELED ⟡ NEXT STEPS (specify by symbol)
### IMMEDIATE
- **⟡push** — 5 unpushed (jac-lit1-normalizer · c5861eb · 41eb8b2 · 408ad54 · 7bb8e6d), all amend-marked; USER pushes.
### ⟡make-import-dag — the validated flat DAG makefile (integrate + decide)
- **⟡mid-integrate** — fold `scratch/gen_flat_makefile.py` into `scripts/gen_build_makefiles.py`; emit the SINGLE
  flat DAG makefile. DECISION: replace the 279 recursive per-dir makefiles, or coexist. (User leans: single makefile.)
- **⟡mid-freshness** — the flat makefile's deps come from catalog.db (materialized from the LAST build) → a
  bootstrap/freshness contract: catalog.db regenerates post-build; an edited import is stale until regen → agda
  self-heals THAT edge (falls back to on-the-fly for it) until the next catalog.db refresh. Resolve + document;
  ensure the pre-commit `gen_build_makefiles --check` covers the flat makefile's drift.
- **⟡mid-aggregator-deps** — the 118 def-less re-export aggregators (no catalog node) currently depend on the
  `rest` sentinel (build-last, agda self-heals their `open import … public` children). Either keep the sentinel
  or source-parse their `public` imports for proper deps. (User's plan: clean ordered build feeds catalog.db →
  proper deps later.)
- **⟡mid-check-sync** — the flat makefile's `check-sync` (disk `.agda` set == generated targets) must fail on drift.
### ⟡sched-batch — best-effort + long-stretch scheduling (verified; build + wire)
- **⟡sched-helper** — `scripts/sched-batch.c` (~30 lines): `sched_setattr` SCHED_BATCH + nice + `sched_runtime`,
  then `execvp`. C (not python) to avoid ~40ms×2003 startup. Compile once (like the agda-shim).
- **⟡sched-wire** — wrap each agda in membudget's scope exec (`scripts/membudget:275,277,281`): `… -- sched-batch
  agda …`, guarded by helper-presence + env tunables `MEMBUDGET_SLICE_MS` / `MEMBUDGET_NICE` / `MEMBUDGET_NOBATCH`.
  Covers interactive agda + make -j + the pre-commit gate uniformly.
- **⟡sched-params** — USER DECISION: yield strength (nice 19 [keeps long slice, recommended] vs cgroup `cpu.idle`
  [harder yield, LOSES the slice — SCHED_IDLE pins 2.8ms]); slice length (100ms = max honored). Locked mechanism:
  SCHED_BATCH+nice19+100ms (chrt-verified: policy=SCHED_BATCH, runtime=100ms, nice=19). NOT SCHED_IDLE (ignores slice).
- **⟡sched-measure** — before/after involuntary-ctxt-switch delta via membudget's existing `/usr/bin/time -v`.
### ⟡cap-128 — the ORIGINAL goal, now with a RELIABLE method (unblocked by ⟡make-import-dag)
- **⟡cap-128-topo-enum** — once the flat DAG makefile is in place: cold-build at `-M128m` via it with `-k` →
  RELIABLE per-module offender list (imports pre-built = own-elaboration heap; no racing, no interleaving). The
  14-from-cold-`-j` list is discarded (noise).
- **⟡cap-128-decide** — gated on the genuine offender count: seal them (OrderOf opaque-TYPE seal / cheaper import)
  + drop MEM_CAP to 128m, OR hold at 256m. MEM_CAP stays 256m until then.
### DISCIPLINE (G9 — save as memories)
- **⟡memory-agda-cold-rm-not-touch** — agda 2.8 content-hash interface validity; only `rm` cores forces cold
  re-elaboration (touch/RTS-flag don't); cap-validation needs rm-cores + a topo-ordered build (not cold `-j`).
- **⟡memory-verify-the-measurement-method** — before concluding from a measurement, verify it measures the thing
  (did it rebuild? check core mtimes; distress? PSI-counter not swap; scheduling? readback not policy-name;
  topology? catalog.db not build-inference). Widens [[read-structure-dont-rebuild]], [[reread-meters-toctou]].
### STANDING
- **⟡pyrig-object-carrier** — the mission's live edge, untouched this arc.

# ⟡REGROUNDING (2026-07-23c) — sched-batch COMPLETE; plan-saturation in flight. COMPACTION-SAFE, stands alone.
> Incremental over #2026-07-23b (which stands: cap-128 instrument odyssey, make-import-dag validated, the
> recursive-either/or collapse = READ THE MATERIALIZED GROUND TRUTH NOT A PROXY). This block adds the sched-batch
> completion + the labeled roster + the 3 saturation agents in flight.

## STATE (one line)
5 commits UNPUSHED (USER pushes): jac-lit1-normalizer · c5861eb · 41eb8b2 cap-384 · 408ad54 single-path ·
7bb8e6d doc-buildtime. Tree 2003/2003 at committed **256m**. **⟡make-import-dag** flat DAG makefile VALIDATED
(`agda/Flat.mk` + `scratch/gen_flat_makefile.py`, UNTRACKED; cold 2003/2003, OOM-storm gone). **⟡sched-batch
DONE + wired + verified** (UNCOMMITTED): `scripts/sched-batch.rs` (single-file Rust, ~2MB/~1ms) + `scripts/
membudget` `_sched_prefix` + exec-block wrap + `.gitignore`; end-to-end through membudget → SCHED_BATCH /
runtime 100ms / nice 19 confirmed. 3 read-only agents SATURATING the open specs (outputs at
`…/tasks/{a53fbbde41253efc4,a97d42d2421c9ed59,ac3dcfed4d9642e07}.output` — mirror below when they land).

## RETROSPECTIVE (gated, LIGHT — the sched-batch completion since #23b was clean)
- **G0.** ⟡sched-params → nice 19 → build+wire the helper + measure.
- **G2 delta.** POSITIVE, clean. Delivered ⟡sched-helper (Rust) + ⟡sched-wire (membudget) + verified. Two
  in-flight corrections, both good: (a) user "python or C?" → measured python's cost (~40ms/~15MB transient,
  does NOT inflate peak_mb since execvp frees it) but user preferred a lean compiled helper → Rust (~1ms/~2MB);
  (b) the wiring "SCHED_OTHER" red-herring was a STALE `snap.cups sleep 3600` (pid 3960191, unkillable system
  daemon) polluting `pgrep -x sleep` — NOT a wiring failure; the real path shows SCHED_BATCH/nice19/100ms.
- **G3 STRUCTURE-CAUSE (of success — PROTECT).** VERIFY-THE-MECHANISM applied correctly this time: when the
  end-to-end test showed SCHED_OTHER, I did NOT assume the wiring failed — I debugged the chain (binary -x?
  _sched_prefix returns path? sched-batch works in-scope?) and found the stale-pid red herring. The corrected
  "read the ground truth, verify the method" discipline from #23b, applied proactively. Also: PROBED sched_setattr
  READBACK (not policy-name) to prove SCHED_IDLE ignores the slice; tested the helper standalone before wiring.
- **G6 SUSTAIN.** measure-the-cost (python overhead), verify-via-readback (not name), debug-the-red-herring
  (stale pid) instead of assuming, best-effort-by-construction (helper ignores sched_setattr failure → never
  blocks a build), env-tunable + MEMBUDGET_NOBATCH escape, gitignore the arch-specific binary + lazy-build.
- **G8 HANDOFF.** `operator=other`: (i) is ⟡cap-128 worth it (genuine offenders unknown until ⟡cap-128-topo-enum);
  (ii) does the flat makefile REPLACE the 279 recursive makefiles or coexist, + the catalog.db→makefile freshness
  contract (the 3 agents saturate this); (iii) ⟡sched-measure needs a real build (piggybacks on the next cold build).
- **G9 ESCALATE.** No new failure class (the #23b lessons held). The saved discipline memories
  (⟡memory-agda-cold-rm-not-touch, ⟡memory-verify-the-measurement-method, reference-cassian-tsdb-observability)
  cover it. The correct-by-construction win remains ⟡make-import-dag (materialized DAG in the build system).

## SHADOW-ENGINEER (Fano, light)
- **L₁ positive-closure:** ⟡sched-batch delivered (helper + wire + verified). **L₆:** the user's python→rust steer
  reconstituted the helper leaner (~15MB→~2MB) — the guard produced the better artifact. **S₃-fixed core
  (unchanged):** READ THE MATERIALIZED GROUND TRUTH (readback not name; the real path not the stale pid).
- Standing line (do NOT force): **⟡pyrig-object-carrier** — the mission's live edge (the user's aside: "someday
  Agda extrudes LLVM IR" — the interned object carrier compiling to executable form; the same center).

## LABELED ⟡ NEXT STEPS (specify by symbol; the 3 agents are saturating mid-integrate/freshness/enum)
### IMMEDIATE
- **⟡push** — 5 unpushed, amend-marked; USER pushes.
- **⟡sched-commit** — commit ⟡sched-batch: `scripts/sched-batch.rs` + `scripts/membudget` + `.gitignore` ONLY
  (precise staging — exclude untracked Flat.mk/gen_flat_makefile.py + scratch). Low-risk, reversible. NOTE:
  scripts-only → the pre-commit gate won't force a full build (stamp fresh), so it won't exercise sched-batch
  through the gate — that validation piggybacks on the next cold build.
### ⟡make-import-dag — the validated flat DAG makefile (agent-saturated below when they land)
- **⟡mid-integrate** — fold `scratch/gen_flat_makefile.py` into `scripts/gen_build_makefiles.py`; single flat
  makefile vs coexist; preserve check-sync / MEM_CAP override / shim PATH / ingest+catalog targets / profiling /
  --check drift-gate. [agent a53fbbde]
- **⟡mid-freshness** — the catalog.db→makefile bootstrap/cycle: SOURCE-PARSE imports (no cycle, always-fresh) vs
  catalog.db-derived (freshness fallback = agda self-heals a stale edge). [agent a97d42d2]
- **⟡mid-aggregator-deps** — the 118 def-less re-export aggregators: `rest` sentinel vs source-parse their
  `public` children (+ the reverse: who imports them). [agent ac3dcfed]
- **⟡mid-check-sync** — disk `.agda` set == generated targets, fail-on-drift + `--check` coverage.
### ⟡sched-batch tail
- **⟡sched-measure** — involuntary-ctxt delta (A/B with `MEMBUDGET_NOBATCH=1`) via membudget's `/usr/bin/time -v`;
  PIGGYBACKS on the next cold build (⟡cap-128-topo-enum or a ⟡mid-integrate validation build).
### ⟡cap-128 — original goal, reliable method now (agent-saturated below)
- **⟡cap-128-topo-enum** — cold-build at `-M128m` via the flat DAG makefile with `-k` → GENUINE per-module
  offenders (the cold-`-j` 14 was NOISE). [agent ac3dcfed]
- **⟡cap-128-decide** — seal genuine offenders (OrderOf opaque-TYPE seal @ `Foundation/Fin/Iterate.agda`) + drop
  MEM_CAP to 128m, OR hold 256m. Gated on the offender count. MEM_CAP stays 256m until then.
### STANDING
- **⟡pyrig-object-carrier** — mission edge, untouched.
### RECOMMENDED SEQUENCE (one cold build serves three)
⟡sched-commit → ⟡mid-integrate (from the agent specs) → ONE cold build via the integrated flat makefile that
simultaneously: validates ⟡make-import-dag, yields ⟡sched-measure (A/B), and (at -M128m) does ⟡cap-128-topo-enum.

## ⟡mid-integrate — SATURATED (agent a53fbbde, file:line-grounded, turn-key)
`scripts/gen_build_makefiles.py` (290 ln) has TWO emitters: `makefile_text()` (per-dir, 100-183) +
`root_text()` (agda/Makefile, 186-252). 280 per-dir Makefiles + root. The prototype
`scratch/gen_flat_makefile.py` already carries the MUST-PRESERVE core (shim PATH, MEM_CAP+RTS, AGDA flags,
find-based check-sync) but is MISSING two things = the integration gap.
- **MUST-PRESERVE in the flat makefile:** (1) `_shim_block()` PATH export (gen 54-70) — the sole membudget/
  proof-cost path; (2) `MEM_CAP ?= 256m` + `+RTS -M$(MEM_CAP) -RTS` per recipe (46,151); (3) `AGDA`/`AGDA_FLAGS`
  overridable; (4) `check-sync` drift guard (132-143 → the prototype's whole-tree `find` form); (5) root-only
  targets `shim`/`catalog`/`check*`(8 invariant scripts, 219-243)/`advise` (208-250) — NOT recursive-agda,
  move VERBATIM; (6) `ingest` (168-176).
- **membudget/shim + catalog SURVIVE UNCHANGED** — routing is PATH-based (agda-shim intercepts bare `agda`),
  not recursion-based; the flat recipe passes the full `Substrate/…/X.agda` path so `dirname`→`.agda-times.tsv`
  autobudget ledger + proof-cost profiling are keyed off the SOURCE dir, unaffected. `catalog`(sppf_db `""
  --argperm`) + `shim` are single-process → move verbatim.
- **TWO genuinely-new engineering decisions (the only non-mechanical parts):**
  (a) **`--check` gains a catalog.db dependency (HIGHEST RISK):** the flat body depends on `module_edges` from
  the 2.9 GB GITIGNORED catalog.db → a fresh clone/CI without a built catalog.db can't reproduce the exact body
  → `--check` false-stale at `.githooks/pre-commit:59`. MUST make `--check` robust to absent/stale catalog.db
  (e.g. degrade to the disk-module target-set check via check-sync; skip the edge-set byte-compare when DB
  absent). The current per-dir `--check` has NO external dep — this is the real new coupling.
  (b) **flat re-expression of `ingest`** (currently recursive `ingest-files`/`ingest-subdirs`) → one `ingest:`
  dep on per-module `i/<Module>` targets (`sppf_db.py --ingest-core <path>`, WAL+busy_timeout); else the
  parallel-to-compile SPPF ingest silently disappears (batched `catalog` still works, so recoverable).
- **RECOMMENDED wiring (lowest blast radius):** keep a THIN `agda/Makefile` with the root-only targets +
  `all:` delegating to `Flat.mk` → `.githooks/pre-commit:196 make -C agda -j` UNCHANGED. Delete the 280
  per-dir Makefiles. No tooling greps per-dir makefiles (grep-confirmed: only `--check` call sites + prose).
- **7-STEP TURN-KEY PLAN:** (1) add `flat_text()` to gen_build_makefiles.py mirroring the prototype (module
  set=disk glob − All; edges=catalog.db; Kahn acyclic check; `m/<Mod>` rules + direct-import prereqs; def-less
  aggregators→`rest` sentinel); (2) carry the must-preserve core; (3) re-emit `ingest` as `i/<Mod>` + root
  catalog/shim; (4) retain thin `agda/Makefile` (root targets + `all:`→Flat.mk); (5) rework `--check` (one
  target + catalog.db-absent robustness); (6) delete the 280 per-dir Makefiles; (7) verify ledgers land
  per-source-dir (confirmed) + no per-dir-makefile consumer (confirmed). Everything but (a)+(b) is a mechanical fold.

## ⟡mid-freshness — SATURATED (agent a97d42d2) — DECISIVE REDIRECT: source-parse imports, NOT catalog.db
**catalog.db `module_edges` is the WRONG source — it is SEMANTIC (elaborated-core name-references), not source
imports, and it DROPS build-required edges.** PROOF: `agda/Substrate/Algebra/Abelian/V4-as-PFG.agda` imports 8
modules in source (incl. `Foundation.Nat`), but `module_edges` returns only 7 — Foundation.Nat is MISSING (its
ℕ/suc/zero refs normalized away in the core). Built at `reuse_catalog.py:412-413` from decoded-core qname refs
(`render_import` docstring 675-678: "excludes unused source imports, includes transitively-used names; NOT source
import lines"). So even a FRESH module_edges is unsound for build ordering (dropped edge = wrong order). AND
catalog.db is regenerated only on a STRUCTURAL (Ε(b′)) or >7-day commit (`.githooks/pre-commit:150-215`), so it's
often days stale.
- **RECOMMENDATION (decisive): SOURCE-PARSE `open import`/`import` at makefile-gen time.** The building block
  EXISTS: `scripts/audit_import_reach.py:20` `re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)`
  + `scripts/_agdatext.py:16-18` `strip()` (removes `{-…-}`/`--…` comments first → kills false positives). Handles
  indented imports (43 in-corpus), `as`/`renaming`/`public`/module-param-application (module path is always token-1
  after `import`). Source-parse is the SOUND SUPER-SET of direct imports (keeps unused/re-export imports — correct,
  Agda needs every imported interface; make recovers transitive via the direct edges).
- **THIS DISSOLVES THREE CONCERNS AT ONCE:** (1) the catalog.db→makefile CYCLE (agent A's mid-integrate) — gone,
  no DB dependency; (2) agent A's "--check robust to absent catalog.db" (its decision (a)) — GONE, the flat body
  is byte-reproducible from the checked-out `.agda` tree alone; (3) ⟡mid-aggregator-deps — the 118 def-less
  aggregators are parsed like everything else (their `open import … public` children ARE in their source), so NO
  `rest` sentinel needed. ⟹ **REVISE the prototype `scratch/gen_flat_makefile.py` to source-parse instead of
  catalog.db module_edges.**
- **FRESHNESS FALLBACK — CONFIRMED SAFE:** the makefile's import prereqs are a SCHEDULING/parallelism optimization,
  NEVER a correctness dependency. If an edge is stale (source gained an import since regen), make may schedule X
  before new-dep Y; agda then builds Y IN-PROCESS via its own transitive recheck (the exact "make is a dispatcher,
  agda decides cached-vs-recheck" invariant the current makefiles already lean on). Correctness floor = Agda's
  in-process recheck; a stale edge costs only parallelism-on-one-edge, never soundness. So source-parse (always
  fresh) makes even this near-moot.

## ⟡mid-aggregator-deps + ⟡cap-128-topo-enum — SATURATED (agent ac3dcfed) — B's source-parse SUBSUMES the aggregator question; cap-128 enum is TURN-KEY

### PART 1 — the 118 "def-less aggregators" (⟡mid-aggregator-deps): RECONCILED WITH AGENT B (source-parse wins, no `rest` sentinel)
Agent C scanned ALL 118 (the `disk 2003 − cat_nodes` set, keying on absence from `module_edges`):
- **~111 are PURE `open import … public` re-exports** (GF256/SymBilinForm/SingerOrder confirmed). For these
  `module_edges` returns src=0 dst=0 — but agent C found the catalog **resolves the re-export THROUGH to the true
  definers**: witness `MixColumns/Scale.agda` does `open import …GF256 using (xtime;…)`, and Scale's catalog out-edges
  are `GF256.Xtime/Mul/Reduce/…` (the submodules), NOT `GF256` itself. ⟹ the def-less aggregator NODE is
  **transparent**: nothing depends on it; importers are already ordered after the real content; building it last
  never blocks anyone (it only re-exports already-built children). This is WHY it's "uncovered".
- **~7 are NOT def-less — they carry real defs yet are fully uninterned** (catalog STALENESS, not def-lessness):
  `Category/Site.agda` (record CoverData/Site), `Foundation/Fin/Literals.agda` (33 `pattern ₀…₃₂`),
  `Category/TwoEquivalence`+`TwoNaturalTransformation`, `UniversalProperty/AdjointPair`+`ExtrudeSetoidFunctor`,
  `GL3F2/AsChainDecomp` (record GL3F2ChainShape), `ShadowArchitecture/CellReconstruct` (record Cellₚ). These have
  real cross-module imports (e.g. Fin.Literals imports Foundation.Fin) that WOULD produce edges if interned. For
  THESE the importer→aggregator edge is DROPPED entirely (no node to resolve to) → importers rely on Agda's
  in-process self-heal.
- **⚑ THE RECONCILIATION:** agent C recommends "keep the `rest` sentinel" ONLY because it assumed the catalog.db
  edge source (Part 2 of the plan pre-B). **Agent B's source-parse redirect makes the whole question moot:**
  source-parsing every module's `open import … public` lines parses the ~111 pure aggregators like everything else
  (their children ARE in their source → real prereqs, NO sentinel) AND recovers the ~7 def-ful outliers' real
  imports (Fin.Literals→Foundation.Fin, etc.) that the STALE catalog dropped. ⟹ **source-parse (agent B) is the
  single move that dissolves both classes; the `rest` sentinel is a catalog.db-era artifact, retired.** Agent C's
  own residual actionable — "the ~7 def-ful modules want catalog regeneration" — is ALSO subsumed (source-parse
  reads their real deps regardless of catalog freshness). NET: ⟡mid-aggregator-deps is CLOSED by ⟡mid-freshness.

### PART 2 — ⟡cap-128-topo-enum: TURN-KEY reliable offender enumeration (the actionable output)
Runs on the flat DAG makefile (`agda/Flat.mk`, `MEM_CAP ?= 256m` line 3; each recipe `+RTS -M$(MEM_CAP) -RTS`;
shim-PATH-prepended → membudget). **Exact procedure (from repo root):**
```
find agda/_build -name '*.agdai' -delete                                    # (a) force COLD: rm all 2003 interfaces
make -f Flat.mk -k -j1 MEM_CAP=128m all 2>&1 | tee scratch/cap128.log        # (b) cold, topo-ordered, keep-going, serial
```
- **MEM_CAP override:** `Flat.mk` uses `?=` (conditional); a **command-line** `MEM_CAP=128m` BEATS `?=` → recipes
  expand `+RTS -M128m -RTS`. **No file edit.** `-M128m` is a GHC RTS heap cap on agda's OWN heap — orthogonal to
  membudget's cgroup lease AND to `MEMBUDGET_RETRY_OOM` (which only retries exit-137 cgroup OOM-kills). A GHC "Heap
  exhausted" is a **deterministic per-module elaboration signal, NOT masked by the membudget retry** — that is what
  makes the cap a clean forcing function.
- **WHY ATTRIBUTION IS RELIABLE (the whole point of the flat DAG):** imports are pre-built as `.agdai` in topo
  order ⟹ agda LOADS interfaces, does NOT elaborate imports in-process ⟹ each module's heap is its OWN elaboration.
  This is exactly what cold recursive `make -j` FAILED to do (built imports on-the-fly, inflated heap + interleaved
  `-j` log → the 14-offender NOISE, 2 with 0 transitive imports = impossible). Each Flat.mk recipe = exactly one
  `agda` for one `m/<Module>`; on heap exhaustion agda exits nonzero → `make -k` prints `make: *** [Flat.mk:<line>:
  m/<Module>] Error 1` — that target line NAMES the offender unambiguously, independent of `-j` interleaving (run
  `-j1` so each "Heap exhausted" sits immediately before its target's Error line).
- **EXTRACT offenders** (distinguish heap-exhaustion from ordinary type errors, both Error 1):
```
grep -E '\*\*\* \[Flat.mk:[0-9]+: m/' scratch/cap128.log     # all failed targets
grep -B2 'Heap exhausted' scratch/cap128.log                 # heap blocks (with -j1, module's Error line follows)
```
  Offenders = failed targets whose stderr block contains `Heap exhausted` (the recipe's `@` silences the command
  echo, so the module name comes from make's `*** [… m/X]` line, not the "Heap exhausted" text itself).
- **`make -k` iteration:** an offender's DEPENDENTS get skipped (`Target 'm/Dep' not remade because of errors`) —
  fine, you want the offenders (the modules you seal), not dependents (they elaborate fine once the offender is
  sealed). Iterate to fixpoint: **enumerate → seal (OrderOf opaque-TYPE template, `Foundation/Fin/Iterate.agda:47-55`)
  → re-run the same cold 128m build.** 2nd pass unblocks skipped dependents → may surface a 2nd tier. Typically 1-2
  iterations (heavy class is concentrated: order-N `HasOrderPerm` neutrals — Z5/Z7-Coxeter-Fin, Coxeter/Cyclic/Base,
  Capabilities/CoxeterFin). ⚑ Per the user directive: the offender LIST comes from THIS build, NOT assumed from the
  known class. Then **⟡cap-128-decide** (seal + drop MEM_CAP to 128m, or hold 256m). MEM_CAP stays 256m until then.

## ⚑ PLAN NOW COMPACTION-SAFE + TURN-KEY (all 3 agents mirrored). Net design after saturation:
1. **⟡mid-integrate** folds mechanically EXCEPT its two decisions — and agent B RETIRES both: (a) `--check`
   catalog.db-robustness → GONE (source-parse, no DB dep); (b) `ingest` re-expression stays (the one real
   engineering fold). Lowest-blast wiring = thin `agda/Makefile` (root targets + `all:`→Flat.mk) + delete 280
   per-dir Makefiles.
2. **⟡mid-freshness** is DECISIVE: source-parse `open import` (audit_import_reach.py regex + _agdatext strip), NOT
   catalog.db. Sound super-set, always-fresh, dissolves the cycle + the --check DB-dep + the 118-aggregator gap.
3. **⟡mid-aggregator-deps** CLOSED by (2) — no `rest` sentinel; the ~7 def-ful stale outliers handled by source-parse.
4. **⟡cap-128-topo-enum** turn-key (rm-cores + `make -f Flat.mk -k -j1 MEM_CAP=128m` + grep Heap-exhausted). Gated
   behind the ⟡mid-integrate flat makefile landing (or run against the existing untracked `agda/Flat.mk` prototype).
