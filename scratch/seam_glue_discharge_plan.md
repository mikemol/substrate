# Σ-SEAM-GLUE discharge — AI-Q plan (M2: realized closure = A₄×ℤ₂ vs S₄)

**Status:** spec `SEAM_GLUE_SPEC.md` (from AI-Π0) GROUNDED + REFRAMED. In-flight `.agda` lives
here in `scratch/` until it compiles + I checkpoint (regen-makefiles → stage-by-path → commit in
one go). I am AI-Q; subtree = `agda/Substrate/…`.

## Grounding (every spec citation verified real, 2026-06-17)
- `Groups/V4` (+ `V4/Axioms`, `V4/Operations`): the V₄ primitive, `_·_`, `ε`, `inv x = x`, `·-comm`.
- `Groups/V4-Cosets`: `V₄-cap-Stab-trivial`, `coset-has-stab-rep`, `coset-stab-rep-unique` — so the
  spec's CORRECTION is grounded (V₄∩Stab={e}; the seam is genuinely not that pairing).
- `WitnessTower/SharedMiddle`: `Lα/Lβ/Lγ` each `HasOrder 2`, `Lβ` shared; **its header states the
  S₄-level seam is OPEN/posited.**
- `Algebra/GL3F2/SylowDecomposition`: "full Sylow-2 of GL(3,F₂) is D₈ of order 8" (a cognate, not S₄).
- `Cocycles/V4Signature/Chirality/Structural`: Chirality(even/odd) ↔ F₂(𝟘/𝟙), the sign character.
- `Actions/S3-on-V4/Generators/{Rotate,RotPow}`: `rotate : V₄→V₄` (the Z₃ 3-cycle), `rot-pow`.
- `Groups/Coxeter/DirectProduct`: the ×ℤ₂ (generic direct product).

## TEST-THE-WALL finding (the spec leans on the heavy half)
SharedMiddle's "two V₄s" are **generating-pairs sharing a generator** within Cayley(V₄):
`⟨Lα,Lβ⟩` and `⟨Lβ,Lγ⟩` each generate ALL of `trans-by(V₄)` — they're the SAME regular rep, not
two distinct S₄ subgroups. The real L-seam (S₄ Sylow-2 = D₈, two distinct V₄ subgroups ∩ = Z(D₈))
is genuinely unbuilt — SharedMiddle says so. The substrate S₄ (`S4-Iso`) is abstract `≈`-transport
through V₄⋊S₃, so "enumerate D₈ by refl" is not free.

## REFRAMING (the substrate-faithful, MATURE discharge — categorical-name-first)
The ACTUAL M40 claim (`applied_grammar.py` L121, `scratch/spectral_view.py:a4z2_compose`):

    A4Z2Element = (s, m, j) ∈ ℤ₂ × V₄ × ℤ₃
    compose((s₉,m₉,j₉),(sₕ,mₕ,jₕ)) = (s₉·sₕ, m₉ ⊕ σ^j₉(mₕ), (j₉+jₕ) mod 3)   -- σ = rotate

The sign `s₉·sₕ` is **decoupled** from `(m,j)`. So the closure is **literally a DIRECT PRODUCT**
`(V₄ ⋊ ℤ₃) × ℤ₂ = A₄ × ℤ₂`, chirality = the ℤ₂ factor. Therefore:

- **L-centrality (M2 bit) = "a direct-product factor is central"** — a UNIVERSAL fact, not a
  D₈-monodromy computation. Trivial/split gluing ⇔ "it's a direct product." The would-be S₄ is the
  NON-split extension where sign is not a direct factor (S₄ center is trivial).
- **Gauge-invariance requirement falls out free**: even↔odd is the ℤ₂-factor automorphism; a direct
  factor stays a direct factor (hence central) under it.
- **Discriminator A₄×ℤ₂ ≠ S₄ = decidable**: element-order distribution. A₄×ℤ₂ has NO order-4
  element ({1:1,2:7,3:8,6:8}); S₄ has six ({…,4:6}). `no-order-4` is the clean --safe witness.

This dissolves the spec's D₈/Sylow/H¹ apparatus into existing universal properties (DirectProduct +
the proven V₄/rotate). The H¹(juncture,ℤ₂)=0 "trivial cocycle" IS "the extension is a direct product."

## Three honest outcomes — PRESERVED (not pre-decided)
The proof formalizes the ACTUAL `a4z2_compose` and DERIVES centrality + no-order-4. If sign were
secretly coupled (→ S₄) the central-chirality lemma would FAIL to typecheck (outcome 2); if the
generators didn't close at 24 the carrier wouldn't be a group (outcome 3). The verdict is forced by
the law, not asserted.

## LABELED ROSTER — the Ξ family (M2 / seam-glue discharge). Dispatch by symbol.
Verify mechanically between each (annealing). State as of 2026-06-17.

- **Ξ1** ✅ DONE (typechecks --safe --without-K, scratch/seam/M40Closure.agda) — `central-χ : (g : A4Z2)
  → compose χ g ≡ compose g χ`, χ = (odd,ε,z0). The M2 centrality bit, in code. Reduces to ℤ₂
  sign-comm + `rotate` fixes ε + V₄ ε-laws.
- **Ξ2** ✅ DONE (typechecks) — `no-order-4 : (g) → sq (sq g) ≡ ι → sq g ≡ ι`. The decidable
  A₄×ℤ₂-vs-S₄ order-invariant (g⁴=ι ⟹ g²=ι; no order-4). Structural: ℤ₃ forces zee=z0, then V₄
  exponent-2 (inv-left) + ℤ₂-square.
- **Ξ3** OPEN — `¬(G ≅ S₄)` CLOSURE: order-preservation-under-iso + an S₄ order-4 witness (a 4-cycle)
  + Ξ2 ⟹ no iso. Converts the last headline either/or into code. (THE M2 closer.)
- **Ξ4** OPEN — DIRECT-PRODUCT UNIVERSAL (spec's B3): exhibit `compose` as `DirectProduct A₄ ℤ₂`
  (A₄ = existing `SemidirectProduct` V₄⋊⟨rotate⟩); Ξ1 then becomes the GENERIC direct-factor-central
  lemma (promotes the per-element proof to the universal — the real abstraction).
- **Ξ5** OPEN — GAUGE-INVARIANCE (spec's B4): even↔odd flip = the ℤ₂ automorphism; centrality
  invariant under it. Immediate from Ξ4 (a direct factor is automorphism-stable).
- **Ξ6** OPEN — HOME into `Substrate/` (the checkpoint): proper module path → regen makefiles →
  stage by path → commit. Unblocks the shim decode (deps resolve in-tree). Gated on Ξ3 (close M2
  before homing) OR can home Ξ1+Ξ2 as standalone proven lemmas earlier.
- **Ξ7** OPEN — PROVENANCE GROUNDING: intern the in-tree `M40Closure.agdai` + Python `a4z2_compose`
  into one forest, read the cross-term. Retires the "checked by eye" comment (the G8 blind spot).
  Gated on Ξ6 (or Φ8). Recursive-common-structure note: Ξ6-vs-Φ8 share the generator "give the shim
  the library context"; Φ8 is the general fix, Ξ6 the special case.

## ADJACENT (Φ family — the apparatus, not the proof)
- **Φ8** OPEN — `agdai_shim` accepts `-i` include paths so LIBRARY-DEPENDENT scratch `.agdai` decode
  (today: defaultOptions, no path → `decode Nothing` on any `.agdai` importing `Substrate.*` from
  outside its build tree). Generalizes Ξ6's special case; unblocks Ξ7 without homing.

## Discipline ledger
- Compose from proven pieces (don't rebuild V₄/rotate). [[feedback_never_discard_residue]]
- Categorical-name-first: centrality = direct-factor universal, not bespoke seam. [[feedback_categorical_name_first]]
- Keep in-flight `.agda` out of the build tree until the commit checkpoint (AI-Q/jea protocol).
- Don't pre-decide the verdict; let the typecheck force outcome 1/2/3.
