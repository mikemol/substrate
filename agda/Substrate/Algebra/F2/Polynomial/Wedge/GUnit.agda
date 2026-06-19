{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit  (generic g = unit, B-INV-UNIT)
--
-- The gcd produced by the fuel-EEA for inverting a byte `a` modulo the AES
-- modulus m = x^8+x^4+x^3+x+1 is the field UNIT (1, 𝟙∷[]) for every NONZERO a.
-- This is exactly the irreducibility obligation (a coprime to m ⟺ gcd = 1),
-- discharged by REFLECTION: `all-vec check` normalises the EEA over all 256
-- bytes and computes to `true` (≈7s, one refl), and `all-vec-sound` extracts
-- the per-byte fact.  Fully --safe, zero postulates — proof IS the computation.
--
-- Delivers `g-unit-nth0` / `g-unit-nths` = the two `nth g …` hypotheses that
-- `inverse-from-bezout` consumes; with the fuel-bezout witness this closes the
-- GF(2⁸) inverse law (a ≠ 0 → a · a⁻¹ = 1) for the Field wrap.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; subst)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_; _∨_)
open import Substrate.Foundation.Bool.Properties using (∧-elimˡ; ∧-elimʳ) public
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly)
open import Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA using (fuel-bezout)
import Substrate.Algebra.Polynomial.Graded.Div as D
open D.Over F₂-CommRing 0 (F2.𝟘 ∷ []) using (nth)

-- AES modulus low part: b-poly = x^8 + x^4+x^3+x+1.
m-lo : Vec F2.F₂ 8
m-lo = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

-- gcd of an invertible byte is EXACTLY the unit (1, 𝟙∷[]).
is-unit-q : QPoly → Bool
is-unit-q (suc zero , (F2.𝟙 ∷ [])) = true
is-unit-q _                        = false

is-zero8 : Vec F2.F₂ 8 → Bool
is-zero8 (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []) = true
is-zero8 _ = false

gcd-of : Vec F2.F₂ 8 → QPoly
gcd-of a = proj₁ (fuel-bezout 10 (8 , a) 7 m-lo)

check : Vec F2.F₂ 8 → Bool
check a = is-unit-q (gcd-of a) ∨ is-zero8 a

-- generic exhaustion over all 2^n bit-vectors + soundness.
all-vec : {n : ℕ} (P : Vec F2.F₂ n → Bool) → Bool
all-vec {zero}  P = P []
all-vec {suc n} P = all-vec (λ v → P (F2.𝟘 ∷ v)) ∧ all-vec (λ v → P (F2.𝟙 ∷ v))

-- Ⓓ: ∧-elimˡ/ʳ are Foundation.Bool.Properties' (imported + re-exported above);
-- they were re-proved here. SBox / SBoxTable consume them via this module.

all-vec-sound : {n : ℕ} (P : Vec F2.F₂ n → Bool) → all-vec P ≡ true
              → (v : Vec F2.F₂ n) → P v ≡ true
all-vec-sound {zero}  P h []         = h
all-vec-sound {suc n} P h (F2.𝟘 ∷ v) = all-vec-sound (λ w → P (F2.𝟘 ∷ w)) (∧-elimˡ {all-vec (λ w → P (F2.𝟘 ∷ w))} h) v
all-vec-sound {suc n} P h (F2.𝟙 ∷ v) = all-vec-sound (λ w → P (F2.𝟙 ∷ w)) (∧-elimʳ {all-vec (λ w → P (F2.𝟘 ∷ w))} h) v

-- THE COMPUTED FACT: every byte passes (9s refl over 256 EEA runs).
all-pass : all-vec check ≡ true
all-pass = refl

∨-elim-false : {a : Bool} → (a ∨ false) ≡ true → a ≡ true
∨-elim-false {true}  h = refl
∨-elim-false {false} ()

-- per-byte: nonzero ⟹ gcd is the unit.
unit-of : (a : Vec F2.F₂ 8) → is-zero8 a ≡ false → is-unit-q (gcd-of a) ≡ true
unit-of a z =
  ∨-elim-false (subst (λ b → (is-unit-q (gcd-of a) ∨ b) ≡ true) z (all-vec-sound check all-pass a))

-- is-unit-q ≡ true forces the two unit conditions.
unit-q-nth0 : (q : QPoly) → is-unit-q q ≡ true → nth (proj₂ q) 0 ≡ F2.𝟙
unit-q-nth0 (suc zero , (F2.𝟙 ∷ [])) h = refl
unit-q-nth0 (suc zero , (F2.𝟘 ∷ [])) ()
unit-q-nth0 (zero , [])              ()
unit-q-nth0 (suc (suc n) , v)        ()

unit-q-nths : (q : QPoly) → is-unit-q q ≡ true → (k : ℕ) → nth (proj₂ q) (suc k) ≡ F2.𝟘
unit-q-nths (suc zero , (F2.𝟙 ∷ [])) h k = refl
unit-q-nths (suc zero , (F2.𝟘 ∷ [])) () k
unit-q-nths (zero , [])              () k
unit-q-nths (suc (suc n) , v)        () k

-- THE GENERIC g = unit: for every nonzero byte, the EEA gcd is the field unit.
g-unit-nth0 : (a : Vec F2.F₂ 8) → is-zero8 a ≡ false → nth (proj₂ (gcd-of a)) 0 ≡ F2.𝟙
g-unit-nth0 a z = unit-q-nth0 (gcd-of a) (unit-of a z)

g-unit-nths : (a : Vec F2.F₂ 8) → is-zero8 a ≡ false → (k : ℕ) → nth (proj₂ (gcd-of a)) (suc k) ≡ F2.𝟘
g-unit-nths a z = unit-q-nths (gcd-of a) (unit-of a z)
