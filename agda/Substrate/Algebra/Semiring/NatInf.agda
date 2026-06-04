------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.NatInf
--
-- The ∞-extended naturals ℕ∞ = ℕ ⊎ {∞}, carrier of the TROPICAL
-- (min-plus) semiring.
--
-- This is the "cost / placement gauge" of the semiring-VM layer
-- (conjecture #6, scratch/commuting_sphere.md): a single tensor over
-- the tropical semiring computes shortest-path / minimum-cost
-- placement, with
--   *  ADD = min          (ε = ∞   : the most-expensive / unreachable)
--   *  MUL = +            (ε = fin 0: free composition)
--
-- The carrier needs the ∞ point because min has no identity inside ℕ
-- alone — ∞ supplies it.
--
-- DEF/PROOF SPLIT: this module declares `data ℕ∞`, so by the separation
-- policy it must import NO *.Properties module. The laws that need the ℕ
-- addition properties (⊕-assoc, ⊕-identityʳ, ⊕-distribʳ-⊓) therefore live
-- in the sibling Substrate.Algebra.Semiring.NatInf.Properties; the laws
-- here are the ones provable by refl/cong alone. Nothing is postulated.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.NatInf where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)

------------------------------------------------------------------------
-- 1. The ∞-extended carrier.
------------------------------------------------------------------------

data ℕ∞ : Set where
  fin : ℕ → ℕ∞
  ∞   : ℕ∞

------------------------------------------------------------------------
-- 2. minℕ — min on the unextended naturals, with its (cong-only) laws.
------------------------------------------------------------------------

minℕ : ℕ → ℕ → ℕ
minℕ zero    _       = zero
minℕ (suc _) zero    = zero
minℕ (suc a) (suc b) = suc (minℕ a b)

minℕ-assoc : (a b c : ℕ) → minℕ (minℕ a b) c ≡ minℕ a (minℕ b c)
minℕ-assoc zero    _       _       = refl
minℕ-assoc (suc _) zero    _       = refl
minℕ-assoc (suc _) (suc _) zero    = refl
minℕ-assoc (suc a) (suc b) (suc c) = cong suc (minℕ-assoc a b c)

-- Addition distributes over min on ℕ:  a + min b c ≡ min (a+b) (a+c).
+-distribˡ-minℕ : (a b c : ℕ) → a + minℕ b c ≡ minℕ (a + b) (a + c)
+-distribˡ-minℕ zero    _ _ = refl
+-distribˡ-minℕ (suc a) b c = cong suc (+-distribˡ-minℕ a b c)

------------------------------------------------------------------------
-- 3. The additive operation: min on ℕ∞ (ε = ∞). Left-pivoted on ∞.
------------------------------------------------------------------------

_⊓_ : ℕ∞ → ℕ∞ → ℕ∞
∞     ⊓ y     = y
fin a ⊓ ∞     = fin a
fin a ⊓ fin b = fin (minℕ a b)

⊓-assoc : (x y z : ℕ∞) → (x ⊓ y) ⊓ z ≡ x ⊓ (y ⊓ z)
⊓-assoc ∞       _       _       = refl
⊓-assoc (fin _) ∞       _       = refl
⊓-assoc (fin _) (fin _) ∞       = refl
⊓-assoc (fin a) (fin b) (fin c) = cong fin (minℕ-assoc a b c)

⊓-identityˡ : (x : ℕ∞) → ∞ ⊓ x ≡ x
⊓-identityˡ _ = refl

⊓-identityʳ : (x : ℕ∞) → x ⊓ ∞ ≡ x
⊓-identityʳ (fin _) = refl
⊓-identityʳ ∞       = refl

------------------------------------------------------------------------
-- 4. The multiplicative operation: ∞-extended addition (ε = fin 0).
--    Left-pivoted on ∞ (∞ ⊕ y = ∞) so the additive-zero absorbs left.
------------------------------------------------------------------------

_⊕_ : ℕ∞ → ℕ∞ → ℕ∞
∞     ⊕ _     = ∞
fin _ ⊕ ∞     = ∞
fin a ⊕ fin b = fin (a + b)

⊕-identityˡ : (x : ℕ∞) → fin zero ⊕ x ≡ x
⊕-identityˡ (fin _) = refl   -- fin (0 + b) = fin b  (0 + b is definitional)
⊕-identityˡ ∞       = refl

------------------------------------------------------------------------
-- 5. Distributivity of ⊕ over ⊓ (left) and ∞-absorption — refl/cong only.
--    (⊕-distribʳ-⊓ needs +-comm, so it lives in NatInf.Properties.)
------------------------------------------------------------------------

⊕-distribˡ-⊓ : (a b c : ℕ∞) → a ⊕ (b ⊓ c) ≡ (a ⊕ b) ⊓ (a ⊕ c)
⊕-distribˡ-⊓ ∞       _       _       = refl
⊕-distribˡ-⊓ (fin _) ∞       _       = refl
⊕-distribˡ-⊓ (fin _) (fin _) ∞       = refl
⊕-distribˡ-⊓ (fin a) (fin b) (fin c) = cong fin (+-distribˡ-minℕ a b c)

⊕-absorbˡ : (a : ℕ∞) → ∞ ⊕ a ≡ ∞
⊕-absorbˡ _ = refl

⊕-absorbʳ : (a : ℕ∞) → a ⊕ ∞ ≡ ∞
⊕-absorbʳ (fin _) = refl
⊕-absorbʳ ∞       = refl
