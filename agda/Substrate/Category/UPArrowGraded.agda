------------------------------------------------------------------------
-- Substrate.Category.UPArrowGraded
--
-- ⟡upfamily-rewire — THE REPLACEMENT for Substrate.Category.UniversalProperty.UPArrow.
--
-- The flat UPArrow was `record UPArrow : Set₁ { Source Target : Set ; Witness :
-- Source → Target → Set }` — Set₁ because it HELD its carriers as fields and its
-- witness was a Set-valued span (a `Fam`). That flatness "counted against us": UPArrow
-- + its 72 instances are the largest slice of the Set₁ census (⟡defect-locate-census).
--
-- This is the UPGRADE, not a bridge (we retain NOTHING of the flat UPArrow):
--   * the carriers are grade-indexed PARAMETERS (Spec Sol : ℕ → Set), never fields —
--     the set1-carrier-always-parameterize move, and the shape of every Set₀ graded
--     object in the arc (GradedProductOver C, LehmerAlgebra C, all measured Set₀);
--   * the proof-relevant span `Witness : Source → Target → Set` (the Set-valued, hence
--     Set₁, cause) is replaced by the CONSTRUCTIVE universal arrow `solve : Spec n →
--     Sol n` — the same shape as OrientationUniversal.fold (LehmerPath n → C n). This
--     is the ∃!-is-a-construction move: the universal witness is the map that BUILDS
--     the solution, not a Set-valued relation asserting one exists.
--
-- Result: `UPArrowᴳ : Set` (level-0, checked). Consumers migrate here and drop from the
-- Set₁ count; UPArrow is then deleted (nothing retained). Universality (uniqueness of
-- `solve`) layers on exactly as OrientationUniversal.fold-unique does — as a Set₀ lemma
-- over the target, NOT a field (so it never re-inflates the universe).
--
-- Zero postulates, zero holes, --safe --without-K. Substrate-only.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UPArrowGraded where

open import Substrate.Foundation.Nat using (ℕ)

------------------------------------------------------------------------
-- The upgraded universal arrow: carriers are grade-indexed PARAMETERS; the content is
-- the constructive solving map. Set₀.
------------------------------------------------------------------------

record UPArrowᴳ (Spec Sol : ℕ → Set) : Set where
  constructor mkUP
  field
    solve : {n : ℕ} → Spec n → Sol n

open UPArrowᴳ public

------------------------------------------------------------------------
-- The trivial universal arrow (was `trivial-UP`, Set₁): the identity solve on any
-- graded carrier. Now Set₀.
------------------------------------------------------------------------

trivial-UPᴳ : (C : ℕ → Set) → UPArrowᴳ C C
trivial-UPᴳ C = mkUP (λ x → x)

------------------------------------------------------------------------
-- Universality is stated over the target as a PARAMETER (Set₀), never a field: a solve
-- that agrees with `u` on every grade IS `u`'s solve — the fold-unique shape. Here at
-- the bare-arrow level it is pointwise determination; richer UPs (Free, Limit) add the
-- structure-respecting hypotheses exactly as OrientationUniversal.fold-unique does.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_)

Determines : {Spec Sol : ℕ → Set} → UPArrowᴳ Spec Sol →
             ({n : ℕ} → Spec n → Sol n) → Set
Determines {Spec} u g = {n : ℕ} (x : Spec n) → g x ≡ solve u x
