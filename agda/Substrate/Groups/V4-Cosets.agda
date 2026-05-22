------------------------------------------------------------------------
-- Substrate.Groups.V4-Cosets
--
-- Slice 13: V_4-coset equivalence in S_4 + unique Stab(X)
-- representative for arbitrary anchor X ∈ Axis. Captures the
-- structural content of S_4 / V_4 ≅ Stab(X) ≅ S_3 at the
-- relational/bijective level — no quotient-group construction
-- (which would require HITs or funext that the extraction
-- discipline forbids).
--
-- The catalog claim "V_4 ⋊ S_3 ≅ S_4 with quotient ≅ S_3" is closed
-- here as: every V_4-coset in S_4 has a UNIQUE Stab(X) representative
-- for any chosen anchor X. Combined with slice 3's factorisation
-- theorem (every σ ∈ S_4 factors as embed v · s with s ∈ Stab(X)),
-- this is structurally equivalent to the quotient isomorphism.
--
-- Three load-bearing claims, all parametric over X : Axis:
--
--   _∼V₄_                — equivalence relation on S_4 with σ ∼V₄ τ
--                          iff τ · σ⁻¹ ∈ V_4-image. (X-independent.)
--
--   coset-has-stab-rep   — every σ has some τ ∈ Stab(X) with σ ∼V₄ τ
--                          (witness: τ = s-for-anchor X σ).
--
--   coset-stab-rep-unique — if τ₁, τ₂ ∈ Stab(X) and both ∼V₄-related
--                          to σ, then τ₁ ≈ τ₂. Uses V_4 ∩ Stab(X) =
--                          {e} (slice 3's V₄-cap-Stab-trivial).
--
-- Per [[feedback-use-vs-commit]]: the cocycle USES whatever anchor
-- the caller chooses, but does not COMMIT to D. The parameterized
-- form makes the gauge-invariance manifest at the type level.
--
-- See: catalog/cocycles.md § CY-5 — V_4 ⋊ S_3 ≅ S_4 picture;
--      Substrate.Groups.SemidirectProduct (slice 3) — factorisation;
--      Substrate.Groups.Subgroup (slice 12) — V_4-image normal-
--      subgroup closure laws + parametric Stab-Subgroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Cosets where

open import Level using (0ℓ)
open import Substrate.Foundation.Product using (∃; Σ; Σ-syntax; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε; _≈_;
         ·-cong; ≈-refl; ≈-sym; ≈-trans;
         inv-right; ⁻¹-cong; inv-l; inv-r)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; V₄-image; act-axis-id)
open import Substrate.Groups.SemidirectProduct
  using (Stab; v-for-anchor; s-for-anchor; s-for-fixes-anchor;
         factorisation; V₄-cap-Stab-trivial)
open import Substrate.Groups.Subgroup
  using (V₄-image-ε; V₄-image-∙; V₄-image-⁻¹; V₄-image-resp-≈;
         Stab-∙; Stab-⁻¹; Stab-resp-≈)

------------------------------------------------------------------------
-- The V_4-coset equivalence (anchor-independent).
--
-- σ ∼V₄ τ iff τ and σ differ by a V_4-image element on the right.
-- Equivalent to "σ and τ are in the same V_4-coset" (using right
-- cosets; V_4 normality makes left and right cosets coincide).
------------------------------------------------------------------------

infix 4 _∼V₄_

_∼V₄_ : Permutation → Permutation → Set
σ ∼V₄ τ = V₄-image (τ · (σ ⁻¹))

------------------------------------------------------------------------
-- Equivalence-relation proofs (anchor-independent).
------------------------------------------------------------------------

-- Reflexivity: σ · σ⁻¹ ≈ ε ∈ V_4-image.
∼V₄-refl : (σ : Permutation) → σ ∼V₄ σ
∼V₄-refl σ =
  V₄-image-resp-≈ {ε} {σ · (σ ⁻¹)}
    (≈-sym {σ · (σ ⁻¹)} {ε} (inv-right σ)) V₄-image-ε

-- Symmetry: (τ · σ⁻¹)⁻¹ ≈ σ · τ⁻¹, so closure under inversion gives
-- the reverse direction.
∼V₄-sym : {σ τ : Permutation} → σ ∼V₄ τ → τ ∼V₄ σ
∼V₄-sym {σ} {τ} τσ⁻¹∈V₄ =
  V₄-image-resp-≈ {(τ · (σ ⁻¹)) ⁻¹} {σ · (τ ⁻¹)}
    inv-eq (V₄-image-⁻¹ {τ · (σ ⁻¹)} τσ⁻¹∈V₄)
  where
    -- (τ · σ⁻¹)⁻¹ x = invₐ τ⁻¹ (invₐ τ x) = applyₛ σ (invₐₛ τ x)
    --              = applyₛ (σ · τ⁻¹) x.   Pointwise refl.
    inv-eq : ((τ · (σ ⁻¹)) ⁻¹) ≈ (σ · (τ ⁻¹))
    inv-eq _ = refl

-- Transitivity: chain V₄-image closure of two ≈-related products
-- with cancellation in the middle.
∼V₄-trans :
  {σ τ ρ : Permutation} → σ ∼V₄ τ → τ ∼V₄ ρ → σ ∼V₄ ρ
∼V₄-trans {σ} {τ} {ρ} τσ⁻¹∈V₄ ρτ⁻¹∈V₄ =
  V₄-image-resp-≈ {(ρ · (τ ⁻¹)) · (τ · (σ ⁻¹))} {ρ · (σ ⁻¹)}
    chain (V₄-image-∙ {ρ · (τ ⁻¹)} {τ · (σ ⁻¹)} ρτ⁻¹∈V₄ τσ⁻¹∈V₄)
  where
    -- ((ρ · τ⁻¹) · (τ · σ⁻¹)) x
    --   = applyₛ ρ (invₐₛ τ (applyₛ τ (invₐₛ σ x)))
    --   = applyₛ ρ (invₐₛ σ x)              [inv-l τ]
    --   = applyₛ (ρ · σ⁻¹) x.
    chain : ((ρ · (τ ⁻¹)) · (τ · (σ ⁻¹))) ≈ (ρ · (σ ⁻¹))
    chain x = cong (applyₛ ρ) (inv-l τ (invₐₛ σ x))

------------------------------------------------------------------------
-- coset-has-stab-rep: every σ has a Stab(X) representative in its
-- V_4-coset, for any anchor X.
--
-- Witness: τ = s-for-anchor X σ. By slice 3:
--   * s-for-fixes-anchor X σ: Stab X (s-for-anchor X σ).
--   * (s-for-anchor X σ) · σ⁻¹ ≈ embed (v-for-anchor X σ) ∈ V_4-image
--     (the V_4 witness from the factorisation, peeled off).
------------------------------------------------------------------------

coset-has-stab-rep :
  (X : Axis) (σ : Permutation) →
  Σ Permutation (λ τ → Stab X τ × σ ∼V₄ τ)
coset-has-stab-rep X σ =
  s-for-anchor X σ , s-for-fixes-anchor X σ , v-for-anchor X σ , prf
  where
    -- ((s-for-anchor X σ) · σ⁻¹) x
    --   = act-axis (v-for-anchor X σ) (applyₛ σ (invₐₛ σ x))
    --   = act-axis (v-for-anchor X σ) x                  [inv-r σ]
    --   = applyₛ (embed (v-for-anchor X σ)) x.
    prf : ((s-for-anchor X σ) · (σ ⁻¹)) ≈ embed (v-for-anchor X σ)
    prf x = cong (act-axis (v-for-anchor X σ)) (inv-r σ x)

------------------------------------------------------------------------
-- coset-stab-rep-unique: a V_4-coset has at most one Stab(X)
-- representative.
--
-- If τ₁, τ₂ ∈ Stab(X) are both ∼V₄-related to σ, then:
--   1. By transitivity: τ₂ · τ₁⁻¹ ∈ V_4-image (i.e., τ₁ ∼V₄ τ₂).
--   2. Stab(X) closure: τ₂ · τ₁⁻¹ ∈ Stab(X).
--   3. V_4 ∩ Stab(X) = {e} (slice 3): the V_4 witness must be e,
--      so τ₂ · τ₁⁻¹ ≈ embed e ≈ ε.
--   4. τ₂ · τ₁⁻¹ ≈ ε ⇒ τ₁ ≈ τ₂.
------------------------------------------------------------------------

coset-stab-rep-unique :
  (X : Axis) (σ τ₁ τ₂ : Permutation) →
  Stab X τ₁ → Stab X τ₂ →
  σ ∼V₄ τ₁ → σ ∼V₄ τ₂ →
  τ₁ ≈ τ₂
coset-stab-rep-unique X σ τ₁ τ₂ τ₁-stab τ₂-stab σ∼τ₁ σ∼τ₂ x =
  sym (trans
        (cong (applyₛ τ₂) (sym (inv-l τ₁ x)))
        (τ₂τ₁⁻¹≈ε (applyₛ τ₁ x)))
  where
    -- Step 1: τ₂ · τ₁⁻¹ ∈ V_4-image (from σ∼τ₂ ∘ sym σ∼τ₁ via trans).
    τ₁∼τ₂ : τ₁ ∼V₄ τ₂
    τ₁∼τ₂ = ∼V₄-trans {τ₁} {σ} {τ₂} (∼V₄-sym {σ} {τ₁} σ∼τ₁) σ∼τ₂

    -- Step 2: τ₂ · τ₁⁻¹ ∈ Stab(X) (subgroup closure).
    τ₂τ₁⁻¹-stab : Stab X (τ₂ · (τ₁ ⁻¹))
    τ₂τ₁⁻¹-stab =
      Stab-∙ {X} {τ₂} {τ₁ ⁻¹} τ₂-stab (Stab-⁻¹ {X} {τ₁} τ₁-stab)

    -- Extract the V_4 witness w with τ₂ · τ₁⁻¹ ≈ embed w.
    w : V₄
    w = proj₁ τ₁∼τ₂

    τ₂τ₁⁻¹≈embed-w : (τ₂ · (τ₁ ⁻¹)) ≈ embed w
    τ₂τ₁⁻¹≈embed-w = proj₂ τ₁∼τ₂

    -- Step 3: Stab X (embed w), then V₄-cap-Stab-trivial gives w ≡ e.
    embed-w-stab : Stab X (embed w)
    embed-w-stab =
      Stab-resp-≈ {X} {τ₂ · (τ₁ ⁻¹)} {embed w} τ₂τ₁⁻¹≈embed-w τ₂τ₁⁻¹-stab

    w≡e : w ≡ e
    w≡e = V₄-cap-Stab-trivial X w embed-w-stab

    -- Step 4: τ₂ · τ₁⁻¹ ≈ ε. Combine the witness with w ≡ e.
    τ₂τ₁⁻¹≈ε : (τ₂ · (τ₁ ⁻¹)) ≈ ε
    τ₂τ₁⁻¹≈ε y =
      trans (τ₂τ₁⁻¹≈embed-w y)
            (trans (cong (λ v → act-axis v y) w≡e)
                   (act-axis-id y))

------------------------------------------------------------------------
-- Bundled coset-bijection record, parametric over anchor X.
--
-- Packages the structural content of S_4 / V_4 ≅ Stab(X) without
-- explicitly constructing the quotient group.
------------------------------------------------------------------------

record S₄/V₄-↔-Stab (X : Axis) : Set₁ where
  field
    -- The equivalence relation on S_4 (anchor-independent).
    _∼_ : Permutation → Permutation → Set

    -- Every σ has a Stab(X) representative in its coset.
    rep : (σ : Permutation) →
          Σ Permutation (λ τ → Stab X τ × σ ∼ τ)

    -- The Stab(X) representative is unique up to pointwise
    -- equivalence.
    rep-unique :
      (σ τ₁ τ₂ : Permutation) →
      Stab X τ₁ → Stab X τ₂ →
      σ ∼ τ₁ → σ ∼ τ₂ →
      τ₁ ≈ τ₂

S₄/V₄-↔-Stab-bijection : (X : Axis) → S₄/V₄-↔-Stab X
S₄/V₄-↔-Stab-bijection X = record
  { _∼_        = _∼V₄_
  ; rep        = coset-has-stab-rep X
  ; rep-unique = coset-stab-rep-unique X
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. With slice 13 in place, the V_4 ⋊ S_3 ≅ S_4 catalog claim is
--    closed at three levels:
--    - Factorisation (slice 3): every σ = embed v · s.
--    - Normality (slice 9 + 12): V_4 is normal.
--    - Quotient bijection (this slice): S_4 / V_4 ↔ Stab(X) for any X.
--
-- 2. The full "S_4 / V_4 ≅ S_3 as GROUPS" statement would require
--    a quotient-group construction. Setoid-quotient approaches
--    work in Agda without HITs but introduce extra abstraction
--    layers. Deferred — the relational bijection here is the
--    structural content the catalog asserts.
--
-- 3. Stab(X) ≅ S_3 (the second iso in S_4/V_4 ≅ S_3) is implicit
--    in this slice — Stab(X) has 6 elements, S_3 has 6 elements,
--    and they're isomorphic by faithful action on Axis \ {X}. The
--    formal iso for X=D is built in Substrate.Cocycles.V4Signature.
--    S4Iso; the parameterization here means the same construction
--    works at any anchor.
--
-- 4. Cross-references:
--    - Substrate.Groups.SemidirectProduct (slice 3) — factorisation,
--      v-for-anchor, s-for-anchor, V₄-cap-Stab-trivial.
--    - Substrate.Groups.V4-Normality (slice 9) — V₄-normal.
--    - Substrate.Groups.Subgroup (slice 12) — V₄-image normal
--      subgroup + parametric Stab-Subgroup closure laws.
------------------------------------------------------------------------
