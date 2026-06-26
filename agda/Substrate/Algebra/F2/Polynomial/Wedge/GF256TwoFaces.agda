------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF256TwoFaces
--
-- The dlog inverse and EEA ≡ dlog equivalence at the AES BYTE field GF(2⁸),
-- for the X-POWERS (the order-51 ⟨x⟩ subgroup).
--
-- MEASURED (this session): in GF(2⁸) = F₂[x]/(x⁸+x⁴+x³+x+1), the element x has
-- multiplicative ORDER 51, not 255 — x is NOT primitive (x⁵¹ ≡ 1, x⁸⁵ ≢ 1; AES
-- uses 0x03 = x+1 as its generator). So the cheap division-regime antilog
-- `gpow = x^·` (DLogHom at GF(2⁸)) reaches only the ⟨x⟩ subgroup, NOT all 255
-- nonzero bytes. The FULL byte field needs the primitive (x+1)^·, whose powers
-- are not ytime-cheap → the Frobenius arc `Ⓐ.gf256-primitive` (rostered).
--
-- For the x-powers this is complete and cheap:
--   • `order255 : gpow 255 ≡ oneC` (x²⁵⁵ = 1 by Lagrange; cheap in the division
--     regime — `xpow 255 oneC` stays degree < 8 throughout).
--   • `dlog-inv-law₈` (the general DLogHom law at GF(2⁸)): gᵏ · g^(255−k) ≡ 1.
--   • `two-faces` : the AES EEA-Bézout inverse (`Inverse.inv`) ≡ the dlog inverse,
--     for x-power elements, by `inv-unique` (structural, no EEA reflection).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF256TwoFaces where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Bool using (false)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo; is-zero8)
open import Substrate.Algebra.F2.Polynomial.Wedge.Inverse using (inv; inv-law)
import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom as DH

open D.Over F₂-CommRing 7 m-lo
  using (Poly; _*Q_; oneC; *Q-comm; *Q-assoc; *Q-identityˡ; *Q-identityʳ)

-- the division-regime antilog at GF(2⁸): x^· (covers the order-51 ⟨x⟩ subgroup).
module GF256 = DH.Over 7 m-lo
gpow : ℕ → Poly 8
gpow = GF256.gpow

-- x²⁵⁵ ≡ 1 (Lagrange; |GF(2⁸)*| = 255). Cheap: bounded magnitude at every step.
order255 : gpow 255 ≡ oneC
order255 = refl

-- the dlog inverse law for x-powers: gᵏ · g^(255−k) ≡ 1, all k+j = 255 at once.
dlog-inv-law₈ : (k j : ℕ) → k + j ≡ 255 → (gpow k *Q gpow j) ≡ oneC
dlog-inv-law₈ = GF256.dlog-inv-law 255 order255

------------------------------------------------------------------------
-- inverse-uniqueness in the *Q commutative monoid (d = 7).
------------------------------------------------------------------------

inv-unique : (a b c : Poly 8) → a *Q b ≡ oneC → a *Q c ≡ oneC → b ≡ c
inv-unique a b c ab ac =
  trans (sym (*Q-identityʳ b))
  (trans (cong (b *Q_) (sym ac))
  (trans (sym (*Q-assoc b a c))
  (trans (cong (_*Q c) (*Q-comm b a))
  (trans (cong (_*Q c) ab)
         (*Q-identityˡ c)))))

------------------------------------------------------------------------
-- TWO FACES at GF(2⁸) (x-powers): the AES EEA-Bézout inverse ≡ the dlog inverse,
-- because the inverse is unique. (gᵏ nonzero; k+j = 255.)
------------------------------------------------------------------------

two-faces : (k j : ℕ) → k + j ≡ 255 → is-zero8 (gpow k) ≡ false →
            inv (gpow k) ≡ gpow j
two-faces k j kj nz =
  inv-unique (gpow k) (inv (gpow k)) (gpow j)
    (inv-law (gpow k) nz) (dlog-inv-law₈ k j kj)

-- a concrete witness: inv(x) = x²⁵⁴ (the EEA inverse of the byte x agrees with
-- its discrete-log inverse).
tf-1 : inv (gpow 1) ≡ gpow 254
tf-1 = two-faces 1 254 refl refl
