------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder.Iterate
--
-- iterate-commutes : iterating the Singer linear map k times tracks
--   singer^k on the Fano Point,
--   iterate k (apply singer-Linear) (point-to-vec p)
--     ≡ point-to-vec (singer^ k p)
-- by induction on k, threading singer-commutes through point-to-vec.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder.Iterate where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.FanoPlane using (Point; point-to-vec; singer; singer-Linear)
open import Substrate.Category.Coalgebra.FiniteOrder using (iterate)
open import Substrate.Algebra.GL3F2.SingerOrder.Commutes using (singer-commutes)

-- k-fold singer on Points.
singer^ : ℕ → Point → Point
singer^ zero    p = p
singer^ (suc k) p = singer (singer^ k p)

iterate-commutes : (k : ℕ) (p : Point) →
  iterate k (apply singer-Linear) (point-to-vec p)
    ≡ point-to-vec (singer^ k p)
iterate-commutes zero    p = refl
iterate-commutes (suc k) p =
  trans (cong (apply singer-Linear) (iterate-commutes k p))
        (singer-commutes (singer^ k p))
