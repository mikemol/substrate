{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalRank — ⟡diagonal-topological-window: the "finite
-- window" (221) is the FINITE-RANK SPECIAL CASE. The dof invariant (224, `cantor`) is GENERIC in
-- the adversary's type A — it never used finiteness — so it ALREADY covers INFINITE-rank
-- adversaries. For A = ℕ (a countably-infinite frozen generator), STILL no surjection
-- ℕ → (ℕ → Bool): the observer P ℕ (uncountable, 2^ℵ₀) strictly exceeds it. "The next larger
-- infinite." The SAME diagonal, at an infinite adversary.
--
-- THE WIN AT ANY RANK = strictly-larger-always-exists (`cantor`, UNCONDITIONAL — |A| < |P A| for
-- every A, finite or infinite) CONDITIONED ON the adversary being FROZEN (222, wire-2 cut) so it
-- CANNOT ESCALATE its rank in response. BOTH are needed:
--   * without freezing, it's an unbounded tower (the cardinal/ordinal hierarchy has NO top) — no
--     terminal winner, just escalation;
--   * with freezing, the observer responds to a FIXED-rank adversary and takes one level up,
--     which is STABLE — a terminal win at any rank, because the adversary can't reach back up.
-- So ⟡diagonal-topological-window = 224 (Cantor: strictly-larger-exists) ∧ 222 (frozen: no
-- escalation). The two prior results COMBINE to give the infinite-rank case.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalRank where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: cantor-ℕ (= cantor at ℕ). Everything else in these comments — 'infinite rank still loses', 'the next larger infinite', 'the win is stable because frozen' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the frozen-adversary / no-escalation claim (a prose model, not formalised here).

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.DiagonalDoF using (cantor)

------------------------------------------------------------------------
-- THE INFINITE-RANK CASE IS THE SAME THEOREM: `cantor` is generic in A, so instantiate it at the
-- countably-infinite adversary ℕ. No surjection ℕ → (ℕ → Bool) — the observer P ℕ (uncountable)
-- strictly exceeds the adversary ℕ (countable). "The next larger infinite" (2^ℵ₀ > ℵ₀), CHECKED.
------------------------------------------------------------------------
cantor-ℕ : (f : ℕ → (ℕ → Bool)) → Σ (ℕ → Bool) (λ g → (n : ℕ) → ¬ (f n ≡ g))
cantor-ℕ = cantor

-- The finite-window case is the SAME `cantor` at a finite A (finite rank ⟹ finite excess ⟹
-- finite lookahead). cantor-ℕ shows it did not depend on that: infinite rank, still dominated.

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the window is the observer's RANK strictly exceeding the
-- adversary's, at ANY rank; strictly-larger-exists ∧ frozen ⟹ stable): the either/or "does the
-- escape need the adversary to be finite-rank?" bottoms out: NO. `cantor` (224) is generic in A;
-- cantor-ℕ instantiates it at an infinite adversary — the observer is the next larger infinite.
-- The finite window (221) is the finite-rank special case; the general invariant is rank(obs) >
-- rank(adv), and strictly-larger-ALWAYS-exists (Cantor for cardinals — the width; ordinal
-- successor/limit for depth). The win is STABLE because the adversary is FROZEN (222) — it can't
-- escalate its rank in response, so the observer's one-level-up is terminal, not a move in an
-- escalating tower.
--
-- HONEST PRECISION on "different sizes of countable infinities": all countable SETS have the same
-- CARDINALITY (ℵ₀) — so if "rank" is width/cardinality, a countable adversary's strictly-larger
-- is UNCOUNTABLE (2^ℵ₀, cantor-ℕ). But if "rank" is DEPTH/ORDER-TYPE — the ORDINAL rank of the
-- generator's unfolding (e.g. its Cantor-Bendixson / Borel rank — the descriptive-set-theoretic
-- "topological complexity") — then countable ordinals DO come in genuinely different sizes
-- (ω < ω+1 < … < ε₀ < …, all countable-as-sets, distinct order-types), and the observer takes the
-- NEXT COUNTABLE ORDINAL. Under THAT reading the phrase is precise: different countable ranks.
-- So "rank" has two faces — WIDTH (cardinal, Cantor, checked here at ℕ) and DEPTH (ordinal /
-- topological complexity, the finer coinductive-lookahead reading). Both: strictly-larger-exists.
--
-- HONEST BOUNDARY (⟡H-overclaim): (a) cantor-ℕ is the WIDTH/cardinal backstop, CHECKED. (b) The
-- DEPTH/ordinal reading (the "topological window" as the adversary's ordinal/CB-rank, observer =
-- next ordinal) is stated precisely but NOT formalized here (a real ordinal development) —
-- ⟡diagonal-ordinal-window. (c) The win is CONDITIONAL on the frozen adversary (222); without it,
-- unbounded escalation, no winner. (d) Structural/cardinality fact — the theorems STAND.
------------------------------------------------------------------------
