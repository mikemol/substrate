------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
--
-- sfin-apply-inj : SFinA.apply is injective. Derived from invₐ + inv-l.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj where

open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

sfin-apply-inj :
  (s : SFinP.Permutation 3) {i j : Fin 3} →
  SFinA.apply s i ≡ SFinA.apply s j → i ≡ j
sfin-apply-inj s {i} {j} eq =
  trans (sym (SFinA.inv-l s i)) (trans (cong (SFinA.invₐ s) eq) (SFinA.inv-l s j))
