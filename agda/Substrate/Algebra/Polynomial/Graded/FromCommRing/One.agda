------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.One
--
-- Defines: 𝟙
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.CommutativeRing.Record
open import Substrate.Algebra.Monoid

module Substrate.Algebra.Polynomial.Graded.FromCommRing.One {A : Set} (CR : CommutativeRing A) where

open import Substrate.Algebra.Monoid

open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesM CR
𝟙 : A
𝟙 = ε *M
