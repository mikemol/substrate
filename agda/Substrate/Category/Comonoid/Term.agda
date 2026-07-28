------------------------------------------------------------------------
-- Substrate.Category.Comonoid.Term (T12)
--
-- Term-algebra encoding of comonoid morphisms — routed THROUGH the witness
-- tower's FREE graded tower of combined generators.
--
-- The flat form was `data ComonoidGen/ComonoidTerm (C : Set) : Set → Set →
-- Set₁` — a hand-rolled free category over Set-valued objects (Set₁), carrying
-- an extra carrier param `C`. A comonoid term is a COMBINATION OF GENERATORS
-- (comonoid morphisms), and the tower's free such structure is `LehmerPath n ≅
-- Perm n`; the carrier/object indices were syntactic scaffolding and dissolve.
-- So (⟡term-algebra-via-witness-tower):
--
--   ComonoidTerm n   = LehmerPath n      -- the free tower of combined generators
--   []c / _++c_      = start / _⊕_       -- combine; grade adds
--   comonoid-product = ⊕-over            -- the GradedProductOver (graded stencil)
--   comonoid-eval    = fold              -- the UNIQUE interpreter
--   comonoid-eval-unique = fold-unique   -- its universal property
--
-- Set₀ throughout; the Set₁ data families + the `C`/object params are gone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid.Term where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The comonoid term carrier: the free graded tower of combined generators.
ComonoidTerm : ℕ → Set
ComonoidTerm = LehmerPath

-- The empty term and composition (combine two generator-towers; the grade adds).
[]c : ComonoidTerm 0
[]c = start

_++c_ : {m n : ℕ} → ComonoidTerm m → ComonoidTerm n → ComonoidTerm (m + n)
_++c_ = _⊕_

infixr 4 _++c_

-- The graded product on terms IS the tower's ⊕-over : GradedProductOver.
comonoid-product : GradedProductOver _+_ 0 ComonoidTerm
comonoid-product = ⊕-over

-- The semantics is the UNIQUE fold into any LehmerAlgebra target: base = the
-- identity comonoid morphism, step = apply one comonoid generator.
comonoid-eval : {C : ℕ → Set} → LehmerAlgebra C → {n : ℕ} → ComonoidTerm n → C n
comonoid-eval = fold

-- The universal property: any interpreter respecting (base, step) IS comonoid-eval.
comonoid-eval-unique :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (g : {n : ℕ} → ComonoidTerm n → C n) →
  (g start ≡ LehmerAlgebra.base alg) →
  (∀ {n} (l : ComonoidTerm n) (p : Fin (suc n)) → g (l ◂ p) ≡ LehmerAlgebra.step alg (g l) p) →
  ∀ {n} (l : ComonoidTerm n) → g l ≡ comonoid-eval alg l
comonoid-eval-unique = fold-unique
