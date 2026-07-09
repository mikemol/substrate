{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aSkiBacked — ⟡x8a-ski-backed: wrap the SKI existence
-- UP (X8aSkiExistence, 215) into a full BackedUP at the real SKI carrier, and register it.
-- Bundles the existence half (215, solve = run over the SKI shedding) with a SKI non-vacuity
-- witness into arrow/solve/solves/content — the extruder as a backed SKI solver.
--
-- Two layers (mirroring the schema/instance split the abstract classifier forces):
--   ① SCHEMA (module SkiBacked ⇒ fpf): for ANY SKI classifier ⇒ (with its fixed-point-free
--      invariant fpf), a full BackedUP. The non-vacuity witness is CLASSIFIER-INDEPENDENT:
--      run 0 t = t (fuel-0 short-circuits before next/fix?), so for term = atom, candidate
--      = app atom atom, we have app atom atom ≢ atom (constructor disjointness) = ¬ Witness —
--      Contentful. So EVERY SKI classifier yields a non-vacuous backed solver.
--   ② CONCRETE INSTANCE + REGISTRATION: FUSep exposes Reduce only abstractly (no concrete SKI
--      classifier is exported), so to REGISTER (registry needs a concrete BackedUP) we take the
--      simplest total classifier — all-stop (⇒₀ t = stop: every term is already its nf, fpf
--      vacuous). x8a-ski-backed = the schema at ⇒₀; x8a-ski-registry conses it (canonical idiom
--      205). The schema ① covers the REAL branching reduction once a concrete FUSep classifier
--      is wired (⟡x8a-wcr-discharge); ⟡ registers a concrete SKI solver now.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aSkiBacked where

open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Nat using (ℕ; zero)
open import Substrate.Foundation.List using (List; _∷_)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed
  using (BackedUP; arrow; solve; solves; content; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.Registry using (registry)
open import Substrate.FUSep.FUSepQReduce using (atom; app; stop; shed; Reduce) renaming (Step to Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.X8aSkiExistence using (module SkiExistence)

------------------------------------------------------------------------
-- ① THE SCHEMA: any SKI classifier ⇒ (+ its fpf) → a full non-vacuous BackedUP. The content
--    witness is classifier-independent (fuel 0: run 0 t = t; atom vs app atom atom disjoint).
------------------------------------------------------------------------
module SkiBacked
  (⇒ : Reduce)
  (fpf : (t t' : Tm⟦533ef80d⟧) → ⇒ t ≡ shed t' → ¬ (t' ≡ t))
  where
  open SkiExistence ⇒ fpf using (x8a-ski-UP; x8a-ski-solve; x8a-ski-solves)

  -- non-vacuity: (fuel 0, atom) with candidate app atom atom. run 0 atom = atom (fuel-0
  -- short-circuit), and app atom atom ≢ atom by constructor disjointness — so ¬ Witness.
  ski-contentful : Contentful x8a-ski-UP
  ski-contentful = (zero , atom) , app atom atom , bad
    where
      -- Witness ((0,atom)) (app atom atom) = (app atom atom ≡ run 0 atom) = (app atom atom ≡ atom).
      bad : ¬ (app atom atom ≡ atom)
      bad ()

  ski-backed : BackedUP
  ski-backed = record
    { arrow   = x8a-ski-UP
    ; solve   = x8a-ski-solve
    ; solves  = x8a-ski-solves
    ; content = ski-contentful
    }

------------------------------------------------------------------------
-- ② CONCRETE INSTANCE + REGISTRATION at the all-stop classifier (⇒₀ t = stop). Every term is
--    its own nf; fpf is vacuous (no shed cases). A genuine, concrete, non-vacuous SKI BackedUP.
------------------------------------------------------------------------
⇒₀ : Reduce
⇒₀ _ = stop

-- fpf for ⇒₀: ⇒₀ t = stop, so ⇒₀ t ≡ shed t' is uninhabited → vacuously fixed-point-free.
fpf₀ : (t t' : Tm⟦533ef80d⟧) → ⇒₀ t ≡ shed t' → ¬ (t' ≡ t)
fpf₀ t t' ()

x8a-ski-backed : BackedUP
x8a-ski-backed = SkiBacked.ski-backed ⇒₀ fpf₀

-- non-vacuous by typing (the Registry's invariant — a real, not padded, SKI solver):
x8a-ski-non-vacuous : ¬ ((s : Source (arrow x8a-ski-backed)) (t : Target (arrow x8a-ski-backed))
                        → Witness (arrow x8a-ski-backed) s t)
x8a-ski-non-vacuous = backed-non-vacuous x8a-ski-backed

-- registered — the canonical cons idiom (205): the SKI extruder solver on the base seed.
x8a-ski-registry : List BackedUP
x8a-ski-registry = x8a-ski-backed ∷ registry

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the SKI extruder is a full BackedUP, registered): the SKI
-- existence UP (215) is now wrapped into arrow/solve/solves/content — a full BackedUP at the
-- real SKI carrier — via the classifier-independent fuel-0 non-vacuity (atom ≢ app atom atom).
-- The SCHEMA (SkiBacked ⇒ fpf) gives this for ANY classifier; the concrete registration takes
-- the all-stop ⇒₀ (the simplest total classifier, fpf vacuous) since FUSep exposes Reduce only
-- abstractly. So the either/or "schema vs concrete registration" dissolves: the schema is the
-- general fact (every SKI classifier yields a backed solver), the ⇒₀ instance the concrete
-- registered witness (x8a-ski-registry = x8a-ski-backed ∷ registry, canonical cons). The
-- extruder now has BOTH a ℕ-demonstrator BackedUP (212, registered X8aRegistry) AND a real-SKI
-- BackedUP (here) — the same frame at two carriers. Wiring ⇒₀ → a concrete branching FUSep
-- classifier (⟡x8a-wcr-discharge) registers the FULL SKI reduction; the frame is complete.
------------------------------------------------------------------------
