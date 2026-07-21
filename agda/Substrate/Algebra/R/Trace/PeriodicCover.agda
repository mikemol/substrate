{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.PeriodicCover — ⟡cover-periodic-streams.
--
-- THE COVER over the periodic-`RealTrace` cluster. Search "constant stream",
-- "periodic stream", "repeat", "const-trace", "alternating", "eventually
-- constant", "period", "cycle" and land HERE.
--
-- ⚑ WHY THIS EXISTS — DISCOVERABILITY, NOT NOVELTY. Nothing below is a new
-- theorem; every member already existed and every proof is `refl`/`head~` deep.
-- It is built because the members were NOT FINDABLE: a saturation pass over
-- this exact cluster predicted three source locations and got three wrong,
-- and did not find the alternating stream at all (it already existed, with its
-- behaviour proven). `catalog/reuse-index.md` cannot help — it indexes
-- STRUCTURES (`data`/`record`), and every member here is a copattern-defined
-- FUNCTION on the coinductive record `RealTrace` (grep it: `repeat`,
-- `const-trace`, `ana` = 0 hits; `RealTrace` = 3). So the reuse-search
-- discipline ("most 'build X' is really 'instantiate the X that exists'")
-- fails SILENTLY on this cluster. A construction can owe a cover for
-- discoverability even when it owes nothing for novelty.
--
-- THE APEX. Every member is `OrbitCover.cover = ana orbit-coalg` at a
-- different finite orbit (S, next, obs):
--   period 1  — `repeat n`      = the stationary orbit (S = ℕ, next = id, obs = id)
--   period 1  — `const-trace v` = THE SAME COPATTERN in a second file (a live duplicate)
--   period 2  — `alt`           = the Bool-flip orbit (S = Bool, next = not, obs = boolToℕ ∘ not)
--   eventually
--   period 1  — `qToRℚ q`       = the ℚ orbit, which junk-pads to a fixpoint
--                                 (`qStep (a , zero) = a , (a , zero)`,
--                                  R.Trace.RationalAdjunction:62)
--
-- AND THE TWO DISCRIMINATION LEMMAS ARE ONE LEMMA AT TWO PERIODS. Both
-- `cover←` (UniversalProperty.ExtrudeCoEmitCyclicGrading:28-29) and
-- `~-discriminates` (R.Trace.OrbitAudit:51-53) are `head~` — read off the
-- head, because `head (ana c s) ≡ proj₁ (c s)` is `refl` (Final:81-82). The
-- apex `orbit-discriminates` is stated once below; both are its instances,
-- and `repeat-discriminates` derives one of them THROUGH the apex to show the
-- covering is load-bearing rather than decorative.
--
-- HONEST SCOPE. This module is a COVER, not a refactor: it does not delete the
-- duplicate. `const-trace` lives inside a parameterized `module Faithful` whose
-- parameters it never uses; `const-trace-is-repeat` WITNESSES the duplication
-- as a term so the dedup is checkable rather than asserted. Retiring it is a
-- separate, importer-touching change.
--
-- Everything here is `refl`/copattern deep; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.PeriodicCover where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Bool using (Bool; not; boolToℕ) renaming (true to tt; false to ff)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-sym; ~-trans)
open import Substrate.Algebra.R.Trace.OrbitUniversality using (module OrbitCover)
open import Substrate.Algebra.R.Trace.OrbitFaithful using (module Faithful)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitCyclicGrading using (repeat)

------------------------------------------------------------------------
-- 1. THE APEX — discrimination, stated ONCE over an arbitrary finite orbit.
--    `head (cover s)` reduces to `obs s` (ana-head is refl), so bisimilar
--    covers have equal observations. This is the single lemma that
--    `cover←` and `~-discriminates` each instantiate.
------------------------------------------------------------------------

module _ (S : Set) (next : S → S) (obs : S → ℕ) where

  open OrbitCover S next obs using (cover)

  orbit-discriminates : {s₁ s₂ : S} → cover s₁ ~ cover s₂ → obs s₁ ≡ obs s₂
  orbit-discriminates p = head~ p

------------------------------------------------------------------------
-- 2. PERIOD 1 — `repeat` IS the stationary orbit's cover.
--    S = ℕ, next = id, obs = id: observe the point, stay put.
------------------------------------------------------------------------

open OrbitCover ℕ (λ v → v) (λ v → v) using () renaming (cover to stationary)

repeat-is-stationary : (n : ℕ) → repeat n ~ stationary n
head~ (repeat-is-stationary n) = refl
tail~ (repeat-is-stationary n) = repeat-is-stationary n

-- the apex covers the ≡-end of the cyclic grading: `cover←` DERIVED, not restated.
repeat-discriminates : {m n : ℕ} → repeat m ~ repeat n → m ≡ n
repeat-discriminates {m} {n} p =
  orbit-discriminates ℕ (λ v → v) (λ v → v)
    (~-trans (~-sym (repeat-is-stationary m))
             (~-trans p (repeat-is-stationary n)))

------------------------------------------------------------------------
-- 3. THE DUPLICATE, WITNESSED. `Faithful.const-trace` is `repeat` under a
--    second name in a second file; its module parameters are unused, so any
--    instantiation exhibits the same stream. This is the `⟡A4` dedup idiom
--    (OrbitAudit:23,33 collapsed `flip`→`not`, `bobs`→`boolToℕ ∘ not`) applied
--    to the constant stream — a THIRD one must not be introduced.
------------------------------------------------------------------------

bobs : Bool → ℕ
bobs b = boolToℕ (not b)

open Faithful Bool not bobs using (const-trace)

const-trace-is-repeat : (v : ℕ) → const-trace v ~ repeat v
head~ (const-trace-is-repeat v) = refl
tail~ (const-trace-is-repeat v) = const-trace-is-repeat v

------------------------------------------------------------------------
-- 4. PERIOD 2 — the alternating stream, NAMED. It already existed as the
--    Bool-flip instance of `cover` (OrbitAudit:30-35 builds it and proves
--    0,1,0,1 by `refl` at :80-85) but under no findable name, which is how a
--    saturation pass came to plan building it from scratch. Named here, with
--    its first two observations re-checked so this module stands alone.
------------------------------------------------------------------------

open OrbitCover Bool not bobs using () renaming (cover to alt-cover)

alt : RealTrace
alt = alt-cover tt

alt-head : head alt ≡ zero
alt-head = refl

alt-tail-head : head (tail alt) ≡ suc zero
alt-tail-head = refl

alt-period-2 : tail (tail alt) ≡ alt
alt-period-2 = refl

------------------------------------------------------------------------
-- 5. NON-VACUITY of the apex: `~` genuinely discriminates on this orbit, so
--    `orbit-discriminates` is not the trivial "everything agrees". This is
--    `OrbitAudit.~-discriminates`' content, obtained HERE through the apex
--    (period 2 rather than period 1) — the second instance that makes §1 a
--    cover rather than a renaming.
------------------------------------------------------------------------

alt-discriminates : alt-cover tt ~ alt-cover ff → zero ≡ suc zero
alt-discriminates = orbit-discriminates Bool not bobs
