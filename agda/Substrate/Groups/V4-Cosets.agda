------------------------------------------------------------------------
-- Substrate.Groups.V4-Cosets
--
-- Slice 13: V_4-coset equivalence in S_4 + unique Stab(D)
-- representative. Captures the structural content of S_4 / V_4 ≅
-- Stab(D) ≅ S_3 at the relational/bijective level — no quotient-group
-- construction (which would require HITs or funext that the
-- extraction discipline forbids).
--
-- The catalog claim "V_4 ⋊ S_3 ≅ S_4 with quotient ≅ S_3" is closed
-- here as: every V_4-coset in S_4 has a UNIQUE Stab(D)
-- representative. Combined with slice 3's factorisation theorem
-- (every σ ∈ S_4 factors as embed v · s with s ∈ Stab(D)), this is
-- structurally equivalent to the quotient isomorphism.
--
-- Three load-bearing claims:
--
--   _∼V₄_                 — equivalence relation on S_4 with σ ∼V₄ τ
--                           iff τ · σ⁻¹ ∈ V_4-image.
--
--   coset-has-stab-rep    — every σ has some τ ∈ Stab(D) with σ ∼V₄
--                           τ (witness: τ = s-for σ).
--
--   coset-stab-rep-unique — if τ₁, τ₂ ∈ Stab(D) and both ∼V₄-related
--                           to σ, then τ₁ ≈ τ₂. Uses V_4 ∩ Stab(D) =
--                           {e} (slice 3's V₄-cap-Stab-D-trivial).
--
-- See: catalog/cocycles.md § CY-5 — V_4 ⋊ S_3 ≅ S_4 picture;
--      Substrate.Groups.SemidirectProduct (slice 3) — factorisation;
--      Substrate.Groups.Subgroup (slice 12) — V_4-image normal-
--      subgroup closure laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Cosets where

open import Level using (0ℓ)
open import Data.Product using (∃; Σ; Σ-syntax; _,_; proj₁; proj₂; _×_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε; _≈_;
         ·-cong; ≈-refl; ≈-sym; ≈-trans;
         inv-right; ⁻¹-cong; inv-l; inv-r)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; V₄-image)
open import Substrate.Groups.SemidirectProduct
  using (Stab-D; v-for; s-for; s-for-fixes-D; factorisation;
         V₄-cap-Stab-D-trivial)
open import Substrate.Groups.Subgroup
  using (V₄-image-ε; V₄-image-∙; V₄-image-⁻¹; V₄-image-resp-≈;
         Stab-D-∙; Stab-D-⁻¹; Stab-D-resp-≈)

------------------------------------------------------------------------
-- The V_4-coset equivalence.
--
-- σ ∼V₄ τ iff τ and σ differ by a V_4-image element on the right.
-- Equivalent to "σ and τ are in the same V_4-coset" (using right
-- cosets; V_4 normality makes left and right cosets coincide).
------------------------------------------------------------------------

infix 4 _∼V₄_

_∼V₄_ : Permutation → Permutation → Set
σ ∼V₄ τ = V₄-image (τ · (σ ⁻¹))

------------------------------------------------------------------------
-- Equivalence-relation proofs.
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
-- coset-has-stab-rep: every σ has a Stab(D) representative in its
-- V_4-coset.
--
-- Witness: τ = s-for σ. By slice 3:
--   * s-for-fixes-D: Stab-D (s-for σ).
--   * (s-for σ) · σ⁻¹ ≈ embed (v-for σ) ∈ V_4-image (the V_4
--     witness from the factorisation, peeled off).
------------------------------------------------------------------------

coset-has-stab-rep :
  (σ : Permutation) →
  Σ Permutation (λ τ → Stab-D τ × σ ∼V₄ τ)
coset-has-stab-rep σ =
  s-for σ , s-for-fixes-D σ , v-for σ , prf
  where
    -- ((s-for σ) · σ⁻¹) x
    --   = act-axis (v-for σ) (applyₛ σ (invₐₛ σ x))
    --   = act-axis (v-for σ) x                  [inv-r σ]
    --   = applyₛ (embed (v-for σ)) x.
    prf : ((s-for σ) · (σ ⁻¹)) ≈ embed (v-for σ)
    prf x = cong (act-axis (v-for σ)) (inv-r σ x)

------------------------------------------------------------------------
-- coset-stab-rep-unique: a V_4-coset has at most one Stab(D)
-- representative.
--
-- If τ₁, τ₂ ∈ Stab(D) are both ∼V₄-related to σ, then:
--   1. By transitivity: τ₂ · τ₁⁻¹ ∈ V_4-image (i.e., τ₁ ∼V₄ τ₂).
--   2. Stab(D) closure: τ₂ · τ₁⁻¹ ∈ Stab(D).
--   3. V_4 ∩ Stab(D) = {e} (slice 3): the V_4 witness must be e,
--      so τ₂ · τ₁⁻¹ ≈ embed e ≈ ε.
--   4. τ₂ · τ₁⁻¹ ≈ ε ⇒ τ₁ ≈ τ₂.
------------------------------------------------------------------------

coset-stab-rep-unique :
  (σ τ₁ τ₂ : Permutation) →
  Stab-D τ₁ → Stab-D τ₂ →
  σ ∼V₄ τ₁ → σ ∼V₄ τ₂ →
  τ₁ ≈ τ₂
coset-stab-rep-unique σ τ₁ τ₂ τ₁-stab τ₂-stab σ∼τ₁ σ∼τ₂ x =
  sym (trans
        (cong (applyₛ τ₂) (sym (inv-l τ₁ x)))
        (τ₂τ₁⁻¹≈ε (applyₛ τ₁ x)))
  where
    -- Step 1: τ₂ · τ₁⁻¹ ∈ V_4-image (from σ∼τ₂ ∘ sym σ∼τ₁ via trans).
    τ₁∼τ₂ : τ₁ ∼V₄ τ₂
    τ₁∼τ₂ = ∼V₄-trans {τ₁} {σ} {τ₂} (∼V₄-sym {σ} {τ₁} σ∼τ₁) σ∼τ₂

    -- Step 2: τ₂ · τ₁⁻¹ ∈ Stab-D (subgroup closure).
    τ₂τ₁⁻¹-stab : Stab-D (τ₂ · (τ₁ ⁻¹))
    τ₂τ₁⁻¹-stab =
      Stab-D-∙ {τ₂} {τ₁ ⁻¹} τ₂-stab (Stab-D-⁻¹ {τ₁} τ₁-stab)

    -- Extract the V_4 witness w with τ₂ · τ₁⁻¹ ≈ embed w.
    w : V₄
    w = proj₁ τ₁∼τ₂

    τ₂τ₁⁻¹≈embed-w : (τ₂ · (τ₁ ⁻¹)) ≈ embed w
    τ₂τ₁⁻¹≈embed-w = proj₂ τ₁∼τ₂

    -- Step 3: Stab-D (embed w), then V₄-cap-Stab-D-trivial gives
    -- w ≡ e.
    embed-w-stab : Stab-D (embed w)
    embed-w-stab =
      Stab-D-resp-≈ {τ₂ · (τ₁ ⁻¹)} {embed w} τ₂τ₁⁻¹≈embed-w τ₂τ₁⁻¹-stab

    w≡e : w ≡ e
    w≡e = V₄-cap-Stab-D-trivial w embed-w-stab

    -- Step 4: τ₂ · τ₁⁻¹ ≈ ε. Combine the witness with w ≡ e.
    τ₂τ₁⁻¹≈ε : (τ₂ · (τ₁ ⁻¹)) ≈ ε
    τ₂τ₁⁻¹≈ε y =
      trans (τ₂τ₁⁻¹≈embed-w y)
            (cong (λ v → act-axis v y) w≡e)

------------------------------------------------------------------------
-- Bundled coset-bijection record.
--
-- Packages the structural content of S_4 / V_4 ≅ Stab(D) without
-- explicitly constructing the quotient group.
------------------------------------------------------------------------

record S₄/V₄-↔-StabD : Set₁ where
  field
    -- The equivalence relation on S_4.
    _∼_ : Permutation → Permutation → Set

    -- Every σ has a Stab(D) representative in its coset.
    rep : (σ : Permutation) →
          Σ Permutation (λ τ → Stab-D τ × σ ∼ τ)

    -- The Stab(D) representative is unique up to pointwise
    -- equivalence.
    rep-unique :
      (σ τ₁ τ₂ : Permutation) →
      Stab-D τ₁ → Stab-D τ₂ →
      σ ∼ τ₁ → σ ∼ τ₂ →
      τ₁ ≈ τ₂

S₄/V₄-↔-StabD-bijection : S₄/V₄-↔-StabD
S₄/V₄-↔-StabD-bijection = record
  { _∼_        = _∼V₄_
  ; rep        = coset-has-stab-rep
  ; rep-unique = coset-stab-rep-unique
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. With slice 13 in place, the V_4 ⋊ S_3 ≅ S_4 catalog claim is
--    closed at three levels:
--    - Factorisation (slice 3): every σ = embed v · s.
--    - Normality (slice 9 + 12): V_4 is normal.
--    - Quotient bijection (this slice): S_4 / V_4 ↔ Stab(D)
--      structurally.
--
-- 2. The full "S_4 / V_4 ≅ S_3 as GROUPS" statement would require
--    a quotient-group construction. Setoid-quotient approaches
--    work in Agda without HITs but introduce extra abstraction
--    layers. Deferred — the relational bijection here is the
--    structural content the catalog asserts.
--
-- 3. Stab(D) ≅ S_3 (the second iso in S_4/V_4 ≅ S_3) is implicit
--    in this slice — Stab(D) has 6 elements, S_3 has 6 elements,
--    and they're isomorphic by faithful action on {C, S, W}. The
--    formal iso (Stab-D-Group ≅ S₃-Group) is not constructed here
--    but is mechanical from the explicit Stab(D) elements in
--    Substrate.Cocycles.V4Signature.S4Iso.
--
-- 4. Cross-references:
--    - Substrate.Groups.SemidirectProduct (slice 3) — factorisation,
--      v-for, s-for, V₄-cap-Stab-D-trivial.
--    - Substrate.Groups.V4-Normality (slice 9) — V₄-normal.
--    - Substrate.Groups.Subgroup (slice 12) — V₄-image and Stab-D
--      subgroup closure laws.
------------------------------------------------------------------------
