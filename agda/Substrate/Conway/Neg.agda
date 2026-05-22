------------------------------------------------------------------------
-- Substrate.Conway.Neg
--
-- S8 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Conway's surreal negation:
--
--   -⟨ L ∣ R ⟩ = ⟨ -R ∣ -L ⟩
--
-- where -R means applying negation to each element of R, then
-- swapping L and R. Recursive but birthday-preserving (the result
-- has the same SurrealFinite index as the input).
--
-- Mutual recursion with neg-Word handles the Word-level recursion;
-- Agda's syntactic termination check accepts this via the strict
-- index decrease (neg calls neg-Word on Word at lower SurrealFinite
-- index, neg-Word calls neg on element at lower index again).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Neg where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Conway.Examples using (Zero; One; NegOne)

------------------------------------------------------------------------
-- 1. Mutual negation and neg-Word.
------------------------------------------------------------------------

mutual
  -ⁿ_ : {n : ℕ} → SurrealFinite n → SurrealFinite n
  -ⁿ_ ⟨ L ∣ R ⟩ = ⟨ neg-Word R ∣ neg-Word L ⟩

  neg-Word : {m : ℕ} → Word (SurrealFinite m) → Word (SurrealFinite m)
  neg-Word []       = []
  neg-Word (s ∷ ss) = (-ⁿ s) ∷ neg-Word ss

------------------------------------------------------------------------
-- 2. Worked examples.
--
-- - Zero = ⟨ [] ∣ [] ⟩ = ⟨ -[] ∣ -[] ⟩ = ⟨ [] ∣ [] ⟩ = Zero
-- - One  = -⟨ Zero ∷ [] ∣ [] ⟩ = ⟨ -[] ∣ -(Zero ∷ []) ⟩
--                              = ⟨ [] ∣ -Zero ∷ [] ⟩
--                              = ⟨ [] ∣ Zero ∷ [] ⟩ = NegOne
------------------------------------------------------------------------

-Zero-≡-Zero : -ⁿ Zero ≡ Zero
-Zero-≡-Zero = refl

-One-≡-NegOne : -ⁿ One ≡ NegOne
-One-≡-NegOne = refl

-NegOne-≡-One : -ⁿ NegOne ≡ One
-NegOne-≡-One = refl

------------------------------------------------------------------------
-- 3. Double negation: -(-x) ≡ x.
--
-- The standard involutive property. Provable by mutual induction:
-- on the outer level, double-neg swaps L and R then swaps again
-- (back to original), and each element gets double-negated
-- (recursively back to itself).
------------------------------------------------------------------------

mutual
  -ⁿ-involutive : {n : ℕ} (s : SurrealFinite n) → -ⁿ (-ⁿ s) ≡ s
  -ⁿ-involutive ⟨ L ∣ R ⟩ =
    cong₂ ⟨_∣_⟩ (neg-Word-involutive L) (neg-Word-involutive R)
    where
      open import Substrate.Foundation.Eq using (cong₂)

  neg-Word-involutive :
    {m : ℕ} (w : Word (SurrealFinite m)) → neg-Word (neg-Word w) ≡ w
  neg-Word-involutive []       = refl
  neg-Word-involutive (s ∷ ss)
    rewrite -ⁿ-involutive s | neg-Word-involutive ss = refl

------------------------------------------------------------------------
-- 4. Capstone for S8.
--
-- Negation is defined; its involution (-(-x) ≡ x) is proven;
-- worked examples (-Zero = Zero, -One = NegOne, -NegOne = One)
-- demonstrate correctness. S9 builds integer embeddings via
-- iterated successor/negation.
------------------------------------------------------------------------
