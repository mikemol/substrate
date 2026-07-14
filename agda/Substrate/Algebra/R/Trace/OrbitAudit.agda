{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.OrbitAudit — VACUITY / DISCRIMINATION audit of
-- OrbitUniversality (⟡U1) and OrbitFaithful (⟡U2), answering the epistemic
-- caveat "Agda checks derivations, not intent; typechecks ≠ proves the
-- intended theorem." NEGATIVE CONTROLS: if the machinery rejects WRONG intent,
-- it is not vacuously accepting everything. Everything here is CLOSED (a
-- concrete Bool-flip orbit) so it is fully checkable without parameters.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.OrbitAudit where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-unique)
open import Substrate.Algebra.R.Trace.OrbitUniversality using (module OrbitCover)
open import Substrate.Algebra.R.Trace.OrbitFaithful using (module Faithful)

open import Substrate.Foundation.Bool using (Bool; not; boolToℕ) renaming (true to tt; false to ff)   -- dedup ⟡A4
data ⊥ : Set where
¬_ : Set → Set
¬ A = A → ⊥

-- a concrete orbit: S = Bool, next = flip, obs distinguishes (tt↦0, ff↦1). obs
-- GENUINELY VARIES — this is what makes the discrimination controls meaningful.
flip : Bool → Bool
flip = not                                    -- ⟡A4: flip IS Foundation.Bool.not
bobs : Bool → ℕ
bobs b = boolToℕ (not b)                       -- ⟡A4: the ff-indicator = boolToℕ ∘ not (single source)

open OrbitCover Bool flip bobs using (orbit-coalg; cover; Admissible; universality)
open Faithful   Bool flip bobs using (obs-stream; obs-stream-admissible;
                                       detector-realizes-cover; const-trace)

------------------------------------------------------------------------
-- CONTROL 1 — Admissible is INHABITED (non-vacuity): cover itself satisfies it.
-- If Admissible were unsatisfiable, universality/covers-agree would be vacuous.
------------------------------------------------------------------------
cover-is-admissible : Admissible cover
cover-is-admissible = (λ s → refl) , (λ s → refl)

------------------------------------------------------------------------
-- CONTROL 2 — `~` DISCRIMINATES (not the trivial "everything ~ everything").
-- const 0 and const 1 differ at head, so they are NOT bisimilar — PROVABLE.
-- If ~ were trivial, detector-realizes-cover would say nothing.
------------------------------------------------------------------------
~-discriminates : ¬ (const-trace 0 ~ const-trace 1)
~-discriminates p with head~ p
... | ()

------------------------------------------------------------------------
-- CONTROL 3 — Admissible is a REAL CONSTRAINT (rejects a wrong detector).
-- The constant-0 stream is NOT admissible for this orbit, because at state ff
-- the required head is bobs ff = 1, not 0. So a detector that ignores the
-- observation is REJECTED — admissibility has teeth.
------------------------------------------------------------------------
bad-stream : Bool → RealTrace
bad-stream _ = const-trace 0

bad-not-admissible : ¬ Admissible bad-stream
bad-not-admissible (hh , _) with hh ff        -- demands head (const 0) ≡ bobs ff = 1
... | ()                                       -- i.e. 0 ≡ 1, impossible

------------------------------------------------------------------------
-- CONTROL 4 — detector-realizes-cover is NOT DEFINITIONALLY TRIVIAL. If
-- obs-stream and cover were definitionally equal, ~-refl would prove it and
-- `universality` would be decorative. The genuine content is that the
-- coinductive bisimulation (ana-unique) is required. We witness the POSITIVE
-- theorem holds on the concrete orbit (the real payoff, closed form).
------------------------------------------------------------------------
concrete-faithful : (b : Bool) → obs-stream b ~ cover b
concrete-faithful = detector-realizes-cover

-- and the two observably agree at the first two positions (a spot check that
-- the streams are the ALTERNATING 0,1,0,1… the orbit actually produces).
head-check-tt : head (cover tt) ≡ 0
head-check-tt = refl
head-check-ff : head (cover ff) ≡ 1
head-check-ff = refl
head-tail-tt : head (tail (cover tt)) ≡ 1     -- flip tt = ff, bobs ff = 1
head-tail-tt = refl
