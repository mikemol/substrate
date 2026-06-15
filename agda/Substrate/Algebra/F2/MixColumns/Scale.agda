{-# OPTIONS --safe --without-K #-}
-- The decomposition of the MixColumns coefficients: {02,03} = {x, x+1}, so scaling a byte
-- by them is NOT a generic gmul but the cheap `xtime` kernel + linearity:
--   gmul a {02} ≡ xtime a            (multiplication by x IS xtime, the reduce-mod-m kernel)
--   gmul a {03} ≡ xtime a +ⱽ a       (since {03} = {02} ⊕ {01}, by distributivity)
-- This is why the 8 "products" never needed a 280MB const×const normalization — each is
-- xtime of a constant (a shift) ⊕ XOR. Both lemmas are generic & abstract over a (cheap).
module Substrate.Algebra.F2.MixColumns.Scale where
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.GF256 using (xtime; gmul-comm; reduce-*P-expand;
  reduce-idempotent; hsum; hsum-zero) public
open import Substrate.Algebra.F2.Vector using (*ₛ-absorbˡ; *ₛ-identityˡ)

-- ×02 = xtime. gmul c02 a = hsum c02 (reduce a); c02 = 𝟘∷𝟙∷𝟎ⱽ picks out exactly xtime a.
gmul-c02 : (a : Vector 8) → gmul a c02 ≡ xtime a
gmul-c02 a =
  trans (gmul-comm a c02)
  (trans (reduce-*P-expand c02 a)
  (trans (cong (hsum c02) (reduce-idempotent a))
         (trans (cong₂ _+ⱽ_ (*ₛ-absorbˡ a)
                            (cong₂ _+ⱽ_ (*ₛ-identityˡ (xtime a)) (hsum-zero {6} (xtime (xtime a)))))
                (trans (+ⱽ-identityˡ (xtime a +ⱽ 𝟎ⱽ)) (+ⱽ-identityʳ (xtime a))))))

-- ×03 = ×02 ⊕ id, since c03 = c02 +ⱽ c01 (x+1 = x ⊕ 1).
gmul-c03 : (a : Vector 8) → gmul a c03 ≡ xtime a +ⱽ a
gmul-c03 a = trans (gmul-distribˡ a c02 c01)
                   (cong₂ _+ⱽ_ (gmul-c02 a) (gmul-identityʳ a))
