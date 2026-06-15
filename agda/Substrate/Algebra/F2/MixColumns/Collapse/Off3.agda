{-# OPTIONS --safe --without-K #-}
-- M⁻¹M offset class d=(c−r)≡3 — a sub-diagonal of I (all zero). The cyclic orbit
-- of the byte-sum {c0e,c0b,b17,b12} ≡ {00}, each in a +ⱽ-reassociated grouping (all refl).
module Substrate.Algebra.F2.MixColumns.Collapse.Off3 where
open import Substrate.Algebra.F2.MixColumns.Base
k03 : (c0e +ⱽ c0b) +ⱽ (b17 +ⱽ b12) ≡ 𝟎ⱽ ; k03 = refl
k10 : (b12 +ⱽ c0e) +ⱽ (c0b +ⱽ b17) ≡ 𝟎ⱽ ; k10 = refl
k21 : (b17 +ⱽ b12) +ⱽ (c0e +ⱽ c0b) ≡ 𝟎ⱽ ; k21 = refl
k32 : (c0b +ⱽ b17) +ⱽ (b12 +ⱽ c0e) ≡ 𝟎ⱽ ; k32 = refl
