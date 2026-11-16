------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.OrbitKeyToS3OfS3ToOrbitKey
--
-- Defines: orbit-key-to-s3-of-s3-to-orbit-key
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.OrbitKeyToS3OfS3ToOrbitKey where

open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.ZeroNeq1
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.TwoNeq0
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.TwoNeq1
open import Substrate.Foundation.Product
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2



orbit-key-to-s3-of-s3-to-orbit-key :
  (s : SFinP.Permutation 3) (i : Fin 3) →
  SFinA.apply (orbit-key-to-s3 (s3-to-orbit-key s)) i ≡ SFinA.apply s i
orbit-key-to-s3-of-s3-to-orbit-key s i
  with SFinA.apply s zero in p0 | SFinA.apply s ₁ in p1
... | zero | zero =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | ₁ | ₁ =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | ₂ | ₂ =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | zero | ₁       = α-even-case i
  where
    α-even-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (α-pair , even)) i ≡ SFinA.apply s i
    α-even-case zero            = sym p0
    α-even-case ₁      = sym p1
    α-even-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | ₁        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | ₂  = refl
... | zero | ₂ = α-odd-case i
  where
    α-odd-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (α-pair , odd)) i ≡ SFinA.apply s i
    α-odd-case zero            = sym p0
    α-odd-case ₁      = sym p1
    α-odd-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | ₁        = refl
    ... | ₂  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | ₁ | zero       = β-odd-case i
  where
    β-odd-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (β-pair , odd)) i ≡ SFinA.apply s i
    β-odd-case zero            = sym p0
    β-odd-case ₁      = sym p1
    β-odd-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | ₁        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | ₂  = refl
... | ₁ | ₂ = β-even-case i
  where
    β-even-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (β-pair , even)) i ≡ SFinA.apply s i
    β-even-case zero            = sym p0
    β-even-case ₁      = sym p1
    β-even-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = refl
    ... | ₁        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | ₂  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | ₂ | zero = γ-even-case i
  where
    γ-even-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (γ-pair , even)) i ≡ SFinA.apply s i
    γ-even-case zero            = sym p0
    γ-even-case ₁      = sym p1
    γ-even-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | ₁        = refl
    ... | ₂  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
... | ₂ | ₁ = γ-odd-case i
  where
    γ-odd-case : (i : Fin 3) → SFinA.apply (orbit-key-to-s3 (γ-pair , odd)) i ≡ SFinA.apply s i
    γ-odd-case zero            = sym p0
    γ-odd-case ₁      = sym p1
    γ-odd-case ₂ with SFinA.apply s ₂ in p2
    ... | zero            = refl
    ... | ₁        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | ₂  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
