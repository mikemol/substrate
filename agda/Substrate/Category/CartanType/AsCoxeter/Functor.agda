------------------------------------------------------------------------
-- Substrate.Category.CartanType.AsCoxeter.Functor
--
-- The backward direction of the Coxeter ↔ Cartan equivalence.
-- Mirrors [[Coxeter.AsCartanType.Functor]] (M8 of the M-arc); the
-- comment there explicitly listed the backward functor as
-- "downstream slices". This file is that completion, per
-- [[feedback-chirality-pair-completeness]].
--
-- Extracts the Coxeter group from a Cartan type (the underlying
-- reflection group W(R) of the root system R). Together with M8's
-- forward functor, this exhibits the substrate-level Coxeter ↔
-- Cartan correspondence as a pair of functors; the full equivalence-
-- of-categories (with isomorphism witnesses + adjunction) composes
-- downstream.
--
-- Module-parametric per substrate convention: user supplies the
-- specific Functor — the substrate names it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.CartanType.AsCoxeter.Functor
  {ℓOT ℓMT ℓOC ℓMC : Level}
  (CartanCat : CategoryOf {ℓOT} {ℓMT})
  (CoxeterCat : CategoryOf {ℓOC} {ℓMC})
  (Cartan→Coxeter : Functor CartanCat CoxeterCat)
  where

------------------------------------------------------------------------
-- 1. The Cartan ↦ Coxeter functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  CartanCat CoxeterCat Cartan→Coxeter public
  renaming (named-Functor to Cartan-AsCoxeter-Functor)
------------------------------------------------------------------------
-- 2. Capstone — chirality completion of M8.
--
-- With this file the Coxeter ↔ Cartan correspondence is named in
-- BOTH directions:
--   forward : Coxeter.AsCartanType.Functor   (M8)
--   backward: CartanType.AsCoxeter.Functor   (this slice)
--
-- The pair are the two functors of the equivalence of categories
-- W : CoxeterCat ⇄ CartanCat : R. Downstream slices supply the
-- isomorphism-of-functors (W ∘ R ≅ id, R ∘ W ≅ id) and assemble the
-- full Adjunction primitive (#4).
------------------------------------------------------------------------
