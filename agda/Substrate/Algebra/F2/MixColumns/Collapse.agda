{-# OPTIONS --safe --without-K #-}
-- The 16 M⁻¹M entries in VALUE form (after the 8 products) ≡ I — pure byte-XOR, cheap.
module Substrate.Algebra.F2.MixColumns.Collapse where
open import Substrate.Algebra.F2.MixColumns.Base
k00 : (b1c +ⱽ c0b) +ⱽ (c0d +ⱽ b1b) ≡ c01 ; k00 = refl
k01 : (b12 +ⱽ b16) +ⱽ (c0d +ⱽ c09) ≡ 𝟎ⱽ ; k01 = refl
k02 : (c0e +ⱽ b1d) +ⱽ (b1a +ⱽ c09) ≡ 𝟎ⱽ ; k02 = refl
k03 : (c0e +ⱽ c0b) +ⱽ (b17 +ⱽ b12) ≡ 𝟎ⱽ ; k03 = refl
k10 : (b12 +ⱽ c0e) +ⱽ (c0b +ⱽ b17) ≡ 𝟎ⱽ ; k10 = refl
k11 : (b1b +ⱽ b1c) +ⱽ (c0b +ⱽ c0d) ≡ c01 ; k11 = refl
k12 : (c09 +ⱽ b12) +ⱽ (b16 +ⱽ c0d) ≡ 𝟎ⱽ ; k12 = refl
k13 : (c09 +ⱽ c0e) +ⱽ (b1d +ⱽ b1a) ≡ 𝟎ⱽ ; k13 = refl
k20 : (b1a +ⱽ c09) +ⱽ (c0e +ⱽ b1d) ≡ 𝟎ⱽ ; k20 = refl
k21 : (b17 +ⱽ b12) +ⱽ (c0e +ⱽ c0b) ≡ 𝟎ⱽ ; k21 = refl
k22 : (c0d +ⱽ b1b) +ⱽ (b1c +ⱽ c0b) ≡ c01 ; k22 = refl
k23 : (c0d +ⱽ c09) +ⱽ (b12 +ⱽ b16) ≡ 𝟎ⱽ ; k23 = refl
k30 : (b16 +ⱽ c0d) +ⱽ (c09 +ⱽ b12) ≡ 𝟎ⱽ ; k30 = refl
k31 : (b1d +ⱽ b1a) +ⱽ (c09 +ⱽ c0e) ≡ 𝟎ⱽ ; k31 = refl
k32 : (c0b +ⱽ b17) +ⱽ (b12 +ⱽ c0e) ≡ 𝟎ⱽ ; k32 = refl
k33 : (c0b +ⱽ c0d) +ⱽ (b1b +ⱽ b1c) ≡ c01 ; k33 = refl
