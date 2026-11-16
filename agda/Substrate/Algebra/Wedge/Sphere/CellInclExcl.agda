------------------------------------------------------------------------
-- C2: degree defect = the AND overlap
-- Context: Substrate/Algebra/Wedge/Sphere/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Sphere.CellInclExcl where

open import Substrate.Algebra.CayleyDickson.Grade.PopcountOrAnd

cell-incl-excl = popcount-or-and
