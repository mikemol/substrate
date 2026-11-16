------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseR
--
-- Defines: +-inverseʳ
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.CommutativeRing.Record
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Trans

module Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseR {A : Set} (CR : CommutativeRing A) where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Trans

open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Neg CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusComm CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseL CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Zero CR
+-inverseʳ : (a : A) → a + neg a ≡ 𝟘
+-inverseʳ a = trans (+-comm a (neg a)) (+-inverseˡ a)

