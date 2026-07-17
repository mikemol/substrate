------------------------------------------------------------------------
-- Substrate.Category.Coalgebra-of-Comonad
--
-- R4 of the R-arc. S-coalgebra: pair (A, β : A → S(A)) satisfying
-- counit + comultiplication compatibility (dual of R3).
--
-- Per the skeleton-as-pullback principle: Algebra/Coalgebra is a
-- 1:2 cone (duality witness). The witness is the Opposite primitive.
-- A Comonad on C is exactly a Monad on (Opposite C); a coalgebra of
-- that comonad is exactly an algebra of the monad on (Opposite C):
--
--   CoalgebraOfComonad C W
--     ≡ AlgebraOfMonad (Opposite C) W
--     ≡ { A : Obj (Opposite C) ; α : Mor (Opposite C) (T A) A }
--     ≡ { A : Obj C            ; α : Mor C A (T A) }
--
-- The field traditionally called β (the coalgebra structure map) is
-- α projected through Opposite — same data, dual typing.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra-of-Comonad where

open import Substrate.Foundation.Level using (Level; _⊔_)

open import Substrate.Category.Algebra-of-Monad using (AlgebraOfMonad)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Comonad using (Comonad)
open import Substrate.Category.Opposite using (Opposite)

CoalgebraOfComonad :
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (C : CategoryOf Obj Mor)
  (W : Comonad C) → Set (ℓO ⊔ ℓM)
CoalgebraOfComonad C W = AlgebraOfMonad (Opposite C) W
