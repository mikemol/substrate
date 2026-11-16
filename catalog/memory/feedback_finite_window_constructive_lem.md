---
name: feedback_finite_window_constructive_lem
description: "An unbounded decision (coinductive productivity, real comparison, 'ingest until emit') IS the LEM problem; resolve it constructively by CONSTRUCTING A FINITE WINDOW you operate within (UNIX 512B blocks, LZ77 windows), where finite ⟹ decidable, then recover the infinite object as a Tarski fixed point (turn the tower upside-down, walk down, turn back up)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When something needs an **unbounded** decision — "ingest input *forever* until I
can emit" (Gosper/coinductive productivity), "decide x < y for reals" (might
ingest forever if x = y), any "this is a hard open problem to prove
total/productive" — that unboundedness IS the LEM move, and we are a constructive
shop, so it is not free.

**The resolution (user, 2026-06-12):** adopt LEM *within a FINITE DOMAIN you
construct to operate within*. Finite ⟹ decidable ⟹ classical reasoning is
constructively admissible there. Exemplars: **UNIX** buffers in 512-byte blocks;
**LZ77** uses a bounded rewrite window. Both turn an unbounded process into a
committed finite window and handle the boundary explicitly.

**Tarski's fixed-point shape** is the recovery move: turn the tower UPSIDE-DOWN
(invert the coinductive ν into the inductive **walk-down** — a finite, well-founded
descent), *demonstrate the walk-down* (it terminates — structural recursion on the
window/fuel), then turn the tower BACK UP-RIGHT and **call it a fixed point**
(recover ν as the limit of the μ-approximations).

**How to apply (the pattern):**
- Coinductive productivity: the productive `head` is a TERMINATING bounded
  walk-down inside the window (fuel n); the `tail` is then trivially guarded
  corecursion. Productivity was never unprovable — it was unBOUNDED. Bound it.
  (This is why genuine Gosper CF arithmetic on RealTrace IS feasible —
  [[project_substrate_real_arc]] B3; my "hard wall" framing was wrong.)
- Undecidable real decisions (x<y, x=y): decide WITHIN the window (compare the
  first n convergents) → a total `lt | gt | unknown-in-window` verdict.

**Fuel is a STAND-IN, not the final form (user, 2026-06-12).** An arbitrary fuel
constant + commit-at-boundary is the UNIX/LZ77 *pragmatic* window — lossy at the
edge. The PRINCIPLED form PROVES the step-bound (a strictly-decreasing measure
that forces the emit) and uses WELL-FOUNDED RECURSION (`Acc`) on it — structural,
correct, no cutoff. The substrate ALREADY does this: `compute-trace-acc :
(a b) → Acc _<_ b → …` terminates by `<`-well-foundedness on the EEA remainder,
not fuel. Replace fuel with the Acc descent.

**SHARPENED (2026-06-12, found while building it):** there are TWO different
"bounds," and only one is state-based.
- The det+growth measure (ingest preserves |ad−bc|; denominators grow ⟹ the
  value-interval width |ad−bc|/(c(c+d)) shrinks to 0 — `det²≡1` + `q-grow`) proves
  the loop PROGRESSES, but it does NOT bound the step COUNT: emit fires when the
  width drops below the value's distance to the nearest integer, which depends on
  the input's FUTURE digits. So the Gosper STATE MACHINE has NO state-based
  termination measure — it is genuinely input-dependent (sized types or an input
  hypothesis territory). Don't claim a state Acc here.
- The user's actual frame, **bounded-OUTPUT**, is the clean fuel-free resolution:
  to emit `n` output digits, the input needed is bounded by x's `n`-th convergent,
  so recurse STRUCTURALLY on n. No fuel, no state-Acc; the bound is the output
  length itself. Landed: `Algebra.R.Trace.Window.homographic-cf` (8eae401) — the
  homographic on x's n-th convergent is a rational, its CF (the EEA trace) is the
  result to a window-prefix. "Reason about ℝ via ℚ in an output window."

**GPU/imperative instance (2026-06-15):** replacing fuel with a DERIVED numeric bound is NOT elimination -- it
is still fuel (a count the loop races; just a tighter guess). The real elimination, same as the Agda code:
PROVE PRODUCTIVITY, then the loop guard is the STRUCTURAL condition alone. jea_engine_pool's drain went from
`while(pending>0 && sw<4_000_000)` (fuel) -> my first cut `sw < 6*depth+16` (still fuel) -> `while(pending>0)`
(no count). Termination proven: (1) DESCENT narg n->n-1, base n==0 emits => spawned DAG finite+acyclic;
(2) NO-DEADLOCK while pending>0 a minimal-incomplete node has all children done => ready => progresses =>
pending strictly decreases each sweep. The ONLY numeric kept is a PROVEN-INVARIANT ASSERTION (sweeps<=nodes
<=npool) that MUST NEVER FIRE (firing = proof violated = bug, err), categorically unlike fuel (which expects to
be hit and returns a partial answer). The unverified-imperative gap vs machine-checked Agda is exactly this
assertion. THE TEST: if exceeding your "bound" is an expected normal outcome, it's fuel; if it's a bug, it's an
assertion and the real control is the structural guard. ([[feedback_judgement_is_demechanization]]: a derived
bound is a judging line; the productivity proof is the mechanizing one.)

Refines [[feedback_scoped_classical_hypotheses]] / [[feedback_reject_lem_in_substrate]]:
the classical/unbounded step enters ONLY inside a constructed finite scope, never
as a global axiom. The window is the scope; Tarski lifts it back to the limit;
and the scope's BOUND is provable, so the window becomes a structural descent.
