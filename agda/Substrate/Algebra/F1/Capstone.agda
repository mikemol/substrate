------------------------------------------------------------------------
-- Substrate.Algebra.F1.Capstone
--
-- F1m5 of the F₁-modules arc per [scratch/m_mod_arc_plan.md].
--
-- F₁-arc summary:
--
--   F1m1  PointedSet            — Set + base
--   F1m2  PointedSetMap         — base-preserving function
--   F1m3  F₁-Module = PointedSet — categorical identification
--   F1m4  GL(n, F₁) = Sₙ        — F₁ⁿ + base-preserving bijections
--   F1m5  (this file)           — capstone + re-export
--
-- The F₁ semantics is now substrate-native: F₁-modules are pointed
-- sets, F₁-linear-maps are base-preserving functions, GL(n,F₁) is
-- the type of base-preserving automorphisms of (Fin (suc n), zero)
-- — which IS Sₙ at the group-structure level (routed through the
-- substrate's existing Coxeter-Sₙ machinery).
--
-- This complements M3's "F₁ as trivial Monoid (⊤)" identification:
-- both views are valid (F₁ as 0-ring AND F₁ as the field-with-one-
-- element). The pointed-set view is the deeper semantic content.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.Capstone where

open import Substrate.Algebra.PointedSet      public
  using (PointedSet; Carrier; base; ⊤-Pointed)
open import Substrate.Algebra.PointedSet.Map  public
  using (PointedSetMap; id-PointedSetMap; compose-PointedSetMap)
open import Substrate.Algebra.F1.AsModule     public
  using (F₁-Module; F₁-Module-Hom; id-F₁-Hom; compose-F₁-Hom)
open import Substrate.Algebra.F1.GL           public
  using (F₁ⁿ; GL-F₁; id-GL-F₁)
open import Substrate.Algebra.Monoid          public
  using (F₁-Monoid)

------------------------------------------------------------------------
-- F₁-arc closure. The substrate now hosts F₁ in both views:
--   * F₁-Monoid = trivial monoid ⊤ (from M3) — the 0-ring view.
--   * F₁-Module = PointedSet (from F1m3) — the field-with-one-
--     element view. GL(n, F₁) realises Sₙ at the automorphism
--     level (F1m4).
--
-- Both views connect: the Monoid view's ⊤ is the basepoint of
-- ⊤-Pointed; the Module view's GL(0, F₁) is the trivial group.
------------------------------------------------------------------------
