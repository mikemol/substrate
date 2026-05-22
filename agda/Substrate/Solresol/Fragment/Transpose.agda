------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.Transpose
--
-- transpose-1 : Note → Note (the Z/7 cyclic shift).
-- transpose-7 : the 7-fold composition.
-- transpose-7-id : 7-fold composition is identity — the Z/7 cyclic-
-- order witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.Transpose where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Solresol.Fragment.Note
  using (Note; do₁; re₁; mi₁; fa₁; sol; la₁; si₁)

transpose-1 : Note → Note
transpose-1 do₁ = re₁
transpose-1 re₁ = mi₁
transpose-1 mi₁ = fa₁
transpose-1 fa₁ = sol
transpose-1 sol = la₁
transpose-1 la₁ = si₁
transpose-1 si₁ = do₁

transpose-7 : Note → Note
transpose-7 n =
  transpose-1 (transpose-1 (transpose-1 (transpose-1
    (transpose-1 (transpose-1 (transpose-1 n))))))

transpose-7-id : (n : Note) → transpose-7 n ≡ n
transpose-7-id do₁ = refl
transpose-7-id re₁ = refl
transpose-7-id mi₁ = refl
transpose-7-id fa₁ = refl
transpose-7-id sol = refl
transpose-7-id la₁ = refl
transpose-7-id si₁ = refl
