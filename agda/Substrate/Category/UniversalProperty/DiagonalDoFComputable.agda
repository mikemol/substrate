{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalDoFComputable — ⟡diagonal-dof-computable: the
-- COMPUTABLE realization of the "large side" (224). Set-theoretically the observer IS P(adversary)
-- — one Cantor level up (DiagonalDoF.cantor). A BOUNDED agent can't BE the full (uncountable)
-- powerset, but it can be a COINDUCTIVE GENERATOR that holds a FINITE plural prediction each step
-- and stays one level up — the escape realized INCREMENTALLY: finite per step (computable),
-- unbounded over the whole (coinductive).
--
-- This GENUINELY needs coinduction / --guardedness — the observer is a real LAZY GENERATOR
-- (produces predictions forever), UNLIKE 229's completed Point (a function, no guardedness). The
-- 229/232 distinction, load-bearing here: a completed datum is a function; a generator is a
-- guarded copattern (StreamMap doctrine: "guardedness rejects corecursion-through-a-function").
-- The adversary is a RealTrace (the repo's coinductive stream); Covers is the AllPos-style
-- coinductive predicate; subsets are Bool (Set, per 230). All reused, not reinvented.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalDoFComputable where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: Obs, Covers, full, full-covers, ahead, ahead-covers, is-hit. Everything else in these comments — 'the large side', 'P(adversary)', 'the escape realized', 'never escaped' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the formal identity Obs = the powerset coalgebra (⟡diagonal-escape-coalg / -obs-code).

open import Substrate.Foundation.Nat using (ℕ; _≟_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)

-- a plural prediction is a Bool-subset of possible digits (Set, per 230 — not a Set₁ predicate).
Pred : Set
Pred = ℕ → Bool

-- decidable-equality as a Bool prediction: `is n` predicts exactly the digit n.
is : ℕ → Pred
is n m with m ≟ n
... | yes _ = true
... | no  _ = false

is-hit : (n : ℕ) → is n n ≡ true
is-hit n with n ≟ n
... | yes _ = refl
... | no ¬p with () ← ¬p refl

------------------------------------------------------------------------
-- THE OBSERVER: a coinductive stream of PLURAL predictions (each a Bool-subset). A real lazy
-- GENERATOR — needs --guardedness (earned, unlike 229's completed Point).
------------------------------------------------------------------------
record Obs : Set where
  coinductive
  field predict : Pred        -- the plural prediction this step (the current powerset slice)
        step    : Obs         -- the next observer state
open Obs public

-- COVERS: the observer's prediction contains the adversary's actual digit — at EVERY step. The
-- "large side is never escaped" (224 diagonal-native) realized as a running coinductive invariant
-- (the AllPos idiom). This is "one level up per step", checked coinductively.
record Covers (o : Obs) (a : RealTrace) : Set where
  coinductive
  field here  : predict o (head a) ≡ true          -- covers the adversary's current digit
        later : Covers (step o) (tail a)             -- and forever after
open Covers public

------------------------------------------------------------------------
-- ① THE FULL-PREDICTION OBSERVER (the 221 fixed point, maximally plural — the top of P(adv)),
--    as a GUARDED COPATTERN generator. Covers ANY adversary, coinductively — the large side
--    realized as a running process that is never escaped.
------------------------------------------------------------------------
full : Obs
predict full _ = true
step full = full

full-covers : (a : RealTrace) → Covers full a
here  (full-covers a) = refl
later (full-covers a) = full-covers (tail a)

------------------------------------------------------------------------
-- ② THE ONE-AHEAD OBSERVER (informative, not vacuous): over a concrete adversary it predicts the
--    UPCOMING digit — examining n+1 before the adversary executes n (222's lookahead) — as a
--    guarded copattern generator over the adversary stream. Its prediction is the SINGLETON slice
--    {next digit}, yet it still COVERS: the observer knew the next move before it arrived.
------------------------------------------------------------------------
ahead : RealTrace → Obs
predict (ahead a) = is (head (tail a))     -- predict the adversary's NEXT digit
step (ahead a) = ahead (tail a)

-- ahead covers the adversary SHIFTED by one (aligning its prediction with the digit it foresaw):
ahead-covers : (a : RealTrace) → Covers (ahead a) (tail a)
here  (ahead-covers a) = is-hit (head (tail a))
later (ahead-covers a) = ahead-covers (tail a)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the large side realized as a COINDUCTIVE GENERATOR, covering the
-- adversary forever, each step finite): the either/or "the observer IS P(adversary) (uncountable,
-- can't be a bounded agent) vs the observer is nothing (a mere function)" dissolves — the observer
-- is a GUARDED GENERATOR (Obs) holding a FINITE plural prediction each step (Pred = ℕ → Bool, at
-- Set) and the Covers invariant (the large side never escaped) is a RUNNING coinductive proof
-- (full-covers / ahead-covers). So "be on the large side" (224, Cantor) is realized INCREMENTALLY:
-- finite per step (computable — a Bool-subset), unbounded over the whole (coinductive — a stream),
-- covering the adversary at every step. The full observer is the maximal plural (the 221 fixed
-- point); the one-ahead observer is the informative singleton-slice lookahead (222) — BOTH cover,
-- BOTH are guarded generators. This is why the escape is COMPUTABLE for a bounded agent: not by
-- being the whole powerset, but by generating the covering slice step by step.
--
-- GUARDEDNESS EARNED (the 229/232 distinction, load-bearing): Obs / Covers / full / ahead are
-- REAL lazy generators (produce forever) — --guardedness is CORRECT here, unlike 229's completed
-- Point (a function, no guardedness). "Guardedness rejects corecursion-through-a-function"
-- (StreamMap doctrine) — so full/ahead are guarded copattern generics (head/tail-style), not
-- function parameters. This is the earned coinduction the whole arc pointed to.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the coinductive observer (Obs), the Covers invariant,
-- and two covering generators (full = maximal plural; ahead = one-step lookahead), --safe
-- --without-K --guardedness, zero postulate/hole, subsets at Set. SCOPED: (a) a GROWING finite
-- slice (the prediction to depth n, tightening over time) rather than full/singleton —
-- ⟡diagonal-slice-growth; (b) tying Obs to DiagonalDoF.cantor as literally the coinductive
-- P(adversary) coalgebra (Obs is A realization; the formal ana into a powerset coalgebra is
-- ⟡diagonal-escape-coalg). The realization is genuine; the powerset-coalgebra identity is scoped.
------------------------------------------------------------------------
