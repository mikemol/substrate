------------------------------------------------------------------------
-- Substrate.Algebra.Involution
--
-- The apex of the involution law-motif f (f x) ≡ x — surfaced by
-- scripts/law_motif_apex.py as a 34-instance cluster with no parametric apex
-- (negBoth/negNeg/negPos-invol, not-invol, swap{E,V}-involutive, complement-
-- involution, dual-grade-involution, sym-sym, recip-invol, …). It is the k=2 case
-- of the torsion-element universal ([[project_torsion_element_universal]]): a
-- finite-order self-map.
--
-- THE universal consequence, parametric over any (f, involution-proof): an
-- involution is INJECTIVE (hence, being its own two-sided inverse, a bijection /
-- self-inverse iso). From f x ≡ f y, `cong f` then the involution law on each side
-- recovers x ≡ y. Every concrete involution instance is therefore injective for free.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Involution where

open import Agda.Primitive using (Level)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

-- THE apex: an involution is injective (the parametric structure the 34 instances
-- all witness). f x ≡ f y  →  f (f x) ≡ f (f y)  →  x ≡ y. The involution hypothesis
-- is written INLINE (`(x) → f (f x) ≡ x`), not behind an alias, so the law-motif is
-- visible at the binder — apex-detectors that don't unfold definitions can see it.
invol-injective :
  {a : Level} {A : Set a}
  (f : A → A) (invol : (x : A) → f (f x) ≡ x) →
  {x y : A} → f x ≡ f y → x ≡ y
invol-injective f invol {x} {y} p =
  trans (sym (invol x)) (trans (cong f p) (invol y))
