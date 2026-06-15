{-# OPTIONS --safe --without-K #-}
-- AI-9 MixColumns round-trip, CIRCULANT-FACTORED. M⁻¹ and M are both circulant, so
-- mix and inv are C4-equivariant: they commute with the cyclic rotation `rot` of a column.
-- The round-trip is therefore proven ONCE at coordinate 0 (`rt-head`, the only place the
-- 8 GF products + 4 collapse representatives are used) and the other three coordinates are
-- `rt-head` transported by `rot` — so rt1/rt2/rt3 and 12 of the 16 collapses EVAPORATE.
--
-- The whole proof is ABSTRACT over the constants (every gmul symbolic ⇒ no const×const
-- normalization), instantiated cheaply below. The 8 GF products are now `xtime`+XOR of
-- constants (Mul02/Mul03 via Scale) — NO const×const normalization remains anywhere.
module Substrate.Algebra.F2.MixColumns.Proof where
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Mul02  -- pe2 pb2 pd2 p92 (= xtime of inv-coeffs)
open import Substrate.Algebra.F2.MixColumns.Mul03  -- pe3 pb3 pd3 p93 (= xtime ⊕ id)
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
  -- the 4 collapse REPRESENTATIVES — one per circulant offset class (row 0 of M⁻¹M = e₀):
  (h00 : (v1c +ⱽ x0b) +ⱽ (x0d +ⱽ v1b) ≡ x01) (h01 : (v12 +ⱽ v16) +ⱽ (x0d +ⱽ x09) ≡ 𝟎ⱽ)
  (h02 : (x0e +ⱽ v1d) +ⱽ (v1a +ⱽ x09) ≡ 𝟎ⱽ) (h03 : (x0e +ⱽ x0b) +ⱽ (v17 +ⱽ v12) ≡ 𝟎ⱽ)
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
  -- coordinate-0 identity: dot4 x01 𝟎 𝟎 𝟎 picks out a0.
  i0 : (a0 a1 a2 a3 : Vector 8) → dot4 x01 𝟎ⱽ 𝟎ⱽ 𝟎ⱽ a0 a1 a2 a3 ≡ a0
  i0 a0 a1 a2 a3 = trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idˡ a0) (zˡ a1)) (cong₂ _+ⱽ_ (zˡ a2) (zˡ a3)))
                        (trans (cong₂ _+ⱽ_ (+ⱽ-identityʳ a0) (+ⱽ-identityˡ 𝟎ⱽ)) (+ⱽ-identityʳ a0))

  mix : Vec (Vector 8) 4 → Vec (Vector 8) 4
  mix (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    dot4 x02 x03 x01 x01 a0 a1 a2 a3 ∷ dot4 x01 x02 x03 x01 a0 a1 a2 a3 ∷
    dot4 x01 x01 x02 x03 a0 a1 a2 a3 ∷ dot4 x03 x01 x01 x02 a0 a1 a2 a3 ∷ []
  inv : Vec (Vector 8) 4 → Vec (Vector 8) 4
  inv (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) =
    dot4 x0e x0b x0d x09 b0 b1 b2 b3 ∷ dot4 x09 x0e x0b x0d b0 b1 b2 b3 ∷
    dot4 x0d x09 x0e x0b b0 b1 b2 b3 ∷ dot4 x0b x0d x09 x0e b0 b1 b2 b3 ∷ []

  -- cyclic rotation of a column (rotate right) and its head.
  rot : Vec (Vector 8) 4 → Vec (Vector 8) 4
  rot (a ∷ b ∷ c ∷ d ∷ []) = d ∷ a ∷ b ∷ c ∷ []
  hd : Vec (Vector 8) 4 → Vector 8
  hd (x ∷ _) = x

  -- mix and inv are CIRCULANT ⇒ C4-equivariant: each coordinate is one dot4-cyc.
  mix-rot : (col : Vec (Vector 8) 4) → mix (rot col) ≡ rot (mix col)
  mix-rot (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    cong₂ _∷_ (dot4-cyc x02 x03 x01 x01 a0 a1 a2 a3)
    (cong₂ _∷_ (dot4-cyc x01 x02 x03 x01 a0 a1 a2 a3)
    (cong₂ _∷_ (dot4-cyc x01 x01 x02 x03 a0 a1 a2 a3)
    (cong₂ _∷_ (dot4-cyc x03 x01 x01 x02 a0 a1 a2 a3) refl)))
  inv-rot : (col : Vec (Vector 8) 4) → inv (rot col) ≡ rot (inv col)
  inv-rot (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) =
    cong₂ _∷_ (dot4-cyc x0e x0b x0d x09 b0 b1 b2 b3)
    (cong₂ _∷_ (dot4-cyc x09 x0e x0b x0d b0 b1 b2 b3)
    (cong₂ _∷_ (dot4-cyc x0d x09 x0e x0b b0 b1 b2 b3)
    (cong₂ _∷_ (dot4-cyc x0b x0d x09 x0e b0 b1 b2 b3) refl)))

  -- hence f = inv ∘ mix is C4-equivariant; iterate for the 2nd/3rd rotation.
  f-rot : (col : Vec (Vector 8) 4) → inv (mix (rot col)) ≡ rot (inv (mix col))
  f-rot col = trans (cong inv (mix-rot col)) (inv-rot (mix col))
  f-rot² : (col : Vec (Vector 8) 4) → inv (mix (rot (rot col))) ≡ rot (rot (inv (mix col)))
  f-rot² col = trans (f-rot (rot col)) (cong rot (f-rot col))
  f-rot³ : (col : Vec (Vector 8) 4)
         → inv (mix (rot (rot (rot col)))) ≡ rot (rot (rot (inv (mix col))))
  f-rot³ col = trans (f-rot (rot (rot col))) (cong rot (f-rot² col))

  -- THE coordinate-0 round-trip: inv-row-0 · (mix col) = col₀. The ONLY use of the 8
  -- products + the 4 collapse representatives; offsets 0,1,2,3 = h00,h01,h02,h03.
  rt-head : (col : Vec (Vector 8) 4) → hd (inv (mix col)) ≡ hd col
  rt-head (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    trans (air x0e x0b x0d x09 a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe2 (idʳ x0b)) (cong₂ _+ⱽ_ (idʳ x0d) q93)) h00)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe3 qb2) (cong₂ _+ⱽ_ (idʳ x0d) (idʳ x09))) h01)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) qb3) (cong₂ _+ⱽ_ qd2 (idʳ x09))) h02)
        (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) (idʳ x0b)) (cong₂ _+ⱽ_ qd3 q92)) h03)) (i0 a0 a1 a2 a3))

  -- the four output coordinates: coord 0 is rt-head; coords 1,2,3 are rt-head on the
  -- rotated column, pulled back through f's equivariance. The redundancy has evaporated.
  round-trip : (col : Vec (Vector 8) 4) → inv (mix col) ≡ col
  round-trip col@(a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
    cong₂ _∷_ (rt-head col)
    (cong₂ _∷_ (trans (sym (cong hd (f-rot³ col))) (rt-head (rot (rot (rot col)))))
    (cong₂ _∷_ (trans (sym (cong hd (f-rot² col))) (rt-head (rot (rot col))))
    (cong₂ _∷_ (trans (sym (cong hd (f-rot  col))) (rt-head (rot col)))
    refl)))

-- INSTANTIATE: the 8 products + the 4 collapse representatives k00,k01,k02,k03.
open G c01 c02 c03 c09 c0b c0d c0e b1c b12 b16 b1d b1a b17 b1b
       pe2 pe3 pb2 pb3 pd2 pd3 p92 p93
       gmul-identityˡ gmul-identityʳ gmul-zeroˡ
       k00 k01 k02 k03
       public

-- the concrete MixColumns round-trip (InvMixColumns ∘ MixColumns ≡ id per column).
mixcolumns-round-trip : (col : Vec (Vector 8) 4) → inv (mix col) ≡ col
mixcolumns-round-trip = round-trip
