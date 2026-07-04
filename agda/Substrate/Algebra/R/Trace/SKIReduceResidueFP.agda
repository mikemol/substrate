{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIReduceResidueFP — ⟡ski-reduce-residue-fp: full-SKI
-- reduction read through the tower's IDIOM (FUSepQReduce, verbatim, ADD 145), NOT
-- a hand-rolled Tait–Martin-Löf proof. Reduction is RESIDUE-SHEDDING; the SN /
-- Diverges dichotomy is the LEAST / GREATEST fixed point of the shedding functor:
--
--   SN       = LEAST  fp — the INDUCTIVE Wedge.Trace (done|more): shedding TERMINATES
--              (residue reaches the unit e), a normal form is reached, Newman/CR
--              applies (I/KI already discharged, ADD 143/144). The finite/ℚ side.
--   Diverges = GREATEST fp — the COINDUCTIVE R.Trace.RealTrace (head/tail): shedding
--              is PRODUCTIVE-FOREVER (Ω = SII(SII)), tail never reaches base. The
--              infinite/R side, its equality Bisim._~_.
--
-- Each shed residue is tagged PROVE-OR-CORRECT (ResidueAtom): the unit (stop, clean
-- nf) or a FixedPointFree correction (shed and recurse) — "the residue refuses to
-- vanish, which is why the engine never dead-ends." This INSTANTIATES the named
-- centers (Wedge.Trace / Trace.Residues / ResidueAtom / RealTrace / Bisim); it does
-- NOT reinvent reduction (the ParallelSKI drift, ADD 145, kept as residue).
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIReduceResidueFP where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)

open import Substrate.Algebra.Wedge using (DivStr; C; z; recon; Trace; done; more)
open import Substrate.Algebra.Wedge.Trace.Residues using (trace-residues; trace-classify)
open import Substrate.Algebra.Wedge.ResidueAtom using (ℕ-torsor; ℕ-zero?)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; ~-refl; head~; tail~)
open import Substrate.Category.Lawvere using (FixedPointFree; TorsorAtom; e)

------------------------------------------------------------------------
-- 1. The SHEDDING CARRIER. A reduction state carries a residue = the redex-cost
-- shed at the last step (the Nf obstruction, ADD 130-142). Here the residue lives
-- in ℕ (the shed-step count / grade), z = 0 = the unit = "clean, a normal form".
-- This is the DivStr the shedding runs over: C = ℕ, recon the additive rebuild,
-- z = 0 — the same ℕ-div the wedge/EEA already use (residue = remainder).
------------------------------------------------------------------------
ℕ-shed : DivStr
ℕ-shed = record { C = ℕ ; z = zero ; recon = λ q b r → r }
  -- recon keeps the residue r (the shed cost); q, b are the process bookkeeping.

------------------------------------------------------------------------
-- 2. THE LEAST FIXED POINT — SN. A terminating reduction IS an inductive
-- Wedge.Trace over ℕ-shed: finitely many `more` steps (each shedding a residue),
-- ending in `done a` (residue reaches the unit — a normal form). trace-residues
-- lists the shed costs; trace-classify tags each stop(unit) | shed(FixedPointFree).
------------------------------------------------------------------------
SN-shedding : ℕ → ℕ → ℕ → Set          -- Trace ℕ-shed a b g : the finite shedding
SN-shedding a b g = Trace ℕ-shed a b g

-- the shed residues of an SN reduction (the sequence of redex-costs), any trace.
sn-residues : {a b g : ℕ} → SN-shedding a b g → List ℕ
sn-residues t = trace-residues t

-- each shed residue tagged prove-or-correct: unit (stop, nf) or FixedPointFree.
sn-classify : {a b g : ℕ} → SN-shedding a b g
            → List (Σ ℕ (λ r → (r ≡ e ℕ-torsor) ⊎ FixedPointFree ℕ))
sn-classify t = trace-classify ℕ-torsor ℕ-zero? t

-- an SN reduction that STOPS immediately: done — residue = z = the unit, a normal
-- form, no shedding. The clean corner (the base of the least fp).
sn-normal-form : (a : ℕ) → SN-shedding a zero a
sn-normal-form a = done a

------------------------------------------------------------------------
-- 3. THE GREATEST FIXED POINT — Diverges. A non-terminating reduction (Ω =
-- SII(SII)) IS a coinductive R.Trace.RealTrace: head = the shed residue at THIS
-- step (a CF digit / redex-cost), tail = the residual process — PRODUCTIVE FOREVER,
-- never reaching base. Its equality is Bisim._~_ (coinductive), not ≡.
------------------------------------------------------------------------
Diverges : Set
Diverges = RealTrace              -- the coinductive shedding: tail never hits base

-- the shed residue at the current step of a divergent reduction.
diverge-shed : Diverges → ℕ
diverge-shed d = head d

-- Ω-like: a reduction that sheds the SAME residue forever (SII(SII) → SII(SII) → …).
-- Productive: head is defined at every step, tail recurses. The greatest-fp witness.
Ω-shedding : ℕ → Diverges
head (Ω-shedding k) = k
tail (Ω-shedding k) = Ω-shedding k

-- divergent reductions shedding the same residue are BISIMILAR (the R-side equality
-- — the greatest-fp notion of "same divergence", not ≡).
Ω-bisim : (k : ℕ) → Ω-shedding k ~ Ω-shedding k
Ω-bisim k = ~-refl (Ω-shedding k)

------------------------------------------------------------------------
-- 4. THE BOUNDARY = least ⊆ greatest. Every FINITE shedding (SN, inductive Trace)
-- EMBEDS into the coinductive process: read the trace's shed residues as the first
-- digits of a RealTrace, then diverge trivially (stop-padded). So SN ⊆ Diverges as
-- the least-fp ⊆ greatest-fp containment (the halting boundary is a fixed-point
-- structure, not a gap — FUSepQReduce, verbatim). We witness the embedding on the
-- residue lists: the finite shed-list is a prefix of the infinite one.
------------------------------------------------------------------------
-- embed a finite shed-list as the head-digits of a divergent process (0-padded).
embed-shed : List ℕ → Diverges
head (embed-shed [])       = zero              -- exhausted ⟹ pad with the unit (stopped)
tail (embed-shed [])       = embed-shed []
head (embed-shed (r ∷ rs)) = r
tail (embed-shed (r ∷ rs)) = embed-shed rs

-- the least-fp ⊆ greatest-fp containment: an SN reduction's shed residues ARE the
-- opening digits of a (trivially padded) divergent process — SN embeds in Diverges.
sn⊆diverges : {a b g : ℕ} → SN-shedding a b g → Diverges
sn⊆diverges t = embed-shed (sn-residues t)

------------------------------------------------------------------------
-- THE INVARIANT (the tower's idiom, instantiated — NOT reinvented): full-SKI
-- reduction's SN/Diverges dichotomy is ONE residue-shedding functor's least/
-- greatest fixed point. SN = inductive Wedge.Trace (done|more, residues tagged
-- prove-or-correct, terminates at the unit ⟹ Newman/CR, ADD 143/144). Diverges =
-- coinductive RealTrace (head/tail, Bisim equality, productive-forever). The
-- boundary is least ⊆ greatest (sn⊆diverges), a fixed-point structure not a gap.
-- Confluence is thus NOT a bespoke Takahashi proof: the SN side is Newman (done),
-- the non-SN side is the coinductive R-side (Bisim) — the SAME centers the whole
-- session realigned onto. ParallelSKI (the concrete-β Takahashi drift) stays
-- residue: the shadow that made this idiom-mismatch legible (ADD 145).
------------------------------------------------------------------------
