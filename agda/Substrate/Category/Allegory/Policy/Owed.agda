------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.Owed
--
-- Defines: Owed
--
-- THE MINIMUM STILL OWED — a ratchet, read as a residual.
--
-- A paydown-only ratchet over a materialized census is the repo's own
-- policy shape (feedback_policy_is_a_ratchet_over_census): baseline plus
-- compare plus auto-lower, never a frozen ALLOW-list.  Written as a
-- relation: with `T` the baseline and `R` the current state, the ratchet
-- admits exactly the moves that shrink `R ∖ T`.  `∖-adjˡ` is what makes
-- "the minimum still owed" a CONSTRUCTION rather than a phrase:
--     (R ⨾ S) ⊆ T  →  S ⊆ (R ∖ T)
-- reads "if doing R then S lands within budget, S is within what is owed."
--
-- ⚑ THIS IS WHY THE RESIDUAL HAD TO COME BACK.  `_⊆_` asks whether a
-- module complies; `_∧_` asks what satisfies both constraints; only `_∖_`
-- asks what is the LEAST work that discharges the gap.  Satisfaction
-- questions were answerable all along ("78 build-failed, 363 blocked");
-- the obligation question was not, and it is the one a paydown needs.
--
-- ⚑⚑ AND ZERO-TOLERANCE IS THIS TERM AT `T = ∅`.  The operator: "I
-- dislike baselines.  I prefer 'you don't get a pass'."  An empty
-- baseline file records no exceptions, so `R ∖ ∅` is the whole of `R` —
-- every offender is owed, nothing is grandfathered.  So the 8 ok / 8
-- zero-tolerance split across this repo's 16 ratchets is not two designs;
-- it is two values of one parameter, and "no pass" is the residual at its
-- strongest rather than a different mechanism.  An empty baseline also
-- cannot drift: `paid` is always empty, so the `write and not added`
-- guard can never lower it into forgiving something.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.Owed where

open import Substrate.Category.Allegory.Division.Backslash
open import Substrate.Category.Allegory.Policy.Corpus
open import Substrate.ShadowArchitecture.Loop


-- `state` relates a gate to the offenders present now; `budget` relates a
-- gate to what its baseline permits.  `Owed` is the residual: the
-- weakest thing that, composed after the current state, still lands
-- within budget.  At an empty budget it is the entire state — which is
-- the zero-tolerance reading, obtained by instantiation rather than by a
-- second definition.
Owed : {Gate Offender Permitted : Set} → Corpus Gate
     → (Gate → Offender → Set) → (Gate → Permitted → Set)
     → Offender → Permitted → Set
Owed _ state budget = state ∖ budget
