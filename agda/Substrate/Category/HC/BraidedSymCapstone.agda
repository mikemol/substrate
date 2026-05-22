------------------------------------------------------------------------
-- Substrate.Category.HC.BraidedSymCapstone
--
-- HC20 — Braided/Symmetric sub-arc capstone (HC11-HC20).
--
-- Each UP names a distinguished object in UPCategory; the
-- substrate's universal-property catalogue now includes the
-- canonical braided + symmetric + cartesian-monoidal + Drinfeld-
-- center landmarks.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.BraidedSymCapstone where

open import Substrate.Category.HC.BraidedMonoidal      public using (BraidedMonoidal-UP)
open import Substrate.Category.HC.BraidedHexagon       public using (BraidedHexagon-UP)
open import Substrate.Category.HC.BraidedFunctor       public using (BraidedFunctor-UP)
open import Substrate.Category.HC.SymmetricMonoidal    public using (SymmetricMonoidal-UP)
open import Substrate.Category.HC.CoxeterBraid         public using (CoxeterBraid-UP)
open import Substrate.Category.HC.EckmannHilton        public using (EckmannHilton-UP)
open import Substrate.Category.HC.F2LinFullCoherence   public using (F2LinFullCoherence-UP)
open import Substrate.Category.HC.CartesianMonoidal    public using (CartesianMonoidal-UP)
open import Substrate.Category.HC.DrinfeldCenter       public using (DrinfeldCenter-UP)
