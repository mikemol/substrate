------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusSwapMid
--
-- Defines: +-swap-mid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusSwapMid where

open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst



+-swap-mid : (a b c : F₂) → ((a +F b) +F c) ≡ ((a +F c) +F b)
+-swap-mid a b c =
  trans (+-assoc a b c) (trans (cong (a +F_) (+-comm b c)) (sym (+-assoc a c b)))
