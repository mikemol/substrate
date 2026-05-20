------------------------------------------------------------------------
-- Substrate.Category.JordanAlgebra.UnderlyingCNAA
--
-- O9 of the O-arc. Forgetful functor Jordan → CNAA (every Jordan
-- algebra is commutative non-associative; drop the Jordan-identity
-- field).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.JordanAlgebra.UnderlyingCNAA
  {ℓOJ ℓMJ ℓOC ℓMC : Level}
  (JordanCat : CategoryOf {ℓOJ} {ℓMJ})
  (CNAA-Cat : CategoryOf {ℓOC} {ℓMC})
  (Jordan→CNAA : Functor JordanCat CNAA-Cat)
  where

Jordan-UnderlyingCNAA-Functor : Functor JordanCat CNAA-Cat
Jordan-UnderlyingCNAA-Functor = Jordan→CNAA
