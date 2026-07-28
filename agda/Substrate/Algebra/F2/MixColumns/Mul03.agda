{-# OPTIONS --safe --without-K #-}
-- The four ×{03} products = (xtime ⊕ id) of the InvMixColumns coefficients {0e,0b,0d,09}.
-- Each is `xtime const +ⱽ const` — a shift and a XOR (cheap refl), NOT a const×const.
module Substrate.Algebra.F2.MixColumns.Mul03 where
open import Substrate.Algebra.F2.GF256.Mul using (gmul)
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Scale using (gmul-c03)
pe3 : gmul c0e c03 ≡ b12 ; pe3 = trans (gmul-c03 c0e) refl
pb3 : gmul c0b c03 ≡ b1d ; pb3 = trans (gmul-c03 c0b) refl
pd3 : gmul c0d c03 ≡ b17 ; pd3 = trans (gmul-c03 c0d) refl
p93 : gmul c09 c03 ≡ b1b ; p93 = trans (gmul-c03 c09) refl
