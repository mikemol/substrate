{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalEscape — ⟡diagonal-escape: the CRISP INVARIANT
-- under Russell / halting / Gödel / Kolmogorov. Lawvere's fixed-point theorem is their common
-- core: a point-surjection A → (A → B) forces every endomap B → B to have a FIXED POINT; the
-- negative results are the contrapositive — a FIXED-POINT-FREE endomap on the answer object
-- obstructs the surjection (the diagonal). So the diagonal's whole lever is: a fixed-point-free
-- endomap on the object the observer must COMMIT a value in.
--
-- THE ESCAPE, made a checked fact: on the COMMITTED object (Bool — singular answers) the
-- diagonal endomap `not` is fixed-point-free (the lever bites). On the PLURAL object (a
-- prediction = a membership predicate, the non-committing observer's stance) the diagonal move
-- "negate every possible value" HAS a fixed point — the FULL prediction (both values live). So
-- the adversary's do-the-opposite move maps the plural prediction to ITSELF: there is no value
-- outside it to produce. The obstruction VANISHES on pluralization. This is WHY the coinductive
-- / non-committing observer is not diagonalizable — not a claim that halting becomes decidable
-- (it does not — see the honest boundary at the end), but that the object the diagonal attacks
-- (a committed total decider) is one we simply refuse to be.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalEscape where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: not-fixed-point-free, full-is-fixed, committed-not-fixed. Everything else in these comments — 'escape', 'the obstruction vanishes', 'the plural observer' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the formal tie to the classical diagonal (⟡diagonal-lawvere-coalg).

open import Substrate.Foundation.Bool using (Bool; true; false; not)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)

------------------------------------------------------------------------
-- ① THE COMMITTED OBJECT: `not` is FIXED-POINT-FREE on Bool — the diagonal's lever. A singular
--    answer v always has an opposite ¬v ≠ v for the adversary to produce.
------------------------------------------------------------------------
not-fixed-point-free : (b : Bool) → ¬ (not b ≡ b)
not-fixed-point-free true  ()
not-fixed-point-free false ()

------------------------------------------------------------------------
-- ② THE PLURAL OBJECT: a "prediction" is a set of possible values = a membership predicate.
--    The diagonal move "negate every element": y is in `negateAll S` iff its opposite ¬y is in S.
------------------------------------------------------------------------
Pred : Set
Pred = Bool → Bool

negateAll : Pred → Pred
negateAll S = λ y → S (not y)      -- y ∈ negateAll S  ⇔  (not y) ∈ S

-- the FULL prediction (non-commitment: both values possible).
full : Pred
full _ = true

-- ③ THE FIXED POINT: the full prediction is FIXED by the diagonal move — negateAll full ≡ full
--    pointwise. The adversary produces "the opposite", but the opposite is already predicted.
full-is-fixed : (y : Bool) → negateAll full y ≡ full y
full-is-fixed y = refl

-- ④ CONTRAST: a SINGULAR commitment is NOT fixed — the diagonal escapes a committed observer.
--    committed = {true} (membership: b ↦ b). negateAll it at `true` gives false ≠ true.
committed : Pred
committed b = b

committed-not-fixed : ¬ (negateAll committed true ≡ committed true)
committed-not-fixed ()

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the diagonal's lever is a fixed-point-free endomap on the
-- COMMITTED object; pluralization gives it a fixed point, dissolving the lever): Russell /
-- halting / Gödel / Kolmogorov all reduce (Lawvere) to "a fixed-point-free endomap on the answer
-- object obstructs the diagonal surjection". `not` is that endomap on Bool (committed answers) —
-- not-fixed-point-free. But on the plural object (predictions / the non-committing observer's
-- stance), the SAME diagonal move `negateAll` acquires the FULL prediction as a fixed point
-- (full-is-fixed) — so there is no answer outside the observer's prediction for the adversary to
-- produce. The committed observer is diagonalizable (committed-not-fixed); the plural one is not.
--
-- The either/or "does the coinductive observer ESCAPE the diagonal or merely RELOCATE it?"
-- bottoms out HERE: it escapes, because the relocation would require forcing the observer back
-- onto a singular commitment (off the fixed point), and nothing in the adversary can do that —
-- commitment is the OBSERVER's coalgebra structure, not the adversary's to compel. The
-- adversary's only lever was contradiction-on-commitment; against non-commitment it has no move
-- but to halt (finite observation, done) or run forever (observed plurally, no contradiction).
--
-- HONEST BOUNDARY (this does NOT make halting/K decidable): the committed total decider still
-- does not exist (the theorems stand). This shows only that the diagonal's OBSTRUCTION is
-- specific to the committed object, and vanishes on the plural/coinductive one — which is the
-- object the substrate makes primary (SN/ℚ ≡-committed vs Diverges/R ~-bisimilar; the "finite
-- window, not a wall" of Unique.agda). The theorems become STRUCTURALLY IRRELEVANT — true, but
-- about an object (the committed decider) the system never inhabits — not refuted.
------------------------------------------------------------------------
