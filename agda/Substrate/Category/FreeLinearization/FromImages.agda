------------------------------------------------------------------------
-- Substrate.Category.FreeLinearization.FromImages
--
-- The canonical FreeLinearization constructor, built from the
-- substrate's existing `linear-from-images` + `apply-linear-from-
-- images-basis` + `linear-extensionality` infrastructure.
--
-- For any f : Fin n → Vector m, the FreeLinearization is:
--   extension = linear-from-images f
--   extension-on-basis = apply-linear-from-images-basis f
--   uniqueness = via linear-extensionality on the two extensions
--     (both agree on basis, hence equal pointwise).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearization.FromImages where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; trans; sym)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Category.FreeLinearization

------------------------------------------------------------------------
-- N-1: The canonical FreeLinearization constructor.
------------------------------------------------------------------------

free-linearize : {n m : ℕ} (f : Fin n → Vector m) → FreeLinearization n m
free-linearize f = record
  { images             = f
  ; extension          = linear-from-images f
  ; extension-on-basis = apply-linear-from-images-basis f
  ; uniqueness         = λ other-ext agree-on-basis v →
      linear-extensionality
        (linear-from-images f)
        other-ext
        (λ i → trans (apply-linear-from-images-basis f i)
                     (sym (agree-on-basis i)))
        v
  }

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: any Fin n → Vector m function lifts to a
-- canonical FreeLinearization via the substrate's universal-
-- property infrastructure.
--
-- The construction reuses linear-from-images (M-3.5), apply-linear-
-- from-images-basis (foundational), and linear-extensionality (the
-- universal-property pillar). The FreeLinearization record names
-- the categorical concept they collectively realize.
--
-- Substrate-wide: every use of linear-from-images IS a use of the
-- free-linearization universal property. The categorical primitive
-- makes this visible at the type level.
------------------------------------------------------------------------
