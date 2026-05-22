------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment
--
-- D8 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- The unified retroactive-alignment module: states the parent-
-- primitive-supersedes-deferrals story as a single substrate-
-- internal record. Each of the six LanguageWitness instances gets
-- a "parent primitive IS now extracted; original deferral note is
-- superseded" entry.
--
-- Companion to D6 (Lojban) and D7 (Toki Pona) per-arc retroactive
-- alignments; D8 is the classification-arc-level summary.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; FreeOverBasis; η;
         FreeConstructionClass; name; class;
         WitnessName;
         Lojban; TokiPona; Solresol; Kelen; Lambda; LieFrag;
         Free-monoid; Free-F2-module; Free-cyclic;
         Free-relation; Free-CCC; Free-Lie)

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

------------------------------------------------------------------------
-- 1. The alignment record.
--
-- For each witness: WitnessName + FreeConstructionClass + a small
-- alignment witness. The alignment is the equality
-- `class (witness-with-name n) ≡ expected-class n` plus
-- `name (witness-with-name n) ≡ n`.
------------------------------------------------------------------------

record WitnessAlignment (W : LanguageWitness) : Set₁ where
  field
    expected-name  : WitnessName
    expected-class : FreeConstructionClass
    name-witness   : name W ≡ expected-name
    class-witness  : class W ≡ expected-class

open WitnessAlignment public

------------------------------------------------------------------------
-- 2. The six aligned witnesses.
------------------------------------------------------------------------

lojban-aligned : WitnessAlignment lojban-witness
lojban-aligned = record
  { expected-name  = Lojban
  ; expected-class = Free-monoid
  ; name-witness   = refl
  ; class-witness  = refl
  }

tokipona-aligned : WitnessAlignment tokipona-witness
tokipona-aligned = record
  { expected-name  = TokiPona
  ; expected-class = Free-F2-module
  ; name-witness   = refl
  ; class-witness  = refl
  }

solresol-aligned : WitnessAlignment solresol-witness
solresol-aligned = record
  { expected-name  = Solresol
  ; expected-class = Free-cyclic
  ; name-witness   = refl
  ; class-witness  = refl
  }

kelen-aligned : WitnessAlignment kelen-witness
kelen-aligned = record
  { expected-name  = Kelen
  ; expected-class = Free-relation
  ; name-witness   = refl
  ; class-witness  = refl
  }

lambda-aligned : WitnessAlignment lambda-witness
lambda-aligned = record
  { expected-name  = Lambda
  ; expected-class = Free-CCC
  ; name-witness   = refl
  ; class-witness  = refl
  }

lie-aligned : WitnessAlignment lie-witness
lie-aligned = record
  { expected-name  = LieFrag
  ; expected-class = Free-Lie
  ; name-witness   = refl
  ; class-witness  = refl
  }

------------------------------------------------------------------------
-- 3. The aggregate record: all six witnesses aligned.
--
-- A single substrate-internal value certifying that the parent
-- primitive (FreeOverBasis from C1) covers all six witnesses with
-- their correct names + classifications.
------------------------------------------------------------------------

record FullRetroactiveAlignment : Set₁ where
  field
    lojban   : WitnessAlignment lojban-witness
    tokipona : WitnessAlignment tokipona-witness
    solresol : WitnessAlignment solresol-witness
    kelen    : WitnessAlignment kelen-witness
    lambda   : WitnessAlignment lambda-witness
    lie      : WitnessAlignment lie-witness

full-alignment : FullRetroactiveAlignment
full-alignment = record
  { lojban   = lojban-aligned
  ; tokipona = tokipona-aligned
  ; solresol = solresol-aligned
  ; kelen    = kelen-aligned
  ; lambda   = lambda-aligned
  ; lie      = lie-aligned
  }

------------------------------------------------------------------------
-- 4. Capstone.
--
-- `full-alignment` is the substrate-internal witness that the
-- parent primitive's coverage of all six witnesses is consistent
-- and complete (within the arc's scope). The "shared parent
-- extraction deferred" prose from Lojban L10 + Toki Pona T10 is
-- now superseded by this aggregate. D9 supplements with a
-- ClosureLog recording WHAT was closed in the D-arc.
------------------------------------------------------------------------
