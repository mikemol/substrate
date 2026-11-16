------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Reduce.Op3
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Reduce; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Reduce.Op3 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Reduce
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Q.Properties.Reduce.Private
open import Substrate.Algebra.Q.Properties.Reduce.Op
open import Substrate.Algebra.Q.Properties.Reduce.Op2


_ : reduce (mkℚ (+ 1) 1) ≡ mkℚ (+ 1) 1
_ = refl
