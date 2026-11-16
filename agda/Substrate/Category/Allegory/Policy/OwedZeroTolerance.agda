------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.OwedZeroTolerance
--
-- Defines: owed-zero-tolerance
--
-- ⚑ THE INSTANTIATION THAT TESTS THE CORRESPONDENCE, rather than
-- asserting it.  `Owed` says a ratchet's obligation is `state ∖ budget`.
-- If that is the right reading, then the operator's preferred setting —
-- "I dislike baselines.  I prefer 'you don't get a pass'" — must come out
-- as the SAME term at an empty budget, not as a second mechanism.
--
-- It does, and this is the proof: at `budget = λ _ _ → ⊥` (an empty
-- baseline file records no exceptions), `Owed` is inhabited exactly when
-- the state at that gate is EMPTY.  Every offender is owed; nothing is
-- grandfathered.  So the 8-ok / 8-zero-tolerance split across this repo's
-- 16 ratchets is two values of one parameter, and no separate
-- zero-tolerance predicate is needed.
--
-- ⚑ AND THE PROOF IS `λ _ ()` — ABSURD-ELIMINATION, WHICH IS THE POINT.
-- The residual `(state ∖ ⊥) o p` unfolds to `(g : Gate) → state g o → ⊥ p`
-- … but `⊥` has no inhabitants, so the obligation is dischargeable only
-- by refuting its premise.  That is what "no pass" MEANS operationally:
-- there is no evidence you could supply that discharges an offender
-- except its absence.  A non-empty baseline, by contrast, hands you the
-- inhabitants that discharge it — which is precisely the pass.
--
-- ⚑ THIS IS ALSO WHY AN EMPTY BASELINE CANNOT DRIFT, stated structurally
-- rather than as a property of the python.  `paid` is always empty
-- because there is nothing to pay down INTO; the `write and not added`
-- guard has no branch that could lower it.  The Agda says the same: ⊥ has
-- no constructor, so no amount of writing can add one.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.OwedZeroTolerance where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Category.Allegory.Division.Backslash
open import Substrate.Category.Allegory.Policy.Corpus
open import Substrate.Category.Allegory.Policy.Owed
open import Substrate.ShadowArchitecture.Loop


-- A gate whose census finds no offender at all owes nothing, whatever
-- its budget: the obligation is vacuous because its premise is.
owed-empty-state : {Gate Offender Permitted : Set} (c : Corpus Gate)
                 → (budget : Gate → Permitted → Set)
                 → (o : Offender) (p : Permitted)
                 → Owed c (λ _ _ → ⊥) budget o p
owed-empty-state _ _ _ _ _ ()

-- ⚑ THE ZERO-TOLERANCE READING.  With an EMPTY budget, an offender that
-- is actually present cannot be discharged — the residual demands a
-- ⊥ and none exists.  So `Owed` at an empty baseline is exactly "every
-- offender is owed", which is the no-pass policy, obtained by
-- instantiation and not by a separate definition.
-- ⚑ `Permitted` STAYS A PARAMETER.  My first cut instantiated it at `Set`
-- by passing `⊥` as the permitted VALUE — and agda refused with
-- `Set₁ != Set`, in the module arguing that Set₁ is always an
-- instantiation defect.  Exactly the Rel-Allegory shape: the definition
-- was fine, `Obj := Set` was not.  Quantify over the inhabitants of
-- Permitted; never let the value slot BE the universe.
owed-zero-tolerance : {Gate Offender Permitted : Set} (c : Corpus Gate)
                    → (state : Gate → Offender → Set)
                    → (g : Gate) (o : Offender) → state g o
                    → (p : Permitted) → Owed c state (λ _ _ → ⊥) o p → ⊥
owed-zero-tolerance _ _ g o present _ k = k g present
