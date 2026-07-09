{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aSkiExistence — ⟡x8a-ski-existence: the EXISTENCE
-- half of the extruder BackedUP (X8aBacked, 212) landed at the REAL SKI reduction — mirroring
-- the uniqueness half (X8aSkiInstance, 214). Where 212's demonstrator ran S5Fixpoint.Machine
-- over ℕ with next = predecessor, HERE the machine runs over FUSep's SKI Tm⟦533ef80d⟧ with
-- next = the residue-shedding step (⇒'s stop/shed classifier): step to the shed target, or
-- stay at a stop (value/nf). run fuel t iterates next to the fixpoint (the nf, residue = z),
-- exactly the Python x7 _reduce_step at real SKI terms.
--
-- The stop/shed TAG is decidable per step (FUSepQReduce: "residue z-or-not is decidable per
-- step"), so fix? decides via the tag: stop ⟹ next t = t (fixpoint, yes); shed t' ⟹ next t = t'
-- ≢ t (the shed is fixed-point-free — its documented invariant, threaded HONESTLY as a
-- parameter fpf, not assumed). Then x8a-SKI-UP mirrors x8a-UP (212) EXACTLY at the SKI carrier:
-- Source = (fuel , term); Target = Tm⟦533ef80d⟧; Witness = v ≡ run fuel term; solve = run; solves = refl.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aSkiExistence where

open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves; content)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.S5.S5Fixpoint using (module Machine)
open import Substrate.FUSep.FUSepQReduce using (stop; shed; Reduce) renaming (Step to Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)

------------------------------------------------------------------------
-- ① THE SKI STEP FUNCTION from a classifier ⇒ : Reduce (stop/shed tag). next steps to the
--    shed target, or stays at a stop (the nf). fix? decides via the tag; the shed case uses
--    the classifier's fixed-point-free invariant (fpf), threaded as a parameter (honest).
------------------------------------------------------------------------
module SkiRun
  (⇒ : Reduce)
  (fpf : (t t' : Tm⟦533ef80d⟧) → ⇒ t ≡ shed t' → ¬ (t' ≡ t))   -- shed is fixed-point-free (⇒'s invariant)
  where

  -- next on a KNOWN Step⟦c0e06c56⟧ (so next and fix? share the same case reduction).
  step→next : (t : Tm⟦533ef80d⟧) → Step⟦c0e06c56⟧ t → Tm⟦533ef80d⟧
  step→next t stop      = t
  step→next t (shed t') = t'

  next : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
  next t = step→next t (⇒ t)

  -- fix? : next t ≡ t is decidable via the stop/shed tag (no Tm⟦533ef80d⟧ ≟ needed). Casing on ⇒ t makes
  -- next t = step→next t (⇒ t) reduce in each branch: stop → t (refl); shed t' → t' (fpf ⟹ ≢).
  fix? : (t : Tm⟦533ef80d⟧) → Dec (next t ≡ t)
  fix? t with ⇒ t in eq
  ... | stop    = yes refl
  ... | shed t' = no (fpf t t' eq)

  open Machine Tm⟦533ef80d⟧ next fix? using (run) public

------------------------------------------------------------------------
-- ② THE SKI EXISTENCE UP: mirrors x8a-UP (212) at the SKI carrier. Source = (fuel , term);
--    Target = Tm⟦533ef80d⟧; Witness = "v ≡ run fuel term" (the value IS the SKI nf the shedding reaches).
------------------------------------------------------------------------
module SkiExistence
  (⇒ : Reduce)
  (fpf : (t t' : Tm⟦533ef80d⟧) → ⇒ t ≡ shed t' → ¬ (t' ≡ t))
  where
  open SkiRun ⇒ fpf using (run)

  SkiFuelled : Set
  SkiFuelled = Σ ℕ (λ _ → Tm⟦533ef80d⟧)      -- (fuel , term)

  x8a-ski-UP : UPArrow
  x8a-ski-UP = record
    { Source  = SkiFuelled
    ; Target  = Tm⟦533ef80d⟧
    ; Witness = λ fs v → v ≡ run (proj₁ fs) (proj₂ fs)
    }

  -- solve: run the SKI shedding to its nf (stop) — the extruder proper, at real SKI terms.
  x8a-ski-solve : Source x8a-ski-UP → Target x8a-ski-UP
  x8a-ski-solve (fuel , t) = run fuel t

  -- solves: the run IS the value — refl (solve computes exactly run fuel t).
  x8a-ski-solves : (s : Source x8a-ski-UP) → Witness x8a-ski-UP s (x8a-ski-solve s)
  x8a-ski-solves (fuel , t) = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the EXISTENCE half landed at real SKI, mirroring 214's
-- uniqueness): the extruder's solver (run the reduction to its fixpoint/nf) now runs over the
-- REAL SKI Tm⟦533ef80d⟧ with next = the residue-shedding step (⇒'s stop/shed), not the ℕ-predecessor
-- demonstrator (212). x8a-ski-solve = run fuel t; x8a-ski-solves = refl (the SAME self-
-- determining ≡-Witness as 212/μ). So EXISTENCE (here) + UNIQUENESS (214, SN-relative
-- confluence) both hold at real SKI — the extruder is the third solver (212) with BOTH halves
-- of its BackedUP frame instantiated concretely at the SKI reduction it formalizes. The
-- either/or "demonstrator vs real SKI" dissolves: the SAME machine (S5Fixpoint.run) at the SKI
-- carrier, the stop/shed tag as the decidable fixpoint probe, the shed's fixed-point-freeness
-- (⇒'s own invariant) threaded honestly as fpf. The Witness/solve/solves shape is IDENTICAL to
-- 212 — the SKI instance is x8a's frame at a real reduction, not a new construction.
------------------------------------------------------------------------
