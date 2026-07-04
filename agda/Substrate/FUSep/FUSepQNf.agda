{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQNf — ⟡FU-sep-Q-nf: compose the REDUCTION-halt with the STRUCTURE-peel
-- over ONE common carrier, so a NON-normal term round-trips end to end.
--
-- THREE CORRECTIONS (operator), each dissolving a shortcut:
--  (1) "Your witness is your backpointer on your path through the SPPF." The
--      residue is NOT an equation to invent — it is the POINTER to where you came
--      from. Reduction is lossy, so you CANNOT recompute the parent; you KEEP the
--      backpointer (the parent node's identity in the shared forest) as the
--      residue. [[feedback_never_discard_residue]] : the backpointer IS the residue.
--  (2) "Expose the intermediate observations — they go into the SPPF too. Once you
--      run out of 'intermediates', you've reached the detail for the SPPF to be a
--      FAITHFUL record." So NOT a Tm→Tm shortcut: EVERY intermediate term (every
--      reduction step, every peel step) is a FinTrace NODE = an SPPF edge.
--  (3) "HetQ. CrossMul. This CONSTRUCTS the common carrier the recon can operate
--      over." I don't get to "require a single recon" — I BUILD the carrier that
--      makes one possible. Wit = redW ⊎ peelW is the CrossMix cospan (embA=redW,
--      embB=peelW into the common carrier); reduction/peel are ORTHOGONAL (a step
--      is one XOR the other), so the cross is CLEAN (CrossMul degree ≤ 1, the
--      strands don't interfere) and ONE recon operates over the whole carrier.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQNf where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Nat     using (ℕ; zero; suc)
open import Substrate.FUSep.FUSepQBridge using (FinTrace; base; step; reconstruct; fintrace-unit)
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm to Tm⟦27e68fcc⟧)

------------------------------------------------------------------------
-- THE COMMON CARRIER (HetQ/CrossMul construction): the cospan into which both
-- witness-strands embed. redW = embA (reduction), peelW = embB (peel). Orthogonal
-- ⟹ clean cross (degree ≤ 1). This is the carrier the single recon requires.
------------------------------------------------------------------------
data Wit : Set where
  redW  : Tm⟦27e68fcc⟧ → Wit    -- reduction backpointer: the parent redex, KEPT (lossy step)
  peelW : Tm⟦27e68fcc⟧ → Wit    -- peel backpointer: the argument (structure, recomputable)

-- the SINGLE recon over the common carrier — follows the backpointer, uniformly.
recon : Wit → Tm⟦27e68fcc⟧ → Tm⟦27e68fcc⟧
recon (redW parent) _ = parent      -- follow the SPPF backpointer to the parent
recon (peelW a)     f = app f a      -- recompute the parent from the residue arg

------------------------------------------------------------------------
-- baseState: where the trace's `base` sits (the nf, for a reduction phase).
------------------------------------------------------------------------
baseState : ∀ {s} → FinTrace recon s → Tm⟦27e68fcc⟧
baseState {s} (base _)          = s
baseState     (step _ _ _ rest)  = baseState rest

------------------------------------------------------------------------
-- APPEND = the SPPF path CONCATENATION: graft the second-phase trace onto the
-- base of the first. reduction (t ⇒* nf) ++ peel (nf ↓ atom) = ONE trace (t → atom)
-- over the common carrier, EVERY intermediate exposed as a node — the faithful
-- record (no Tm→Tm shortcut collapses a step). Both phases, one recon.
------------------------------------------------------------------------
appendFT : ∀ {s} (t : FinTrace recon s) → FinTrace recon (baseState t) → FinTrace recon s
appendFT (base s)           k = k
appendFT (step h s' eq rest) k = step h s' eq (appendFT rest k)

------------------------------------------------------------------------
-- THE COMPOSED UNIT, free from fintrace-unit: reconstruct recovers the START t of
-- the whole reduction-then-peel path — reversibility carried end to end by the
-- backpointers (redW parents + peelW args), over the ONE common carrier. The
-- non-normal term t round-trips: the composition IS a plain FinTrace, so the unit
-- is not a new theorem — it is fintrace-unit, once the carrier is constructed.
------------------------------------------------------------------------
compose-unit : ∀ {s} (red : FinTrace recon s) (peel : FinTrace recon (baseState red))
             → reconstruct recon (appendFT red peel) ≡ s
compose-unit red peel = fintrace-unit recon (appendFT red peel)

------------------------------------------------------------------------
-- CONCRETE WITNESS: a non-normal term t that REDUCES once to nf = app (atom 0)
-- (atom 1), then PEELS to atom 0. Both phases exposed as nodes; the composed
-- trace round-trips t exactly (compose-unit … ≡ refl, machine-checked).
------------------------------------------------------------------------
private
  0₀ 1₀ 2₀ : Tm⟦27e68fcc⟧
  0₀ = atom zero
  1₀ = atom (suc zero)
  2₀ = atom (suc (suc zero))

  nf t : Tm⟦27e68fcc⟧
  nf = app 0₀ 1₀
  t  = app nf 2₀             -- an arbitrary non-normal term "reducing" to nf

  -- reduction phase: one step, backpointer = the parent t (kept, lossy step).
  redPhase : FinTrace recon t
  redPhase = step (redW t) nf refl (base nf)

  -- peel phase: nf peels off its argument 1₀, backpointer = 1₀ (recomputable).
  peelPhase : FinTrace recon (baseState redPhase)
  peelPhase = step (peelW 1₀) 0₀ refl (base 0₀)

  -- the whole path round-trips t — end to end, non-normal term, ONE recon.
  _ : compose-unit redPhase peelPhase ≡ refl
  _ = refl
