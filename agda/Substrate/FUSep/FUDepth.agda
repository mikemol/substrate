{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- FUDepth — ⟡FU-depth: the theorem-backed probe-depth choice.
--
-- ADD 98 deferred this as "sig_d refines ≈ for size-≤-n terms at d ≥ f(n)".
-- That target is a TRAP: full ≈-separation by finite probes is Böhm-hard for
-- normalizing terms and UNDECIDABLE for non-normalizing ones. The dissolution
-- (this module) separates the question into three, and proves the two the
-- extruder actually needs:
--
--   (1) sound SPLITTING  — `complete`: a ≈ b ⟹ same sig at every depth. So a
--       sig-DIFFERENCE is a genuine ≈-difference; the fold never wrongly splits
--       convertible terms. (Contrapositive: different sig ⟹ not ≈.)
--   (2) sound for LAW-FINDING — `fold-sound-for-law`: at probe depth ≥ the
--       law's depth, merging same-sig terms PRESERVES the law verdict, because
--       the laws are themselves sig-based. THIS is the bound the extruder
--       needs; the ADD-96 "is this merge sound?" worry aimed at the wrong
--       target. The depth choice: probe depth ≥ max law depth.
--   (3) interchangeable in ARBITRARY contexts — needs sig_d refines ≈ (Böhm /
--       undecidable general). DEFERRED = ⟡FU-sep (residue).
--
-- `sigOf-mono` (deeper determines shallower) makes precise the ADD-96 practice:
-- deepening the probe monotonically refines the fold.
------------------------------------------------------------------------

module Substrate.FUSep.FUDepth where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
import Substrate.FUSep.ConversionCongruence as ConversionCongruence
open ConversionCongruence using (ARS)

-- local equality helpers ----------------------------------------------

∷-inj₁ : {A : Set} {x y : A} {xs ys : List A} → (x ∷ xs) ≡ (y ∷ ys) → x ≡ y
∷-inj₁ refl = refl

∷-inj₂ : {A : Set} {x y : A} {xs ys : List A} → (x ∷ xs) ≡ (y ∷ ys) → xs ≡ ys
∷-inj₂ refl = refl

∷-cong : {A : Set} {x y : A} {xs ys : List A} → x ≡ y → xs ≡ ys → (x ∷ xs) ≡ (y ∷ ys)
∷-cong refl refl = refl

module _ (R : ARS) (Obs : Set) (obs : ARS.Carrier R → Obs) where
  open ARS R

  -- conversion of this ARS, and its left-compatibility (from ⟡FU-cong).
  _≈_ : Carrier → Carrier → Set
  x ≈ y = ConversionCongruence._≈_ R x y

  ≈-congˡ : ∀ {a a' b} → a ≈ a' → (a · b) ≈ (a' · b)
  ≈-congˡ p = ConversionCongruence.≈-congˡ R p

  ----------------------------------------------------------------------
  -- SIG: the finite-probe signature = observations of t applied along the
  -- probe list (all prefixes). Depth = length of the probe list. This is the
  -- decidable approximation of behavioral equivalence the extruder folds by.
  ----------------------------------------------------------------------
  sigOf : Carrier → List Carrier → List Obs
  sigOf t []       = obs t ∷ []
  sigOf t (p ∷ ps) = obs t ∷ sigOf (t · p) ps

  -- head of a sigOf-equality: obs a ≡ obs b, WITHOUT case-splitting the probe
  -- list (sigOf t ps is cons-headed with head obs t in both branches).
  sig-head : ∀ {a b} (ps : List Carrier) → sigOf a ps ≡ sigOf b ps → obs a ≡ obs b
  sig-head []       eq = ∷-inj₁ eq
  sig-head (p ∷ ps) eq = ∷-inj₁ eq

  ----------------------------------------------------------------------
  -- MONOTONE REFINEMENT: a deeper signature determines a shallower one — if
  -- two terms agree at depth (qs ++ rs) they agree at depth qs. This is the
  -- ADD-96 practice ("check deeper") made precise: deepening only refines.
  ----------------------------------------------------------------------
  sigOf-mono : ∀ {a b} (qs rs : List Carrier)
             → sigOf a (qs ++ rs) ≡ sigOf b (qs ++ rs)
             → sigOf a qs ≡ sigOf b qs
  sigOf-mono []       rs eq = ∷-cong (sig-head (_ ++ rs) eq) refl
  sigOf-mono (q ∷ qs) rs eq = ∷-cong (∷-inj₁ eq) (sigOf-mono qs rs (∷-inj₂ eq))

  ----------------------------------------------------------------------
  -- (1) SOUND SPLITTING: conversion is never split by the probe. a ≈ b ⟹ same
  -- sig at every depth (needs obs to respect ≈ — true for whnf-head, nf-under-
  -- confluence, …). Contrapositive: DIFFERENT sig ⟹ NOT ≈, so every distinction
  -- the fold makes is a genuine ≈-difference.
  ----------------------------------------------------------------------
  complete : (obs-resp : ∀ {a b} → a ≈ b → obs a ≡ obs b)
           → ∀ {a b} (ps : List Carrier) → a ≈ b → sigOf a ps ≡ sigOf b ps
  complete or []       ab = ∷-cong (or ab) refl
  complete or (p ∷ ps) ab = ∷-cong (or ab) (complete or ps (≈-congˡ ab))

  ----------------------------------------------------------------------
  -- (2) SOUND FOR LAW-FINDING — the theorem-backed DEPTH BOUND. A law L is
  -- DECIDED at depth qs when its verdict factors through sigOf · qs (the x7
  -- laws each factor through a fixed probe prefix). Then at fold depth
  -- (qs ++ rs) ≥ qs, merging same-sig terms PRESERVES the L verdict — keeping
  -- one representative per sig-class never drops an L-satisfying behavior.
  -- The depth choice: set the probe depth ≥ the max law depth, and the fold is
  -- SOUND for law-finding, regardless of whether the finite-probe ~ equals ≈.
  ----------------------------------------------------------------------
  Factors : (Carrier → Set) → List Carrier → Set
  Factors L qs = ∀ {a b} → sigOf a qs ≡ sigOf b qs → L a → L b

  fold-sound-for-law :
    ∀ {L : Carrier → Set} {qs} → Factors L qs →
    ∀ (rs : List Carrier) {a b} →
    sigOf a (qs ++ rs) ≡ sigOf b (qs ++ rs) →
    L a → L b
  fold-sound-for-law fac rs eq La = fac (sigOf-mono _ rs eq) La
