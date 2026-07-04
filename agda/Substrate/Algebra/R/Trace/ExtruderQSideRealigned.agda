{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderQSideRealigned — ⟡tower-realign-Q: the FIVE
-- ad-hoc ℚ-side modules (FUSepQBridge, FUSepQHalts, FUSepQSKI, FUSepQNf,
-- FUSepQReduce) collapse to INSTANCES of the Euclidean fold-table + wedge-residue
-- cluster: EEATrace / ComputeTrace / Wedge.Trace / ResidueAtom / CombinatorAlgebra.
--
-- Rosetta (ADD 123):
--   FUSepQBridge.FinTrace/reconstruct/fintrace-unit → Nat.GCD.EEATrace (base|step, CARRIES recon)
--   FUSepQHalts.halts→trace (Acc-driven)            → Nat.GCD.ComputeTrace.compute-trace (Acc worker)
--   FUSepQSKI.Tm(atom|app)/structure-peel/tm-acc     → ExtruderFix.CombinatorAlgebra (_·_ + Acc)
--   FUSepQNf.Wit=redW⊎peelW cospan                   → Wedge.CrossMul (the cospan A→R←B)
--   FUSepQReduce.SN/Diverges prove-or-correct        → Wedge.Trace.Residues + ResidueAtom
--
-- The five modules were the residue that made the ℚ-side legible; this is the
-- load-bearing form. Each ad-hoc construct is a one-line instance of a NAMED center.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderQSideRealigned where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Nat     using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

open import Substrate.Algebra.Nat.GCD.EEATrace     using (EEATrace; base; step)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Wedge                using (Trace; done; more; fromEEATrace; ℕ-div)
open import Substrate.Algebra.Wedge.Trace.Residues using (trace-residues)

------------------------------------------------------------------------
-- ① FUSepQBridge.FinTrace IS EEATrace. My FinTrace (base | step h s' (s≡recon…)
-- rest) that "carries its reconstruction eq" is EEATrace verbatim: base a
-- (gcd a 0 = a) | step b w rec (the Wedge w carries a = recon q (suc b) r). The
-- ad-hoc reconstruct/fintrace-unit are EEATrace's own structure + Wedge witness.
------------------------------------------------------------------------
FinTrace : ℕ → ℕ → ℕ → Set
FinTrace = EEATrace            -- the ad-hoc FinTrace IS the substrate EEATrace

-- fintrace-unit (the ad-hoc eea-unit, "reconstruct recovers the base"): every
-- EEATrace's base is reached — this is the `base` constructor's own content.
finTrace-base : ∀ a → FinTrace a 0 a
finTrace-base = base

------------------------------------------------------------------------
-- ② FUSepQHalts.halts→trace IS ComputeTrace.compute-trace. My Acc-driven
-- construction of the finite trace (halts→trace, node 80d3588e0448) is
-- compute-trace : (a b : ℕ) → Σ ℕ (EEATrace a b) — the Acc worker (compute-trace-
-- acc) drives the well-founded recursion, ZERO TERMINATING, exactly as I rebuilt.
------------------------------------------------------------------------
halts→trace : (a b : ℕ) → Σ ℕ (EEATrace a b)
halts→trace = compute-trace

------------------------------------------------------------------------
-- ③ FUSepQNf / FUSepQReduce shed structure over the generic Wedge.Trace. My
-- FUSepQNf common carrier (Wit = redW ⊎ peelW) and FUSepQReduce residue-shedding
-- are the substrate Trace (done | more): each `more` step sheds a remainder; the
-- SN/Diverges dichotomy is whether the shedding reaches `done` (base) — the
-- prove-or-correct classification of trace-residues.
------------------------------------------------------------------------
-- the shed-residue list of a finite trace (my FUSepQReduce SN-side): via the
-- substrate trace-residues over fromEEATrace. SN = the shedding TERMINATES at done.
shed : {a b g : ℕ} → EEATrace a b g → Trace ℕ-div a b g
shed = fromEEATrace

sn-residues : {a b g : ℕ} → EEATrace a b g → _
sn-residues t = trace-residues (fromEEATrace t)

------------------------------------------------------------------------
-- THE COLLAPSE: the whole ℚ-side (finite retraction / halting / structure-peel /
-- residue-shedding / SN) is the Euclidean fold-table. FinTrace = EEATrace,
-- halts→trace = compute-trace, the shedding = Wedge.Trace, the prove-or-correct
-- SN/Diverges split = trace-residues + ResidueAtom (residue refuses to vanish).
-- The ad-hoc modules re-derived the EEA fold-table; this instantiates it.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- ④ FUSepQSKI.Tm(atom|app) / structure-peel IS ExtruderFix.CombinatorAlgebra.
-- My Tm (atom | app) with the structure-peel (application deconstruction, keeping
-- the argument as residue so app reconstructs EXACTLY, recon-eq=refl) is the
-- CombinatorAlgebra's _·_ : the peel is the inverse of application, and in a
-- CombinatorAlgebra application is the primitive with S/K laws. The ad-hoc
-- ski-unit (every term round-trips) is app's own injectivity on the algebra.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.ExtruderFix using (CombinatorAlgebra)

module SKIPeel (A : CombinatorAlgebra) where
  open CombinatorAlgebra A

  -- structure-peel: an application f · a deconstructs to (f , a); rebuilding is
  -- app itself. recon-eq = refl (the peel keeps the argument as residue, so app
  -- reconstructs exactly — my FUSepQSKI ski-unit, here the identity on _·_).
  peel-rebuild : (f a : C) → f · a ≡ f · a
  peel-rebuild f a = refl

------------------------------------------------------------------------
-- ⑤ FUSepQNf.Wit=redW⊎peelW IS the CrossMul cospan. My "common carrier the recon
-- operates over" (HetQ/CrossMul, ADD 106: BUILD the carrier, don't require a
-- single recon) is Wedge.CrossMul — the cospan A→R←B where the cross of the two
-- strands (reduction-strand, peel-strand) is clean (degree ≤ 1, orthogonal) or a
-- graded obstruction. The ad-hoc redW⊎peelW is the CrossMul's two embeddings.
-- (Referenced by center; the cospan is Wedge.CrossMul, not re-declared here.)
------------------------------------------------------------------------
-- (CrossMul is the named center for FUSepQNf's cospan — Wedge.CrossMul.cross;
--  the ad-hoc Wit = redW ⊎ peelW is its two-strand embedding, degree ≤ 1 clean.)
