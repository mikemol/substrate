------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.NatInf.Properties
--
-- The tropical-semiring laws on ℕ∞ that depend on the ℕ ADDITION
-- properties (Foundation.Nat.Properties.Add): the multiplicative ⊕'s
-- associativity and right identity, and the right-distributivity of ⊕
-- over ⊓. These are split out of NatInf so that NatInf — which declares
-- `data ℕ∞` — imports no proof module (the def/proof separation policy).
--
-- Nothing is postulated; each is the corresponding ℕ fact lifted through
-- `fin`, with the absorbing/∞ cases by refl.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.NatInf.Properties where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans)
open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-assoc; +-identityʳ; +-comm)
open import Substrate.Algebra.Semiring.NatInf
  using (ℕ∞; fin; ∞; minℕ; +-distribˡ-minℕ; _⊓_; _⊕_)

------------------------------------------------------------------------
-- ⊕ associativity and right identity (need +-assoc / +-identityʳ).
------------------------------------------------------------------------

⊕-assoc : (x y z : ℕ∞) → (x ⊕ y) ⊕ z ≡ x ⊕ (y ⊕ z)
⊕-assoc ∞       _       _       = refl
⊕-assoc (fin _) ∞       _       = refl
⊕-assoc (fin _) (fin _) ∞       = refl
⊕-assoc (fin a) (fin b) (fin c) = cong fin (+-assoc a b c)

⊕-identityʳ : (x : ℕ∞) → x ⊕ fin 0 ≡ x
⊕-identityʳ (fin a) = cong fin (+-identityʳ a)
⊕-identityʳ ∞       = refl

------------------------------------------------------------------------
-- Right-distributivity of ⊕ over ⊓ (needs +-comm to conjugate the
-- left version proved in NatInf).
------------------------------------------------------------------------

⊕-distribʳ-⊓ : (a b c : ℕ∞) → (a ⊓ b) ⊕ c ≡ (a ⊕ c) ⊓ (b ⊕ c)
⊕-distribʳ-⊓ ∞       _       _       = refl
⊕-distribʳ-⊓ (fin _) ∞       ∞       = refl
⊕-distribʳ-⊓ (fin _) ∞       (fin _) = refl
⊕-distribʳ-⊓ (fin _) (fin _) ∞       = refl
⊕-distribʳ-⊓ (fin a) (fin b) (fin c) = cong fin (right-distrib a b c)
  where
    -- minℕ a b + c ≡ minℕ (a+c) (b+c): the left distribution conjugated
    -- by commutativity.
    right-distrib : (a b c : ℕ) → minℕ a b + c ≡ minℕ (a + c) (b + c)
    right-distrib a b c =
      trans (+-comm (minℕ a b) c)
            (trans (+-distribˡ-minℕ c a b)
                   (cong₂ minℕ (+-comm c a) (+-comm c b)))
