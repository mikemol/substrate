{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.OrbitUniversality — ⟡U1. The universality of
-- OrbitInduction, formalized: an admissible online cover of an orbit is a
-- coalgebra morphism into the terminal coalgebra RealTrace, and by
-- Final.ana-unique any two admissible covers are BISIMILAR — so the cover is
-- unique up to iso (the Nerode/OBDD-style canonicity the challenge asked for).
--
-- This is the SAME shape as RationalAdjunction (ℚ→R = ana qStep, forced by
-- ana-unique): the embedding is "FORCED, NOT CHOSEN — a theorem, not prose."
-- Here the state is an orbit state, the observation is its shape-digit, and the
-- cover is the anamorphism. Landing entirely on the substrate's own ana-unique.
--
-- HONEST SCOPE (⟡H-overclaim): this formalizes the UNIQUENESS CORE — that any
-- coalgebra morphism from the orbit into RealTrace is `ana`, so admissible
-- covers agree up to bisimulation. The A–D admissibility conditions are encoded
-- AS "being a coalgebra morphism" (online = the coalgebra shape; bounded/sound/
-- complete/canonical = the commuting squares). The claim "A–D ⟹ coalgebra
-- morphism" is argued in orbit-induction-universality.md §3; what is MACHINE-
-- CHECKED here is the payoff: coalgebra-morphism ⟹ unique cover.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.OrbitUniversality where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-unique)

------------------------------------------------------------------------
-- The orbit coalgebra. A state S with a step `next : S → S` and a shape
-- observation `obs : S → ℕ` (the interned shape-digit, CFDigitHet's codecA)
-- IS a Coalg S: observe the current shape, continue to the next state. This is
-- the online, minimal-state signature (correction §1 of the writeup): current
-- state + observation + successor, nothing else.
------------------------------------------------------------------------
module OrbitCover
  (S : Set) (next : S → S) (obs : S → ℕ)
  where

  -- the orbit as a coalgebra: S → ℕ × S  (shape-digit , next state)
  orbit-coalg : Coalg S
  orbit-coalg s = (obs s , next s)

  -- THE COVER: the anamorphism into RealTrace — the orbit's observation stream,
  -- the minimal cover. This is what OrbitInduction computes online.
  cover : S → RealTrace
  cover = ana orbit-coalg

  -- an ADMISSIBLE cover is any h : S → RealTrace that commutes with the orbit
  -- coalgebra (its head is the observed shape; its tail is the cover of the next
  -- state). A–D reduce to exactly these two commuting squares.
  Admissible : (S → RealTrace) → Set
  Admissible h = (∀ s → head (h s) ≡ obs s)
               × (∀ s → tail (h s) ≡ h (next s))

  -- THE UNIVERSALITY THEOREM: every admissible cover is bisimilar to `cover`.
  -- Directly `ana-unique`. So the online, bounded, sound cover is UNIQUE up to
  -- iso (bisimulation = equality in the terminal coalgebra) — "the" algorithm,
  -- not "an" algorithm.
  universality : (h : S → RealTrace) → Admissible h → ∀ s → h s ~ cover s
  universality h (hh , ht) s = ana-unique orbit-coalg h hh ht s

  -- corollary: ANY TWO admissible covers agree (up to ~). So the prediction
  -- chart is unique up to iso — every admissible P factors through `cover`.
  covers-agree : (h₁ h₂ : S → RealTrace)
               → Admissible h₁ → Admissible h₂
               → ∀ s → h₁ s ~ h₂ s
  covers-agree h₁ h₂ a₁ a₂ s = ~trans (universality h₁ a₁ s) (~sym (universality h₂ a₂ s))
    where
      -- ~ is an equivalence (symmetric/transitive), the terminal-coalgebra
      -- equality; proven inline by coinduction here for self-containment.
      ~sym : {x y : RealTrace} → x ~ y → y ~ x
      head~ (~sym p) rewrite head~ p = refl
      tail~ (~sym p) = ~sym (tail~ p)
      ~trans : {x y z : RealTrace} → x ~ y → y ~ z → x ~ z
      head~ (~trans p q) rewrite head~ p = head~ q
      tail~ (~trans p q) = ~trans (tail~ p) (tail~ q)
