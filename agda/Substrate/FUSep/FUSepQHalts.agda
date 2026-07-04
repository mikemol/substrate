{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQHalts — ⟡FU-sep-Q-halts, instantiating the substrate's Acc-driven trace
-- construction (operator: don't build a new trace type; the repo has ALREADY
-- lifted this — find it and instantiate).
--
-- ⟡H0 (EXHAUSTIVE search → ComputeTrace + Foundation.WellFounded): the canonical
-- move is  compute-trace-acc : (a b : ℕ) → Acc _<_ b → Σ ℕ (EEATrace a b) —
-- an ACCESSIBILITY witness DRIVES a well-founded recursion that CONSTRUCTS the
-- finite trace, bottoming at base. The `Acc rec` witness IS "Halts". So this is
-- compute-trace instantiated for the SKI step: a term with a measure decreasing
-- under `next`, given Acc, PRODUCES a FinTrace whose base is the value/nf. My
-- "maybe FinTrace is wrong" reconsideration is answered NO: FinTrace is the
-- target, Acc is the driver — exactly EEATrace ← Acc.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQHalts where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.FUSep.FUSepQBridge using (FinTrace; base; step; reconstruct; fintrace-unit)

-- a state either IS a value (base) or STEPS (with a decrease + reconstruction).
-- This ⊎ is the `Obs × (1 + −)` termination the substrate names — the `1` is base.
data Progress {S H : Set} (recon : H → S → S) (next : S → S) (μ< : S → Set) (s : S) : Set where
  isVal  : FinTrace {H} {S} recon s → Progress recon next μ< s   -- base reached
  stepsD : (h : H) → s ≡ recon h (next s) → μ< s → Progress recon next μ< s

-- the halting system, parameterized EXACTLY as ComputeTrace parameterizes GCD.
record HaltSystem : Set₁ where
  field
    St     : Set
    Hd     : Set
    M      : Set
    R      : M → M → Set
    mu     : St → M
    nxt    : St → St
    rcn    : Hd → St → St
    -- at each state: either a value (⟹ base FinTrace) or a step carrying the
    -- reconstruction equation AND a strict measure-decrease (the Acc feeder).
    prog   : (s : St) → Progress rcn nxt (λ s' → R (mu (nxt s')) (mu s')) s
open HaltSystem public

module _ (Hs : HaltSystem) where
  private
    S₀ = St Hs
    H₀ = Hd Hs
    M₀ = M Hs
    R₀ = R Hs
    μ₀ = mu Hs
    n₀ = nxt Hs
    r₀ = rcn Hs
    p₀ = prog Hs

  -- HALTS→TRACE — the compute-trace-acc analog: Acc on the measure DRIVES the
  -- recursion; at a value → base (its FinTrace); at a step → step + recurse on
  -- the strictly-smaller measure. Terminates by Acc (μ strictly decreases).
  halts→trace : (s : S₀) → Acc R₀ (μ₀ s) → FinTrace r₀ s
  halts→trace s (acc rec) with p₀ s
  ... | isVal ft            = ft
  ... | stepsD h eq μdec    =
        step h (n₀ s) eq (halts→trace (n₀ s) (rec (μ₀ (n₀ s)) μdec))

  -- THE RETRACTION for an actual halting term, end to end: build its finite
  -- trace, then fintrace-unit recovers the start = the ℚ-side unit.
  halts-retract : (s : S₀) → Acc R₀ (μ₀ s) → S₀
  halts-retract s a = reconstruct r₀ (halts→trace s a)

  halts-unit : (s : S₀) (a : Acc R₀ (μ₀ s)) → halts-retract s a ≡ s
  halts-unit s a = fintrace-unit r₀ (halts→trace s a)
