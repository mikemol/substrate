{-# OPTIONS --safe --without-K #-}
-- The four ×{02} products = xtime of the InvMixColumns coefficients {0e,0b,0d,09}.
-- Each is `xtime const` — a shift (cheap refl), NOT a const×const normalization.
module Substrate.Algebra.F2.MixColumns.Mul02 where
open import Substrate.Algebra.F2.GF256.Mul using (gmul)
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Scale using (gmul-c02)
pe2 : gmul c0e c02 ≡ b1c ; pe2 = trans (gmul-c02 c0e) refl
pb2 : gmul c0b c02 ≡ b16 ; pb2 = trans (gmul-c02 c0b) refl
pd2 : gmul c0d c02 ≡ b1a ; pd2 = trans (gmul-c02 c0d) refl
p92 : gmul c09 c02 ≡ b12 ; p92 = trans (gmul-c02 c09) refl
