------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Action
--
-- The bridge between Z5-Coxeter's `insert a` and σ₅ via Z5-Coxeter-Fin.
--
-- Mirror of Z3-Coxeter-Action at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Action where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Z5-Coxeter-Fin using (canonical-to-Fin)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
  using (σ₅)

action-of-a-is-σ₅ :
  {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  canonical-to-Fin (Z₅.insert-canonical Z₅.a c) ≡ σ₅ (canonical-to-Fin c)
action-of-a-is-σ₅ Z₅.c-ε    = refl
action-of-a-is-σ₅ Z₅.c-a    = refl
action-of-a-is-σ₅ Z₅.c-aa   = refl
action-of-a-is-σ₅ Z₅.c-aaa  = refl
action-of-a-is-σ₅ Z₅.c-aaaa = refl
