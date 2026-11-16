---
name: project_sppf_eea_unification
description: arc unifying the balanced SPPF (Wedge/AxisWord/Packed*) with the EEA/Trace framework; ℚ reduce/Canonical via the shared shape invariant — STAGES 2/3 COMPLETE (shape route)
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The balanced SPPF (`Wedge/AxisWord/Packed*`) and the EEA/Euclidean-trace
framework are the SAME structure; ℚ `reduce`/`Canonical` is the driving consumer.
**Shared spine:** `Algebra/Wedge.agda` `DivStr`/`Wedge D`/`Trace D`; `EEATrace`
= ℕ instance; `Wedge/Shape.agda` `shape : Trace D → List ℕ` (the carrier-free
quotient sequence = CONTINUED FRACTION; `ℕ-shape t = shape (fromEEATrace t)`).

**STAGE 1 — DONE (b559d21).** `reduce : ℚ → ℚ` projects the cofactor quotients
kept by `gcd-divides-left/right`; soundness `≈-canonical : q ≈ℚ reduce q` in
`Q/Properties/Reduce.agda`.

**STAGE 2/3 — DONE (commits 47da254, 018258c, 5e427f0, b7988eb).** User chose the
**shape route** (SPPF supplies uniqueness) over a Bézout-only route. Landed
`ℚ-Canonical : Canonical⟦30f92ad5⟧ ℚ-Quotient` (zero postulates, --safe
--without-K, each module typechecks standalone). The whole arc collapses to
`canonical-respects-≈ : a ≈ℚ b → reduce a ≡ reduce b` (idempotent =
`sym ∘ respects-≈ ∘ ≈-canonical`; the other 2 fields already landed).

**ARCHITECTURE (anti-amnesia):** the shipped proof inducts on the **`EEATrace`
datatype's own base/step constructors**, where the recurrence `ℕ-shape (step b w
tr) ≡ quotient w ∷ ℕ-shape tr` is **refl**; `compute-trace` is touched only
wholesale via `gcd-trace = proj₂ (compute-trace a b)` (refl-clean: `gcd-ℕ a b =
proj₁ (compute-trace a b)` definitionally). Template: `TraceDivides.agda`.

**CORRECTION (commit 12333c1) — the original "compute-trace can't reduce, so I
HAD to avoid it" framing was an OVERCLAIM** (user caught it). Two distinct claims:
(1) GENERAL Acc proof-irrelevance `(p q : Acc R x) → p ≡ q` does need funext
(equate the wrapped functions) — unavailable; (2) RESULT-irrelevance —
`compute-trace-acc`'s OUTPUT is independent of the Acc witness — needs NO funext,
NO K: structural induction on the accessibility proofs, applying the wrapped
functions pointwise (never comparing them). `Nat/GCD/ComputeTraceStep.agda`:
`cta-irr` (result-irrelevance) → `cta-step` (uniform step for any witness =
"frontier-2→-1 is the same step as -1→frontier") → `compute-trace-step` →
**`cf-step`: the CF recurrence on the EXTERIOR compute-trace**, the very thing
the framing wrongly ruled out. So EEATrace-induction was a sound CHOICE, not
forced. Lesson: in a finite/well-founded domain, "undecidable/irrelevant in
general" can be made constructive by demonstrating the uniform inductive step.

**The two keystones (the "shape is canonical key" content):**
- `shape-value-invariance` (Nat/GCD/CFInvariance.agda): `a*d ≡ c*b → ℕ-shape t₁ ≡
  ℕ-shape t₂`, dual-trace structural induction. `0 < g` (gcd index) hyps exclude
  degenerate `base 0` (=0/0); g preserved by `step` so positivity threads free.
  Head step `divmod-cross` multiplies the two reconstruction eqs into one
  division-by-(suc b'·suc d') + `divmod-unique` (Nat/DivMod/Unique).
- `cf-injective` (Nat/GCD/CFInjective.agda): coprime + equal shape ⟹ equal
  (num,den). Coprimality = gcd index pinned to **1**; it forces the base to n/1
  and threads through `step` — so NO separate coprime-step lemma. (`shape` is NOT
  injective without coprimality: 4/2,6/3 both have shape [2].)

**Glue:** `reduced-≈⇒≡` spine (Q/Properties/Canonical.agda) — `reduce a ≈ℚ a ≈ℚ b
≈ℚ reduce b` gives `reduce a ≈ℚ reduce b` free; then both being REDUCED, compare
their coprime traces DIRECTLY (no scale-invariance needed). `reduce-is-reduced` ←
`cofactor-coprime` (Z/Coprime.agda, via `bezout-ℤ` + cancel g + `∣-one`;
**must live in Z layer — Z.Bezout imports Nat.GCD, so Nat.GCD can't import it
back**). Sign split: `ℤ-sign-mag`/`abs-*ℤ-pos` (Q/Properties/Abs.agda), cross-sign
cases by +/-suc clash.

**CONVERGENCE PASS (all 6 deliverables landed; [[feedback_convergence_over_isolation]]):**
(1+2) `ShapeBridge`: `trace-shape-det` + `shape-canonical` de-orphan cf-step
(exterior compute-trace shape = any interior trace's shape); `shape-step` named,
cf-step refactored to factor as exterior∘interior. (3) `CanonicalBezout`: SECOND
proof of `canonical-respects-≈` via Euclid (`Z.Euclid`, bezout-ℤ + ℤ→ℕ
pos-divides) + `∣-antisym` (`Divides.Antisym`); both routes share the SAME
`uniq-from-mag-den` assembly (`Q.Properties.Uniqueness`) + `reduce-is-reduced`,
differing only in cf-injective vs euclid+antisym. (4) `Q.Properties.Decidable`:
`_≈ℚ?_` decides via the Register's `_≟ˢ_` on reduced CF shape keys — Register now
LOAD-BEARING, computationally verified (`isYes (2/4 ≈ℚ? 1/2) ≡ true` by refl) and
proven to agree with `canonical-respects-≈`. (5) chirality pairs + `*≡1ˡ/ʳ`.
(6) is-reduced oracles discharged. So the PackedTree-uniqueness ⟷ propositional
caveat is now cashed for the Register half. Backbone added: `∣-one`,`*≡1`,
`divmod-unique`,Order mono sextet,`gcd-pos`/`gcd-suc-pos`,`bezout-1→coprime`/
`cofactor-coprime`,`∣-antisym`,`euclid`. See [[feedback_never_discard_residue]],
[[project_carrier_locality_gate]].

**OUTSTANDING / RESUME HERE (2026-06-11).** Arc is COMPLETE & green (HEAD verified
by clean rebuild); these are deferred/optional, priority order:
- **[MEDIUM — the real remaining math] PackedTree⟷ℚ.** The suffix-sharing DAG
  (`AxisWord/PackedRecall`,`PackedSize`,`PackedReadout`, capacity-2 carry-cascade)
  is still ORPHANED w.r.t. ℚ — referenced only in a comment in
  `Q/Properties/Canonical.agda`, never in code. Only the **Register** half
  (`Wedge/Shape/Register._≟ˢ_`, whole-shape interning) got cashed, in
  `Q/Properties/Decidable.agda`. Cashing commit 09c4e81's "suffix-sharing DAG IS
  the EEA trace" for ℚ is what would actually COMPLETE the SPPF≅EEA claim.
- **[SMALL] 0/0 branch cut as CODE** (currently prose only): exhibit that
  `cf-injective`/shape-determinism genuinely needs the `0 < g` guard at gcd-index
  0 — the chart-transition singularity (ln(0)=−∞ analog from the chart/phase lens).
- **[SMALL] two Canonical instances unreconciled.** `Q.Properties.Canonical.ℚ-Canonical`
  (shape) and `Q.Properties.CanonicalBezout.ℚ-Canonical-bezout` (Euclid) agree
  POINTWISE (`Q.Properties.RouteAgreement.routes-agree`), but record-equality needs
  funext (absent under --safe). Downstream QU-arc wiring (QU5/QU6 "attach a
  Canonical witness") has an UNMADE gauge choice of which is THE instance — decide
  or document as gauge.
- **[HYGIENE] no `Q.Properties` barrel** (9 modules built via Makefile, un-barreled;
  deliberate under load-bound discipline, or add a curated one).
- **[MEMORY] chart/phase lens** (gcd/Bézout≅exp/ln≅set/proof-relevant≅detector/carrier
  + 0/0 branch cut + `--without-K`-as-phase-index) is folded into
  [[feedback_convergence_over_isolation]]; a standalone project-lens memory tying it
  to the commuting-sphere/Dent program is offered, not written.
RECOMMENDED NEXT = PackedTree⟷ℚ (only item with real math; completes the claim).
Hedberg machinery EXISTS (`Foundation.Hedberg.Decidable⇒UIP`) — verify, don't re-add.
