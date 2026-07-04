{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- ConversionCongruence — ⟡FU-cong: discharge FoldUnfold's Congruence
-- hypothesis for the equivalence the extruder actually rests on.
--
-- THE DISSOLUTION (ADD 96 left "is the finite-probe ~ a congruence?" open):
-- three relations were conflated —
--   * CONVERSION ≈ (equivalence closure of reduction): the IDEAL behavioral
--     equivalence. PROVEN here to be a CONGRUENCE from COMPATIBILITY ALONE
--     (reduction closed under application contexts) — NO confluence needed for
--     the congruence property. Discharges FoldUnfold.Congruence unconditionally.
--   * bare-nf-equality: a SOUND but COARSE decidable congruence.
--   * the finite-probe sig: the DECIDABLE APPROXIMATION of ≈, a congruence only
--     when the probe depth suffices; the ADD-96 probe test is the per-merge
--     soundness guard.
--
-- So rep-closure-complete (FoldUnfold, the SPPF reuse soundness) applies to
-- CONVERSION with zero added hypotheses; the finite-probe is its decidable
-- stand-in, sound where it refines ≈ (bound = ⟡FU-depth, deferred).
--
-- The extruder's own reduction (next_step, a contextual single-step) IS a
-- compatible reduction — an ARS instance — so ≈ over it is a congruence, and
-- the finite-probe sig approximates THAT ≈. This is the machine-checked form of
-- the ADD-96 test that found CB's rep congruent to 6 probes.
------------------------------------------------------------------------

module Substrate.FUSep.ConversionCongruence where

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.FUSep.FoldUnfold using (Congruence)

-- an APPLICATIVE REDUCTION SYSTEM: a magma with a COMPATIBLE reduction — closed
-- under application contexts (the ONLY property the congruence proof needs).
record ARS : Set₁ where
  field
    Carrier : Set
    _·_     : Carrier → Carrier → Carrier
    _⟶_     : Carrier → Carrier → Set
    ·-congˡ : ∀ {a a' b} → a ⟶ a' → (a · b) ⟶ (a' · b)
    ·-congʳ : ∀ {a b b'} → b ⟶ b' → (a · b) ⟶ (a · b')

module _ (R : ARS) where
  open ARS R

  -- CONVERSION: the equivalence closure of ⟶ (an equivalence BY CONSTRUCTION).
  -- Church-Rosser convertibility — the ideal ~ the finite-probe sig approximates.
  data _≈_ : Carrier → Carrier → Set where
    emb    : ∀ {a b}   → a ⟶ b → a ≈ b
    ≈refl  : ∀ {a}     → a ≈ a
    ≈sym   : ∀ {a b}   → a ≈ b → b ≈ a
    ≈trans : ∀ {a b c} → a ≈ b → b ≈ c → a ≈ c

  -- ≈ respects application on the LEFT (lift ·-congˡ through the closure).
  ≈-congˡ : ∀ {a a' b} → a ≈ a' → (a · b) ≈ (a' · b)
  ≈-congˡ (emb r)      = emb (·-congˡ r)
  ≈-congˡ ≈refl        = ≈refl
  ≈-congˡ (≈sym p)     = ≈sym (≈-congˡ p)
  ≈-congˡ (≈trans p q) = ≈trans (≈-congˡ p) (≈-congˡ q)

  -- ≈ respects application on the RIGHT.
  ≈-congʳ : ∀ {a b b'} → b ≈ b' → (a · b) ≈ (a · b')
  ≈-congʳ (emb r)      = emb (·-congʳ r)
  ≈-congʳ ≈refl        = ≈refl
  ≈-congʳ (≈sym p)     = ≈sym (≈-congʳ p)
  ≈-congʳ (≈trans p q) = ≈trans (≈-congʳ p) (≈-congʳ q)

  -- THE CONGRUENCE: conversion respects application in BOTH arguments — the
  -- FoldUnfold.Congruence.~-cong obligation, discharged from compatibility.
  ≈-cong : ∀ {a a' b b'} → a ≈ a' → b ≈ b' → (a · b) ≈ (a' · b')
  ≈-cong p q = ≈trans (≈-congˡ p) (≈-congʳ q)

  -- plain (non-mixfix) accessors, so qualified references parse cleanly
  -- (the HetQ lesson: expose plain names, don't force mixfix through qualification).
  conv-rel : Carrier → Carrier → Set
  conv-rel a b = a ≈ b
  conv-refl : ∀ {a} → conv-rel a a
  conv-refl = ≈refl
  conv-sym : ∀ {a b} → conv-rel a b → conv-rel b a
  conv-sym = ≈sym
  conv-trans : ∀ {a b c} → conv-rel a b → conv-rel b c → conv-rel a c
  conv-trans = ≈trans

  -- the magma underlying this ARS (carrier = ARS's Carrier; canonical Magma)
  ars-magma : Magma Carrier
  ars-magma = record { _·_ = _·_ }

  -- DISCHARGE: build a FoldUnfold.Congruence instance from conversion. With
  -- this, FoldUnfold.rep-closure-complete (SPPF reuse soundness) applies to
  -- CONVERSION with ZERO added hypotheses — the fold is provably safe under
  -- the ideal ~, so a missing term is ALWAYS an unfold-completeness issue
  -- (never fold-aggression), exactly as ADD 96 diagnosed.
  ars-congruence : Congruence ars-magma
  ars-congruence = record
    { _~_     = _≈_
    ; ~-refl  = ≈refl
    ; ~-sym   = ≈sym
    ; ~-trans = ≈trans
    ; ~-cong  = ≈-cong
    }
