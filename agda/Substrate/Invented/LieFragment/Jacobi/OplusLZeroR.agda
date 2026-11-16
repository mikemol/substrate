------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi.OplusLZeroR
--
-- Defines: ⊕L-zeroʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.Jacobi; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi.OplusLZeroR where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.Jacobi.LieAlgExpr
open import Substrate.Invented.LieFragment.Jacobi.ApproxL



------------------------------------------------------------------------
-- 5. Right-identity of ⊕L (derived).
--
-- a ⊕L zero-L ≈L a, from ⊕L-comm + ⊕L-zeroˡ.
------------------------------------------------------------------------

⊕L-zeroʳ : (a : LieAlgExpr) → a ⊕L zero-L ≈L a
⊕L-zeroʳ a = trans-L (⊕L-comm a zero-L) (⊕L-zeroˡ a)

------------------------------------------------------------------------
-- 6. Capstone.
--
-- LieAlgExpr + _≈L_ is the substrate-native realisation of the Lie
-- equational quotient over the C7 generators. D3 + D4 jointly
-- close the "fuller Lie treatment" deferred at C7's capstone.
--
-- Future arc: connect to Substrate.Category.LieAlgebra (which
-- provides the abstract Lie-algebra record). The connection would
-- be a functor LieAlgExpr/≈L → LieAlgebra-instance, demonstrating
-- the substrate's general Lie primitive subsumes the LieFragment.
------------------------------------------------------------------------
