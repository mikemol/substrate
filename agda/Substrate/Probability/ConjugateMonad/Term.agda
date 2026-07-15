------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad.Term (T17)
--
-- Term-algebra encoding of conjugate-prior updates — routed THROUGH the
-- witness tower's FREE graded tower of combined generators.
--
-- The flat form was `data ConjGen/ConjTerm : ConjState → ConjState → Set₁`
-- over `ConjState = Set × Set` — a hand-rolled free category over a Set₁
-- object type, reinventing the tower's free construction. The ⟡term-algebra-
-- via-witness-tower arc dissolves it: a term is a COMBINATION OF GENERATORS,
-- taken up to permutation (Bayesian updates commute — the sufficient-
-- statistic property, [[CommutativeConjugateMonad]]), and that free structure
-- IS the tower's `LehmerPath n ≅ Perm n` (LehmerPath.agda:54, the factoradic
-- witness tower). So:
--
--   ConjTerm n   = LehmerPath n          -- the free tower of n combined gens
--   []ᶜ          = start                 -- the empty update sequence
--   _++ᶜ_        = _⊕_                    -- combine two sequences (grade adds)
--   conj-product = ⊕-over                -- the GradedProductOver (graded stencil)
--   conj-eval    = fold                  -- the UNIQUE interpreter into any target
--   conj-eval-unique = fold-unique       -- its universal property (initiality)
--
-- Set₀ throughout (LehmerPath is Set₀); the Set₁ data families are gone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad.Term where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedProductOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-over)

-- The conjugate-update term carrier: the free graded tower of combined
-- generators. `ConjTerm n` = an n-update Bayesian-update sequence, up to
-- permutation (the sufficient-statistic / commutativity property).
ConjTerm : ℕ → Set
ConjTerm = LehmerPath

-- The empty term and composition (combine two update-towers; the grade adds).
[]ᶜ : ConjTerm 0
[]ᶜ = start

_++ᶜ_ : {m n : ℕ} → ConjTerm m → ConjTerm n → ConjTerm (m + n)
_++ᶜ_ = _⊕_

infixr 4 _++ᶜ_

-- The graded product on terms IS the tower's own ⊕-over : GradedProductOver
-- (the graded stencil), so its associativity/unit come from the tower (.Category).
conj-product : GradedProductOver _+_ 0 ConjTerm
conj-product = ⊕-over

-- The semantics of a term is the UNIQUE fold into any LehmerAlgebra target:
-- base = the prior state, step = apply one Bayesian update at each rung.
conj-eval : {C : ℕ → Set} → LehmerAlgebra C → {n : ℕ} → ConjTerm n → C n
conj-eval = fold

-- The universal property: any interpreter respecting (base, step) IS conj-eval.
conj-eval-unique :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (g : {n : ℕ} → ConjTerm n → C n) →
  (g start ≡ LehmerAlgebra.base alg) →
  (∀ {n} (l : ConjTerm n) (p : Fin (suc n)) → g (l ◂ p) ≡ LehmerAlgebra.step alg (g l) p) →
  ∀ {n} (l : ConjTerm n) → g l ≡ conj-eval alg l
conj-eval-unique = fold-unique
