{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.HornerSeam
--
-- The MULTIPLY-LEVEL cap of the field/GF256 seam.  `GF256.Bridge` proves the
-- reduce-level half (reduce-eq, *P-eq) below `Mul`; this caps it with the byte
-- multiply, which needs `gmul` (Mul) and `_*Q_` (Quotient):
--
--   *Q-is-gmul : a *Q b ≡ gmul a b
--
-- i.e. the field's multiply (SubBytes) and GF256's (MixColumns) are ONE
-- operation.  `a *Q b = reduce-mod-f (a *Pg b)` and `gmul a b = reduce-mod-m
-- (a *P b)`, so the seam is `*P-eq` then `reduce-eq`.  Fully --safe, zero
-- postulates, structural.
------------------------------------------------------------------------
module Substrate.Algebra.F2.GF256.HornerSeam where

open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base using (m-lo)
open import Substrate.Algebra.F2.Polynomial using (_*P_)
open import Substrate.Algebra.F2.GF256.Mul using (gmul)
open import Substrate.Algebra.F2.GF256.Bridge using (reduce-eq; *P-eq)
import Substrate.Algebra.Polynomial.Graded.Mod as Mod
import Substrate.Algebra.Polynomial.Graded.Quotient as Quot
open Mod.Over F₂-CommRing 7 m-lo using (reduce-mod-f)
open Quot.Over F₂-CommRing 7 m-lo using (_*Q_)

-- ★★ THE SEAM CLOSED: the field's multiply (SubBytes) IS GF256's (MixColumns).
*Q-is-gmul : (a b : Vector 8) → a *Q b ≡ gmul a b
*Q-is-gmul a b = trans (cong reduce-mod-f (*P-eq a b)) (reduce-eq (a *P b))
