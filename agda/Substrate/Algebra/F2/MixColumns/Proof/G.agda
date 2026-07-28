{-# OPTIONS --safe --without-K #-}
-- ⟡cap-128-forcing: the ABSTRACT MixColumns round-trip, split out of
-- Substrate.Algebra.F2.MixColumns.Proof so it elaborates ONCE with every constant
-- SYMBOLIC. Its three heavy halves — `air` (the regrouping lemma, .G.Air), the
-- C₄-equivariance chain (.G.Equiv) and the coordinate-0 round-trip (.G.Head) — are
-- PLAIN TOP-LEVEL operators over their hypotheses, not parameterized modules: a
-- module application COPIES, so opening them would re-elaborate all three inside
-- this one unit (measured: 190MB unsplit, 160MB with module-application halves,
-- both over the 128MiB cap). As references each is paid for exactly once.
--
-- What is left here is only the C₄ assembly: coordinate 0 is `rt-head`; coordinates
-- 1,2,3 are `rt-head` on the rotated column, pulled back through f's equivariance.
module Substrate.Algebra.F2.MixColumns.Proof.G where
open import Substrate.Algebra.F2.GF256.Mul
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Proof.G.Equiv
open import Substrate.Algebra.F2.MixColumns.Proof.G.Head

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
  -- the 4 collapse REPRESENTATIVES — one per circulant offset class (row 0 of M⁻¹M = e₀):
  (h00 : (v1c +ⱽ x0b) +ⱽ (x0d +ⱽ v1b) ≡ x01) (h01 : (v12 +ⱽ v16) +ⱽ (x0d +ⱽ x09) ≡ 𝟎ⱽ)
  (h02 : (x0e +ⱽ v1d) +ⱽ (v1a +ⱽ x09) ≡ 𝟎ⱽ) (h03 : (x0e +ⱽ x0b) +ⱽ (v17 +ⱽ v12) ≡ 𝟎ⱽ)
  where
  head₀ : (col : Vec (Vector 8) 4)
        → hd (invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col)) ≡ hd col
  head₀ = rt-head x01 x02 x03 x09 x0b x0d x0e v1c v12 v16 v1d v1a v17 v1b
                  qe2 qe3 qb2 qb3 qd2 qd3 q92 q93 idˡ idʳ zˡ h00 h01 h02 h03

  -- the four output coordinates: coord 0 is head₀; coords 1,2,3 are head₀ on the
  -- rotated column, pulled back through f's equivariance. The redundancy has evaporated.
  round-trip : (col : Vec (Vector 8) 4) → invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col) ≡ col
  round-trip col@(a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    cong₂ _∷_ (head₀ col)
    (cong₂ _∷_ (trans (sym (cong hd (f-rot³ x01 x02 x03 x09 x0b x0d x0e col)))
                      (head₀ (rot (rot (rot col)))))
    (cong₂ _∷_ (trans (sym (cong hd (f-rot² x01 x02 x03 x09 x0b x0d x0e col)))
                      (head₀ (rot (rot col))))
    (cong₂ _∷_ (trans (sym (cong hd (f-rot  x01 x02 x03 x09 x0b x0d x0e col)))
                      (head₀ (rot col)))
    refl)))

-- INSTANTIATE: the 8 products + the 4 collapse representatives k00,k01,k02,k03.
