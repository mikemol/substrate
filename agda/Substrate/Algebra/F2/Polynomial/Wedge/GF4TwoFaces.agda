------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF4TwoFaces
--
-- Ⓐ.two-faces — THE CRYPTOGRAPHIC-TOTAL-SPACE CAPSTONE at GF(4): the two
-- constructions of the field inverse compute the ONE object.
--
--   FACE 1 (EEA-Bézout): `eea-inv` — run the extended Euclidean algorithm,
--           read the Bézout cofactor (mirror of `GF16Inverse` at d=1).
--   FACE 2 (discrete-log): `dlog-inv` — g^(neg(log a)), the additive negation
--           transported by the antilog (`GF4DLog`, via `ExpLogCodec.codec-inverse`).
--
-- `two-faces : eea-inv (g^k) ≡ dlog-inv k` — they AGREE, and the proof is
-- structural, not enumerative: BOTH are right-inverses of the same element, and
-- a right-inverse in the *Q commutative monoid is UNIQUE (`inv-unique`). So the
-- agreement is not a coincidence of computation — it is forced by the object
-- being uniquely determined. Two faces, one inverse.
--
-- (This also retires GF4DLog's orphan-leaf advisory: it is now imported here.)
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF4TwoFaces where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _∨_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly; divisor-q)
open import Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA using (fuel-bezout)
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base using (BezoutNthWitness)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (is-unit-q; ∨-elim-false; unit-q-nth0; unit-q-nths)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base using (all-vec; all-vec-sound)
import Substrate.Algebra.Polynomial.Graded.ModZero as MZ
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.GF4DLog
  using (Exp3; z0; z1; z2; expL₃; dlog-inv; dlog-inv-law; m-lo₂)

open F.Over F₂-CommRing
open M.Over F₂-CommRing 1 m-lo₂
open Q.Over F₂-CommRing 1 m-lo₂
open D.Over F₂-CommRing 1 m-lo₂
  using (Poly; _*Q_; oneC; reduce-mod-f; *Q-comm; *Q-assoc; *Q-identityˡ; *Q-identityʳ)
module M₂ = MZ.Over F₂-CommRing 1 m-lo₂

------------------------------------------------------------------------
-- inverse-uniqueness: in the *Q commutative monoid, a right-inverse is unique.
-- b = b·1 = b·(a·c) = (b·a)·c = (a·b)·c = 1·c = c.
------------------------------------------------------------------------

inv-unique : (a b c : Poly 2) → a *Q b ≡ oneC → a *Q c ≡ oneC → b ≡ c
inv-unique a b c ab ac =
  trans (sym (*Q-identityʳ b))
  (trans (cong (b *Q_) (sym ac))
  (trans (sym (*Q-assoc b a c))
  (trans (cong (_*Q c) (*Q-comm b a))
  (trans (cong (_*Q c) ab)
         (*Q-identityˡ c)))))

------------------------------------------------------------------------
-- FACE 1 — the EEA-Bézout inverse at GF(4) (mirror of GF16Inverse at d=1).
------------------------------------------------------------------------

is-zero2 : Vec F2.F₂ 2 → Bool
is-zero2 (F2.𝟘 ∷ F2.𝟘 ∷ []) = true
is-zero2 _                   = false

W₂ : (a : Poly 2) → Σ QPoly (BezoutNthWitness (2 , a) (divisor-q 1 m-lo₂))
W₂ a = fuel-bezout 4 (2 , a) 1 m-lo₂

gcd-of₂ : Vec F2.F₂ 2 → QPoly
gcd-of₂ a = proj₁ (W₂ a)

check₂ : Vec F2.F₂ 2 → Bool
check₂ a = is-unit-q (gcd-of₂ a) ∨ is-zero2 a

-- x²+x+1 is irreducible over F₂ → every nonzero element's gcd with m is the unit
-- (a 4-element reflection).
all-pass₂ : all-vec check₂ ≡ true
all-pass₂ = refl

unit-of₂ : (a : Vec F2.F₂ 2) → is-zero2 a ≡ false → is-unit-q (gcd-of₂ a) ≡ true
unit-of₂ a z =
  ∨-elim-false (subst (λ b → (is-unit-q (gcd-of₂ a) ∨ b) ≡ true) z
                      (all-vec-sound check₂ all-pass₂ a))

eea-inv : Poly 2 → Poly 2
eea-inv a = reduce-mod-f (proj₂ (proj₁ (proj₂ (W₂ a))))

eea-inv-law : (a : Poly 2) → is-zero2 a ≡ false → a *Q (eea-inv a) ≡ oneC
eea-inv-law a z = M₂.inverse-from-bezout
  (proj₂ (proj₁ (proj₂ (W₂ a))))
  a
  (proj₂ (proj₁ (proj₂ (proj₂ (W₂ a)))))
  (proj₂ (proj₁ (W₂ a)))
  (proj₂ (proj₂ (proj₂ (W₂ a))))
  (unit-q-nth0 (gcd-of₂ a) (unit-of₂ a z))
  (unit-q-nths (gcd-of₂ a) (unit-of₂ a z))

------------------------------------------------------------------------
-- each antilog image g^k is a nonzero field element (so FACE 1 applies).
------------------------------------------------------------------------

nonzero-expL : (k : Exp3) → is-zero2 (expL₃ k) ≡ false
nonzero-expL z0 = refl
nonzero-expL z1 = refl
nonzero-expL z2 = refl

------------------------------------------------------------------------
-- Ⓐ.two-faces: the EEA-Bézout inverse ≡ the discrete-log inverse, BECAUSE the
-- inverse is unique. Different constructions, one object.
------------------------------------------------------------------------

two-faces : (k : Exp3) → eea-inv (expL₃ k) ≡ dlog-inv k
two-faces k = inv-unique (expL₃ k) (eea-inv (expL₃ k)) (dlog-inv k)
                (eea-inv-law (expL₃ k) (nonzero-expL k))
                (dlog-inv-law k)
