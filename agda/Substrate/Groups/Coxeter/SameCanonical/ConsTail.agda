------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SameCanonical.ConsTail
--
-- Defines: ∷-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.SameCanonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.SameCanonical.ConsTail where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.SameCanonical.Private


∷-tail : {Gen : Set} {x y : Gen} {xs ys : Word Gen} →
         (x ∷ xs) ≡ (y ∷ ys) → xs ≡ ys
∷-tail refl = refl
