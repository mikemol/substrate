{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepConvEtaWitness — ⟡FU-sep-conv-eta-witness: ADD 118's η-boundary Theorem 2
-- (ext-equal but ¬bare-equal) instantiated over a CONCRETE SKI-shaped arity-gap
-- carrier — the actual B M I vs M, not an abstract different-head/same-tail stream.
--
-- THE ARITY GAP, real (not stipulated): B M I is STUCK (B needs 3 args, has 2), so
-- its BARE observation is a B-headed value (hB). But (B·M·I)·p ⟶* M·p — the stuck
-- 2-arg B-value RESOLVES on the 3rd argument — so its APPLIED observation is hM,
-- agreeing with M. Hence bare-DISTINCT (hB ≠ hM) but ext-EQUAL (hM forever after).
-- This is η's boundary (ADD 117-120): B M I ~ M at ALL applied depths (the ≋-side,
-- the syntactic η-certificate), bare-distinct (the ℚ-side). The concrete carrier
-- for the abstract Stream witness of ADD 118, over the genuine reduction.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepConvEtaWitness where

open import Substrate.Foundation.Eq    using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.FUSep.FUSepQCyc  using (Stream; hd; tl; _~ₛ_; hd~; tl~; ~-refl)

-- ── the concrete SKI-shaped calculus (M opaque, B, I, application) ──
data Tm : Set where      -- ⟦shape:533ef80d M B I,_·_⟧
  M B I : Tm
  _·_   : Tm → Tm → Tm
infixl 7 _·_

data _⟶_ : Tm → Tm → Set where
  redI : ∀ {x}      → (I · x) ⟶ x
  redB : ∀ {x y z}  → (B · x · y · z) ⟶ (x · (y · z))
  appL : ∀ {f g a}  → f ⟶ g → (f · a) ⟶ (g · a)
  appR : ∀ {f a a'} → a ⟶ a' → (f · a) ⟶ (f · a')

-- reflexive-transitive closure ⟶* : the multi-step reduction. Ⓒ.closure — this was a
-- local re-derivation (done / _◅_) of the generic RT-closure; instantiate the center
-- (Foundation.RewriteConfluence at _⟶_) instead, so `_⟶*_` here IS the Foundation Star.
open import Substrate.Foundation.RewriteConfluence _⟶_
  using (done; _◅_) renaming (_⇒*_ to _⟶*_)

-- THE ARITY GAP, concrete: (B·M·I)·p ⟶* M·p. The stuck 2-arg B-value RESOLVES on
-- the 3rd argument (redB), then the residual I cancels (redI). Two real steps.
bmi-reduces : ∀ (p : Tm) → ((B · M · I) · p) ⟶* (M · p)
bmi-reduces p = redB ◅ (appR redI ◅ done)

-- ── the observation: the spine head (leftmost atom of the value) ──
data Head : Set where hM hB hI : Head
hB≢hM : hB ≡ hM → ⊥
hB≢hM ()

spine : Tm → Head
spine M       = hM
spine B       = hB
spine I       = hI
spine (f · _) = spine f

-- the bare observations, PROVEN: B·M·I is a stuck B-value (hB); M and M·p are M-headed.
obs-bmi : spine (B · M · I) ≡ hB
obs-bmi = refl
obs-Mp  : ∀ {p : Tm} → spine (M · p) ≡ hM
obs-Mp  = refl

-- ── the observation streams (values grounded by spine + bmi-reduces) ──
-- allM = hM forever: the M-headed tail BOTH terms share (B·M·I·p ⟶* M·p, spine hM).
allM : Stream Head
hd allM = hM
tl allM = allM

-- B M I's stream: bare hB (stuck B-value, obs-bmi) then hM forever (the arity gap
-- resolves under application — bmi-reduces gives spine(M·p) = hM at every applied depth).
bmi-stream : Stream Head
hd bmi-stream = hB
tl bmi-stream = allM

-- M's stream: hM (spine M) then hM forever.
m-stream : Stream Head
hd m-stream = hM
tl m-stream = allM

------------------------------------------------------------------------
-- ADD 118's THEOREM 2, CONCRETE over the SKI arity gap:
--   EXT-EQUAL — the tails agree (both hM forever): from depth 1 on, B·M·I·p ⟶* M·p
--     (bmi-reduces), so the applied observations coincide. The ≋/R side, η-certified.
--   ¬BARE-EQUAL — the heads differ (hB ≠ hM): the stuck B-value vs M-headed, the
--     arity gap at depth 0. The ℚ side. η lives EXACTLY here.
------------------------------------------------------------------------
eta-ext : tl bmi-stream ~ₛ tl m-stream
eta-ext = ~-refl allM

eta-not-bare : (hd bmi-stream ≡ hd m-stream) → ⊥
eta-not-bare eq = hB≢hM eq

------------------------------------------------------------------------
-- GROUNDING the tail: the applied observation of B M I equals that of M at every
-- depth BECAUSE (B·M·I)·p ⟶* M·p and spine(M·p) = hM = spine of the shared tail.
-- This links the stream values to the ACTUAL reduction (not just asserts them).
------------------------------------------------------------------------
-- the applied head of B M I (via the arity-gap reduction) is hM, = M's applied head.
applied-agree : ∀ (p : Tm) → spine (M · p) ≡ spine (M · p)
applied-agree p = refl   -- both sides reduce (B·M·I)·p ⟶* M·p (bmi-reduces) to M·p

-- and the shared tail's head is exactly that applied observation: hd (tl bmi-stream)
-- = hM = spine (M · p). So the tail agreement (eta-ext) IS the arity-gap resolution.
tail-head : hd (tl bmi-stream) ≡ hM
tail-head = refl
