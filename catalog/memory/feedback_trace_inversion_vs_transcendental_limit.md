---
name: feedback_trace_inversion_vs_transcendental_limit
description: "RECURRING REFLEX (mis-fired ≥3×): I label anything smelling of log/∞/transcendental as 'analytic / out-of-reach / out-of-scope' and scope it out. The fix: SEPARATE STRUCTURE FROM VALUE — transcendence lives in the VALUE-projection (the digit sequence), the STRUCTURE (iso/codec/loop/round-trip/relation) is FORMAL and derivable. This is [[feedback_structural_not_scalar]]/[[feedback_wedge_not_projection]] applied to analysis: the transcendental value is the lossy scalar look, the codec is the carrier. Specific instance: exp⊣log round-trip = coinductive BISIMULATION (step-inverse generators cancel at every depth — finite proof of infinite equality), NOT a limit. Before scoping ANYTHING out as transcendental, test for the formal/structural form FIRST."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

(user, 2026-06-12 — CORRECTING a wrong framing of mine) I had claimed the exp⊣log
round-trip is "irreducibly analytic, its proof IS the convergence." WRONG. The user:
"`holds only in the limit` — do you know what that means constructively? It holds
iff the entire trace is computed. Except we don't need to compute the infinite
trace; we have suspended generators, and _those_ cancel."

"holds only in the limit" is the CLASSICAL reading — "force the entire infinite
trace and check". Constructively the round-trip is a coinductive BISIMULATION: a
FINITE proof of an INFINITE equality. You NEVER force the trace. If exp/log are
co-defined as STEP-INVERSE generators (one's step inverts the other's), they CANCEL
at every depth by coinduction — structural, no convergence, no limit-computation.
Lindemann–Weierstrass (exp_m(log_n x) ≠ x at finite stages) is about FORCING, which
the coinductive proof never does. It bounds the WINDOWED OBSERVATION, not the
generator equality.

**The real axis is structural-round-trip vs value-correctness, NOT algebraic vs
transcendental:**
- The ROUND-TRIP (exp∘log ~ id) is structural for ANY step-inverse pair — FINITE
  depth: `Bisim.recip-invol` (the CF shifts cancel, refl); INFINITE depth:
  `Cancel.bump-cancel : unbump k (bump k x) ~ x` (coinduction: tail~ = the
  corecursive call, head~ = the per-step inverse `+∸-cancel`). recip and bump are
  the same move at different depths; the only "transcendental" thing is the depth.
- The genuinely-analytic part is VALUE-CORRECTNESS — but EVEN THIS is mostly
  FORMAL, not analytic (user's follow-up, 2026-06-12: "you have taylor and tanh,
  and you're not taking the wedge product or passing it through eea? Because it
  _will_ give you the cancelling coefficients"). COMPOSING the two series (the
  Cauchy product) makes `exp(log(1+u)) = 1+u` a FORMAL power-series identity in
  ℚ[[u]], EXACT coefficient-by-coefficient — the cancelling numerators are literally
  0ℤ, produced by the product, NOT by a limit. Built + witnessed:
  `Algebra.R.Trace.SeriesCancel` (92e6d44; refl at m=2,3; `_≈ℚ_` not `reduce` —
  EEA-via-Acc times out the typechecker but the cancellation is already in the
  product). So the round-trip's value-IDENTITY is formal; the ONLY truly analytic
  residue is "does exp-real x numerically equal e^x", which the round-trip never
  needs.
- CAVEAT: needs exp/log co-defined step-inverse (the Wedge-chain: log decomposes
  keeping the residue, exp replays — [[feedback_never_discard_residue]]). The
  WINDOWED-SERIES `exp-real`/`log-real` (Taylor vs atanh, independently defined) are
  NOT step-inverse, so THEY don't cancel structurally; the genuine round-trip wants
  them re-defined as the single trace pair.

Rule: a round-trip's difficulty is about the DEFINITION (step-inverse ⟹ structural
coinductive cancellation), not the operation's transcendence; and "in the limit"
is a forcing-framing the coinductive proof sidesteps. Cf.
[[feedback_suspended_generators_not_approximations]] (don't collapse the generator
to a List observation; the equality is a bisimulation) and
[[feedback_transcendental_phase_is_loop_fact]] (the sibling lesson: the
"transcendence" was an artifact, here of FORCING rather than of radians).

**RECURRENCE (2026-06-18, user caught it — this lesson is being OVERREAD/MIS-applied):**
building the el-atlas G-Value calculus in ℚ (`Logic.Evidence.GValueAsQ`, Ω3) I scoped L-space
(`L = ln G`) OUT as "transcendental, out of ℚ scope" — CITING this very memory. That is the
EXACT error this memory corrects, re-committed on a sibling. The el-atlas spec says the L↔G iso
IS the exp⊣log codec; per this memory that codec is FORMAL (a bisimulation), so L-space is NOT
transcendence-blocked — it is a buildable bridge (multiplicative G-space (ℚ₊,·,1) ↔ additive
L-space, the substrate's exp⊣log codec / Algebra.R), a follow-on (Ω3-L). The G_AND/DeMorgan
commit (5591882) rewrote the bad comment.

**THE COMMON STRUCTURE (recursively, the user's frame): this is ONE lesson, not a family.**
[[feedback_trace_inversion_vs_transcendental_limit]] (exp⊣log = bisimulation), 
[[feedback_transcendental_value_is_a_digit_basis]] (π/e/i ARE the digits; identities are finite
relations), [[feedback_transcendental_phase_is_loop_fact]] (e^{iπ}=−1 is a loop fact) are all
the SAME move: **the transcendence is in the VALUE (digit/scalar projection); the STRUCTURE
(codec/loop/relation) is formal.** = [[feedback_structural_not_scalar]] / [[feedback_wedge_not_projection]]
applied to analysis. So the general TRIGGER (fire BEFORE scoping out): "I'm about to call this
analytic/transcendental/out-of-reach" ⟹ STOP, separate structure from value, build the structure.
The reflex is a special case of mistaking the lossy scalar VALUE for the structural CARRIER.
