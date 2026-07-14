------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aSkiBackedGraded — ⟡C2g-m-x8aski (graded): the SKI extruder
-- (reduction-to-normal-form) UP as a Set₀ graded backing.
--
-- Migrates the flat `x8a-ski-backed : BackedUP` (X8aSkiBacked.agda:76). Class A in spirit (flat Witness
-- = `v ≡ run …`), but heavier: needs --guardedness and the X8aSkiExistence internals. FUEL IS THE
-- GRADE: solve {n} t = x8a-ski-solve (n , t) (run the SKI shedding n steps) at the concrete all-stop
-- classifier ⇒₀ (the simplest total classifier; FUSep exposes Reduce only abstractly). `solves` (refl)
-- vanishes. Content: run 0 atom = atom (fuel-0 short-circuit), candidate (app atom atom) ≢ atom by
-- constructor disjointness. Drops the flat `x8a-ski-registry` cons per ⟡C2g-registry.
--
-- Zero postulates, --safe --without-K --guardedness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.X8aSkiBackedGraded where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.FUSep.FUSepQReduce using (atom; app; stop; shed; Reduce) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.X8aSkiExistence using (module SkiExistence)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- the concrete all-stop classifier (every term is its own nf; fpf vacuous).
⇒₀ : Reduce
⇒₀ _ = stop

fpf₀ : (t t' : Tm⟦533ef80d⟧) → ⇒₀ t ≡ shed t' → ¬ (t' ≡ t)
fpf₀ t t' ()

open SkiExistence ⇒₀ fpf₀ using (x8a-ski-solve)

-- FUEL IS THE GRADE: solve {n} t = run the SKI shedding n steps.
x8a-ski-arrowᴳ : UPArrowᴳ (λ _ → Tm⟦533ef80d⟧) (λ _ → Tm⟦533ef80d⟧)
x8a-ski-arrowᴳ = mkUP (λ {n} t → x8a-ski-solve (n , t))

-- content at grade 0: run 0 atom = atom; candidate (app atom atom) ≠ atom (constructor disjointness).
x8a-ski-backedᴳ : BackedUPᴳ (λ _ → Tm⟦533ef80d⟧) (λ _ → Tm⟦533ef80d⟧)
x8a-ski-backedᴳ = record
  { arrowᴳ  = x8a-ski-arrowᴳ
  ; content = 0 , atom , app atom atom , λ ()
  }
