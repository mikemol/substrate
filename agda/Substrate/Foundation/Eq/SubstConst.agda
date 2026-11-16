------------------------------------------------------------------------
-- Substrate.Foundation.Eq.SubstConst
--
-- Defines: subst-const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.SubstConst where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst



-- `subst` over a CONSTANT family is the identity. Agda cannot reduce this
-- under an abstract proof, so the step must be named — and it recurs: it was
-- proved locally at OrientationRigCatSym (Σ-≡ pairing, the second component
-- transported along the first) and again at Algebra.Z.JacobianNegSemiring
-- (GradedAssocOver at a constant carrier family). Same shape, same argument
-- order (proof, value); homed here beside `subst`, level-polymorphic.
-- (⟡subst-const-home — DISCHARGED.)
subst-const : {A : Set a} {B : Set b} {x y : A} (p : x ≡ y) (v : B) →
              subst (λ _ → B) p v ≡ v
subst-const refl v = refl
