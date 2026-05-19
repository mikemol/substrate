------------------------------------------------------------------------
-- Substrate.Algebra.N-to-F2-Parity
--
-- The parity homomorphism ℕ → F₂ (mod-2).
--
-- For each n : ℕ, parity n ∈ F₂ is 𝟘 if n is even, 𝟙 if n is odd.
-- Defined as `parity 0 = 𝟘; parity (suc n) = 𝟙 + parity n` so that
-- the parity flips with each successor.
--
-- The key property: parity IS a CommutativeMonoid homomorphism
-- (ℕ, +, 0) → (F₂, +, 𝟘). The substrate uses this to convert
-- length-based ℕ-gradings into F₂-parity-gradings.
--
-- Used by: V₄-as-F₂-graded (slice 15), where the chirality element
-- = parity of length in the Coxeter word representation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.N-to-F2-Parity where

open import Data.Nat using (ℕ; zero; suc; _+_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong)

open import Substrate.Algebra.F2
  using (F₂; 𝟘; 𝟙)
  renaming (_+_ to _+F_; +-assoc to +F-assoc; +-identityˡ to +F-identityˡ)

------------------------------------------------------------------------
-- N-1: parity — the ℕ → F₂ map.
------------------------------------------------------------------------

parity : ℕ → F₂
parity zero    = 𝟘
parity (suc n) = 𝟙 +F parity n

------------------------------------------------------------------------
-- N-2: parity preserves zero.
------------------------------------------------------------------------

parity-zero : parity 0 ≡ 𝟘
parity-zero = refl

------------------------------------------------------------------------
-- N-3: parity is additive (monoid homomorphism).
--
--   parity (a + b) ≡ parity a + parity b
--
-- Proof by induction on a:
--   a = 0:    parity (0 + b) = parity b = 𝟘 + parity b
--                            = parity 0 + parity b ✓
--   a = suc a': parity (suc a' + b) = parity (suc (a' + b))
--                                   = 𝟙 + parity (a' + b)
--                                   ≡ 𝟙 + (parity a' + parity b)  [IH]
--                                   ≡ (𝟙 + parity a') + parity b  [+F-assoc]
--                                   = parity (suc a') + parity b ✓
------------------------------------------------------------------------

parity-+ : (a b : ℕ) → parity (a + b) ≡ parity a +F parity b
parity-+ zero    b = refl
parity-+ (suc a) b =
  trans (cong (𝟙 +F_) (parity-+ a b))
        (sym (+F-assoc 𝟙 (parity a) (parity b)))
  where
    open import Relation.Binary.PropositionalEquality using (trans; sym)

------------------------------------------------------------------------
-- N-4: Capstone — parity homomorphism lands.
--
-- After this slice, parity : ℕ → F₂ is the canonical
-- CommutativeMonoid homomorphism for converting ℕ-graded structures
-- into F₂-graded ones. The substrate uses this for parity-grading
-- of word lengths (V₄, Coxeter instances).
------------------------------------------------------------------------
