------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives
--
-- Companion to ReservedBridge.agda. Formalizes alternative Vector 3 ↔
-- SelfDual bijections from the gauge-freedom space.
--
-- The canonical bijection (`vector3-to-selfdual` in ReservedBridge.agda)
-- is ONE of 168 F₂-linear bijections; this file formalizes two more
-- to partially populate the gauge-freedom coset.
--
-- Per memory `project_reserved_selfdual_bijection_gauge`:
--
--   * F₂-linear bijections SelfDual ↔ Vector 3: |GL(3, F₂)| = 168
--   * Basis-permutation subgroup: |S₃| = 6
--   * The 3 "axes of alignment" themselves instantiate F₂² Klein four /
--     F₂³ at the meta-level (fractal recurrence of the 3+1 parity
--     universal pattern).
--
-- Alternatives in this file:
--   * **Alt A — cyclic shift** (3-cycle on generators):
--       (c₀, c₁, c₂) ↦ c₀ *ₛ sd-pair-02-13 + c₁ *ₛ sd-pair-03-12 + c₂ *ₛ sd-pair-01-23
--   * **Alt B — last-two transposition** (swap c₁ and c₂ targets):
--       (c₀, c₁, c₂) ↦ c₀ *ₛ sd-pair-01-23 + c₁ *ₛ sd-pair-03-12 + c₂ *ₛ sd-pair-02-13
--
-- Both are F₂-linear (live in the 168-coset) and pass the same kind
-- of round-trip proofs as the canonical. None is privileged at the
-- F₂-linear level; the catalog's choice (if any) is a separate
-- gauge-fixing question that lives at the meta-level (the F₂³/S₃
-- "axes of alignment" structure).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives where

open import Data.Fin using (zero; suc)
open import Data.Vec using ([]; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar
open import Substrate.Algebra.F2.HodgeDim4.SelfDual

------------------------------------------------------------------------
-- Alternative A — Cyclic-shifted bijection.
--
-- Permutes the 3 sd-pair generators in a 3-cycle:
--   c₀ ↦ sd-pair-02-13   (canonical maps c₀ ↦ sd-pair-01-23)
--   c₁ ↦ sd-pair-03-12
--   c₂ ↦ sd-pair-01-23
------------------------------------------------------------------------

vector3-to-selfdual-cyclic : Vector 3 → Bivector
vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  (c₀ *ₛ sd-pair-02-13) +ⱽ
  ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-01-23))

vector3-to-selfdual-cyclic-sd :
  (v : Vector 3) → SelfDual-Pred (vector3-to-selfdual-cyclic v)
vector3-to-selfdual-cyclic-sd (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  sd-closed-+ⱽ
    (c₀ *ₛ sd-pair-02-13)
    ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-01-23))
    (sd-closed-*ₛ c₀ sd-pair-02-13 sd-pair-02-13-self-dual)
    (sd-closed-+ⱽ
      (c₁ *ₛ sd-pair-03-12)
      (c₂ *ₛ sd-pair-01-23)
      (sd-closed-*ₛ c₁ sd-pair-03-12 sd-pair-03-12-self-dual)
      (sd-closed-*ₛ c₂ sd-pair-01-23 sd-pair-01-23-self-dual))

-- Inverse extraction: matches the permuted assignment.
-- The cyclic bivector at coordinates (c₀, c₁, c₂) has explicit form
-- (c₂, c₀, c₁, c₁, c₀, c₂) (vs canonical (c₀, c₁, c₂, c₂, c₁, c₀)).
-- So extract: c₀ from lookup 1, c₁ from lookup 2, c₂ from lookup 0.

selfdual-coefficients-cyclic : Bivector → Vector 3
selfdual-coefficients-cyclic ω =
  lookup ω (suc zero) ∷ lookup ω (suc (suc zero)) ∷ lookup ω zero ∷ []

-- Lookup helpers (same F₂ chain shape as the canonical bridge).
lookup-1-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ≡ c₀
lookup-1-cyclic c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟙) + ((c₁ · 𝟘) + (c₂ · 𝟘))
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟘))) (·-identityʳ c₀))
  (trans (cong (c₀ +_) (cong (_+ (c₂ · 𝟘)) (·-absorbʳ c₁)))
  (trans (cong (c₀ +_) (+-identityˡ _))
  (trans (cong (c₀ +_) (·-absorbʳ c₂))
         (+-identityʳ c₀))))

lookup-2-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ≡ c₁
lookup-2-cyclic c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟘) + ((c₁ · 𝟙) + (c₂ · 𝟘))
  trans (cong (_+ ((c₁ · 𝟙) + (c₂ · 𝟘))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟘)) (·-identityʳ c₁))
  (trans (cong (c₁ +_) (·-absorbʳ c₂))
         (+-identityʳ c₁))))

lookup-0-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₂
lookup-0-cyclic c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟘) + ((c₁ · 𝟘) + (c₂ · 𝟙))
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟙))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟙)) (·-absorbʳ c₁))
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))

selfdual-coefficients-cyclic-roundtrip :
  (v : Vector 3) →
  selfdual-coefficients-cyclic (vector3-to-selfdual-cyclic v) ≡ v
selfdual-coefficients-cyclic-roundtrip (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  trans (cong (λ x →
                x ∷
                lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ∷
                lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ∷ [])
              (lookup-1-cyclic c₀ c₁ c₂))
  (trans (cong (λ x →
                 c₀ ∷ x ∷
                 lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ∷ [])
               (lookup-2-cyclic c₀ c₁ c₂))
         (cong (λ x → c₀ ∷ c₁ ∷ x ∷ [])
               (lookup-0-cyclic c₀ c₁ c₂)))

------------------------------------------------------------------------
-- Alternative B — Last-two transposition bijection.
--
-- Swaps the targets of c₁ and c₂ relative to the canonical:
--   c₀ ↦ sd-pair-01-23   (same as canonical)
--   c₁ ↦ sd-pair-03-12   (canonical maps c₁ ↦ sd-pair-02-13)
--   c₂ ↦ sd-pair-02-13   (canonical maps c₂ ↦ sd-pair-03-12)
------------------------------------------------------------------------

vector3-to-selfdual-swap : Vector 3 → Bivector
vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  (c₀ *ₛ sd-pair-01-23) +ⱽ
  ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-02-13))

vector3-to-selfdual-swap-sd :
  (v : Vector 3) → SelfDual-Pred (vector3-to-selfdual-swap v)
vector3-to-selfdual-swap-sd (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  sd-closed-+ⱽ
    (c₀ *ₛ sd-pair-01-23)
    ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-02-13))
    (sd-closed-*ₛ c₀ sd-pair-01-23 sd-pair-01-23-self-dual)
    (sd-closed-+ⱽ
      (c₁ *ₛ sd-pair-03-12)
      (c₂ *ₛ sd-pair-02-13)
      (sd-closed-*ₛ c₁ sd-pair-03-12 sd-pair-03-12-self-dual)
      (sd-closed-*ₛ c₂ sd-pair-02-13 sd-pair-02-13-self-dual))

-- The swap bivector at (c₀, c₁, c₂) has explicit form
-- (c₀, c₂, c₁, c₁, c₂, c₀) (vs canonical (c₀, c₁, c₂, c₂, c₁, c₀)).
-- So extract: c₀ from lookup 0, c₁ from lookup 2, c₂ from lookup 1.

selfdual-coefficients-swap : Bivector → Vector 3
selfdual-coefficients-swap ω =
  lookup ω zero ∷ lookup ω (suc (suc zero)) ∷ lookup ω (suc zero) ∷ []

lookup-0-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₀
lookup-0-swap c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟙) + ((c₁ · 𝟘) + (c₂ · 𝟘))
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟘))) (·-identityʳ c₀))
  (trans (cong (c₀ +_) (cong (_+ (c₂ · 𝟘)) (·-absorbʳ c₁)))
  (trans (cong (c₀ +_) (+-identityˡ _))
  (trans (cong (c₀ +_) (·-absorbʳ c₂))
         (+-identityʳ c₀))))

lookup-2-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ≡ c₁
lookup-2-swap c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟘) + ((c₁ · 𝟙) + (c₂ · 𝟘))
  trans (cong (_+ ((c₁ · 𝟙) + (c₂ · 𝟘))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟘)) (·-identityʳ c₁))
  (trans (cong (c₁ +_) (·-absorbʳ c₂))
         (+-identityʳ c₁))))

lookup-1-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ≡ c₂
lookup-1-swap c₀ c₁ c₂ =
  -- LHS reduces to (c₀ · 𝟘) + ((c₁ · 𝟘) + (c₂ · 𝟙))
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟙))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟙)) (·-absorbʳ c₁))
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))

selfdual-coefficients-swap-roundtrip :
  (v : Vector 3) →
  selfdual-coefficients-swap (vector3-to-selfdual-swap v) ≡ v
selfdual-coefficients-swap-roundtrip (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  trans (cong (λ x →
                x ∷
                lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ∷
                lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ∷ [])
              (lookup-0-swap c₀ c₁ c₂))
  (trans (cong (λ x →
                 c₀ ∷ x ∷
                 lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ∷ [])
               (lookup-2-swap c₀ c₁ c₂))
         (cong (λ x → c₀ ∷ c₁ ∷ x ∷ [])
               (lookup-1-swap c₀ c₁ c₂)))

------------------------------------------------------------------------
-- Status (documentation).
--
-- Three of the 168 F₂-linear Vector 3 ↔ SelfDual bijections now
-- formalised:
--
--   1. Canonical (ReservedBridge.agda): identity permutation
--   2. Cyclic shift (this file, Alt A): 3-cycle on generators
--   3. Last-two swap (this file, Alt B): transposition on generators
--
-- These three are S₃-related (3 of the 6 basis-permutation
-- bijections; the other 3 are reachable via composition). The
-- remaining 162 F₂-linear bijections involve non-permutation linear
-- changes-of-basis (e.g., one coordinate mapped to a sum of
-- generators); none are formalised yet.
--
-- See memory `project_reserved_selfdual_bijection_gauge` for the
-- full gauge-freedom analysis and the fractal-recurrence observation
-- (the alignment-axis space itself instantiates 3+1 parity).
------------------------------------------------------------------------
