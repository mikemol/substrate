{-# OPTIONS --safe --without-K #-}
-- AI-9 MixColumns round-trip. The whole proof lives in a module ABSTRACT over the
-- byte constants + the 8 products + the 16 value-form collapses + the unit/zero laws,
-- so its body type-checks with every gmul SYMBOLIC (no const×const normalization).
-- Instantiating with the concrete constants + the imported products/collapses is cheap
-- (Agda substitutes, it does not re-check the body). The ONLY const×const normalization
-- in the whole development is the 8 product files — the "8 tests".
module Substrate.Algebra.F2.MixColumns.Proof where
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Pe2 ; open import Substrate.Algebra.F2.MixColumns.Pe3
open import Substrate.Algebra.F2.MixColumns.Pb2 ; open import Substrate.Algebra.F2.MixColumns.Pb3
open import Substrate.Algebra.F2.MixColumns.Pd2 ; open import Substrate.Algebra.F2.MixColumns.Pd3
open import Substrate.Algebra.F2.MixColumns.P92 ; open import Substrate.Algebra.F2.MixColumns.P93
open import Substrate.Algebra.F2.MixColumns.Collapse

module G
  (x01 x02 x03 x09 x0b x0d x0e : Vector 8)
  (v1c v12 v16 v1d v1a v17 v1b : Vector 8)
  (qe2 : gmul x0e x02 ≡ v1c) (qe3 : gmul x0e x03 ≡ v12)
  (qb2 : gmul x0b x02 ≡ v16) (qb3 : gmul x0b x03 ≡ v1d)
  (qd2 : gmul x0d x02 ≡ v1a) (qd3 : gmul x0d x03 ≡ v17)
  (q92 : gmul x09 x02 ≡ v12) (q93 : gmul x09 x03 ≡ v1b)
  (idˡ : (a : Vector 8) → gmul x01 a ≡ a)
  (idʳ : (b : Vector 8) → gmul b x01 ≡ b)
  (zˡ  : (a : Vector 8) → gmul 𝟎ⱽ a ≡ 𝟎ⱽ)
  (h00 : (v1c +ⱽ x0b) +ⱽ (x0d +ⱽ v1b) ≡ x01) (h01 : (v12 +ⱽ v16) +ⱽ (x0d +ⱽ x09) ≡ 𝟎ⱽ)
  (h02 : (x0e +ⱽ v1d) +ⱽ (v1a +ⱽ x09) ≡ 𝟎ⱽ) (h03 : (x0e +ⱽ x0b) +ⱽ (v17 +ⱽ v12) ≡ 𝟎ⱽ)
  (h10 : (v12 +ⱽ x0e) +ⱽ (x0b +ⱽ v17) ≡ 𝟎ⱽ) (h11 : (v1b +ⱽ v1c) +ⱽ (x0b +ⱽ x0d) ≡ x01)
  (h12 : (x09 +ⱽ v12) +ⱽ (v16 +ⱽ x0d) ≡ 𝟎ⱽ) (h13 : (x09 +ⱽ x0e) +ⱽ (v1d +ⱽ v1a) ≡ 𝟎ⱽ)
  (h20 : (v1a +ⱽ x09) +ⱽ (x0e +ⱽ v1d) ≡ 𝟎ⱽ) (h21 : (v17 +ⱽ v12) +ⱽ (x0e +ⱽ x0b) ≡ 𝟎ⱽ)
  (h22 : (x0d +ⱽ v1b) +ⱽ (v1c +ⱽ x0b) ≡ x01) (h23 : (x0d +ⱽ x09) +ⱽ (v12 +ⱽ v16) ≡ 𝟎ⱽ)
  (h30 : (v16 +ⱽ x0d) +ⱽ (x09 +ⱽ v12) ≡ 𝟎ⱽ) (h31 : (v1d +ⱽ v1a) +ⱽ (x09 +ⱽ x0e) ≡ 𝟎ⱽ)
  (h32 : (x0b +ⱽ v17) +ⱽ (v12 +ⱽ x0e) ≡ 𝟎ⱽ) (h33 : (x0b +ⱽ x0d) +ⱽ (v1b +ⱽ v1c) ≡ x01)
  where
  -- regroup an inverse-row applied to the four MixColumns outputs (abstract constants).
  air : (e0 e1 e2 e3 a0 a1 a2 a3 : Vector 8)
    → dot4 e0 e1 e2 e3 (dot4 x02 x03 x01 x01 a0 a1 a2 a3) (dot4 x01 x02 x03 x01 a0 a1 a2 a3)
        (dot4 x01 x01 x02 x03 a0 a1 a2 a3) (dot4 x03 x01 x01 x02 a0 a1 a2 a3)
    ≡ dot4 ((gmul e0 x02 +ⱽ gmul e1 x01) +ⱽ (gmul e2 x01 +ⱽ gmul e3 x03))
           ((gmul e0 x03 +ⱽ gmul e1 x02) +ⱽ (gmul e2 x01 +ⱽ gmul e3 x01))
           ((gmul e0 x01 +ⱽ gmul e1 x03) +ⱽ (gmul e2 x02 +ⱽ gmul e3 x01))
           ((gmul e0 x01 +ⱽ gmul e1 x01) +ⱽ (gmul e2 x03 +ⱽ gmul e3 x02)) a0 a1 a2 a3
  air e0 e1 e2 e3 a0 a1 a2 a3 =
    trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (gmul-dot4 e0 x02 x03 x01 x01 a0 a1 a2 a3) (gmul-dot4 e1 x01 x02 x03 x01 a0 a1 a2 a3))
            (cong₂ _+ⱽ_ (gmul-dot4 e2 x01 x01 x02 x03 a0 a1 a2 a3) (gmul-dot4 e3 x03 x01 x01 x02 a0 a1 a2 a3)))
    (trans (cong₂ _+ⱽ_ (dot4-add (gmul e0 x02) (gmul e0 x03) (gmul e0 x01) (gmul e0 x01)
                      (gmul e1 x01) (gmul e1 x02) (gmul e1 x03) (gmul e1 x01) a0 a1 a2 a3)
            (dot4-add (gmul e2 x01) (gmul e2 x01) (gmul e2 x02) (gmul e2 x03)
                      (gmul e3 x03) (gmul e3 x01) (gmul e3 x01) (gmul e3 x02) a0 a1 a2 a3))
           (dot4-add (gmul e0 x02 +ⱽ gmul e1 x01) (gmul e0 x03 +ⱽ gmul e1 x02)
                     (gmul e0 x01 +ⱽ gmul e1 x03) (gmul e0 x01 +ⱽ gmul e1 x01)
                     (gmul e2 x01 +ⱽ gmul e3 x03) (gmul e2 x01 +ⱽ gmul e3 x01)
                     (gmul e2 x02 +ⱽ gmul e3 x01) (gmul e2 x03 +ⱽ gmul e3 x02) a0 a1 a2 a3))
  i0 : (a0 a1 a2 a3 : Vector 8) → dot4 x01 𝟎ⱽ 𝟎ⱽ 𝟎ⱽ a0 a1 a2 a3 ≡ a0
  i0 a0 a1 a2 a3 = trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idˡ a0) (zˡ a1)) (cong₂ _+ⱽ_ (zˡ a2) (zˡ a3)))
                        (trans (cong₂ _+ⱽ_ (+ⱽ-identityʳ a0) (+ⱽ-identityˡ 𝟎ⱽ)) (+ⱽ-identityʳ a0))
  i1 : (a0 a1 a2 a3 : Vector 8) → dot4 𝟎ⱽ x01 𝟎ⱽ 𝟎ⱽ a0 a1 a2 a3 ≡ a1
  i1 a0 a1 a2 a3 = trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (zˡ a0) (idˡ a1)) (cong₂ _+ⱽ_ (zˡ a2) (zˡ a3)))
                        (trans (cong₂ _+ⱽ_ (+ⱽ-identityˡ a1) (+ⱽ-identityˡ 𝟎ⱽ)) (+ⱽ-identityʳ a1))
  i2 : (a0 a1 a2 a3 : Vector 8) → dot4 𝟎ⱽ 𝟎ⱽ x01 𝟎ⱽ a0 a1 a2 a3 ≡ a2
  i2 a0 a1 a2 a3 = trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (zˡ a0) (zˡ a1)) (cong₂ _+ⱽ_ (idˡ a2) (zˡ a3)))
                        (trans (cong₂ _+ⱽ_ (+ⱽ-identityˡ 𝟎ⱽ) (+ⱽ-identityʳ a2)) (+ⱽ-identityˡ a2))
  i3 : (a0 a1 a2 a3 : Vector 8) → dot4 𝟎ⱽ 𝟎ⱽ 𝟎ⱽ x01 a0 a1 a2 a3 ≡ a3
  i3 a0 a1 a2 a3 = trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (zˡ a0) (zˡ a1)) (cong₂ _+ⱽ_ (zˡ a2) (idˡ a3)))
                        (trans (cong₂ _+ⱽ_ (+ⱽ-identityˡ 𝟎ⱽ) (+ⱽ-identityˡ a3)) (+ⱽ-identityˡ a3))
  mix : Vec (Vector 8) 4 → Vec (Vector 8) 4
  mix (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    dot4 x02 x03 x01 x01 a0 a1 a2 a3 ∷ dot4 x01 x02 x03 x01 a0 a1 a2 a3 ∷
    dot4 x01 x01 x02 x03 a0 a1 a2 a3 ∷ dot4 x03 x01 x01 x02 a0 a1 a2 a3 ∷ []
  inv : Vec (Vector 8) 4 → Vec (Vector 8) 4
  inv (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) =
    dot4 x0e x0b x0d x09 b0 b1 b2 b3 ∷ dot4 x09 x0e x0b x0d b0 b1 b2 b3 ∷
    dot4 x0d x09 x0e x0b b0 b1 b2 b3 ∷ dot4 x0b x0d x09 x0e b0 b1 b2 b3 ∷ []
  round-trip : (col : Vec (Vector 8) 4) → inv (mix col) ≡ col
  round-trip (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    cong₂ _∷_ (trans (air x0e x0b x0d x09 a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe2 (idʳ x0b)) (cong₂ _+ⱽ_ (idʳ x0d) q93)) h00)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe3 qb2) (cong₂ _+ⱽ_ (idʳ x0d) (idʳ x09))) h01)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) qb3) (cong₂ _+ⱽ_ qd2 (idʳ x09))) h02)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) (idʳ x0b)) (cong₂ _+ⱽ_ qd3 q92)) h03)) (i0 a0 a1 a2 a3)))
    (cong₂ _∷_ (trans (air x09 x0e x0b x0d a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ q92 (idʳ x0e)) (cong₂ _+ⱽ_ (idʳ x0b) qd3)) h10)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ q93 qe2) (cong₂ _+ⱽ_ (idʳ x0b) (idʳ x0d))) h11)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x09) qe3) (cong₂ _+ⱽ_ qb2 (idʳ x0d))) h12)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x09) (idʳ x0e)) (cong₂ _+ⱽ_ qb3 qd2)) h13)) (i1 a0 a1 a2 a3)))
    (cong₂ _∷_ (trans (air x0d x09 x0e x0b a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qd2 (idʳ x09)) (cong₂ _+ⱽ_ (idʳ x0e) qb3)) h20)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qd3 q92) (cong₂ _+ⱽ_ (idʳ x0e) (idʳ x0b))) h21)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0d) q93) (cong₂ _+ⱽ_ qe2 (idʳ x0b))) h22)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0d) (idʳ x09)) (cong₂ _+ⱽ_ qe3 qb2)) h23)) (i2 a0 a1 a2 a3)))
    (cong₂ _∷_ (trans (air x0b x0d x09 x0e a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qb2 (idʳ x0d)) (cong₂ _+ⱽ_ (idʳ x09) qe3)) h30)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qb3 qd2) (cong₂ _+ⱽ_ (idʳ x09) (idʳ x0e))) h31)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0b) qd3) (cong₂ _+ⱽ_ q92 (idʳ x0e))) h32)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0b) (idʳ x0d)) (cong₂ _+ⱽ_ q93 qe2)) h33)) (i3 a0 a1 a2 a3)))
    refl)))

-- INSTANTIATE with the concrete constants + the imported products/collapses/laws.
open G c01 c02 c03 c09 c0b c0d c0e b1c b12 b16 b1d b1a b17 b1b
       pe2 pe3 pb2 pb3 pd2 pd3 p92 p93
       gmul-identityˡ gmul-identityʳ gmul-zeroˡ
       k00 k01 k02 k03 k10 k11 k12 k13 k20 k21 k22 k23 k30 k31 k32 k33
       public

-- the concrete MixColumns round-trip (InvMixColumns ∘ MixColumns ≡ id per column).
mixcolumns-round-trip : (col : Vec (Vector 8) 4) → inv (mix col) ≡ col
mixcolumns-round-trip = round-trip
