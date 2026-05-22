------------------------------------------------------------------------
-- Substrate.Lojban.Lujvo
--
-- L4 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Lujvo construction via Coxeter-Word composition (L2's free-merge)
-- with arity inheritance from the head gismu (tertau).
--
-- Structure: a lujvo is a (possibly empty) prefix word of modifier
-- gismu (seltau) followed by a single head gismu (tertau). Lifted to
-- LojbanWord by concatenation. Arity inherits from the head per the
-- standard Lojban convention (tanru/lujvo are right-headed).
--
-- This fragment treats lujvo as right-headed concatenations without
-- imposing rafsi-merge relations; per
-- [[feedback-comments-dont-overclaim]], full lujvo semantics in real
-- Lojban are richer than head-inheritance. The fragment intentionally
-- simplifies — the Coxeter framework supports adding rafsi-merge
-- equations at a later slice via ListPresentation.
--
-- Per [[feedback-grothendieck-coherence-rule]]: prepending modifiers
-- is associative with the word-lift; lemma `prepend-modifier-word`
-- discharges this at the syntactic level. L8 lifts to the semantic
-- monoid-homomorphism statement.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Lujvo where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (Gismu; arity)
open import Substrate.Lojban.Word Gismu
  using (LojbanWord; ε; single; free-merge; free-merge-assoc)

------------------------------------------------------------------------
-- 1. The Lujvo record.
--
-- modifiers : the seltau as a (possibly empty) word of gismu.
-- head      : the tertau, always a single gismu in this fragment.
------------------------------------------------------------------------

record Lujvo : Set where
  constructor mkLujvo
  field
    modifiers : LojbanWord
    head      : Gismu

open Lujvo public

------------------------------------------------------------------------
-- 2. Lifted word.
--
-- The LojbanWord form: modifiers ++ single head.
------------------------------------------------------------------------

lujvo-word : Lujvo → LojbanWord
lujvo-word ℓ = free-merge (modifiers ℓ) (single (head ℓ))

------------------------------------------------------------------------
-- 3. Arity inheritance.
--
-- A lujvo's place-structure size is its head gismu's arity. (Real
-- Lojban allows place-structure modification via SE/TE/VE; deferred
-- per [[project-linguistic-rosetta-arc]] §"Deferred".)
------------------------------------------------------------------------

lujvo-arity : Lujvo → ℕ
lujvo-arity ℓ = arity (head ℓ)

------------------------------------------------------------------------
-- 4. The trivial lujvo: a bare gismu with no modifiers.
------------------------------------------------------------------------

gismu-as-lujvo : Gismu → Lujvo
gismu-as-lujvo g = mkLujvo ε g

gismu-as-lujvo-word :
  (g : Gismu) → lujvo-word (gismu-as-lujvo g) ≡ single g
gismu-as-lujvo-word _ = refl

gismu-as-lujvo-arity :
  (g : Gismu) → lujvo-arity (gismu-as-lujvo g) ≡ arity g
gismu-as-lujvo-arity _ = refl

------------------------------------------------------------------------
-- 5. Prepending modifiers.
--
-- Adds a word of modifier gismu to the seltau side. Composition
-- with the lifted word is associative (lemma below).
------------------------------------------------------------------------

prepend-modifiers : LojbanWord → Lujvo → Lujvo
prepend-modifiers w ℓ = mkLujvo (free-merge w (modifiers ℓ)) (head ℓ)

prepend-modifier : Gismu → Lujvo → Lujvo
prepend-modifier g ℓ = prepend-modifiers (single g) ℓ

------------------------------------------------------------------------
-- 6. Arity is invariant under prepending modifiers.
--
-- Modifiers do not change the head; arity follows.
------------------------------------------------------------------------

prepend-modifiers-arity :
  (w : LojbanWord) (ℓ : Lujvo) →
  lujvo-arity (prepend-modifiers w ℓ) ≡ lujvo-arity ℓ
prepend-modifiers-arity _ _ = refl

------------------------------------------------------------------------
-- 7. Word-lift is functorial under prepend.
--
-- prepend-modifiers w ℓ lifted equals w ++ (ℓ lifted). This is the
-- Grothendieck-coherence obligation [[feedback-grothendieck-coherence-rule]]
-- at the syntactic layer; L8 lifts it to the semantic homomorphism.
------------------------------------------------------------------------

prepend-modifiers-word :
  (w : LojbanWord) (ℓ : Lujvo) →
  lujvo-word (prepend-modifiers w ℓ) ≡ free-merge w (lujvo-word ℓ)
prepend-modifiers-word w ℓ =
  free-merge-assoc w (modifiers ℓ) (single (head ℓ))

------------------------------------------------------------------------
-- 8. Bridge to Selbri (L1 side), via parametric denotation.
--
-- A lujvo's Selbri is its head gismu's Selbri (head-inheritance
-- semantics). Real-Lojban tanru semantics enriches this; deferred.
------------------------------------------------------------------------

module WithDenotation
  (Sumti : Set) (Sem : Set)
  (denote : (g : Gismu) → Vec Sumti (arity g) → Sem)
  where

  open import Substrate.Lojban.Gismu using (module WithDenotation)
  open Substrate.Lojban.Gismu.WithDenotation Sumti Sem denote
    using (gismu-to-selbri)
  open import Substrate.Lojban.PlaceStructure using (Selbri)

  lujvo-to-selbri : (ℓ : Lujvo) → Selbri (lujvo-arity ℓ) Sumti Sem
  lujvo-to-selbri ℓ = gismu-to-selbri (head ℓ)
