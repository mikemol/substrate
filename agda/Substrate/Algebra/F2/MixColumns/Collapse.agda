{-# OPTIONS --safe --without-K #-}
-- The 16 M⁻¹M entries in VALUE form (after the 8 products) ≡ I — pure byte-XOR, cheap.
-- RE-EXPORT HUB. M⁻¹ and M are both circulant ⇒ M⁻¹M is circulant ⇒ entry (r,c)
-- depends only on the offset (c−r) mod 4. So the 16 are 4 CYCLIC ORBITS (one per
-- offset), each holding the orbit's byte-sum; split theorem-per-orbit under Collapse/:
--   Diag (d≡0) ≡ {01}   ·   Off1/Off2/Off3 (d≡1,2,3) ≡ {00}.
module Substrate.Algebra.F2.MixColumns.Collapse where
open import Substrate.Algebra.F2.MixColumns.Collapse.Diag public
open import Substrate.Algebra.F2.MixColumns.Collapse.Off1 public
open import Substrate.Algebra.F2.MixColumns.Collapse.Off2 public
open import Substrate.Algebra.F2.MixColumns.Collapse.Off3 public
