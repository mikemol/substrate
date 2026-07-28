------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip
--
-- orbit-key-to-s3-of-s3-to-orbit-key :
--   ∀ s i → SFinA.apply (orbit-key-to-s3 (s3-to-orbit-key s)) i ≡ SFinA.apply s i.
-- The SFin-side round-trip (pointwise). 27-leaf case analysis:
-- outer trichotomy on apply s 0, middle on apply s 1, inner on apply
-- s 2. 21 leaves die by sfin-apply-inj; 6 leaves close by refl/sym.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip where

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; _≢_; refl; sym; trans)
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.Chirality.Type using (even; odd)
open import Substrate.Cocycles.V4Signature.Pairing.Type using (α-pair; β-pair; γ-pair)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
  using (orbit-key-to-s3)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
  using (s3-to-orbit-key)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
  using (sfin-apply-inj)

-- Fin 3 inequality witnesses for impossible-case discharge.
private
  0≢1 : _≢_ {A = Fin 3} zero ₁
  0≢1 ()
  2≢0 : _≢_ {A = Fin 3} ₂ zero
  2≢0 ()
  2≢1 : _≢_ {A = Fin 3} ₂ ₁
  2≢1 ()

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
