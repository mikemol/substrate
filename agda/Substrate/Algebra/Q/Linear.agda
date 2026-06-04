------------------------------------------------------------------------
-- Substrate.Algebra.Q.Linear
--
-- Q9 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- ℚ-linear maps between fixed-length ℚ-vector spaces. Sister
-- structure to Substrate.Algebra.F2.Linear — same shape, ℚ
-- entries instead of F₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Linear where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Function using (id; _∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; trans)

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Vector using (Vector; _+ℚⱽ_; _*ℚₛ_)

------------------------------------------------------------------------
-- 1. ℚ-linear map: record bundling apply + linearity proofs.
------------------------------------------------------------------------

record Linear (n m : ℕ) : Set where      -- ⟦shape:f21965c7 apply,(u v,(c⟧
  field
    apply         : Vector n → Vector m
    preserves-+   :
      (u v : Vector n) → apply (u +ℚⱽ v) ≡ apply u +ℚⱽ apply v
    preserves-*ₛ  :
      (c : ℚ) (v : Vector n) → apply (c *ℚₛ v) ≡ c *ℚₛ apply v

open Linear public

------------------------------------------------------------------------
-- 2. Identity linear map.
------------------------------------------------------------------------

id-LQ : ∀ {n} → Linear n n
id-LQ = record
  { apply        = id
  ; preserves-+  = λ _ _ → refl
  ; preserves-*ₛ = λ _ _ → refl
  }

------------------------------------------------------------------------
-- 3. Composition.
--
-- Composing two ℚ-linear maps yields a ℚ-linear map.
------------------------------------------------------------------------

compose-LQ :
  ∀ {n m k} →
  Linear m k → Linear n m → Linear n k
compose-LQ {n} {m} {k} g f = record
  { apply        = λ v → apply g (apply f v)
  ; preserves-+  = λ u v →
      trans (cong (apply g) (preserves-+ f u v))
            (preserves-+ g (apply f u) (apply f v))
  ; preserves-*ₛ = λ c v →
      trans (cong (apply g) (preserves-*ₛ f c v))
            (preserves-*ₛ g c (apply f v))
  }

------------------------------------------------------------------------
-- 4. Capstone for Q9.
--
-- ℚ-Linear with identity + composition. Q10 caps the arc with
-- re-exports + a future-FreeLinearization-over-ℚ note.
------------------------------------------------------------------------
