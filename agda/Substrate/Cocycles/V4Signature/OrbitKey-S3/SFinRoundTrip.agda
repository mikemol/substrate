------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip
--
-- orbit-key-to-s3-of-s3-to-orbit-key :
--   ∀ s i → SFin.apply (orbit-key-to-s3 (s3-to-orbit-key s)) i ≡ SFin.apply s i.
-- The SFin-side round-trip (pointwise). 27-leaf case analysis:
-- outer trichotomy on apply s 0, middle on apply s 1, inner on apply
-- s 2. 21 leaves die by sfin-apply-inj; 6 leaves close by refl/sym.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip where

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; _≢_; refl; sym; trans)
import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature
  using (α-pair; β-pair; γ-pair; even; odd)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
  using (orbit-key-to-s3)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
  using (s3-to-orbit-key)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
  using (sfin-apply-inj)

-- Fin 3 inequality witnesses for impossible-case discharge.
private
  0≢1 : _≢_ {A = Fin 3} zero (suc zero)
  0≢1 ()
  2≢0 : _≢_ {A = Fin 3} (suc (suc zero)) zero
  2≢0 ()
  2≢1 : _≢_ {A = Fin 3} (suc (suc zero)) (suc zero)
  2≢1 ()

orbit-key-to-s3-of-s3-to-orbit-key :
  (s : SFin.Permutation 3) (i : Fin 3) →
  SFin.apply (orbit-key-to-s3 (s3-to-orbit-key s)) i ≡ SFin.apply s i
orbit-key-to-s3-of-s3-to-orbit-key s i
  with SFin.apply s zero in p0 | SFin.apply s (suc zero) in p1
... | zero | zero =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | suc zero | suc zero =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | suc (suc zero) | suc (suc zero) =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | zero | suc zero       = α-even-case i
  where
    α-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (α-pair , even)) i ≡ SFin.apply s i
    α-even-case zero            = sym p0
    α-even-case (suc zero)      = sym p1
    α-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc zero        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc (suc zero)  = refl
... | zero | suc (suc zero) = α-odd-case i
  where
    α-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (α-pair , odd)) i ≡ SFin.apply s i
    α-odd-case zero            = sym p0
    α-odd-case (suc zero)      = sym p1
    α-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc zero        = refl
    ... | suc (suc zero)  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | suc zero | zero       = β-odd-case i
  where
    β-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (β-pair , odd)) i ≡ SFin.apply s i
    β-odd-case zero            = sym p0
    β-odd-case (suc zero)      = sym p1
    β-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc zero        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc (suc zero)  = refl
... | suc zero | suc (suc zero) = β-even-case i
  where
    β-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (β-pair , even)) i ≡ SFin.apply s i
    β-even-case zero            = sym p0
    β-even-case (suc zero)      = sym p1
    β-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = refl
    ... | suc zero        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc (suc zero)  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | suc (suc zero) | zero = γ-even-case i
  where
    γ-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (γ-pair , even)) i ≡ SFin.apply s i
    γ-even-case zero            = sym p0
    γ-even-case (suc zero)      = sym p1
    γ-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc zero        = refl
    ... | suc (suc zero)  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
... | suc (suc zero) | suc zero = γ-odd-case i
  where
    γ-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (γ-pair , odd)) i ≡ SFin.apply s i
    γ-odd-case zero            = sym p0
    γ-odd-case (suc zero)      = sym p1
    γ-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = refl
    ... | suc zero        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc (suc zero)  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
