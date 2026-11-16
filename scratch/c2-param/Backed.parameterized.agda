------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Backed
--
-- THE COMMON NON-VACUOUS SOLVER backing the EXISTENCE half of a universal
-- property. Across the whole arc every universal property has the same
-- backing shape:
--   * carriers (S, T) + a witness relation W : S → T → Set,
--   * a `solve` returning the mediating witness for every problem (THE
--     BRIDGE — recognition returns the witness, not a residue),
--   * `solves`: the bridge satisfies the coherence (the equation), and
--   * `content`: a non-vacuity certificate (some problem genuinely excludes
--     some candidate).
--
-- ⟡C2-param — the backing is CARRIER-GENERIC: `BackedUP` is PARAMETERIZED over
-- its carriers (S, T, W) instead of FIELDING a UPArrow, so a BackedUP term
-- inhabits Set₀ (not Set₁). The heterogeneous registry bundles the carriers via
-- `Registered` (Set₁, ONE def) — `registry : List Registered`. The carriers of the
-- concrete backings are still taken from the existing UPArrows (eq-UP / crt-UP),
-- which stay in Vacuity / Recognized and drive the recognizer layer (UPArrow is
-- untouched — 99 consumers). `content`'s parameterized type at (Source U, Target U,
-- Witness U) is EXACTLY the old `Contentful U`, so the existing X-contentful proofs
-- plug in unchanged.
--
-- SCOPE: BackedUP certifies EXISTENCE (a non-vacuous solver), NOT universality.
-- The UNIQUENESS half is the separate `UniversalProperty.Unique.WitnessUnique`
-- layer, relative to a bound. It is gated by non-vacuity: the ⊤-collapse cannot
-- supply `content`. The CRT-Witness (gcd→Bézout→inverse→idempotent→combine) IS
-- the solver backing the CRT UP.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Backed where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (eq-UP; eq-contentful)
open import Substrate.Category.UniversalProperty.Recognized using (crt-UP; crt-recognized; content)
open import Substrate.Algebra.Quotient.CRT using (combine; combine-mod-m; combine-mod-n)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (witness-3-5)

------------------------------------------------------------------------
-- 1. The carrier-generic bridge: solve (returns the witness) + solves + content.
--    Parameterized over (S, T, W) ⟹ a BackedUP term is Set₀.
------------------------------------------------------------------------

record BackedUP (S T : Set) (W : S → T → Set) : Set where
  field
    solve   : S → T
    solves  : (s : S) → W s (solve s)
    content : Σ S (λ s → Σ T (λ t → ¬ (W s t)))

open BackedUP public

-- the parameterized ⊤-collapse: the witness imposes no constraint.
Vacuousᴾ : (S T : Set) (W : S → T → Set) → Set
Vacuousᴾ S T W = (s : S) (t : T) → W s t

-- a backed UP is non-vacuous (its content cannot collapse to the ⊤-relation).
backed-non-vacuous : {S T : Set} {W : S → T → Set} → BackedUP S T W → ¬ (Vacuousᴾ S T W)
backed-non-vacuous b vac with content b
... | (s , t , ¬w) = ¬w (vac s t)

------------------------------------------------------------------------
-- 2. The heterogeneous bundle: a REGISTERED backing packages its carriers with the
--    Set₀ backing. This is the ONE Set₁ definition the registry needs (the carriers
--    S,T are Set-valued, so bundling them is Set₁); the backings themselves are Set₀.
------------------------------------------------------------------------

record Registered : Set₁ where
  constructor pack
  field
    {S T} : Set
    {W}   : S → T → Set
    backed : BackedUP S T W

open Registered public

------------------------------------------------------------------------
-- 3. Instances — the bridge is COMMON: the same shape backs each. Carriers taken from
--    the existing UPArrows (eq-UP / crt-UP), so each backing is Set₀.
------------------------------------------------------------------------

-- equality UP: the bridge is the identity (s solved by s).
eq-backed : BackedUP (Source eq-UP) (Target eq-UP) (Witness eq-UP)
eq-backed = record
  { solve = λ s → s ; solves = λ s → refl ; content = eq-contentful }

-- CRT UP (moduli 3,5): the bridge is the CRT-Witness's combine — the whole
-- gcd→Bézout→inverse→idempotent→combine chain — and `solves` is its proven
-- congruences. The real number-theoretic wedge backing the universal property.
crt-backed : BackedUP (Source crt-UP) (Target crt-UP) (Witness crt-UP)
crt-backed = record
  { solve   = λ p → combine witness-3-5 p
  ; solves  = λ p → combine-mod-m witness-3-5 (proj₁ p) (proj₂ p)
                  , combine-mod-n witness-3-5 (proj₁ p) (proj₂ p)
  ; content = content crt-recognized
  }
