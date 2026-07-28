------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type
--
-- SymBilinForm-3: symmetric 3×3 matrix over F₂ stored as Vector 6,
-- with named accessors for the six independent entries.
--
--   [[ a  d  e ]
--    [ d  b  f ]
--    [ e  f  c ]]   →   (a, b, c, d, e, f) at positions (0..5)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Algebra.F2     using (F₂)
open import Substrate.Algebra.F2.Vector using (Vector)

SymBilinForm-3 : Set
SymBilinForm-3 = Vector 6

entry-a entry-b entry-c entry-d entry-e entry-f : SymBilinForm-3 → F₂
entry-a m = lookup m zero
entry-b m = lookup m ₁
entry-c m = lookup m ₂
entry-d m = lookup m ₃
entry-e m = lookup m ₄
entry-f m = lookup m ₅
