------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge
--
-- M-11.dim4.reserved-bridge. Validates the catalog conjecture
-- "8 reserved = signed singletons" at the F₂-vector-space level by
-- establishing the structural bijection:
--
--   SelfDual ↔ Vector 3 ↔ Reserved
--
-- Where:
--   * SelfDual ⊂ Λ²(F₂⁴): the 8 bivectors fixed by Hodge ★ in F₂⁴
--     (from M-11.dim4 SelfDual.agda); 3-parameter family with
--     coefficients (c₀, c₁, c₂) one per fixed-point-free pair of
--     the Hodge index-reversal involution.
--   * Reserved ⊂ Codeword (Bool⁵): the 8 codewords with
--     bit₃ = bit₄ = false (from Codeword.agda); 3-parameter family
--     with free bits (bit₀, bit₁, bit₂) — matched to the catalog
--     reading `Reserved ↔ Axis × Bool` (4 axes × 2 signs).
--
-- This file provides the SelfDual ↔ Vector 3 side via the **closure-
-- based approach**: build self-dual bivectors as F₂-linear combinations
-- of the 3 canonical generators (sd-pair-01-23, sd-pair-02-13,
-- sd-pair-03-12); self-duality follows from sd-closed-+ⱽ and
-- sd-closed-*ₛ.
--
-- The Reserved ↔ Vector 3 side is documented in Codeword.agda's
-- existing "first reading" (Axis × Bool ≅ F₂² × F₂ ≅ F₂³ = Vector 3).
-- Formal connection deferred to M-10A.consumer-bridge.
--
-- **Catalog conjecture validation status**: cardinality (8 = 8) and
-- F₂-vector-space structure (both are 3-dim F₂-subspaces) MATCH.
-- The deeper structural correspondence (does V₄ action on Reserved
-- match an analogous action on SelfDual? does chirality bit on
-- Reserved correspond to the c₂ pair of SelfDual?) is a follow-up
-- question.
--
-- **Gauge-freedom warning.** The `vector3-to-selfdual` defined here
-- is ONE of 168 F₂-linear Vector 3 ↔ SelfDual bijections (= the
-- identity permutation on the 3 sd-pair generators). Two alternatives
-- are formalised in
-- `Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives`
-- (cyclic shift + last-two swap). At the F₂-linear level, none is
-- privileged; the catalog has no preferred choice. See memory
-- `project_reserved_selfdual_bijection_gauge` for the full 168-coset
-- analysis, the V₄-equivariance impossibility, and the fractal
-- recurrence at the meta-level (alignment-axis space ≅ 3+1 parity
-- universal). Downstream consumers depending on this specific
-- bijection should declare so explicitly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃; ₄)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar
open import Substrate.Algebra.F2.HodgeDim4.SelfDual

------------------------------------------------------------------------
-- Backward: Vector 3 → SelfDual (via canonical generators).
--
-- Build the self-dual bivector for coefficients (c₀, c₁, c₂) as
-- the F₂-linear combination of the 3 canonical generators.
-- Self-duality follows by closure of self-duality under +ⱽ and *ₛ.
------------------------------------------------------------------------

vector3-to-selfdual : Vector 3 → Bivector
vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  (c₀ *ₛ sd-pair-01-23) +ⱽ
  ((c₁ *ₛ sd-pair-02-13) +ⱽ (c₂ *ₛ sd-pair-03-12))

vector3-to-selfdual-sd :
  (v : Vector 3) → SelfDual-Pred (vector3-to-selfdual v)
vector3-to-selfdual-sd (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  sd-closed-+ⱽ
    (c₀ *ₛ sd-pair-01-23)
    ((c₁ *ₛ sd-pair-02-13) +ⱽ (c₂ *ₛ sd-pair-03-12))
    (sd-closed-*ₛ c₀ sd-pair-01-23 sd-pair-01-23-self-dual)
    (sd-closed-+ⱽ
      (c₁ *ₛ sd-pair-02-13)
      (c₂ *ₛ sd-pair-03-12)
      (sd-closed-*ₛ c₁ sd-pair-02-13 sd-pair-02-13-self-dual)
      (sd-closed-*ₛ c₂ sd-pair-03-12 sd-pair-03-12-self-dual))

------------------------------------------------------------------------
-- Forward: SelfDual → Vector 3 (extract the 3 free coefficients).
--
-- The 3 coefficients are lookup ω 0, lookup ω 1, lookup ω 2 (the
-- "first half" of the 6-component bivector; the "second half"
-- equals the first reversed via the SelfDual condition).
--
-- Predicate-independent: we extract from any Bivector. The
-- SelfDual-Pred is needed only for the forward-then-backward
-- round-trip (deferred).
------------------------------------------------------------------------

selfdual-coefficients : Bivector → Vector 3
selfdual-coefficients ω =
  lookup ω zero ∷ lookup ω ₁ ∷ lookup ω ₂ ∷ []

------------------------------------------------------------------------
-- Round-trip (backward-then-forward): coefficients ∘ vector3-to-selfdual ≡ id.
--
-- Computes lookup at indices 0, 1, 2 of the constructed self-dual
-- bivector and verifies it equals the original (c₀, c₁, c₂).
-- Each lookup reduces via F₂ axioms applied to the canonical-generator
-- form's Vec components.
------------------------------------------------------------------------

-- Helper: lookup at index 0 of `vector3-to-selfdual (c₀, c₁, c₂)` is c₀.
-- After Agda's reduction of the basis / +ⱽ / *ₛ expressions:
--   = (c₀ · 𝟙) + ((c₁ · 𝟘) + (c₂ · 𝟘))
--   = c₀ via ·-identityʳ, ·-absorbʳ, +-identityˡ, +-identityʳ chains.
lookup-0-roundtrip :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₀
lookup-0-roundtrip c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟘) + (c₂ · 𝟘))) (·-identityʳ c₀)
  (cong-trans (c₀ +_) (cong (_+ (c₂ · 𝟘)) (·-absorbʳ c₁))
  (cong-trans (c₀ +_) (+-identityˡ _)
  (cong-trans (c₀ +_) (·-absorbʳ c₂)
         (+-identityʳ c₀))))

-- Helper: lookup at index 1 is c₁.
-- After reduction: = (c₀ · 𝟘) + ((c₁ · 𝟙) + (c₂ · 𝟘))
lookup-1-roundtrip :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₁ ≡ c₁
lookup-1-roundtrip c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟙) + (c₂ · 𝟘))) (·-absorbʳ c₀)
  (trans (+-identityˡ _)
  (cong-trans (_+ (c₂ · 𝟘)) (·-identityʳ c₁)
  (cong-trans (c₁ +_) (·-absorbʳ c₂)
         (+-identityʳ c₁))))

-- Helper: lookup at index 2 is c₂.
-- After reduction: = (c₀ · 𝟘) + ((c₁ · 𝟘) + (c₂ · 𝟙))
lookup-2-roundtrip :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₂ ≡ c₂
lookup-2-roundtrip c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟘) + (c₂ · 𝟙))) (·-absorbʳ c₀)
  (trans (+-identityˡ _)
  (cong-trans (_+ (c₂ · 𝟙)) (·-absorbʳ c₁)
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))

-- The round-trip itself.
selfdual-coefficients-roundtrip :
  (v : Vector 3) →
  selfdual-coefficients (vector3-to-selfdual v) ≡ v
selfdual-coefficients-roundtrip (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  cong-trans (λ x →
                x ∷
                lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₁ ∷
                lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₂ ∷ [])
             (lookup-0-roundtrip c₀ c₁ c₂)
  (cong-trans (λ x →
                 c₀ ∷ x ∷
                 lookup (vector3-to-selfdual (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₂ ∷ [])
              (lookup-1-roundtrip c₀ c₁ c₂)
              (cong (λ x → c₀ ∷ c₁ ∷ x ∷ [])
                    (lookup-2-roundtrip c₀ c₁ c₂)))
