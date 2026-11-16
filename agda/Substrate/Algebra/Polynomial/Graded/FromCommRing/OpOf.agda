------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.OpOf
--
-- Defines: opOf
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Magma
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Semigroup

module Substrate.Algebra.Polynomial.Graded.FromCommRing.OpOf {A : Set} where

open import Substrate.Algebra.Magma
open import Substrate.Algebra.Semigroup
open import Substrate.Algebra.Monoid

opOf : Monoid A → (A → A → A)
opOf M = Magma._·_ (magma (semigroup M))

