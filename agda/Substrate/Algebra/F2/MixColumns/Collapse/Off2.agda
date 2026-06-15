{-# OPTIONS --safe --without-K #-}
-- M⁻¹M offset class d=(c−r)≡2 — a sub-diagonal of I (all zero). The cyclic orbit
-- of the byte-sum {c0e,b1d,b1a,c09} ≡ {00}, each in a +ⱽ-reassociated grouping (all refl).
module Substrate.Algebra.F2.MixColumns.Collapse.Off2 where
open import Substrate.Algebra.F2.MixColumns.Base
k02 : (c0e +ⱽ b1d) +ⱽ (b1a +ⱽ c09) ≡ 𝟎ⱽ ; k02 = refl
k13 : (c09 +ⱽ c0e) +ⱽ (b1d +ⱽ b1a) ≡ 𝟎ⱽ ; k13 = refl
k20 : (b1a +ⱽ c09) +ⱽ (c0e +ⱽ b1d) ≡ 𝟎ⱽ ; k20 = refl
k31 : (b1d +ⱽ b1a) +ⱽ (c09 +ⱽ c0e) ≡ 𝟎ⱽ ; k31 = refl
