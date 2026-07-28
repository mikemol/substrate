------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Fires
--
-- NON-VACUITY: the decision actually FIRES on closed inputs, which forces
-- `_≟ˢ_` (and the whole EEA/shape-interning stack under it) to COMPUTE.
--
-- ⟡cap-128-forcing: this file is the elaboration cost of the whole Decidable
-- cluster — the two `refl`s below evaluate the interned shape keys.  It is a
-- SIBLING rather than a tail of Decide.agda precisely so that cost is its own
-- elaboration unit and the definitions stay cheap.
--
--   2/4 ≈ℚ 1/2 ⟹ YES;  1/2 ≈ℚ 1/3 ⟹ NO (the reduced shape keys differ).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Fires where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Algebra.Z using (+_)
open import Substrate.Algebra.Q using (mkℚ)
open import Substrate.Algebra.Q.Properties.Decidable.Key
open import Substrate.Algebra.Q.Properties.Decidable.Decide

isYes : {A : Set} → Dec A → Bool
isYes (yes _) = true
isYes (no  _) = false

opaque
  unfolding q-key

  _ : isYes ((mkℚ (+ 2) 3) ≈ℚ? (mkℚ (+ 1) 1)) ≡ true
  _ = refl

  _ : isYes ((mkℚ (+ 1) 1) ≈ℚ? (mkℚ (+ 1) 2)) ≡ false
  _ = refl
