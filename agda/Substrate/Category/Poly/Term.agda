------------------------------------------------------------------------
-- Substrate.Category.Poly.Term (T7)
--
-- Term-algebra encoding of polynomial-functor morphisms — routed THROUGH the
-- witness tower's FREE graded tower of combined generators.
--
-- The flat form was `data PolyGen/PolyTerm : Poly → Poly → Set₁` (a hand-rolled
-- free category over the Set₁ object type `Poly`). A poly term is a COMBINATION
-- OF GENERATORS (content-free poly-moves), and the tower's free such structure
-- is `LehmerPath n ≅ Perm n`; the `Poly` object indices were syntactic
-- scaffolding and dissolve. So (⟡term-algebra-via-witness-tower):
--
--   PolyTerm n   = LehmerPath n          -- the free tower of combined generators
--   []ₚ / _++ₚ_  = start / _⊕_           -- combine; grade adds
--   poly-product = ⊕-over                -- the GradedProductOver (graded stencil)
--
-- Semantics (eval) is in .Eval; the monoid laws are in .Category. Set₀
-- throughout; the Set₁ data families are gone. (The `Poly` record itself — the
-- object type — is unchanged; only the term-algebra is dissolved.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Term where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The poly term carrier: the free graded tower of combined generators.
PolyTerm : ℕ → Set
PolyTerm = LehmerPath

-- The empty term and composition (combine two generator-towers; the grade adds).
[]ₚ : PolyTerm 0
[]ₚ = start

_++ₚ_ : {m n : ℕ} → PolyTerm m → PolyTerm n → PolyTerm (m + n)
_++ₚ_ = _⊕_

infixr 4 _++ₚ_

-- The graded product on terms IS the tower's ⊕-over : GradedProductOver.
poly-product : GradedProductOver _+_ 0 PolyTerm
poly-product = ⊕-over
