------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.DetSign
--
-- THE MORPHISM-SIDE ℤ/2 (user, 2026-06-13: "This whole thing is derived from an
-- arrow category. I don't accept interfaces that don't equally admit objects and
-- morphisms as inputs. So you need both… take a look at how the traces are built;
-- they're CF, a continually evolving ℤ/2 of numerator/denominator addressing.").
--
-- I had located the torsor only on the OBJECT side (CF representations of a value)
-- and wrongly said the morphism side was pinned. The morphism side's ℤ/2 was
-- already PROVED in B2 (`Trace.Properties`), I just hadn't named it: the convergent
-- neighbour DETERMINANT is the continually-evolving ℤ/2.
--
--   • It is ℤ/2-VALUED: `det²≡1` — the determinant of every convergent state
--     squares to +1, so it lives in {+1, −1} ≅ ℤ/2.
--   • The Euclidean STEP acts by the ℤ/2 generator: `det-flip` — one CF step
--     NEGATES the determinant (×−1).
--   • That generator IS the numerator/denominator SWAP: `⊖-swap-neg`
--     (b ⊖ a ≡ −(a ⊖ b)). The CF step (a,b) ↦ (b, a mod b) swaps which position is
--     primary; the convergent matrix [[aₙ,1],[1,0]] has det −1 — the swap.
--
-- So the trace (a MORPHISM of the arrow category) carries a ℤ/2 cochain evolving by
-- the swap at each step. Paired with the OBJECT-side ℤ/2 (the CF-representation
-- flip [a₀;…;n] ↔ [a₀;…;n−1,1] on a value's representations), the arrow-category
-- interface admits BOTH, as it must. This module names the morphism side; the
-- object side is the CF-representation gauge (a sibling cocycle to V4Signature.CY5).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.DetSign where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq  using (_≡_; refl)

open import Substrate.Algebra.Z       using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Add   using (_⊖_)
open import Substrate.Algebra.Z.Mul   using (_*ℤ_)

open import Substrate.Algebra.R.Trace using (RealTrace)
open import Substrate.Algebra.R.Trace.Properties
  using (det4; det-after; det-flip; det²≡1; ⊖-swap-neg)

------------------------------------------------------------------------
-- The gauge group is ℤ/2: its nontrivial generator is negation, an involution.
------------------------------------------------------------------------

sign-flip-invol : (x : ℤ) → -ℤ (-ℤ x) ≡ x
sign-flip-invol (+ zero)    = refl
sign-flip-invol (+ (suc n)) = refl
sign-flip-invol (-suc n)    = refl

------------------------------------------------------------------------
-- The determinant is ℤ/2-valued (det² ≡ +1 ⟹ it lives in {+1, −1}).
------------------------------------------------------------------------

det-is-ℤ/2-valued : (n : ℕ) (r : RealTrace) →
  det-after n 1 0 0 1 r *ℤ det-after n 1 0 0 1 r ≡ + 1
det-is-ℤ/2-valued = det²≡1

------------------------------------------------------------------------
-- The per-step ℤ/2 ACTION: one CF step negates the determinant (the trace is a
-- ℤ/2 cochain evolving by ×−1 each step).
------------------------------------------------------------------------

step-acts-by-flip : (a p₁ q₁ p₀ q₀ : ℕ) →
  det4 (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁ ≡ -ℤ (det4 p₁ q₁ p₀ q₀)
step-acts-by-flip = det-flip

------------------------------------------------------------------------
-- The generator IS the numerator/denominator swap.
------------------------------------------------------------------------

swap-is-generator : (a b : ℕ) → (b ⊖ a) ≡ -ℤ (a ⊖ b)
swap-is-generator = ⊖-swap-neg
