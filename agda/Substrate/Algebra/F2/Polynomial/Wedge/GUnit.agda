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
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base public
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly)
open import Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA using (fuel-bezout)
import Substrate.Algebra.Polynomial.Graded.Base as GB
open GB.Over F2.𝟘 using (nth)

-- m-lo / is-zero8 / all-vec / all-vec-sound live in GUnit.Base (EEA-free
-- slice), re-exported via `open … GUnit.Base public` above.

-- gcd of an invertible byte is EXACTLY the unit (1, 𝟙∷[]).
is-unit-q : QPoly → Bool
is-unit-q (suc zero , (F2.𝟙 ∷ [])) = true
is-unit-q _                        = false

gcd-of : Vec F2.F₂ 8 → QPoly
gcd-of a = proj₁ (fuel-bezout 10 (8 , a) 7 m-lo)

check : Vec F2.F₂ 8 → Bool
check a = is-unit-q (gcd-of a) ∨ is-zero8 a

-- all-vec / all-vec-sound (generic 2ⁿ bit-vector exhaustion) live in
-- GUnit.Base, re-exported via `open … GUnit.Base public`; SBox / SBoxTable
-- consume them (and ∧-elimˡ/ʳ) via this module's re-export.

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
