------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities.IsZeroPoly
--
-- Decidable zero-polynomial predicate.
--   is-zero-poly  : the predicate (all coefficients are 𝟘).
--   is-zero-poly? : its decision procedure (Yes/No witness).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities.IsZeroPoly where

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Negation using (Dec; yes; no)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)

is-zero-poly : ∀ {n} → Polynomial n → Set
is-zero-poly []      = ⊤
is-zero-poly (𝟘 ∷ p) = is-zero-poly p
is-zero-poly (𝟙 ∷ _) = ⊥

is-zero-poly? : ∀ {n} (p : Polynomial n) → Dec (is-zero-poly p)
is-zero-poly? []      = yes tt
is-zero-poly? (𝟘 ∷ p) = is-zero-poly? p
is-zero-poly? (𝟙 ∷ _) = no λ ()
