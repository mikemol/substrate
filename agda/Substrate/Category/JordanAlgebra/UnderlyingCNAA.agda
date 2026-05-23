------------------------------------------------------------------------
-- Substrate.Category.JordanAlgebra.UnderlyingCNAA
--
-- O9 of the O-arc. Forgetful functor Jordan → CNAA (every Jordan
-- algebra is commutative non-associative; drop the Jordan-identity
-- field).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.JordanAlgebra.UnderlyingCNAA
  {ℓOJ ℓMJ ℓOC ℓMC : Level}
  (JordanCat : CategoryOf {ℓOJ} {ℓMJ})
  (CNAA-Cat : CategoryOf {ℓOC} {ℓMC})
  (Jordan→CNAA : Functor JordanCat CNAA-Cat)
  where

open import Substrate.Category.Functor.AsNamed
  JordanCat CNAA-Cat Jordan→CNAA public
  renaming (named-Functor to Jordan-UnderlyingCNAA-Functor)