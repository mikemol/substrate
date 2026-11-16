------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.GenDec
--
-- Defines: gen-≟
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Negation.Dec

module Substrate.Groups.Coxeter.Cyclic.Base.GenDec where

open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

-- Decidable equality on Gen. Identical across every Z_n-Coxeter
-- instance because Gen is the single-generator type; previously
-- re-declared verbatim in Z2/Z3/Z4/Z5/Z7-Coxeter.
gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl
