------------------------------------------------------------------------
-- Substrate.Category.HC.Interchange
--
-- HC5 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- Interchange law UP: in any 2-category / bicategory, vertical and
-- horizontal composition of 2-cells commute (Eckmann-Hilton at the
-- 2-cell level).
--
-- Substrate's existing partial interchange (Linguistic/Interchange)
-- discharges the identity case; this UP names the full obligation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.Interchange where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)

Interchange-UP : UPArrow
Interchange-UP = placeholder
