------------------------------------------------------------------------
-- Substrate.Category.HC.Pentagon
--
-- HC2 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- The Pentagon coherence UP: the canonical Mac-Lane pentagon for
-- monoidal categories. Two paths from (((a⊗b)⊗c)⊗d) to (a⊗(b⊗(c⊗d)))
-- via associators must agree.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.Pentagon where

open import Substrate.Category.HC.PlaceholderUP using (placeholder; PlaceholderUPArrow)

Pentagon-UP : PlaceholderUPArrow
Pentagon-UP = placeholder
