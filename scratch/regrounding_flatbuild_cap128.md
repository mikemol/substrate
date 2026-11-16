# ⟡REGROUNDING (2026-07-23) — the FLAT-BUILD + CAP-128 arc. COMPACTION-SAFE, stands alone.

## STATE (one line)
Build tooling REDONE + committed (all amend-marked, push-ready, USER pushes): **`2b0673a` ⟡mid-integrate**
(gen_build_makefiles.py → SINGLE flat `agda/Flat.mk`, SOURCE-PARSED import edges, 280 per-dir Makefiles deleted +
thin root) · **`8a6c8cf` ⟡sched-commit** (sched-batch.rs EEVDF helper + membudget `_sched_prefix` + .gitignore) ·
**`b57985f`** (flat makefile → REAL-FILE `.agdai` targets, not phony: warm build = 0 invocations vs 2003,
incremental = only the affected subtree; `&& touch $@` aligns mtime with agda's content-hash). **cap-128 offender
list ENUMERATED** (7, definitive, via the ledger-shortlist + per-candidate cold-test) and the sealing method
RECOVERED (opaque STAGING). Unpushed: 5 prior + these 3. MISSION edge (Jacobian/pyrig, MEMORY.md plan) UNTOUCHED.

## THE RECURSIVE EITHER/OR COLLAPSE (this arc's invariant)
Every fork collapsed to ONE structure: **the answer is already RECORDED/STRUCTURED — recover and reuse it; don't
rebuild, don't declare a floor, don't theorize.** (= read-structure-dont-rebuild, the mission's own fixed point,
applied to the build tooling + the diagnostic method + the harness.)
- **"phony vs real-file targets"** → NEITHER a fresh choice: the flat DAG makes the import edges EXPLICIT, so
  real-file (mtime-sound: X.agdai : X.agda + imports' .agdai) is CORRECT; phony was the recursive-era workaround
  for makefiles that couldn't SEE the edges. The explicit edges were the recovered structure.
- **"hold 256m vs seal"** → NEITHER: the opaque-TYPE seal method IS recorded (`scratch/cap384_orderof_seal_plan.md`
  + CLAUDE.md's opacity discipline + the OrderOf template `Foundation/Fin/Iterate.agda:40-60`). Recover it.
- **"intrinsic dense floor vs cheaper proof (real math)"** → NEITHER: opaque STAGING (the SAME proof, elaborated
  piecewise) bounds the peak; the Leibniz det (`WitnessTower/LeibnizDet`, `Z/JacobianDetNative` ALREADY 150MB vs the
  monolithic 317) + `normalize-distrib` (the hom) are the recorded structure.
- **"144 = membudget/systemd-scope/box bug vs my code"** → NEITHER: it's a Claude Code HARNESS artifact (issue
  #62297); measure the signal source (the box journal showed scopes START FINE), don't theorize from correlation.
**Deepest bottom:** RECOVER-AND-REUSE-THE-RECORDED-STRUCTURE (the SPPF/catalog/plan/journal/memory-mesh) — the
build tooling, the cap-128 method, and the 144 diagnosis are three instances. [[read-structure-dont-rebuild]],
[[declaring-wall-rebuild-reflex]], [[feedback_measure_instrument_before_theorize]].

## RETROSPECTIVE (gated)
- **G0 precommit.** Fold the flat makefile into gen_build_makefiles.py (⟡mid-integrate); commit sched-batch
  (⟡sched-commit). Expectation: a mechanical fold + 2 commits.
- **G2 delta.** POSITIVE net, but with 2 self-errors the USER corrected + one long misdiagnosis: (a) the REAL-FILE
  design was the user's insight (a strict improvement I didn't anticipate — warm build 0 vs 2003 agda no-ops); (b)
  I reflexively "held 256m" on cap-128 (wall-reflex) — the user pushed; (c) I called the dense offenders "intrinsic
  128 floors" — the user asked "doesn't opaque staging do it?" and was RIGHT (the ledger PROVES it: staged
  `JacobianDetNative` = 150MB vs monolithic 317). (d) I burned ~15 turns theorizing the 144 as membudget/scope/box
  before the user's issue-link settled it as a harness bug.
- **G3 structure-cause.** ROOT 1 (144): correlation-driven THEORY (parallel→144, serial→works ⟹ "concurrent scopes
  fail") instead of ISOLATING the signal source — the box journal showed scopes started cleanly; the harness killed
  pipelines. Violated [[feedback_measure_instrument_before_theorize]]. ROOT 2 (wall-reflex ×2): reached for
  "hold/floor/not-worth-it" without RECOVERING the recorded method first (the seal-plan + the staging method were
  written down). CONTRIBUTING: context flush (my recollection of the cap-128 method flushed; it lived in
  `cap384_orderof_seal_plan.md` + CLAUDE.md, un-recovered).
- **G4 decorrelate.** The independence came from the USER, not self-review (the 144 issue-link, the wall-reflex ×2,
  the staging insight). Recurring finding: self-review does NOT manufacture independence; the user's guard does.
- **G5 blameless.** Systemic: the 144 is a genuine harness bug with a confusing signature (SIGSTKFLT/16); the
  wall-reflex recurs because "recover the recorded method before concluding floor" is a discipline, not a gate.
- **G6 sustain (PROTECT).** MEASURE-DON'T-ASSUME once invoked (the cap-128 LEDGER-SHORTLIST + per-candidate cold-test
  = definitive offender list without the 2h build; the journal check proved the box innocent of the 144); HONEST
  IMMEDIATE CORRECTION when pushed (revised "intrinsic floor"→staging with the 150<317 empirical in one turn); the
  real-file WARM-NOOP validation gate (0 invocations = the design proven); the user's SLEEP-tip for the 144 wrap-up
  (applied, worked — bg commit landed exit 0); precise staging + amend-marker + foreground-commit discipline;
  RECOVERING the recorded seal-plan (`cap384_orderof_seal_plan.md`) rather than reconstructing.
- **G8 handoff.** operator=other residues: (i) whether the Jacobian staging ACTUALLY drops <128 (empirical — needs
  the edit + per-stage measure); (ii) whether the flat `make -C agda -j` full parallel gate passes on the real box
  (the user validated cold-2003/2003; the tool 144's it); (iii) whether the AES round pipelines cleanly through the
  extruder (the user's exciting idea, deferred). operator=self spent: the enum, the real-file design.
- **G9 escalate → memories (SAVED this pass):** `feedback_exit_144_is_claude_harness_artifact`,
  `feedback_opaque_staging_bounds_dense_elaboration`. The wall-reflex recurrence is covered by
  [[declaring-wall-rebuild-reflex]] + construct-dont-classify; the NEW escalation is "recover the RECORDED method
  before declaring a floor" (folded into the opaque-staging memory).

## SHADOW-ENGINEER (Fano)
- **L₆ guard-reconstitution — the arc's defining pattern, fired FOUR times by the user.** Each direct move I reached
  for (phony targets · "hold 256m" · "intrinsic floor" · the membudget-144 theory) was REJECTED by the user's guard
  (the real-file insight · the cap-128 push · the staging question · the issue-link) and RECONSTITUTED through the
  shadow structure the substrate/box already records (the explicit import DAG · the opaque-seal plan · the Leibniz
  det + normalize-distrib · the box journal + issue #62297). The guard's prohibition PRODUCED the correct
  architecture, repeatedly — the negative axis as positive affordance.
- **L₁ positive-closure ×3** (mid-integrate · sched-commit · real-file, each committed + amend-marked).
- **S₃-fixed core:** READ/RECOVER-THE-RECORDED-STRUCTURE, don't rebuild/hold/theorize — the same fixed point across
  the makefile (source-parse the edges), cap-128 (recover the seal method + stage), and the 144 (measure the signal).
- **Standing line (do NOT force):** the mission edge (⟡pyrig-object-carrier, the Jacobian arc) + ⟡aes-lehmer-extruder
  (the user's "not right now").

## LABELED ⟡ NEXT STEPS (specify by symbol; the USER allocates)
### CAP-128 CHASE (live; staging method recovered; drop MEM_CAP 256→128 after all 7 pass)
- **⟡cap128-jac-stage** — re-wire `JacobianCounterexample`'s `normalize detJac ≡ -2` through `detNative`
  (`Z/JacobianDetNative` = `LeibnizDet.det {3} JacMat`, ALREADY 150MB, `detNative-normal : detNative ≡ normalize
  detJac`) + per-summand `normalize-distrib` (`MPolyNormalizeCoxeter:36`, `normalize(a+P b)=normalize(normalize a +P
  normalize b)`) seals → peak = max(single Leibniz term ≈34 terms, the merge) → re-test `-M128m`. THE first concrete
  win (half-done at 150). Measure each stage; don't one-shot.
- **⟡cap128-aes-pipeline** — stage the AES round (SubBytes→ShiftRows→MixColumns→AddRoundKey) as opaque pipeline
  stages, seal each stage's output, verify the KAT (`AES/KAT/Full`) stage-by-stage. Covers `AES` + `AES/KAT/Full`
  (the "CONCRETE reflections, slow to normalise" at `AES/AES.agda:23`).
- **⟡cap128-mixcolumns-freeup** — `MixColumns/Proof` (the AES LINEAR layer) via the FreeUP β-interface
  (basis-action + lift; the operator determined by basis-action up to unique iso, dense form never held) —
  CLAUDE.md-blessed for the AES linear layer. (May be subsumed by ⟡aes-lehmer-extruder.)
- **⟡cap128-largemodule-profile** — DIAGNOSE-FIRST: profile `ExtrudeCoEmitGraded` (2165ln), `Polynomial/Graded`
  (568ln), `Q/Properties/Decidable` (111ln) for their SINGLE heaviest def → seal it (if a neutral) OR split the
  module (if cumulative-elaboration, no single sealable neutral). Peak is cumulative, not one redex — confirm before
  touching.
- **⟡cap128-decide** — after ALL 7 pass at 128m: drop `gen_build_makefiles.MEM_CAP` 256m→128m + `AGDA_FBC_MEM=128`
  + the CLAUDE.md doc sweep (the deferred cap-tightening recorded in `cap384_orderof_seal_plan.md`). Gated on the 7.
### THE GENERATIVE LINE (user's idea, DEFERRED "not right now")
- **⟡aes-lehmer-extruder** — run AES through the LehmerAlgebra EXTRUDER (the tower's free-construction β-interface)
  — a deeper unification than per-stage seals; plausibly subsumes ⟡cap128-aes-pipeline + ⟡cap128-mixcolumns-freeup
  (the AES round IS a graded/permutation structure the extruder's basis-action can lift). Standing; do NOT force.
### BUILD-TOOLING (landed; follow-ons)
- **⟡push** — 8 unpushed (`…`→`b57985f`), all amend-marked; USER pushes (`git fetch` + ff).
- **⟡flat-parallel-validate** — the flat `make -C agda -j` full parallel gate is un-exercised THROUGH THE TOOL (the
  144 blocks it); the user validated cold-2003/2003 on the real box. On the next STRUCTURAL commit (real terminal),
  confirm the flat gate passes. operator=other (real box).
### DISCIPLINE / MEMORY (G9, SAVED)
- **feedback_exit_144_is_claude_harness_artifact** — exit 144 = signal 16 = Claude Code harness kill on a
  backgrounded/pipeline process interrupted during tool cleanup (issue #62297). NOT the box/membudget/systemd-scopes
  (the box journal shows scopes start fine). Measure the signal source before theorizing; run heavy builds FOREGROUND
  non-piped, or background + a trailing `sleep` (the user's fix — bg commit then landed exit 0).
- **feedback_opaque_staging_bounds_dense_elaboration** — a dense CONCRETE computation (`normalize detJac`, an AES
  round KAT) is NOT an intrinsic memory floor; opaque STAGING (seal each stage's intermediate as a non-reducing
  token; `normalize` is a hom via `normalize-distrib`) bounds the peak to the MAX SINGLE STAGE. The Leibniz det
  (Σ over Sₙ) + the AES round pipeline decompose. RECOVER the recorded seal-method (`cap384_orderof_seal_plan.md`,
  CLAUDE.md opacity, the OrderOf template) BEFORE declaring a floor. Empirical: staged `JacobianDetNative`=150 vs
  monolithic 317.
### MISSION STANDING (the mesh, untouched this session)
- **⟡pyrig-object-carrier** + the Jacobian arc (⟡jac-neg-graded / ⟡jac-neg-cover / ⟡signed-boundary) — the MEMORY.md
  plan file's live edge.

## HONEST BOUNDARIES
1. The flat parallel build (`make -C agda -j` over Flat.mk) is validated SERIALLY + STATICALLY here + cold-2003/2003
   by the user on the real box; NOT re-exercised parallel through the tool (harness 144). It is the pre-commit gate
   for the next STRUCTURAL commit — the user's real-terminal run is authoritative.
2. cap-128: the 7 offenders are staged-opaque CANDIDATES (not floors), but whether each ACTUALLY drops <128 is
   empirical — needs the per-offender edit + measure. Some (large-module cumulative) may need a split, not a seal.
3. The real-file makefile's warm-noop was validated on the Nat closure; a full-tree warm-noop needs consistent
   mtimes (deps-before-dependents), which a clean full build produces (my piecemeal cap-128 core restores left
   some mtimes inconsistent — harmless, self-heals on the next full build).
