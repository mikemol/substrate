------------------------------------------------------------------------
-- Substrate.Category.CascadedCoalgebra.Term (T15)
--
-- Term-algebra encoding of cascaded-coalgebra morphisms — routed THROUGH the
-- witness tower's FREE graded tower of combined generators.
--
-- The flat form was `data CascadeGen/CascadeTerm : CascadeState → CascadeState
-- → Set₁` over `CascadeState = Set × Set` (Set₁), a hand-rolled free category
-- over a Set₁ object type. A cascade term is a COMBINATION OF GENERATORS (each
-- cascade layer), and the tower's free such structure is `LehmerPath n ≅ Perm n`.
-- So (⟡term-algebra-via-witness-tower):
--
--   CascadeTerm n  = LehmerPath n        -- the free tower of combined generators
--   []ᶜᶜ / _++ᶜᶜ_  = start / _⊕_         -- combine; grade adds
--   cascade-product = ⊕-over             -- the GradedProductOver (graded stencil)
--   cascade-eval   = fold                -- the UNIQUE interpreter (each layer's step)
--   cascade-eval-unique = fold-unique    -- its universal property
--
-- Set₀ throughout; the Set₁ data families are gone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CascadedCoalgebra.Term where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The cascade term carrier: the free graded tower of combined generators.
CascadeTerm : ℕ → Set
CascadeTerm = LehmerPath

-- The empty term and composition (combine two generator-towers; the grade adds).
[]ᶜᶜ : CascadeTerm 0
[]ᶜᶜ = start

_++ᶜᶜ_ : {m n : ℕ} → CascadeTerm m → CascadeTerm n → CascadeTerm (m + n)
_++ᶜᶜ_ = _⊕_

infixr 4 _++ᶜᶜ_

-- The graded product on terms IS the tower's ⊕-over : GradedProductOver.
cascade-product : GradedProductOver _+_ 0 CascadeTerm
cascade-product = ⊕-over

-- The semantics is the UNIQUE fold into any LehmerAlgebra target: base = the
-- initial cascade state, step = apply one cascade layer.
cascade-eval : {C : ℕ → Set} → LehmerAlgebra C → {n : ℕ} → CascadeTerm n → C n
cascade-eval = fold

-- The universal property: any interpreter respecting (base, step) IS cascade-eval.
cascade-eval-unique :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (g : {n : ℕ} → CascadeTerm n → C n) →
  (g start ≡ LehmerAlgebra.base alg) →
  (∀ {n} (l : CascadeTerm n) (p : Fin (suc n)) → g (l ◂ p) ≡ LehmerAlgebra.step alg (g l) p) →
  ∀ {n} (l : CascadeTerm n) → g l ≡ cascade-eval alg l
cascade-eval-unique = fold-unique
