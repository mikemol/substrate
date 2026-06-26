------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF16TwoFaces
--
-- Ⓐ.two-faces-16 — the Cryptographic-Total-Space capstone at GF(2⁴): the two
-- constructions of the field inverse compute the ONE object, at the AES nibble
-- field (where `x` is primitive, so every nonzero element is a power gᵏ).
--
--   FACE 1 (EEA-Bézout): `inv₄`   — run the EEA, read the Bézout cofactor (GF16Inverse).
--   FACE 2 (discrete-log): `gpow` — gᵏ in the division regime (DLogHom).
--
-- `two-faces : inv₄ (gᵏ) ≡ gʲ` whenever `k+j = 15` (gᵏ nonzero) — proved
-- STRUCTURALLY by `inv-unique` (a right-inverse in the *Q commutative monoid is
-- unique): both `inv₄(gᵏ)` and `gʲ` are right-inverses of `gᵏ`, so they agree.
-- No EEA reflection in the proof; the inverse is uniquely determined.
--
-- Scales the GF(4) `GF4TwoFaces` capstone to GF(2⁴), using the GENERAL dlog law
-- `DLogHom.dlog-inv₄`. Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF16TwoFaces where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Bool using (false)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.GF16Inverse
  using (inv₄; inv-law₄; is-zero4; m-lo₄)
import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom as DH

open D.Over F₂-CommRing 3 m-lo₄
  using (Poly; _*Q_; oneC; *Q-comm; *Q-assoc; *Q-identityˡ; *Q-identityʳ)

-- the dlog antilog at GF(2⁴) (division regime; x primitive, order 15).
gpow : ℕ → Poly 4
gpow = DH.GF16.gpow

------------------------------------------------------------------------
-- inverse-uniqueness in the *Q commutative monoid: b = b·1 = b·(a·c) = (b·a)·c
-- = (a·b)·c = 1·c = c.
------------------------------------------------------------------------

inv-unique : (a b c : Poly 4) → a *Q b ≡ oneC → a *Q c ≡ oneC → b ≡ c
inv-unique a b c ab ac =
  trans (sym (*Q-identityʳ b))
  (trans (cong (b *Q_) (sym ac))
  (trans (sym (*Q-assoc b a c))
  (trans (cong (_*Q c) (*Q-comm b a))
  (trans (cong (_*Q c) ab)
         (*Q-identityˡ c)))))

------------------------------------------------------------------------
-- Ⓐ.two-faces-16: the EEA-Bézout inverse ≡ the discrete-log inverse, at GF(2⁴),
-- because the inverse is unique. (gᵏ nonzero; k+j = 15.)
------------------------------------------------------------------------

two-faces : (k j : ℕ) → k + j ≡ 15 → is-zero4 (gpow k) ≡ false →
            inv₄ (gpow k) ≡ gpow j
two-faces k j kj nz =
  inv-unique (gpow k) (inv₄ (gpow k)) (gpow j)
    (inv-law₄ (gpow k) nz) (DH.dlog-inv₄ k j kj)

-- concrete witnesses across the cycle (gᵏ nonzero is a cheap refl per element).
tf-1·14 : inv₄ (gpow 1)  ≡ gpow 14 ; tf-1·14 = two-faces 1  14 refl refl
tf-7·8  : inv₄ (gpow 7)  ≡ gpow 8  ; tf-7·8  = two-faces 7  8  refl refl
tf-13·2 : inv₄ (gpow 13) ≡ gpow 2  ; tf-13·2 = two-faces 13 2  refl refl
