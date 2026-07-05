{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQCyc — ⟡FU-sep-cyc: the R-SIDE COUNIT. ADD 109-110 finished the ℚ side
-- (SN → Newman → Church-Rosser, the LEAST fixed point). This is the dual: the
-- Diverges residue (ADD 110, the GREATEST fixed point) is SELF-SIMILAR — a
-- divergent term's observation is PERIODIC — and periodic ~ the cyclic unfolding
-- of its period, by BISIMULATION (the CycleWire analog). The coinductive counit.
--
-- THE DISSOLUTION: "does divergence break the theory?" No — divergence IS the
-- periodic real, exactly as an irrational IS an infinite CF. CycleWire (⟡H0-read)
-- proves cycle 2 [] ~ twos by bisimulation: "productive-periodic ⇒ ℝ, one
-- machinery." Here: a divergent (Diverges) term ~ its period, greatest fixed
-- point — dual to the ℚ-side finite unit (fintrace-unit/bt-reflect, ADD 102-103).
--
-- ⟡H0 (read Bisim + CycleWire): bisimilarity is head~ (obs equal) + tail~
-- (coinductive); cyc unfolds a finite period into a periodic stream (guarded).
-- Instantiate exactly.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQCyc where

open import Substrate.Foundation.Eq   using (_≡_; refl; sym)
open import Substrate.Foundation.List using (List; []; _∷_)

-- the observation stream (RealTrace analog): head + coinductive tail.
record Stream (A : Set) : Set where
  coinductive
  field hd : A ; tl : Stream A
open Stream public

-- CycleWire's cycle: unfold a finite period into a PERIODIC stream (guarded
-- corecursion, the tail loops to the period start). THE greatest-fixed-point
-- object — the productive-periodic real.
cyc-go : {A : Set} → A → List A → List A → Stream A
hd (cyc-go x xs [])       = x
tl (cyc-go x xs [])       = cyc-go x xs xs
hd (cyc-go x xs (y ∷ ys)) = y
tl (cyc-go x xs (y ∷ ys)) = cyc-go x xs ys

cyc : {A : Set} → A → List A → Stream A
cyc x xs = cyc-go x xs (x ∷ xs)

-- the constant stream (period-1 unfolding — the Ω / twos case).
const : {A : Set} → A → Stream A
hd (const x) = x
tl (const x) = const x

-- BISIMILARITY (Bisim._~_): head~ + coinductive tail~. The R-side equality.
record _~ₛ_ {A : Set} (s t : Stream A) : Set where      -- stream bisimilarity (distinct-shape from Trace.Bisim._~_, pinned)
  coinductive
  field hd~ : hd s ≡ hd t ; tl~ : tl s ~ₛ tl t
open _~ₛ_ public

private
  symEq : {X : Set}{a b : X} → a ≡ b → b ≡ a
  symEq refl = refl
  -- ⟡def-eq: this private helper IS Foundation.Eq.sym (pointwise, definitionally).
  symEq≡sym : {X : Set}{a b : X} (p : a ≡ b) → symEq p ≡ sym p
  symEq≡sym refl = refl
  trEq : {X : Set}{a b c : X} → a ≡ b → b ≡ c → a ≡ c
  trEq refl r = r

~-refl : {A : Set} (s : Stream A) → s ~ₛ s
hd~ (~-refl s) = refl
tl~ (~-refl s) = ~-refl (tl s)

~-sym : {A : Set} {s t : Stream A} → s ~ₛ t → t ~ₛ s
hd~ (~-sym p) = symEq (hd~ p)
tl~ (~-sym p) = ~-sym (tl~ p)

~-trans : {A : Set} {s t u : Stream A} → s ~ₛ t → t ~ₛ u → s ~ₛ u
hd~ (~-trans p q) = trEq (hd~ p) (hd~ q)
tl~ (~-trans p q) = ~-trans (tl~ p) (tl~ q)

------------------------------------------------------------------------
-- THE COUNIT (period-1, the Ω / twos analog): cyc x [] ~ const x, by GUARDED
-- COINDUCTION. CycleWire proves cycle 2 [] ~ twos; this is that, generic. The
-- self-loop (Ω → Ω) is bisimilar to the constant periodic real — the greatest
-- fixed point's periodic point is unique up to bisimilarity.
------------------------------------------------------------------------
cyc-loop~const : {A : Set} (x : A) → cyc-go x [] [] ~ₛ const x
hd~ (cyc-loop~const x) = refl
tl~ (cyc-loop~const x) = cyc-loop~const x

cyc~const : {A : Set} (x : A) → cyc x [] ~ₛ const x
hd~ (cyc~const x) = refl
tl~ (cyc~const x) = cyc-loop~const x

------------------------------------------------------------------------
-- THE GENERAL COUNIT: a SELF-SIMILAR stream (all heads x — a divergent process
-- with constant observation, the residue that refuses to vanish, ADD 110/
-- ResidueAtom) IS bisimilar to cyc x []. `AllHeads` is the periodicity witness;
-- the greatest-fixed-point universal property (uniqueness up to ~).
------------------------------------------------------------------------
record AllHeads {A : Set} (x : A) (s : Stream A) : Set where
  coinductive
  field ah-hd : hd s ≡ x ; ah-tl : AllHeads x (tl s)
open AllHeads public

allHeads~const : {A : Set} (x : A) (s : Stream A) → AllHeads x s → s ~ₛ const x
hd~ (allHeads~const x s ah) = ah-hd ah
tl~ (allHeads~const x s ah) = allHeads~const x (tl s) (ah-tl ah)

-- so any self-similar (constant-observation) divergent stream ~ cyc x [] — the
-- Diverges residue IS the periodic real, up to bisimilarity.
selfSimilar~cyc : {A : Set} (x : A) (s : Stream A) → AllHeads x s → s ~ₛ cyc x []
selfSimilar~cyc x s ah = ~-trans (allHeads~const x s ah) (~-sym (cyc~const x))

------------------------------------------------------------------------
-- THE BRIDGE to ADD-110's Diverges: a divergent term's observation is a Stream;
-- a SELF-LOOPING divergent term (Ω → Ω, obs constant along the loop) is AllHeads,
-- hence ~ cyc — its observation IS the periodic real. This wires Diverges (the
-- greatest fixed point, ADD 110) to the periodic RealTrace (≋/CycleWire).
------------------------------------------------------------------------
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm; Reduce)

module _ (⇒ : Reduce) (A : Set) (obs : Tm → A) where
  -- the observation stream of a divergent path (unfold via Diverges.onward).
  divStream : (t : Tm) → FUSepQReduce.Diverges ⇒ t → Stream A
  hd (divStream t d) = obs t
  tl (divStream t d) = divStream (FUSepQReduce.Diverges.next d) (FUSepQReduce.Diverges.onward d)

  -- if the divergent path stays observationally constant (a self-loop at obs x),
  -- its observation is AllHeads x — hence ~ cyc x [], the periodic real. The
  -- Diverges residue, observed, IS the greatest-fixed-point periodic stream.
  divStream-const→cyc :
    (t : Tm) (d : FUSepQReduce.Diverges ⇒ t) (x : A)
    → AllHeads x (divStream t d) → divStream t d ~ₛ cyc x []
  divStream-const→cyc t d x ah = selfSimilar~cyc x (divStream t d) ah

------------------------------------------------------------------------
-- CONCRETE WITNESS: the twos = const 2 (CycleWire's twos) is the period-1 cyc.
-- cyc 2 [] ~ const 2, machine-checked — the substrate's cycle 2 [] ~ twos, here.
------------------------------------------------------------------------
data ℕ₀ : Set where z : ℕ₀ ; s : ℕ₀ → ℕ₀

_ : cyc (s (s z)) [] ~ₛ const (s (s z))
_ = cyc~const (s (s z))
