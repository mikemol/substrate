------------------------------------------------------------------------
-- …PhaseAdvance.Z4.AsSigma — phase-advance IS σ₄ under the Fin bijection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance.Z4.AsSigma where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Coxeter.Cyclic.Base 3 as Z₄B
import Substrate.Groups.Coxeter.Cyclic.Existential 3 as Z₄E
import Substrate.Groups.Coxeter.Fin-from-Cyclic 3 as Z₄Fin
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)

phase-advance-Z₄-as-σ₄ :
  {w-p : Word Z₄B.Gen}
  (c : Z₄E.Canonical-ex w-p) →
  Z₄Fin.canonical-to-Fin-ex (Z₄E.insert-canonical-ex Z₄B.a c)
    ≡ cyclic-suc {3} (Z₄Fin.canonical-to-Fin-ex c)
phase-advance-Z₄-as-σ₄ (Z₄E.c-pos zero) = refl
phase-advance-Z₄-as-σ₄ (Z₄E.c-pos ₁)    = refl
phase-advance-Z₄-as-σ₄ (Z₄E.c-pos ₂)    = refl
phase-advance-Z₄-as-σ₄ (Z₄E.c-pos ₃)    = refl
