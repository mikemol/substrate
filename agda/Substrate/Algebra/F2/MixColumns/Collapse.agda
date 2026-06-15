{-# OPTIONS --safe --without-K #-}
-- The 4 collapse REPRESENTATIVES of M⁻¹M ≡ I, in value form (after the 8 products).
-- M⁻¹ and M are both circulant ⇒ M⁻¹M is circulant ⇒ entry (r,c) depends only on the
-- offset (c−r) mod 4. So row 0 (entries (0,0),(0,1),(0,2),(0,3) = offsets 0,1,2,3) gives
-- ONE representative per offset class; the circulant-factored Proof recovers all 16 entries
-- from these four by the C4 rotation. (The other 12 entries evaporated with rt1/rt2/rt3.)
--   k00 = offset 0 (diagonal) ≡ {01} ;  k01,k02,k03 = offsets 1,2,3 ≡ {00}.
module Substrate.Algebra.F2.MixColumns.Collapse where
open import Substrate.Algebra.F2.MixColumns.Base
k00 : (b1c +ⱽ c0b) +ⱽ (c0d +ⱽ b1b) ≡ c01 ; k00 = refl
k01 : (b12 +ⱽ b16) +ⱽ (c0d +ⱽ c09) ≡ 𝟎ⱽ ; k01 = refl
k02 : (c0e +ⱽ b1d) +ⱽ (b1a +ⱽ c09) ≡ 𝟎ⱽ ; k02 = refl
k03 : (c0e +ⱽ c0b) +ⱽ (b17 +ⱽ b12) ≡ 𝟎ⱽ ; k03 = refl
