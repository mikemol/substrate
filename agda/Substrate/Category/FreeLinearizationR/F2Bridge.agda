------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.F2Bridge
--
-- FLQ5 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Bridge: the parametric FreeLinearizationR at the F₂-LinearAlgebra
-- instance reproduces (up to record shape) the existing F₂-specific
-- Substrate.Category.FreeLinearization.
--
-- The two records have IDENTICAL field types (since F₂-LinearAlgebra
-- supplies Vector = F₂-Vector and Linear = F₂-Linear). The lift
-- functions in both directions are essentially the identity at the
-- type level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.F2Bridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.FreeLinearization
  using (FreeLinearization)
  renaming (extension to F₂-extension;
            images to F₂-images;
            extension-on-basis to F₂-extension-on-basis;
            uniqueness to F₂-uniqueness)
open import Substrate.Category.FreeLinearizationR
  using (FreeLinearizationR)
open import Substrate.Algebra.F2.AsLinearAlgebra
  using (F₂-LinearAlgebra)

------------------------------------------------------------------------
-- 1. Lift: F₂-FreeLinearization → FreeLinearizationR at F₂.
--
-- The two records have the same field types because
-- F₂-LinearAlgebra populates Vector / Linear identically.
-- ⟡set1-paydown: FreeLinearizationR now carries LinearAlgebra's R/Vector/Linear as
-- explicit params (inferred here via `_ _ _` from F₂-LinearAlgebra's type).
------------------------------------------------------------------------

F₂-to-R :
  {n m : ℕ} →
  FreeLinearization n m →
  FreeLinearizationR _ _ _ F₂-LinearAlgebra n m
F₂-to-R fl = record
  { images             = F₂-images fl
  ; extension          = F₂-extension fl
  ; extension-on-basis = F₂-extension-on-basis fl
  ; uniqueness         = F₂-uniqueness fl
  }

------------------------------------------------------------------------
-- 2. Descent: FreeLinearizationR at F₂ → F₂-FreeLinearization.
--
-- The reverse direction; same shape, identity at type level.
------------------------------------------------------------------------

R-to-F₂ :
  {n m : ℕ} →
  FreeLinearizationR _ _ _ F₂-LinearAlgebra n m →
  FreeLinearization n m
R-to-F₂ flr = record
  { images             = FreeLinearizationR.images flr
  ; extension          = FreeLinearizationR.extension flr
  ; extension-on-basis = FreeLinearizationR.extension-on-basis flr
  ; uniqueness         = FreeLinearizationR.uniqueness flr
  }

------------------------------------------------------------------------
-- 3. The round-trips: the two lifts are mutually inverse (the WITNESS the
--    "and back / essentially the identity" prose asserted but did not prove).
--
-- Both records have identical field types, so each lift just re-packages the
-- other's projections; by record-η the round-trip is the identity — refl. So
-- F₂-FreeLinearization ≅ FreeLinearizationR-at-F₂ (a genuine iso, both legs +
-- both round-trips), not "essentially" one. The lift is not ONLY one
-- direction; it is the two-sided identity.
------------------------------------------------------------------------

R-to-F₂∘F₂-to-R :
  {n m : ℕ} (fl : FreeLinearization n m) → R-to-F₂ (F₂-to-R fl) ≡ fl
R-to-F₂∘F₂-to-R fl = refl

F₂-to-R∘R-to-F₂ :
  {n m : ℕ} (flr : FreeLinearizationR _ _ _ F₂-LinearAlgebra n m) →
  F₂-to-R (R-to-F₂ flr) ≡ flr
F₂-to-R∘R-to-F₂ flr = refl

------------------------------------------------------------------------
-- 4. Capstone for FLQ5.
--
-- F₂ bridge complete and WITNESSED. The parametric FreeLinearizationR is a
-- strict generalisation: every existing F₂-FreeLinearization lifts to the
-- parametric version and back, the two legs mutually inverse (§3 — proved,
-- no longer asserted). FLQ6 supplies the ℚ instance; FLQ7 the ℚ
-- free-linearize constructor.
------------------------------------------------------------------------
