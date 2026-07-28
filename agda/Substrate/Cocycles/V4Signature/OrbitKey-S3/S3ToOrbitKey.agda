------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
--
-- s3-to-orbit-key : SFinP.Permutation 3 → OrbitKey.
-- Classifies a permutation by its action on positions 0 and 1.
-- Factored through `s3-to-orbit-key-from` so with-cases unfold under
-- proof-level `with SFinA.apply ... in eq`.
--
-- s3-to-orbit-key-cong : only inspects apply at zero / suc zero, so
-- pointwise equality at those two indices suffices for propositional
-- congruence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; cong₂)
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.Chirality.Type using (even; odd)
open import Substrate.Cocycles.V4Signature.OrbitKey.Type using (OrbitKey)
open import Substrate.Cocycles.V4Signature.Pairing.Type using (α-pair; β-pair; γ-pair)

s3-to-orbit-key-from : Fin 3 → Fin 3 → OrbitKey
s3-to-orbit-key-from zero            ₁       = α-pair , even
s3-to-orbit-key-from zero            ₂ = α-pair , odd
s3-to-orbit-key-from ₁       ₂ = β-pair , even
s3-to-orbit-key-from ₁       zero            = β-pair , odd
s3-to-orbit-key-from ₂ zero            = γ-pair , even
s3-to-orbit-key-from ₂ ₁       = γ-pair , odd
s3-to-orbit-key-from _                _                = α-pair , even
                                                       -- impossible default

s3-to-orbit-key : SFinP.Permutation 3 → OrbitKey
s3-to-orbit-key s =
  s3-to-orbit-key-from (SFinA.apply s zero) (SFinA.apply s ₁)

s3-to-orbit-key-cong :
  ∀ (s₁ s₂ : SFinP.Permutation 3) →
  SFinA.apply s₁ zero ≡ SFinA.apply s₂ zero →
  SFinA.apply s₁ ₁ ≡ SFinA.apply s₂ ₁ →
  s3-to-orbit-key s₁ ≡ s3-to-orbit-key s₂
s3-to-orbit-key-cong s₁ s₂ eq0 eq1 =
  cong₂ s3-to-orbit-key-from eq0 eq1
