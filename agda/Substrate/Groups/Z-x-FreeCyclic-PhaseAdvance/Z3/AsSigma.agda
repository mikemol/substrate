------------------------------------------------------------------------
-- …PhaseAdvance.Z3.AsSigma — phase-advance IS σ₃ under the Fin bijection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance.Z3.AsSigma where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Fin-from-Cyclic 2 as Z₃Fin
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)

phase-advance-Z₃-as-σ₃ :
  {w-p : Word Z₃B.Gen}
  (c : Z₃E.Canonical-ex w-p) →
  Z₃Fin.canonical-to-Fin-ex (Z₃E.insert-canonical-ex Z₃B.a c)
    ≡ cyclic-suc {2} (Z₃Fin.canonical-to-Fin-ex c)
phase-advance-Z₃-as-σ₃ (Z₃E.c-pos zero) = refl
phase-advance-Z₃-as-σ₃ (Z₃E.c-pos ₁)    = refl
phase-advance-Z₃-as-σ₃ (Z₃E.c-pos ₂)    = refl
