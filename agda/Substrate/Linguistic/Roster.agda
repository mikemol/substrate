------------------------------------------------------------------------
-- Substrate.Linguistic.Roster
--
-- W5 (⟡rc-lang) of the Set₁-paydown: the Linguistic tier's OBJECT
-- UNIVERSE, enumerated at Set₀.
--
-- `LanguageWitness` (Substrate.Category.FreeOverBasis) was reparam-
-- eterized: `Basis`/`FreeCarrier` moved from fields (which pinned
-- the record at Set₁, quantifying over Set) to explicit PARAMETERS.
-- What remains is a genuine choice among finitely many concrete
-- instances — C2 through C7 of the Categorical Linguistics
-- Classification arc each produce exactly one witness, at its own
-- concrete (Basis, FreeCarrier) pair. That finite choice IS the
-- mission's enumerable-objects doctrine: name the objects with a
-- Set₀ `data` type, and DECODE each constructor to its concrete
-- witness rather than quantifying over an existential Set₁ family.
--
-- `Lang` is that enumeration. `Basis-of`/`FreeCarrier-of` decode a
-- `Lang` value to the (Basis, FreeCarrier) pair its LanguageWitness
-- was built at; `witness-of` decodes to the witness itself. Every
-- downstream consumer that used to range over `LanguageWitness`
-- (the morphism tier, the classification tables, the Yoneda
-- embedding) now ranges over `Lang` and reaches the witness via
-- `witness-of` — the same move as `split-Canonical` for the UP-topos
-- object universe ([[object-universe-is-split-canonical]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Roster where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)

open import Substrate.Lojban.Gismu using (Gismu)
open import Substrate.Lojban.Word Gismu using (LojbanWord)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)

open import Substrate.TokiPona.Nimi using (Nimi; nimi-count)
open import Substrate.TokiPona.SemanticSpace using (SemVec)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)

open import Substrate.Solresol.Fragment.Note using (Note)
open import Substrate.Solresol.Fragment.Word using (SolresolWord)
open import Substrate.Solresol.Fragment.Witness using (solresol-witness)

open import Substrate.Kelen.Fragment using (Relational; KelenWord; kelen-witness)

open import Substrate.Lambda.Fragment using (Combinator; SKIWord; lambda-witness)

open import Substrate.Invented.LieFragment using (LieGen; LieExpr; lie-witness)

------------------------------------------------------------------------
-- 1. The enumeration: one constructor per witness instance.
------------------------------------------------------------------------

data Lang : Set where
  lojban      : Lang
  tokipona    : Lang
  solresol    : Lang
  kelen       : Lang
  lambda-lang : Lang
  lie-lang    : Lang

------------------------------------------------------------------------
-- 2. Decode families: each Lang value's concrete Basis/FreeCarrier.
------------------------------------------------------------------------

Basis-of : Lang → Set
Basis-of lojban      = Gismu
Basis-of tokipona    = Nimi
Basis-of solresol    = Note
Basis-of kelen       = Relational
Basis-of lambda-lang = Combinator
Basis-of lie-lang    = LieGen

FreeCarrier-of : Lang → Set
FreeCarrier-of lojban      = LojbanWord
FreeCarrier-of tokipona    = SemVec nimi-count
FreeCarrier-of solresol    = SolresolWord
FreeCarrier-of kelen       = KelenWord
FreeCarrier-of lambda-lang = SKIWord
FreeCarrier-of lie-lang    = LieExpr

------------------------------------------------------------------------
-- 3. witness-of: the decode to the packaged LanguageWitness.
------------------------------------------------------------------------

witness-of : (l : Lang) → LanguageWitness (Basis-of l) (FreeCarrier-of l)
witness-of lojban      = lojban-witness
witness-of tokipona    = tokipona-witness
witness-of solresol    = solresol-witness
witness-of kelen       = kelen-witness
witness-of lambda-lang = lambda-witness
witness-of lie-lang    = lie-witness
