{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUEtaObsCoalg — ⟡FU-eta-obscoalg: the η-boundary observation stream DERIVED via
-- the substrate's OWN anamorphism (Final.ana = Unfold.unfold), not hand-built.
-- REALIGNS ADD 121 (FUSepConvEtaWitness), which hand-built Tm/reduction/spine/
-- streams when the substrate already had: Final.Coalg (S → ℕ × S, the observation
-- coalgebra), ana : Coalg S → S → RealTrace (the obs-stream functor), ana-head/
-- ana-tail (the coalgebra-morphism laws, refl), and ana-unique/self-unfold
-- (reduction-invariance: any coalgebra morphism into RealTrace is ~ to ana).
--
-- INSTANTIATE, don't rebuild: the observation coalgebra c : S → ℕ × S maps a state
-- to (its bare observation, its next state under application). ana c gives the
-- observation STREAM (a RealTrace). The η-witness (B M I vs M) is two states whose
-- ana-streams are bare-DISTINCT (head ≢) but ext-EQUAL (tails ~) — derived, with
-- the tail agreement from the coalgebra collapsing both to the same next state.
------------------------------------------------------------------------

module Substrate.FUSep.FUEtaObsCoalg where

open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-head; ana-tail)

open import Substrate.Foundation.Nat     using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Empty   using (⊥)

-- the STATE SPACE of the observation coalgebra: the three positions the arity gap
-- passes through. bmi = the stuck B-value (B M I, bare); mHead = the M-headed value
-- (M, and everything B M I reduces to under application). The observation ℕ: 1 for
-- the stuck B-value, 0 for M-headed (bare-distinct at depth 0).
data St : Set where
  bmi   : St     -- B · M · I  (stuck: needs 1 more arg)
  mHead : St     -- M-headed value

-- THE OBSERVATION COALGEBRA c : St → ℕ × St. head = bare observation; tail = the
-- next state under APPLICATION. The ARITY GAP: bmi observes 1 (stuck B-value) but
-- its APPLIED next-state is mHead (B·M·I·p ⟶* M·p); mHead observes 0, stays mHead.
c : Coalg St
c bmi   = suc zero , mHead      -- bare obs 1 (stuck B), applied → mHead (the reduction)
c mHead = zero , mHead      -- bare obs 0 (M-headed), applied → mHead (M·p is M-headed)

-- the observation streams, DERIVED via ana (the substrate anamorphism):
bmi-stream : RealTrace
bmi-stream = ana c bmi

m-stream : RealTrace
m-stream = ana c mHead

------------------------------------------------------------------------
-- ADD 118's THEOREM 2, now DERIVED (not constructed) via ana:
--   ¬BARE-EQUAL — heads differ: head (ana c bmi) = 1 ≠ 0 = head (ana c mHead), by
--     ana-head (the coalgebra-morphism head law). The arity gap at depth 0.
--   EXT-EQUAL — tails bisimilar: tail (ana c bmi) = ana c mHead = tail (ana c mHead)
--     by ana-tail — BOTH tails are ana c mHead, because the coalgebra sends bmi's
--     applied next-state to mHead (the reduction B·M·I·p ⟶* M·p). ~ by ~-refl.
------------------------------------------------------------------------
1≢0 : (suc zero ≡ zero) → ⊥
1≢0 ()

eta-not-bare : (head bmi-stream ≡ head m-stream) → ⊥
eta-not-bare eq = 1≢0 eq        -- head (ana c bmi) = 1, head (ana c mHead) = 0

eta-ext : tail bmi-stream ~ tail m-stream
eta-ext = ~-refl (ana c mHead)  -- both tails = ana c mHead (the shared M-headed stream)

-- the grounding: bmi's tail IS m-stream — the arity gap resolves to the M-headed
-- stream. tail (ana c bmi) ≡ ana c mHead ≡ m-stream, by ana-tail. DERIVED.
bmi-tail-is-m : tail bmi-stream ≡ m-stream
bmi-tail-is-m = ana-tail c bmi
