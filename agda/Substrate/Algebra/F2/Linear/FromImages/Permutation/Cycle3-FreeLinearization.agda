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
-- Ⓖ.cyclen-collapse-registry: σ₃ was the Cycle3 orbit-module's thin alias for
-- cyclic-suc {2}; that module is dissolved, so use the generator directly.
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)
open import Substrate.Category.FreeLinearization using (FreeLinearization)
open import Substrate.Category.FreeLinearization.FromImages using (free-linearize)

------------------------------------------------------------------------
-- The images function for cycle3-Linear: basis ∘ (the 3-cycle σ₃ = cyclic-suc {2}).
------------------------------------------------------------------------

cycle3-images : Fin 3 → Vector 3
cycle3-images i = basis (cyclic-suc {2} i)

------------------------------------------------------------------------
-- cycle3-Linear IS the FreeLinearization at cycle3-images.
------------------------------------------------------------------------

Cycle3-FreeLin : FreeLinearization 3 3
Cycle3-FreeLin = free-linearize cycle3-images
