------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus
--
-- Defines: _+_
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.CommutativeRing.Record

module Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus {A : Set} (CR : CommutativeRing A) where


open import Substrate.Algebra.Polynomial.Graded.FromCommRing.OpOf
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusM CR
_+_ : A → A → A
_+_ = opOf +M
