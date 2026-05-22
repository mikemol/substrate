------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.Det
--
-- det-sym3: determinant of a symmetric 3×3 matrix over F₂. The
-- standard det formula simplifies under x²=x, 2x=0, -x=x in F₂:
--
--   det [[a,d,e],[d,b,f],[e,f,c]] = a·b·c + a·f + c·d + e·b.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.Det where

open import Substrate.Algebra.F2 using (F₂; _·_; _+_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type
  using (SymBilinForm-3; entry-a; entry-b; entry-c; entry-d; entry-e; entry-f)

det-sym3 : SymBilinForm-3 → F₂
det-sym3 m =
  let a = entry-a m; b = entry-b m; c = entry-c m
      d = entry-d m; e = entry-e m; f = entry-f m
  in a · b · c + a · f + c · d + e · b
