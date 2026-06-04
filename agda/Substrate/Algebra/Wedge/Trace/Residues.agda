------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Trace.Residues
--
-- THE RESIDUE-SHEDDING IS CARRIER-GENERIC. EEATrace.Keystone showed the
-- Euclidean trace sheds residues and classifies each by prove-or-correct — but
-- only for ℕ. The generic wedge Trace (Algebra.Wedge.Trace, the Free read over
-- ANY DivStr) sheds residues the same way: this module lifts eea-residues /
-- eea-classify off ℕ onto every wedge carrier.
--
--   trace-residues — the remainder shed at each step (any carrier).
--   trace-classify — with a TorsorAtom + a unit-decision on the carrier, each
--     shed residue is tagged by prove-or-correct: the unit (stop, clean) or a
--     fixed-point-free correction (shed and recurse).
--
-- So "recursive factoring, shedding residues, never dead-ending" is a property
-- of the wedge Trace as such, not of ℕ. EEATrace.Keystone is the ℕ instance
-- (via Algebra.Wedge.fromEEATrace + ResidueAtom's ℕ-torsor).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Trace.Residues where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Sum using (_⊎_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace; done; more; rem)
open import Substrate.Category.Lawvere
  using (FixedPointFree; TorsorAtom; prove-or-correct; e)

------------------------------------------------------------------------
-- 1. The residues a trace sheds — the remainder at each step, any carrier.
------------------------------------------------------------------------

trace-residues : {D : DivStr} {a b g : C D} → Trace D a b g → List (C D)
trace-residues (done _)       = []
trace-residues (more _ w rec) = rem w ∷ trace-residues rec

------------------------------------------------------------------------
-- 2. Each shed residue classified by prove-or-correct (carrier-generic):
--    the unit (stop — clean reconstruction) or a fixed-point-free correction.
------------------------------------------------------------------------

trace-classify :
  {D : DivStr} (T : TorsorAtom (C D))
  (dec : (g : C D) → (g ≡ e T) ⊎ (g ≡ e T → ⊥))
  {a b g : C D} → Trace D a b g →
  List (Σ (C D) (λ r → (r ≡ e T) ⊎ FixedPointFree (C D)))
trace-classify T dec (done _)       = []
trace-classify T dec (more _ w rec) =
  (rem w , prove-or-correct T dec (rem w)) ∷ trace-classify T dec rec
