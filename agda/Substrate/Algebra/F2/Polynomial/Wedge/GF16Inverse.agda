------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF16Inverse
--
-- Ⓐ.gfinv-witness — the EEA-inverse template (Wedge.Inverse) WITNESSED at a
-- SECOND field, GF(2⁴) = F₂[x]/(x⁴+x+1). This proves the GF(2⁸) inverse-law is
-- one INSTANCE of a field-generic construction (the "AES isn't restricted to
-- 8-bit bytes" point made concrete): the same `fuel-bezout` + generic
-- `inverse-from-bezout` + generic `is-unit-q`/`unit-q-nth0` machinery, re-aimed
-- at (d=3, m-lo₄). Only the irreducibility witness is new — and at GF(2⁴) it is
-- a cheap 16-nibble reflection (vs 256 bytes at GF(2⁸)).
--
-- A mirror of Wedge.Inverse at degree 4; everything generic is REUSED, not
-- rebuilt (the reuse-search discipline: `fuel-bezout`, `inverse-from-bezout`,
-- `is-unit-q`, `all-vec`/`all-vec-sound`, `unit-q-nth0/nths`, `∨-elim-false`).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF16Inverse where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; subst)
open import Substrate.Foundation.Bool using (Bool; true; false; _∨_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly; divisor-q)
open import Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA using (fuel-bezout)
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold using (BezoutNthWitness)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit
  using (is-unit-q; all-vec; all-vec-sound; ∨-elim-false; unit-q-nth0; unit-q-nths)
import Substrate.Algebra.Polynomial.Graded.ModZero as MZ
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D

-- GF(2⁴) modulus  x⁴ + x + 1  (low part, x⁰..x³ = 1,1,0,0; the leading x⁴ implicit).
m-lo₄ : Vec F2.F₂ 4
m-lo₄ = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

open F.Over F₂-CommRing using (Poly)
open M.Over F₂-CommRing 3 m-lo₄ using (reduce-mod-f; oneC)
open Q.Over F₂-CommRing 3 m-lo₄ using (_*Q_)
module M₄ = MZ.Over F₂-CommRing 3 m-lo₄

is-zero4 : Vec F2.F₂ 4 → Bool
is-zero4 (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []) = true
is-zero4 _ = false

-- the fuel-EEA Bézout run for a nibble (fuel 8 ≥ 4 EEA steps).
W₄ : (a : Poly 4) → Σ QPoly (BezoutNthWitness (4 , a) (divisor-q 3 m-lo₄))
W₄ a = fuel-bezout 8 (4 , a) 3 m-lo₄

gcd-of₄ : Vec F2.F₂ 4 → QPoly
gcd-of₄ a = proj₁ (W₄ a)

check₄ : Vec F2.F₂ 4 → Bool
check₄ a = is-unit-q (gcd-of₄ a) ∨ is-zero4 a

-- THE IRREDUCIBILITY WITNESS: every nonzero nibble's gcd with m is the unit
-- (x⁴+x+1 is irreducible over F₂) — a 16-element reflection (cheap).
all-pass₄ : all-vec check₄ ≡ true
all-pass₄ = refl

unit-of₄ : (a : Vec F2.F₂ 4) → is-zero4 a ≡ false → is-unit-q (gcd-of₄ a) ≡ true
unit-of₄ a z =
  ∨-elim-false (subst (λ b → (is-unit-q (gcd-of₄ a) ∨ b) ≡ true) z
                      (all-vec-sound check₄ all-pass₄ a))

-- a⁻¹ = reduce (the Bézout cofactor s) — read off the same EEA trace as GF(2⁸).
inv₄ : Poly 4 → Poly 4
inv₄ a = reduce-mod-f (proj₂ (proj₁ (proj₂ (W₄ a))))

-- THE GF(2⁴) INVERSE LAW: every nonzero nibble has a · a⁻¹ ≡ 𝟙. Same proof shape
-- as Wedge.Inverse.inv-law, at (d=3, m-lo₄) — the template at a second field.
inv-law₄ : (a : Poly 4) → is-zero4 a ≡ false → a *Q (inv₄ a) ≡ oneC
inv-law₄ a z = M₄.inverse-from-bezout
  (proj₂ (proj₁ (proj₂ (W₄ a))))
  a
  (proj₂ (proj₁ (proj₂ (proj₂ (W₄ a)))))
  (proj₂ (proj₁ (W₄ a)))
  (proj₂ (proj₂ (proj₂ (W₄ a))))
  (unit-q-nth0 (gcd-of₄ a) (unit-of₄ a z))
  (unit-q-nths (gcd-of₄ a) (unit-of₄ a z))
