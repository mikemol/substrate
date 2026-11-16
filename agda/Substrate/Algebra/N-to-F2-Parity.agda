------------------------------------------------------------------------
-- Substrate.Algebra.N-to-F2-Parity
--
-- The parity homomorphism ℕ → F₂ (mod-2).
--
-- For each n : ℕ, parity n ∈ F₂ is 𝟘 if n is even, 𝟙 if n is odd.
-- Defined as `parity 0 = 𝟘; parity (suc n) = 𝟙 ℕ+ parity n` so that
-- the parity flips with each successor.
--
-- The key property: parity IS a CommutativeMonoid homomorphism
-- (ℕ, ℕ+, 0) → (F₂, ℕ+, 𝟘). The substrate uses this to convert
-- length-based ℕ-gradings into F₂-parity-gradings.
--
-- Used by: V₄-as-F₂-graded (slice 15), where the chirality element
-- = parity of length in the Coxeter word representation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.N-to-F2-Parity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
  renaming (+-assoc to +F-assoc)
open import Substrate.Algebra.F2.PlusF
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

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
--   parity (a ℕ+ b) ≡ parity a ℕ+ parity b
--
-- Proof by induction on a:
--   a = 0:    parity (0 ℕ+ b) = parity b = 𝟘 ℕ+ parity b
--                            = parity 0 ℕ+ parity b ✓
--   a = suc a': parity (suc a' ℕ+ b) = parity (suc (a' ℕ+ b))
--                                   = 𝟙 ℕ+ parity (a' ℕ+ b)
--                                   ≡ 𝟙 ℕ+ (parity a' ℕ+ parity b)  [IH]
--                                   ≡ (𝟙 ℕ+ parity a') ℕ+ parity b  [+F-assoc]
--                                   = parity (suc a') ℕ+ parity b ✓
------------------------------------------------------------------------

parity-+ : (a b : ℕ) → parity (a ℕ+ b) ≡ parity a +F parity b
parity-+ zero    b = refl
parity-+ (suc a) b =
  trans (cong (𝟙 +F_) (parity-+ a b))
        (sym (+F-assoc 𝟙 (parity a) (parity b)))
  where
    open import Substrate.Foundation.Eq.Sym
    open import Substrate.Foundation.Eq.Trans

------------------------------------------------------------------------
-- N-4: Capstone — parity homomorphism lands.
--
-- After this slice, parity : ℕ → F₂ is the canonical
-- CommutativeMonoid homomorphism for converting ℕ-graded structures
-- into F₂-graded ones. The substrate uses this for parity-grading
-- of word lengths (V₄, Coxeter instances).
------------------------------------------------------------------------
