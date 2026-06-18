------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Cancel
--
-- ℕ cancellation lemmas: left-addend cancellation and right-multiplication
-- cancellation by a positive factor. Needed for cross-multiplication
-- transitivity (the ℚ equivalence `_≈ℚ_`).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Cancel where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

-- Ⓓ: suc-injective is Foundation.Nat's (it was re-proved here identically);
-- re-exported with `public` so this module's existing consumers (which import
-- suc-injective FROM Cancel) are unaffected. +-cancelˡ below uses it.
open import Substrate.Foundation.Nat using (suc-injective) public

-- cancel a left addend.
+-cancelˡ : (k : ℕ) {m n : ℕ} → (k + m) ≡ (k + n) → m ≡ n
+-cancelˡ zero    eq = eq
+-cancelˡ (suc k) eq = +-cancelˡ k (suc-injective eq)

-- cancel a positive right multiplier (suc d ≥ 1).
*-cancelʳ-suc : (m n d : ℕ) → (m * suc d) ≡ (n * suc d) → m ≡ n
*-cancelʳ-suc zero    zero    d eq = refl
*-cancelʳ-suc zero    (suc n) d ()
*-cancelʳ-suc (suc m) zero    d ()
*-cancelʳ-suc (suc m) (suc n) d eq =
  cong suc (*-cancelʳ-suc m n d (+-cancelˡ (suc d) eq))
