------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Eval (T6)
--
-- LensTerm semantics — the UNIQUE fold out of the free tower. With the term
-- carrier routed through the witness tower (LensTerm = LehmerPath), the
-- denotation of a term is `fold` into any LehmerAlgebra target (base = the
-- identity lens, step = apply one lens generator), and it is UNIQUE
-- (fold-unique) — the term-algebra's universal property, from the tower.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Eval where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique)
open import Substrate.Category.StochasticLens.Term using (LensTerm)

-- The denotation: the unique fold into any LehmerAlgebra target.
eval : {C : ℕ → Set} → LehmerAlgebra C → {n : ℕ} → LensTerm n → C n
eval = fold

-- Its universal property: any interpreter respecting (base, step) IS eval.
eval-unique :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (g : {n : ℕ} → LensTerm n → C n) →
  (g start ≡ LehmerAlgebra.base alg) →
  (∀ {n} (l : LensTerm n) (p : Fin (suc n)) → g (l ◂ p) ≡ LehmerAlgebra.step alg (g l) p) →
  ∀ {n} (l : LensTerm n) → g l ≡ eval alg l
eval-unique = fold-unique
