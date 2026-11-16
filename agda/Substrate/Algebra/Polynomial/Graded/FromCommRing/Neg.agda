------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.Neg
--
-- Defines: neg
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.AbelianGroup
open import Substrate.Algebra.CommutativeRing.Record
open import Substrate.Algebra.Group
open import Substrate.Algebra.Ring

module Substrate.Algebra.Polynomial.Graded.FromCommRing.Neg {A : Set} (CR : CommutativeRing A) where

open import Substrate.Algebra.Group
open import Substrate.Algebra.AbelianGroup
open import Substrate.Algebra.Ring

open import Substrate.Algebra.Polynomial.Graded.FromCommRing.R CR
neg : A → A
neg = inv (group (+-abelian R))
