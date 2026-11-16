------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.ClassDecide
--
-- Defines: class-decide
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.ClassDecide where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf
open import Substrate.Linguistic.Classification.AllWitnesses
open import Substrate.Linguistic.Classification.ClassCompwitnessByClass
open import Substrate.Linguistic.Classification.NameCompwitnessByName
open import Substrate.Linguistic.Classification.SumOR
open import Substrate.Linguistic.Classification.WitnessByClass
open import Substrate.Linguistic.Classification.WitnessByName
open import Substrate.Linguistic.Classification.WitnessCount
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RosettaTable.RosettaEntry



------------------------------------------------------------------------
-- 2. Decidable same-class? for pairs of witnesses.
--
-- The 6×6 = 36 pairs decompose: 6 reflexive same-class entries +
-- 30 different-class entries. Decided structurally on the class
-- enum.
------------------------------------------------------------------------

class-decide :
  (a b : FreeConstructionClass) →
  (a ≡ b) ⊎-OR (a ≡ b → ⊥)
-- Diagonal: same-class entries (7 cases)
class-decide Free-monoid    Free-monoid    = here refl
class-decide Free-F2-module Free-F2-module = here refl
class-decide Free-cyclic    Free-cyclic    = here refl
class-decide Free-relation  Free-relation  = here refl
class-decide Free-CCC       Free-CCC       = here refl
class-decide Free-Lie       Free-Lie       = here refl
class-decide Free-other     Free-other     = here refl
-- Off-diagonal: different-class entries (42 cases)
class-decide Free-monoid    Free-F2-module = there (λ ())
class-decide Free-monoid    Free-cyclic    = there (λ ())
class-decide Free-monoid    Free-relation  = there (λ ())
class-decide Free-monoid    Free-CCC       = there (λ ())
class-decide Free-monoid    Free-Lie       = there (λ ())
class-decide Free-monoid    Free-other     = there (λ ())
class-decide Free-F2-module Free-monoid    = there (λ ())
class-decide Free-F2-module Free-cyclic    = there (λ ())
class-decide Free-F2-module Free-relation  = there (λ ())
class-decide Free-F2-module Free-CCC       = there (λ ())
class-decide Free-F2-module Free-Lie       = there (λ ())
class-decide Free-F2-module Free-other     = there (λ ())
class-decide Free-cyclic    Free-monoid    = there (λ ())
class-decide Free-cyclic    Free-F2-module = there (λ ())
class-decide Free-cyclic    Free-relation  = there (λ ())
class-decide Free-cyclic    Free-CCC       = there (λ ())
class-decide Free-cyclic    Free-Lie       = there (λ ())
class-decide Free-cyclic    Free-other     = there (λ ())
class-decide Free-relation  Free-monoid    = there (λ ())
class-decide Free-relation  Free-F2-module = there (λ ())
class-decide Free-relation  Free-cyclic    = there (λ ())
class-decide Free-relation  Free-CCC       = there (λ ())
class-decide Free-relation  Free-Lie       = there (λ ())
class-decide Free-relation  Free-other     = there (λ ())
class-decide Free-CCC       Free-monoid    = there (λ ())
class-decide Free-CCC       Free-F2-module = there (λ ())
class-decide Free-CCC       Free-cyclic    = there (λ ())
class-decide Free-CCC       Free-relation  = there (λ ())
class-decide Free-CCC       Free-Lie       = there (λ ())
class-decide Free-CCC       Free-other     = there (λ ())
class-decide Free-Lie       Free-monoid    = there (λ ())
class-decide Free-Lie       Free-F2-module = there (λ ())
class-decide Free-Lie       Free-cyclic    = there (λ ())
class-decide Free-Lie       Free-relation  = there (λ ())
class-decide Free-Lie       Free-CCC       = there (λ ())
class-decide Free-Lie       Free-other     = there (λ ())
class-decide Free-other     Free-monoid    = there (λ ())
class-decide Free-other     Free-F2-module = there (λ ())
class-decide Free-other     Free-cyclic    = there (λ ())
class-decide Free-other     Free-relation  = there (λ ())
class-decide Free-other     Free-CCC       = there (λ ())
class-decide Free-other     Free-Lie       = there (λ ())
