{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5EEA — ⟡N1b-EEA. Combinator reduction as a DivStr wedge-zip, so the
-- regress detector's Q-trace IS a `Trace` over that DivStr and `shape`
-- (the generic, DivStr-parametric quotient sequence, Wedge/Shape.agda)
-- applies. Then: fixed point = the terminal `z` (GCD / final Bézout term);
-- regress = a Trace whose `shape` is (eventually) periodic — an infinite CF.
--
-- ⟡H0 findings (grep, honest split):
--  * Wedge.agda DivStr is MINIMAL: C, z, recon : C→C→C→C. ℕ-div is the template
--    (recon q b r = q*b + r). An instance needs only these three.
--  * Wedge/Shape.shape : {D} → Trace D a b g → WedgeShape D is GENERIC (any
--    DivStr) — "the shape is the invariant the correspondence is read against."
--  * shape-value-invariance (CFInvariance) is ℕ-SPECIFIC (uses divmod-unique,
--    ℚ cross-multiplication a*d≡c*b). It is NOT a generic DivStr theorem. So
--    "regress-soundness = shape-value-invariance instantiated" is owed a
--    GENERIC value-invariance OR a combinator-specific proof — flagged, NOT
--    claimed. What IS buildable now: the DivStr instance + the Trace/shape.
--
-- This module builds the INSTANCE (a real DivStr) abstractly: given a step
-- `next : S → S` and a terminal test, the reduction is a wedge-zip whose
-- quotient at each step is the generator. The carrier is S; recon rebuilds a
-- state from (generator, sub-state, remainder). Kept standalone-checkable
-- (mirrors the substrate's DivStr shape field-for-field); wiring to the
-- substrate's own Wedge.DivStr is ⟡N1b-EEA-wire.
------------------------------------------------------------------------

module Substrate.S5.S5EEA where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong)

-- the DivStr interface, reproduced field-for-field from Algebra.Wedge.DivStr
record DivStr : Set₁ where
  field
    C     : Set
    z     : C
    recon : C → C → C → C     -- recon q b r = "q·b, then remainder r"
open DivStr public

record Wedge (D : DivStr) (a b : C D) : Set where      -- ⟦shape:478f66a6 quot,rem,wedge-eq⟧
  field
    quot     : C D
    rem      : C D
    wedge-eq : a ≡ recon D quot b rem
open Wedge public

data Trace (D : DivStr) : C D → C D → C D → Set where
  done : (a : C D) → Trace D a (z D) a
  more : {a g : C D} (b : C D) (w : Wedge D a b) →
         Trace D b (rem w) g → Trace D a b g

-- the generic quotient-sequence shape (Wedge/Shape.shape), reproduced.
data QSeq (D : DivStr) : Set where
  []  : QSeq D
  _∷_ : C D → QSeq D → QSeq D

shape : {D : DivStr} {a b g : C D} → Trace D a b g → QSeq D
shape (done _)     = []
shape (more b w t) = quot w ∷ shape t

------------------------------------------------------------------------
-- THE COMBINATOR INSTANCE. Reduction states S with a step `next : S → S`
-- and a terminal `nf` (a normal form marker). The wedge decomposition of a
-- step: quotient = the GENERATOR g (the one-hole growth / head), divisor =
-- the sub-state, remainder = the continuation. We give a recon that rebuilds
-- a state from (q, b, r) so the DivStr laws hold definitionally.
--
-- Minimal faithful recon: recon q b r = "apply generator q to b, carry r".
-- We model the carrier as S and take recon to REBUILD via a supplied
-- reconstruction `rb : S → S → S → S` (the evaluator's _unspine/_wrap in
-- Agda-abstract form). The instance is parametric in (S, nf, rb).
------------------------------------------------------------------------
module Reduction (S : Set) (nf : S) (rb : S → S → S → S) where
  combinator-DivStr : DivStr
  combinator-DivStr = record { C = S ; z = nf ; recon = rb }

  -- a reduction that has reached nf is `done` — the terminal (GCD). A step
  -- that produces a wedge (generator q, remainder r) is `more`. So a finite
  -- reduction IS a Trace ending in done (value = GCD reached), and its shape
  -- is the generator sequence — the continued fraction of the reduction.
  ReductionTrace : S → S → S → Set
  ReductionTrace = Trace combinator-DivStr

  -- the CF of a reduction = the generator sequence read off its trace.
  reduction-CF : {a b g : S} → ReductionTrace a b g → QSeq combinator-DivStr
  reduction-CF = shape

  -- fixed point / value = the trace is `done` at the terminal: its CF is [].
  value-is-empty-CF : (a : S) → reduction-CF (done a) ≡ []
  value-is-empty-CF a = refl

  ------------------------------------------------------------------------
  -- REGRESS = a Trace whose CF is (eventually) PERIODIC. We can STATE this
  -- generically: a periodic CF is one where the generator sequence repeats.
  -- The `done` (terminal/GCD) trace has CF [] — finite. A regress trace never
  -- reaches `done`; its CF is infinite. Here we capture the DECIDABLE observable
  -- the detector uses: two trace prefixes with EQUAL shape (shape t₁ ≡ shape t₂)
  -- at different depths = a detected period. That equality is the ADD-36
  -- online-Sequitur hit (interning identity on the generator sequence).
  ------------------------------------------------------------------------
  -- a period witness: two sub-traces whose shapes coincide (the recurrence
  -- the detector interns). This is the OBSERVABLE; it is decidable (shape
  -- equality on the generator sequence = interning identity).
  PeriodWitness :
    {a₁ b₁ g₁ a₂ b₂ g₂ : S} →
    ReductionTrace a₁ b₁ g₁ → ReductionTrace a₂ b₂ g₂ → Set
  PeriodWitness t₁ t₂ = shape t₁ ≡ shape t₂

  -- and it is exactly the equality online-Sequitur detects. The SOUNDNESS
  -- (period ⟹ infinite ⟹ no value) is shape-value-invariance's job, which is
  -- ℕ-SPECIFIC in the repo (CFInvariance) — the generic version is owed. So:
  -- INSTANCE + shape + period-observable: BUILT. period ⟹ non-termination
  -- for the combinator DivStr: OWED (⟡N1b-EEA-sound).
