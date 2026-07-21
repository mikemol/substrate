{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.EventualPeriod — ⟡eventual-period-separates.
--
-- EVENTUAL PERIOD IS A `~`-INVARIANT, AND IT SEPARATES. Every `qToRℚ q`
-- reaches a constant tail (eventual period 1); `alt` never does (period 2);
-- 1 ≢ 2. A POSITIVE statement about an invariant computed on both sides.
--
-- ⚑ THE FRAMING IS THE POINT — this module deliberately contains NO `¬`.
-- An earlier label for this arc was "⟡not-cf-rational", and it was wrong twice:
--   (1) "not" framed a CONSTRUCTIVE SEPARATION as a REFUTATION. Nothing here is
--       refuted. `settles` CONSTRUCTS the settling depth and value; `alt`'s
--       period is READ OFF its head. The clash is then observed, not derived
--       from an assumption — the `orbit-discriminates` shape (PeriodicCover §1):
--       read an observable, see it differ. Every statement below therefore ends
--       in `zero ≡ suc zero`, an absurd EQUATION, and the caller may do the `()`.
--       (A constructive `¬P = P → ⊥` would have been sound — LEM is `P ⊎ ¬P`,
--       DNE is `¬¬P → P`, and neither appears — but the SHAPE of the statement
--       is what carries the intent, and a derived equation carries it better.)
--   (2) "cf-rational" asserted a tie the construction does not wire. In THIS
--       repo `qToRℚ`'s image is NOT the rationals: `qStep` junk-pads
--       (`qStep (a , zero) = a , (a , zero)`, RationalAdjunction:62), so the
--       image is the EVENTUALLY-CONSTANT streams — which is exactly why
--       `sqrt2 ~ qToRℚ (2 , 2)` is provable and why the original irrationality
--       claim was false as posed. So the predicate this arc characterizes is
--       EVENTUALLY-CONSTANT, and it is named that.
--
-- THIS MODULE LANDS ON ⟡cover-periodic-streams (`R.Trace.PeriodicCover`): `alt`
-- and `alt-cover` are taken from the cover rather than rebuilt, and the period-2
-- separation is the cover's `orbit-discriminates` shape one level up (iterated).
--
-- --safe --without-K --guardedness; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.EventualPeriod where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Bool using (Bool; not) renaming (true to tt; false to ff)
open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-trans)
open import Substrate.Algebra.R.Trace.RationalAdjunction using (qToRℚ)
open import Substrate.Algebra.R.Trace.PeriodicCover using (alt; alt-cover)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitCyclicGrading using (repeat)

------------------------------------------------------------------------
-- 0. Iterated tail — the depth at which an invariant is read. Searched for an
--    existing one (`drop`/`iterate`/`nth`/`take` over R.Trace): the `nth`s
--    index Lists, `iterate` iterates a refinement operator Φ, and `take`
--    discards the residual stream. So this is genuinely new, and it peels from
--    the OUTSIDE so each step reduces definitionally through `ana-tail`.
------------------------------------------------------------------------

tail-iterate : ℕ → RealTrace → RealTrace
tail-iterate zero    x = x
tail-iterate (suc n) x = tail-iterate n (tail x)

tail-iterate-cong : (n : ℕ) {x y : RealTrace} → x ~ y → tail-iterate n x ~ tail-iterate n y
tail-iterate-cong zero    p = p
tail-iterate-cong (suc n) p = tail-iterate-cong n (tail~ p)

------------------------------------------------------------------------
-- 1. EVENTUALLY CONSTANT — the predicate `qToRℚ`'s image actually satisfies.
--    NOT called `IsRational`: the junk-pad means the image is this, not ℚ.
------------------------------------------------------------------------

EventuallyConstant : RealTrace → Set
EventuallyConstant x = Σ ℕ (λ n → Σ ℕ (λ c → tail-iterate n x ~ repeat c))

------------------------------------------------------------------------
-- 2. PERIOD 1, POSITIVELY — every `qToRℚ q` IS eventually constant. The
--    settling depth and value are CONSTRUCTED, by well-founded recursion on the
--    denominator: `qStep (a , suc b)` steps to `(suc b , a mod-suc b)` and
--    `mod-suc-bound` is the descent. At b = 0 the junk-pad IS the constant tail.
--    ⚑ `Foundation.WellFounded` exports `Acc`/`acc` and NO recursor, so this
--    pattern-matches `acc rec` directly — the repo's own idiom (`acc-suc`).
------------------------------------------------------------------------

-- the junk-pad is the period-1 orbit: qStep (a , 0) = a , (a , 0), so the
-- corecursive call sits under `tail~` unchanged — guarded, no transport.
pad-is-constant : (a : ℕ) → qToRℚ (a , zero) ~ repeat a
head~ (pad-is-constant a) = refl
tail~ (pad-is-constant a) = pad-is-constant a

qToRℚ-eventually-constant : (q : ℕ × ℕ) → EventuallyConstant (qToRℚ q)
qToRℚ-eventually-constant (a , b) = go a b (<-wellFounded b)
  where
    go : (a b : ℕ) → Acc _<_ b → EventuallyConstant (qToRℚ (a , b))
    go a zero    _         = zero , a , pad-is-constant a
    go a (suc b) (acc rec) with go (suc b) (a mod-suc b) (rec (a mod-suc b) (mod-suc-bound a b))
    ... | n , c , p = suc n , c , p

------------------------------------------------------------------------
-- 3. PERIOD 2, POSITIVELY — `alt` is never constant, at any depth. The base is
--    two `head~` reads at consecutive depths: the Bool-flip orbit observes 0
--    then 1, so a constant stream would have to be both. This is
--    `PeriodicCover.orbit-discriminates` at period 2, iterated.
--    ⚑ `tail (alt-cover b) = alt-cover (not b)` DEFINITIONALLY (`ana-tail` is
--    `refl`), so the depth recursion just flips the state.
------------------------------------------------------------------------

alt-cover-not-constant : (b : Bool) (c : ℕ) → alt-cover b ~ repeat c → zero ≡ suc zero
alt-cover-not-constant tt c p = trans (head~ p) (sym (head~ (tail~ p)))
alt-cover-not-constant ff c p = trans (head~ (tail~ p)) (sym (head~ p))

alt-no-constant-tail : (b : Bool) (n c : ℕ)
                     → tail-iterate n (alt-cover b) ~ repeat c → zero ≡ suc zero
alt-no-constant-tail b zero    c p = alt-cover-not-constant b c p
alt-no-constant-tail b (suc n) c p = alt-no-constant-tail (not b) n c p

-- `alt` is NOT eventually constant — stated as the absurd equation, not as `¬`.
alt-not-eventually-constant : EventuallyConstant alt → zero ≡ suc zero
alt-not-eventually-constant (n , c , p) = alt-no-constant-tail tt n c p

------------------------------------------------------------------------
-- 4. THE SEPARATION. Eventual constancy is a `~`-invariant (transport it along
--    a bisimulation with `tail-iterate-cong` + `~-trans`), `qToRℚ q` has it for
--    every `q`, and `alt` does not. So no `q` puts `alt` in `qToRℚ`'s image —
--    obtained by READING the invariant on both sides, never by refutation.
------------------------------------------------------------------------

eventually-constant-invariant : {x y : RealTrace}
                              → x ~ y → EventuallyConstant y → EventuallyConstant x
eventually-constant-invariant p (n , c , q) =
  n , c , ~-trans (tail-iterate-cong n p) q

eventual-period-separates : (q : ℕ × ℕ) → alt ~ qToRℚ q → zero ≡ suc zero
eventual-period-separates q p =
  alt-not-eventually-constant
    (eventually-constant-invariant p (qToRℚ-eventually-constant q))
