{-# OPTIONS --safe --without-K #-}
-- M⁻¹M offset class d=(c−r)≡0 — the DIAGONAL of I. M⁻¹ and M are both circulant,
-- so the entry depends only on (c−r) mod 4; these four are the CYCLIC ORBIT of the
-- single byte-sum {b1c,c0b,c0d,b1b} ≡ {01}, each in a +ⱽ-reassociated grouping (all refl).
module Substrate.Algebra.F2.MixColumns.Collapse.Diag where
open import Substrate.Algebra.F2.MixColumns.Base
k00 : (b1c +ⱽ c0b) +ⱽ (c0d +ⱽ b1b) ≡ c01 ; k00 = refl
k11 : (b1b +ⱽ b1c) +ⱽ (c0b +ⱽ c0d) ≡ c01 ; k11 = refl
k22 : (c0d +ⱽ b1b) +ⱽ (b1c +ⱽ c0b) ≡ c01 ; k22 = refl
k33 : (c0b +ⱽ c0d) +ⱽ (b1b +ⱽ b1c) ≡ c01 ; k33 = refl
