------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.DecB
--
-- Defines: _≟B_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.DecB where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



-- the two circumstances are TOTAL: the law is DECIDABLE at every (p, σ), so
-- holds ⊎ ¬holds is exhaustive by construction — no quantified negative needed.
_≟B_ : (a b : Bool) → Dec (a ≡ b)
true  ≟B true  = yes refl
true  ≟B false = no (λ ())
false ≟B true  = no (λ ())
false ≟B false = yes refl
