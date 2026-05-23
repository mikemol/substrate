------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
--
-- s3-to-orbit-key : SFin.Permutation 3 → OrbitKey.
-- Classifies a permutation by its action on positions 0 and 1.
-- Factored through `s3-to-orbit-key-from` so with-cases unfold under
-- proof-level `with SFin.apply ... in eq`.
--
-- s3-to-orbit-key-cong : only inspects apply at zero / suc zero, so
-- pointwise equality at those two indices suffices for propositional
-- congruence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; cong₂)
import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature
  using (α-pair; β-pair; γ-pair; even; odd; OrbitKey)

s3-to-orbit-key-from : Fin 3 → Fin 3 → OrbitKey
s3-to-orbit-key-from zero            ₁       = α-pair , even
s3-to-orbit-key-from zero            ₂ = α-pair , odd
s3-to-orbit-key-from ₁       ₂ = β-pair , even
s3-to-orbit-key-from ₁       zero            = β-pair , odd
s3-to-orbit-key-from ₂ zero            = γ-pair , even
s3-to-orbit-key-from ₂ ₁       = γ-pair , odd
s3-to-orbit-key-from _                _                = α-pair , even
                                                       -- impossible default

s3-to-orbit-key : SFin.Permutation 3 → OrbitKey
s3-to-orbit-key s =
  s3-to-orbit-key-from (SFin.apply s zero) (SFin.apply s ₁)

s3-to-orbit-key-cong :
  ∀ (s₁ s₂ : SFin.Permutation 3) →
  SFin.apply s₁ zero ≡ SFin.apply s₂ zero →
  SFin.apply s₁ ₁ ≡ SFin.apply s₂ ₁ →
  s3-to-orbit-key s₁ ≡ s3-to-orbit-key s₂
s3-to-orbit-key-cong s₁ s₂ eq0 eq1 =
  cong₂ s3-to-orbit-key-from eq0 eq1
