------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Term (T19)
--
-- Term-algebra encoding of DFT morphisms — routed THROUGH the witness tower's
-- FREE graded tower of combined generators.
--
-- The flat form was `data DFTGen/DFTTerm : DFTContext → DFTContext → Set₁`
-- over `DFTContext = Set × Set` (Set₁), a hand-rolled free category over a Set₁
-- object type. A DFT term is a COMBINATION OF GENERATORS (forward/inverse/lift),
-- and the tower's free such structure is `LehmerPath n ≅ Perm n` — which
-- additionally supplies the INVERTIBILITY the DFT forward/inverse pair wants (a
-- free cons-list had none). So (⟡term-algebra-via-witness-tower):
--
--   DFTTerm n    = LehmerPath n          -- the free tower of combined generators
--   []ᶠ / _++ᶠ_  = start / _⊕_           -- combine; grade adds
--   dft-product  = ⊕-over                -- the GradedProductOver (graded stencil)
--   dft-eval     = fold                  -- the UNIQUE interpreter (forward/inverse
--                                           as the target LehmerAlgebra's step)
--   dft-eval-unique = fold-unique        -- its universal property
--
-- Set₀ throughout; the Set₁ data families are gone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Term where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The DFT term carrier: the free graded tower of combined generators.
DFTTerm : ℕ → Set
DFTTerm = LehmerPath

-- The empty term and composition (combine two generator-towers; the grade adds).
[]ᶠ : DFTTerm 0
[]ᶠ = start

_++ᶠ_ : {m n : ℕ} → DFTTerm m → DFTTerm n → DFTTerm (m + n)
_++ᶠ_ = _⊕_

infixr 4 _++ᶠ_

-- The graded product on terms IS the tower's ⊕-over : GradedProductOver.
dft-product : GradedProductOver _+_ 0 DFTTerm
dft-product = ⊕-over

-- The semantics is the UNIQUE fold into any LehmerAlgebra target: base = the
-- identity transform, step = apply one DFT generator (forward / inverse / lift).
dft-eval : {C : ℕ → Set} → LehmerAlgebra C → {n : ℕ} → DFTTerm n → C n
dft-eval = fold

-- The universal property: any interpreter respecting (base, step) IS dft-eval.
dft-eval-unique :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (g : {n : ℕ} → DFTTerm n → C n) →
  (g start ≡ LehmerAlgebra.base alg) →
  (∀ {n} (l : DFTTerm n) (p : Fin (suc n)) → g (l ◂ p) ≡ LehmerAlgebra.step alg (g l) p) →
  ∀ {n} (l : DFTTerm n) → g l ≡ dft-eval alg l
dft-eval-unique = fold-unique
