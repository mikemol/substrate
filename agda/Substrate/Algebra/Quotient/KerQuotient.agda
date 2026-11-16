------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.KerQuotient
--
-- Defines: ker-Quotient
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.KerQuotient where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



-- Every map's kernel is an equivalence (≡ is, and KerRel just pulls it back).
ker-Quotient : {a b : Level} {A : Set a} {B : Set b}
             → (F : A → B) → Quotient A (KerRel F)
ker-Quotient F = record { ≈-refl = λ _ → refl ; ≈-sym = sym ; ≈-trans = trans }
