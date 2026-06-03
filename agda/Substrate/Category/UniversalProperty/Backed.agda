------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Backed
--
-- THE COMMON NON-VACUOUS BRIDGE backing a universal property. Across the
-- whole arc every universal property has the same backing shape:
--   * a UPArrow (the problem↛solution span),
--   * a `solve` returning the mediating witness for every problem (THE
--     BRIDGE — recognition returns the witness, not a residue),
--   * `solves`: the bridge satisfies the coherence (the equation), and
--   * `content`: a Contentful certificate (the wedge is non-vacuous —
--     some problem genuinely excludes some candidate).
--
-- This bundle is "the common non-vacuous bridge the universal property is
-- backed by." It is gated by the vacuity recognizer: the ⊤-collapse has no
-- BackedUP (it cannot supply `content`). And the concrete number-theoretic
-- wedges instantiate it — notably the CRT-Witness (built from gcd via
-- Bézout→inverse→idempotent→combine) IS the bridge backing the CRT UP.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Backed where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity
  using (Vacuous; Contentful; contentful→¬vacuous; eq-UP; eq-contentful)
open import Substrate.Category.UniversalProperty.Recognized using (crt-UP; crt-recognized; content)
open import Substrate.Algebra.Quotient.CRT using (combine; combine-mod-m; combine-mod-n)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (witness-3-5)

------------------------------------------------------------------------
-- 1. The common bridge: solve (returns the witness) + solves + content.
------------------------------------------------------------------------

record BackedUP : Set₁ where
  field
    arrow   : UPArrow
    solve   : Source arrow → Target arrow
    solves  : (s : Source arrow) → Witness arrow s (solve s)
    content : Contentful arrow

open BackedUP public

-- a backed UP is non-vacuous (its content cannot collapse to ⊤).
backed-non-vacuous : (b : BackedUP) → ¬ Vacuous (arrow b)
backed-non-vacuous b = contentful→¬vacuous (arrow b) (content b)

------------------------------------------------------------------------
-- 2. Instances — the bridge is COMMON: the same shape backs each.
------------------------------------------------------------------------

-- equality UP: the bridge is the identity (s solved by s).
eq-backed : BackedUP
eq-backed = record
  { arrow = eq-UP ; solve = λ s → s ; solves = λ s → refl ; content = eq-contentful }

-- CRT UP (moduli 3,5): the bridge is the CRT-Witness's combine — the whole
-- gcd→Bézout→inverse→idempotent→combine chain — and `solves` is its proven
-- congruences. The real number-theoretic wedge backing the universal property.
crt-backed : BackedUP
crt-backed = record
  { arrow   = crt-UP
  ; solve   = λ p → combine witness-3-5 p
  ; solves  = λ p → combine-mod-m witness-3-5 (proj₁ p) (proj₂ p)
                  , combine-mod-n witness-3-5 (proj₁ p) (proj₂ p)
  ; content = content crt-recognized
  }
