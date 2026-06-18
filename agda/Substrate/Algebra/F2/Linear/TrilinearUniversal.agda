------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.TrilinearUniversal
--
-- The arity-3 rung of the multilinear extensionality ladder (ⁿ̌) — the
-- INDUCTIVE STEP made concrete. A trilinear map is determined by its values
-- on basis TRIPLES, proved by peeling the first slot with the arity-1
-- `linear-extensionality` and discharging the remaining two slots with the
-- arity-2 `bilinear-extensionality` (= β̌, the induction hypothesis).
--
-- This is the "generator of generators" recursion at n = 3:
--   n-linear-extensionality  =  linear-extensionality (slot 1)
--                               ∘ (n-1)-linear-extensionality (rest).
-- Each leg of a Trilinear, with the other slots fixed, IS an arity-(<3) map
-- (its leg-laws ARE the lower record's fields), so the lower rungs apply
-- directly. The generic Multilinear fold over a Vec of arities (routing the
-- codomain through Algebra.Module so the legs land in a module, not just
-- Vector) is the next brick; this rung confirms the recursion mechanism.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.TrilinearUniversal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.BilinearFromImages
  using ( Bilinear; apply₂′
        ; preserves-+ₗ; preserves-*ₛₗ; preserves-+ᵣ; preserves-*ₛᵣ )
open import Substrate.Algebra.F2.Linear.BilinearUniversal using (bilinear-extensionality)

------------------------------------------------------------------------
-- A trilinear map: linear in each of its three arguments (6 leg-laws).
------------------------------------------------------------------------

record Trilinear (k l p n : ℕ) : Set where
  field
    ap₃ : Vector k → Vector l → Vector p → Vector n
    -- slot 1 (left)
    +₁ : (u u' : Vector k) (v : Vector l) (w : Vector p) →
         ap₃ (u +ⱽ u') v w ≡ (ap₃ u v w +ⱽ ap₃ u' v w)
    *₁ : (c : F₂) (u : Vector k) (v : Vector l) (w : Vector p) →
         ap₃ (c *ₛ u) v w ≡ (c *ₛ ap₃ u v w)
    -- slot 2 (middle)
    +₂ : (u : Vector k) (v v' : Vector l) (w : Vector p) →
         ap₃ u (v +ⱽ v') w ≡ (ap₃ u v w +ⱽ ap₃ u v' w)
    *₂ : (c : F₂) (u : Vector k) (v : Vector l) (w : Vector p) →
         ap₃ u (c *ₛ v) w ≡ (c *ₛ ap₃ u v w)
    -- slot 3 (right)
    +₃ : (u : Vector k) (v : Vector l) (w w' : Vector p) →
         ap₃ u v (w +ⱽ w') ≡ (ap₃ u v w +ⱽ ap₃ u v w')
    *₃ : (c : F₂) (u : Vector k) (v : Vector l) (w : Vector p) →
         ap₃ u v (c *ₛ w) ≡ (c *ₛ ap₃ u v w)

open Trilinear public

------------------------------------------------------------------------
-- The legs: fix all-but-one slot ⟹ a lower-arity map (codomain stays Vector).
------------------------------------------------------------------------

-- slot 1, with v, w fixed: u ↦ T u v w is an arity-1 Linear map.
leg₁ : ∀ {k l p n} → Trilinear k l p n → Vector l → Vector p → Linear k n
leg₁ T v w = record
  { apply        = λ u → ap₃ T u v w
  ; preserves-+  = λ u u' → +₁ T u u' v w
  ; preserves-*ₛ = λ c u → *₁ T c u v w
  }

-- slots 2,3, with u fixed: (v, w) ↦ T u v w is an arity-2 Bilinear map.
leg₂₃ : ∀ {k l p n} → Trilinear k l p n → Vector k → Bilinear l p n
leg₂₃ T u = record
  { apply₂′       = λ v w → ap₃ T u v w
  ; preserves-+ₗ  = λ v v' w → +₂ T u v v' w
  ; preserves-*ₛₗ = λ c v w → *₂ T c u v w
  ; preserves-+ᵣ  = λ v w w' → +₃ T u v w w'
  ; preserves-*ₛᵣ = λ c v w → *₃ T c u v w
  }

------------------------------------------------------------------------
-- Trilinear extensionality: agreement on all basis TRIPLES ⟹ agreement
-- everywhere. (linear-extensionality on slot 1; bilinear-extensionality,
-- per fixed basis vector in slot 1, on slots 2,3.)
------------------------------------------------------------------------

trilinear-extensionality :
  ∀ {k l p n} (T T' : Trilinear k l p n) →
  ((i : Fin k) (j : Fin l) (h : Fin p) →
     ap₃ T (basis i) (basis j) (basis h) ≡ ap₃ T' (basis i) (basis j) (basis h)) →
  (u : Vector k) (v : Vector l) (w : Vector p) → ap₃ T u v w ≡ ap₃ T' u v w
trilinear-extensionality T T' agree u v w =
  linear-extensionality (leg₁ T v w) (leg₁ T' v w)
    (λ i → bilinear-extensionality (leg₂₃ T (basis i)) (leg₂₃ T' (basis i)) (agree i) v w)
    u
