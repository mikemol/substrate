------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationUniversal
--
-- ⟡rig-UP (the Set₀ core) — the UNIVERSAL PROPERTY of the free ordering tower, done the way
-- we discussed: NOT the Σ ℕ / Set₁ collapse (which is exactly what blocks the existing
-- FreeUP/UPArrow — "UPArrow.Source : Set can't hold the graded thing"), NOT a new
-- 2-categorical framework. It is the TWO-WITNESS-TOWERS-MEET: the free tower and any target
-- tower meet at each rung, and the higher-order witness recording the meet is Set₀ — the
-- SAME construction as OrientationFixedPoint's decode-injective (the μΦ≅νΦ pairing-witness),
-- and the same as combining the generators into a tuple and witnessing their synchronized
-- action through the tower growth (FourPointReflection's wordAct-hom is the free monoid hom).
--
-- Concretely: LehmerPath IS the initial algebra μΦ of the tower functor. Its universal
-- property is the unique FOLD (catamorphism) into any graded LehmerAlgebra, with uniqueness
-- by LehmerPath induction — grade-by-grade, each grade Set₀.
--
--   fold        : LehmerAlgebra C → LehmerPath n → C n          -- THE unique structure-map
--   fold-unique : any g respecting (base, step) IS the fold     -- the Set₀ meet-witness
--
-- So the tower is the free/initial structure on its generators, formalized at Set₀. (The full
-- symmetric-RIG-functor UP layers the ⊕/⊗ operations on top of this initial-algebra UP.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationUniversal where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)

------------------------------------------------------------------------
-- 1. A LehmerAlgebra: a graded target (C : ℕ → Set, each grade Set₀) carrying the tower
--    functor's structure — a grade-0 base and a rung-step (the ◂ / insert operation).
------------------------------------------------------------------------

record LehmerAlgebra (C : ℕ → Set) : Set where
  field
    base : C 0
    step : ∀ {n} → C n → Fin (suc n) → C (suc n)

open LehmerAlgebra public

------------------------------------------------------------------------
-- 2. THE FOLD (catamorphism): the structure-map out of the initial algebra LehmerPath.
------------------------------------------------------------------------

fold : ∀ {C} → LehmerAlgebra C → ∀ {n} → LehmerPath n → C n
fold alg start    = base alg
fold alg (l ◂ p)  = step alg (fold alg l) p

------------------------------------------------------------------------
-- 3. UNIVERSALITY: any map g that respects the algebra structure IS the fold. The proof is
--    the two-tower-meet witnessed grade-by-grade (LehmerPath induction) — the Set₀
--    higher-order witness, structurally identical to OrientationFixedPoint's decode-injective.
------------------------------------------------------------------------

fold-unique : ∀ {C} (alg : LehmerAlgebra C) (g : ∀ {n} → LehmerPath n → C n) →
              (g start ≡ base alg) →
              (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≡ step alg (g l) p) →
              ∀ {n} (l : LehmerPath n) → g l ≡ fold alg l
fold-unique alg g g-base g-step start    = g-base
fold-unique alg g g-base g-step (l ◂ p)  =
  trans (g-step l p) (cong (λ z → step alg z p) (fold-unique alg g g-base g-step l))
