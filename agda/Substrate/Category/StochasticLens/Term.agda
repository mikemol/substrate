------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Term (T4)
--
-- Term-algebra encoding of stochastic lenses — routed THROUGH the witness
-- tower's FREE graded tower of combined generators.
--
-- The flat form was `data LensGen/LensTerm : LensTriple → LensTriple → Set₁`
-- over `LensTriple = Set × Set × Set` (Set₁), a hand-rolled free category over
-- a Set₁ object type. A lens term is a COMBINATION OF GENERATORS (content-free
-- lens moves), and the tower's free such structure is `LehmerPath n ≅ Perm n`;
-- the (state, view, obs) object indices were syntactic scaffolding and dissolve.
-- So (⟡term-algebra-via-witness-tower):
--
--   LensTerm n   = LehmerPath n          -- the free tower of combined generators
--   []ₗ / _++ₗ_  = start / _⊕_           -- combine; grade adds
--   lens-product = ⊕-over                -- the GradedProductOver (graded stencil)
--
-- Semantics (eval) is in .Eval; the monoid laws are in .Category. Set₀
-- throughout; the Set₁ data families are gone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Term where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The lens term carrier: the free graded tower of combined generators.
LensTerm : ℕ → Set
LensTerm = LehmerPath

-- The empty term and composition (combine two generator-towers; the grade adds).
[]ₗ : LensTerm 0
[]ₗ = start

_++ₗ_ : {m n : ℕ} → LensTerm m → LensTerm n → LensTerm (m + n)
_++ₗ_ = _⊕_

infixr 4 _++ₗ_

-- The graded product on terms IS the tower's ⊕-over : GradedProductOver.
lens-product : GradedProductOver _+_ 0 LensTerm
lens-product = ⊕-over
