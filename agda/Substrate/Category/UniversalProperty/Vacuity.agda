------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Vacuity
--
-- The VACUITY RECOGNIZER — the meta-tool that makes the universal-property
-- recognizer safe. A claimed universal property (a UPArrow) is REAL only if
-- its Witness DISCRIMINATES (some problem has a non-solution); the ⊤-collapse
-- (Witness ≡ λ _ _ → ⊤, the terminal object) is vacuous — any function
-- "satisfies" it. This is the architecture test of the whole arc, made into
-- a checkable predicate:
--
--   Vacuous U    = every (s,t) solves   (the relation imposes nothing)
--   Contentful U = some (s,t) does NOT  (the relation has content)
--
-- A reducibility/instance claim is a FALSE POSITIVE exactly when its UPArrow
-- is Vacuous. Contentful ⟹ ¬ Vacuous: content cannot collapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Vacuity where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.UniversalProperty
  using (UPArrowP; mkUP; SourceP; TargetP; WitnessP; trivial-UPP)

------------------------------------------------------------------------
-- 1. The recognizer. ⟡UPArrow-dissolve: re-indexed over the Set₀
--    UPArrowP (carriers as params); the projections are the SourceP/
--    TargetP/WitnessP shims, which reduce to the params definitionally.
------------------------------------------------------------------------

-- vacuous: the Witness imposes no constraint (the ⊤-collapse).
Vacuous : {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set
Vacuous U = (s : SourceP U) (t : TargetP U) → WitnessP U s t

-- contentful: some problem genuinely excludes some candidate.
Contentful : {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set
Contentful U = Σ (SourceP U) (λ s → Σ (TargetP U) (λ t → ¬ (WitnessP U s t)))

-- content cannot collapse: a contentful UP is not vacuous.
contentful→¬vacuous : {S T : Set} {W : S → T → Set}
                      (U : UPArrowP S T W) → Contentful U → ¬ Vacuous U
contentful→¬vacuous U (s , t , ¬w) vac = ¬w (vac s t)

------------------------------------------------------------------------
-- 2. The poles: the ⊤-collapse is vacuous; a discriminating UP is not.
------------------------------------------------------------------------

-- the catalogue's trivial UP (Source = Target = ⊤, Witness = ⊤) — the
-- false-positive shape: it is provably vacuous.
trivial-vacuous : Vacuous trivial-UPP
trivial-vacuous _ _ = tt

-- a content-bearing UP: Witness = equality on ℕ. It discriminates (0 ≢ 1),
-- so it is Contentful, hence not vacuous. This is the shape every REAL
-- witness in the arc has (bezout: s·a+t·b ≡ g; crt: combine ≡ ...; the
-- Witnesses are equalities, which discriminate).
eq-UP : UPArrowP ℕ ℕ _≡_
eq-UP = mkUP

eq-contentful : Contentful eq-UP
eq-contentful = 0 , 1 , (λ ())

eq-not-vacuous : ¬ Vacuous eq-UP
eq-not-vacuous = contentful→¬vacuous eq-UP eq-contentful
