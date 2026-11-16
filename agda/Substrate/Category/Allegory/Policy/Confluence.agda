------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.Confluence
--
-- Defines: policy-confluent
--
-- ⚑ THE ONLY THEOREM ON THIS BOARD.  The four siblings state policies;
-- this one states a CONSEQUENCE, and it is the property the pipeline
-- actually needs: once the shape function is deterministic, splitting and
-- deduplicating COMMUTE.  Apply them in either order, land in the same
-- place.
--
-- It is `map-meet-⊇-pointfree` (StencilDedekindCollapse.agda:41) under
-- the policy reading:
--     ((f ⨾ S) ∧ (f ⨾ T)) ⊆ (f ⨾ (S ∧ T))
-- "maps preserve meets", proved point-free from `modular` plus
-- `deterministic` — NOT assumed, and not proved for arbitrary relations.
-- Determinism is the hypothesis, which is exactly why the shape-hash
-- defects were not cosmetic: each one broke the precondition of the
-- confluence the whole split/dedupe pipeline rests on.
--
-- ⚑ SO THE HASH DEFECTS AND THE PIPELINE ORDER ARE ONE ISSUE, not two.
-- With `f` non-deterministic, `(f ⨾ S) ∧ (f ⨾ T)` may strictly exceed
-- `f ⨾ (S ∧ T)`: deduping first and splitting first can disagree.  The
-- π-typing fix in `_agdatext.shape_decls` restored the hypothesis, so it
-- restored the confluence — and that is a stronger statement than "the
-- hash reports better numbers now."
--
-- ⚑ THE MAP IS THE SHAPE FUNCTION, and it enters as a `Map` bundle
-- (Maps.agda:110) carrying its relation as a PARAMETER — the Set₀ form.
-- The ex-Σ-holder `Map A B = Σ (Rel A B) isMap : Set₁` is what that
-- record replaced, and its own note records the reason the Σ version was
-- kept so long: "the 'genuine Σ-holder' label was the wall-reflex."
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.Confluence where

open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Maps
open import Substrate.Category.UniversalProperty.StencilDedekindCollapse
open import Substrate.Category.Allegory.Policy.Corpus


-- Given a deterministic shape map `f`, the two orders agree: taking the
-- meet after mapping is no weaker than mapping the meet.  `S` and `T` are
-- the two policy constraints (conservation and granularity); `f` is the
-- shape function that licenses collapse.
policy-confluent : {Site Shape Target : Set} → Corpus Site
                 → (f : Site → Shape → Set) → (det : deterministic f)
                 → (S T : Shape → Target → Set)
                 → ((f ⨾ S) ∧ (f ⨾ T)) ⊆ (f ⨾ (S ∧ T))
policy-confluent _ f det S T = map-meet-⊇-pointfree f det S T
