------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
--
-- sfin-apply-inj : SFin.apply is injective. Derived from invₐ + inv-l.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
import Substrate.Groups.SFin as SFin

sfin-apply-inj :
  (s : SFin.Permutation 3) {i j : Fin 3} →
  SFin.apply s i ≡ SFin.apply s j → i ≡ j
sfin-apply-inj s {i} {j} eq =
  trans (sym (SFin.inv-l s i)) (trans (cong (SFin.invₐ s) eq) (SFin.inv-l s j))
