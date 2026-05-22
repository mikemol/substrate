------------------------------------------------------------------------
-- Substrate.Lojban.Bridi
--
-- L5 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Sentence application: a bridi is the result of applying a Selbri n
-- to a Vec Sumti n of arguments. This IS the n-ary morphism
-- application from L1; the Bridi record makes the structural parts
-- (selbri + argument vector) introspectable while exposing the
-- semantic value via `interpret`.
--
-- Per [[feedback-categorical-name-first]]: this is the standard
-- n-ary morphism application; the substrate's universal-property
-- discipline ([[feedback-universal-property-discipline]]) says reach
-- for the universal property before per-instance unfolding.
--
-- Per [[feedback-grothendieck-coherence-rule]]: bridi-postcompose and
-- bridi-precompose are provided as functorial handles; the
-- compatibility lemmas with `interpret` are stated here at L5 and
-- consumed by L7.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Bridi where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Lojban.PlaceStructure
  using (Selbri; mkSelbri; apply; selbri-postcompose; selbri-precompose)

private
  variable
    ℓA ℓB ℓC ℓD : Level
    n : ℕ

------------------------------------------------------------------------
-- 1. The Bridi record.
--
-- Arity-indexed so functoriality lemmas can range over a fixed n.
-- The semantic value is `interpret`; the structural pair (selbri,
-- args) is preserved for introspection (L9 examples display them;
-- L10 routes them into the CCC).
------------------------------------------------------------------------

record Bridi (n : ℕ) (Sumti : Set ℓA) (Sem : Set ℓB)
    : Set (ℓA ⊔ ℓB) where
  constructor mkBridi
  field
    selbri : Selbri n Sumti Sem
    args   : Vec Sumti n

open Bridi public

------------------------------------------------------------------------
-- 2. Semantic interpretation.
--
-- The n-ary morphism application: apply the selbri to its argument
-- vector to obtain the semantic value.
------------------------------------------------------------------------

interpret :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  Bridi n Sumti Sem → Sem
interpret b = apply (selbri b) (args b)

------------------------------------------------------------------------
-- 3. Post-composition on a bridi (functorial in Sem).
--
-- Lifts h : Sem → Sem' to a transformation Bridi n Sumti Sem →
-- Bridi n Sumti Sem' by post-composing the selbri.
------------------------------------------------------------------------

bridi-postcompose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} →
  (Sem → Sem') → Bridi n Sumti Sem → Bridi n Sumti Sem'
bridi-postcompose h b = mkBridi (selbri-postcompose h (selbri b)) (args b)

------------------------------------------------------------------------
-- 4. Interpret-postcompose coherence.
--
-- Interpreting a post-composed bridi factors through the codomain
-- function: this is the n-ary application's functoriality at the
-- bridi level. L7 lifts to identity + composition laws.
------------------------------------------------------------------------

interpret-postcompose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} →
  (h : Sem → Sem') (b : Bridi n Sumti Sem) →
  interpret (bridi-postcompose h b) ≡ h (interpret b)
interpret-postcompose _ _ = refl

------------------------------------------------------------------------
-- 5. Pre-composition on the argument vector (Sumti renaming).
--
-- Lifts a substitution s : Vec Sumti' n → Vec Sumti n to a
-- transformation on the Sumti carrier. Used by L6 for cmavo that
-- rearrange arguments (deferred SE/TE/VE convert can also land here
-- when the arc grows).
------------------------------------------------------------------------

bridi-precompose :
  {Sumti Sumti' : Set ℓA} {Sem : Set ℓB} →
  (Vec Sumti' n → Vec Sumti n) →
  Vec Sumti' n →
  Bridi n Sumti Sem → Bridi n Sumti' Sem
bridi-precompose s args' b =
  mkBridi (selbri-precompose s (selbri b)) args'

------------------------------------------------------------------------
-- 6. Bridi as a convenient constructor.
--
-- `make-bridi S args = mkBridi S args` is provided as a more
-- conversational name at the sentence-construction layer; the L9
-- example sentences use it.
------------------------------------------------------------------------

make-bridi :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  Selbri n Sumti Sem → Vec Sumti n → Bridi n Sumti Sem
make-bridi = mkBridi
