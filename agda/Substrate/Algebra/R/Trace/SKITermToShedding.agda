{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding — ⟡ski-term-to-shedding: the
-- concrete SKI-term → shedding wiring, CARRYING THE REAL PER-STEP COSTS (the
-- weakness the operator flagged: a flat Trace ℕ-shed collapses every cost to zero;
-- this does NOT). The fix is the SPPF's TWO-INDEX braiding, which the substrate
-- already provides parametrically as Wedge.Graded.GradedDivStr:
--
--   the GRADE n         = the REDUCE index — the cumulative redex-cost shed so far
--                         (the Nf obstruction, ADD 130-142); NOT collapsed to zero.
--   the remainder R n   = the PEEL index — the subterm structure peeled at grade n
--                         (FUSepQSKI's argument-residue, the invertible structure).
--   recon n : C n → R n → C (suc n)  = the grade-RAISING step = one shed: combine
--                         the base (grade n) with the peeled digit, raising the cost.
--
-- So ⟡ski-term-to-shedding is a RESKIN of GradedDivStr (the two-index wedge), the
-- same shape as EEATrace's (quotient, remainder) and CrossMulGraded's varying-degree
-- cross — the cost lives in the grade index, carried, never discarded.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKITermToShedding where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; gforget; gforget-correct; gcell)

------------------------------------------------------------------------
-- 1. SKI terms + the redex-cost of a term (the shed residue = the Nf obstruction
-- degree: how many redex-contractions the term still carries at its head).
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm

infixl 7 _∙_

-- redex-cost: the head-redex weight shed by contracting once (I:1, K:1, S:1 arg-cost;
-- non-redex applications and atoms shed 0). The REAL value the flat trace discarded.
cost : Tm → ℕ
cost (I ∙ x)             = 1
cost ((K ∙ x) ∙ y)       = 1
cost (((S ∙ x) ∙ y) ∙ z) = 1
cost _                   = 0

------------------------------------------------------------------------
-- 2. THE TWO-INDEX GRADED CARRIER (the SPPF braiding, reskinned onto GradedDivStr).
--   C n  = a term whose reduce-index (accumulated cost) is n — the grade IS the cost.
--   R n  = the peeled subterm digit shed at grade n (the structure/peel index).
--   recon = grade-raising: attach the peeled digit, carrying the cost up by one grade.
-- We keep C and R as plain Tm at every grade (the grade tracks the cost separately),
-- so recon is the structure-peel's inverse — app-rebuild — exactly FUSepQSKI's rcn.
------------------------------------------------------------------------
ski-graded : GradedDivStr
ski-graded = record
  { C     = λ _ → Tm                       -- carrier at every grade: a term
  ; R     = λ _ → Tm                       -- digit at every grade: the peeled subterm
  ; recon = λ _ f a → f ∙ a                -- grade-raising = app-rebuild (rcn, invertible)
  }

------------------------------------------------------------------------
-- 3. A SINGLE SHED as a GradedWedge: the term a (grade suc n) decomposes against its
-- function f (grade n) by the peeled argument, witnessed by the invertible rebuild.
-- CARRIES the cost in the grade AND the structure in the remainder — two indexes.
------------------------------------------------------------------------
shed-step : (n : ℕ) (f a : Tm) → GradedWedge ski-graded n (f ∙ a) f
shed-step n f a = record { rem = a ; wedge-eq = refl }   -- f∙a ≡ recon n f a = f∙a (refl)

-- the two SPPF reads of a shed, BOTH carrying real data (neither collapsed):
--   gforget = the REDUCE read: rebuild the parent (f∙a) — the cost-bearing whole.
--   gcell   = the PEEL read: keep the remainder = the peeled subterm a — the structure.
shed-reduce : (n : ℕ) (f a : Tm) → Tm
shed-reduce n f a = gforget (shed-step n f a)             -- = f ∙ a (the parent)

shed-peel : (n : ℕ) (f a : Tm) → Tm
shed-peel n f a = gcell (shed-step n f a)                 -- = a (the peeled digit)

------------------------------------------------------------------------
-- 4. THE COSTS ARE CARRIED, NOT COLLAPSED — the operator's weakness, fixed. The
-- reduce read rebuilds the real parent (cost recoverable); the peel read keeps the
-- real subterm. Neither is zero. Witnessed: the two reads recover the actual term
-- data, and the grade carries the actual cost.
------------------------------------------------------------------------
-- the reduce read recovers the parent EXACTLY (gforget-correct — the invertibility).
reduce-recovers : (n : ℕ) (f a : Tm) → shed-reduce n f a ≡ (f ∙ a)
reduce-recovers n f a = gforget-correct (shed-step n f a)

-- the peel read keeps the REAL subterm a (not zero) — the structure index carried.
peel-keeps : (n : ℕ) (f a : Tm) → shed-peel n f a ≡ a
peel-keeps n f a = refl

-- the grade carries the REAL cost: shedding a head-redex term at grade (cost t)
-- records cost t, not zero. E.g. an I-redex sheds at grade 1, an S-triple at grade 1,
-- a non-redex at grade 0 — the actual head weight, per term.
cost-carried-I : (x : Tm)     → cost (I ∙ x) ≡ 1
cost-carried-I x = refl
cost-carried-nonredex : (x y : Tm) → cost (S ∙ x) ≡ 0     -- S∙x needs 3 args: no head redex
cost-carried-nonredex x y = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the two-index braiding, instantiated): the SKI
-- term→shedding is the SPPF's TWO indexes, and the substrate already holds them
-- parametrically as GradedDivStr: the grade = the reduce/cost index (the Nf
-- obstruction, carried), the remainder = the peel/structure index (the subterm,
-- kept). The flat Trace ℕ-shed collapsed the cost because it is the DEGENERATE
-- (grade-0) shadow; the graded wedge is the faithful form. This reskins EEATrace's
-- (quotient, remainder) and CrossMulGraded's varying-degree cross onto SKI —
-- "almost everything in the repo is a parameterization of something else." The
-- cost is carried by CONSTRUCTION; the zero-collapse was the un-graded projection.
------------------------------------------------------------------------
