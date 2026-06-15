{-# OPTIONS --safe --without-K #-}
-- M⁻¹M offset class d=(c−r)≡1 — a sub-diagonal of I (all zero). The cyclic orbit
-- of the byte-sum {b12,b16,c0d,c09} ≡ {00}, each in a +ⱽ-reassociated grouping (all refl).
module Substrate.Algebra.F2.MixColumns.Collapse.Off1 where
open import Substrate.Algebra.F2.MixColumns.Base
k01 : (b12 +ⱽ b16) +ⱽ (c0d +ⱽ c09) ≡ 𝟎ⱽ ; k01 = refl
k12 : (c09 +ⱽ b12) +ⱽ (b16 +ⱽ c0d) ≡ 𝟎ⱽ ; k12 = refl
k23 : (c0d +ⱽ c09) +ⱽ (b12 +ⱽ b16) ≡ 𝟎ⱽ ; k23 = refl
k30 : (b16 +ⱽ c0d) +ⱽ (c09 +ⱽ b12) ≡ 𝟎ⱽ ; k30 = refl
