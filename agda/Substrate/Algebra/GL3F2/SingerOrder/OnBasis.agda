------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder.OnBasis
--
-- order-on-basis : iterate 7 (apply singer-Linear) (basis i) ≡ basis i
-- for each basis index i : Fin 3.
--
-- The three basis vectors ARE the basis Fano Points (e₁,e₂,e₃ = basis
-- 0,1,2); order-7 on them follows from the Point 7-cycle singer⁷-id via
-- iterate-commutes. No dense reduction — this is the combinatorics of
-- the 7-cycle, not a matrix power.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder.OnBasis where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.FanoPlane
  using (Point; e₁; e₂; e₃; point-to-vec; singer⁷; singer⁷-id; singer-Linear)
open import Substrate.Category.Coalgebra.FiniteOrder using (iterate)
open import Substrate.Algebra.GL3F2.SingerOrder.Iterate
  using (singer^; iterate-commutes)

basis-point : Fin 3 → Point
basis-point zero          = e₁
basis-point (suc zero)    = e₂
basis-point (suc (suc _)) = e₃

basis≡point-to-vec : (i : Fin 3) → basis i ≡ point-to-vec (basis-point i)
basis≡point-to-vec zero             = refl
basis≡point-to-vec (suc zero)       = refl
basis≡point-to-vec (suc (suc zero)) = refl
basis≡point-to-vec (suc (suc (suc ())))

-- singer^ 7 ≡ singer⁷ pointwise (both are 7-fold singer); bridges the
-- Iterate module's singer^ to FanoPlane's singer⁷-id.
singer^7≡singer⁷ : (p : Point) → singer^ 7 p ≡ singer⁷ p
singer^7≡singer⁷ p = refl

order-on-basis : (i : Fin 3) →
  iterate 7 (apply singer-Linear) (basis i) ≡ basis i
order-on-basis i =
  trans (cong (iterate 7 (apply singer-Linear)) (basis≡point-to-vec i))
  (trans (iterate-commutes 7 (basis-point i))
  (trans (cong point-to-vec
            (trans (singer^7≡singer⁷ (basis-point i))
                   (singer⁷-id (basis-point i))))
         (sym (basis≡point-to-vec i))))
