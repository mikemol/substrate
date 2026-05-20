------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar-FreeLinearization
--
-- Hodge ★ at dim 4 packaged as a FreeLinearization 6 6 instance.
--
-- The Hodge ★ on Bivectors (= Vector 6) is defined as
-- `linear-from-images hodge-star-images` where
-- `hodge-star-images i = basis (complement i)`. This IS the
-- FreeLinearization universal property's extension: any function
-- f : Fin 6 → Vector 6 extends to a unique linear map; for f =
-- hodge-star-images, the extension IS hodge-star.
--
-- Per [[project-freelinearization-names-linear-from-images]]: this
-- is a worked example of the FreeLinearization primitive at a
-- substrate site (Hodge ★ at dim 4).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.HodgeStar-FreeLinearization where

open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star-images)
open import Substrate.Category.FreeLinearization using (FreeLinearization)
open import Substrate.Category.FreeLinearization.FromImages using (free-linearize)

------------------------------------------------------------------------
-- Hodge ★ at dim 4 IS the FreeLinearization at hodge-star-images.
------------------------------------------------------------------------

HodgeStar-FreeLin : FreeLinearization 6 6
HodgeStar-FreeLin = free-linearize hodge-star-images
