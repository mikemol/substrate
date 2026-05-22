------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3-FreeLinearization
--
-- The cycle3-Linear (= basis-permutation-Linear σ₃) packaged as a
-- FreeLinearization 3 3 instance.
--
-- σ₃'s linear lift IS the FreeLinearization at the basis-permutation
-- images function (basis ∘ σ₃). This works for any basis-permutation-
-- Linear; cycle3 is the worked example.
--
-- Per [[project-freelinearization-names-linear-from-images]]: second
-- worked example at a substrate site (cyclic basis-permutation).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3-FreeLinearization where

open import Substrate.Foundation.Fin using (Fin)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3 using (σ₃)
open import Substrate.Category.FreeLinearization using (FreeLinearization)
open import Substrate.Category.FreeLinearization.FromImages using (free-linearize)

------------------------------------------------------------------------
-- The images function for cycle3-Linear: basis ∘ σ₃.
------------------------------------------------------------------------

cycle3-images : Fin 3 → Vector 3
cycle3-images i = basis (σ₃ i)

------------------------------------------------------------------------
-- cycle3-Linear IS the FreeLinearization at cycle3-images.
------------------------------------------------------------------------

Cycle3-FreeLin : FreeLinearization 3 3
Cycle3-FreeLin = free-linearize cycle3-images
