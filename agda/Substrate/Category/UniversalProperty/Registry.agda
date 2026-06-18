------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Registry
--
-- The REALITY anchor for universal-property-backed interoperability.
--
-- A structure REALLY has a non-vacuous SOLVER bridge (the EXISTENCE half)
-- iff a BackedUP term exists for it AND TYPECHECKS — because
-- backed-non-vacuous makes the checker REFUSE a ⊤-collapse. So conformance is
-- not "absence of a ⊤-stub" (an obligation / self-report a grep can read) but
-- "presence of a compiled BackedUP" (reality the typechecker enforces). This
-- module IS the mechanical checklist: every entry below is a real, non-vacuous
-- SOLVER by the mere fact that this file compiles. To register a primitive is
-- to back its existence for real; the registry cannot be padded with vacuous
-- claims. NOTE: typechecking forces EXISTENCE + non-vacuity, NOT universality
-- (uniqueness) — that is the separate `UniversalProperty.Unique.WitnessUnique`
-- layer, available relative to a bound. So an entry here is a backed solver;
-- "the universal property" in full = this entry ⊕ its WitnessUnique.
--
-- COVERAGE (the unification metric) = registry entries vs the primitives
-- that claim a universal property. Grow this list to unify the repo.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Registry where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Vacuity using (Vacuous)
open import Substrate.Category.UniversalProperty.Backed
  using (BackedUP; arrow; backed-non-vacuous; eq-backed; crt-backed)
open import Substrate.Category.UniversalProperty.Interop
  using (Z3-backed; Z5-backed)

------------------------------------------------------------------------
-- The registry: the structures REALLY backed by a non-vacuous bridge.
-- (Each entry compiled ⟹ each is a genuine, content-bearing universal
--  property — the typechecker is the gate, not a grep.)
--
-- This List is the ADDITIVE seed (⊕ = ++, the free monoid) of the topos
-- ring K₀(Backed, ⊕, ⊗). The MULTIPLICATIVE operation ⊗ is Interop._⊗_∣_
-- (the backed combination of a pair); the first ring identity it backs is
-- [ℤ/3] ⊗ [ℤ/5] = [ℤ/15] (Interop.crt-ring-identity).
------------------------------------------------------------------------

registry : List BackedUP
registry = eq-backed       -- equality UP (the identity bridge)
         ∷ Z3-backed       -- ℤ/3 residue UP   ⎫ the two factors…
         ∷ Z5-backed       -- ℤ/5 residue UP   ⎭
         ∷ crt-backed      -- …and their product [ℤ/3] ⊗ [ℤ/5] = [ℤ/15]
         ∷ []

-- Every registered backing is non-vacuous — and this is FORCED by typing,
-- not asserted: backed-non-vacuous holds for ANY BackedUP, so no vacuous
-- entry could ever appear here.
every-backing-non-vacuous : (b : BackedUP) → ¬ Vacuous (arrow b)
every-backing-non-vacuous = backed-non-vacuous

------------------------------------------------------------------------
-- COVERAGE NOTE (the checklist, checked against reality):
--   BACKED (in registry, real): equality UP; CRT(3,5) — the gcd→Bézout→
--     inverse→idempotent→combine chain as the bridge.
--   BACKED DOWNSTREAM (a real BackedUP, but homed in the Logic tier because
--     Category must NOT import Logic): the verdict-tier COEQUALIZER — the
--     Nedge scalar shadow `bias` collapsing the distinct corners eU∼eV, with
--     content = U≢V (verdict refuses the collapse, so it is genuinely non-refl)
--     — in Substrate.Logic.Evidence.Verdict.BiasCoequalizer. There it conses
--     its backing onto this list as `verdict-registry = bias-coeq-backed ∷ registry`.
--   PROVED-BUT-NOT-YET-REGISTERED (real content exists; needs a BackedUP
--     wrapper — these are NOT debt, the reality is backed): free monoid
--     (FreeUniversalProperty.FreeMonoid), free F₂-module, Z₂ presentation,
--     the limit/product (LimitUniversalProperty), the units (ℤ/M)*.
--   OBLIGATION-ONLY ⊤-STUBS (self-reported placeholders; reality may differ
--     — e.g. FreeMonoid-UP in Instances is a stub whose content IS proved
--     above): see scratch/up_nonvacuity_policy.md.
------------------------------------------------------------------------
