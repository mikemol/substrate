------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.AsField  (AI-8: GF(2⁸) : Field)
--
-- THE KEYSTONE.  GF(2⁸) = F₂[x]/(x⁸+x⁴+x³+x+1) packaged as a `Field`:
-- the Rijndael field with a fully-verified multiplicative inverse for every
-- nonzero byte.  The ring is `Quotient-Ring` (instance d=7, f-lo=m-lo), whose
-- `_*_` is `_*Q_` and whose `𝟙` is `oneC` — exactly the operations the inverse
-- law (`Inverse.inv-law`) speaks of, so the wrap needs NO bridge, just:
--   * `is-zero8-sound` — the reflection's Bool nonzero is the real nonzero;
--   * `0≢1`           — `nth 𝟎C 0 = 𝟘 ≠ 𝟙 = nth oneC 0`.
-- Fully --safe --without-K, ZERO postulates.  The inverse is constructed
-- (fuel-EEA) and its correctness proven (Bézout + irreducibility-by-reflection),
-- not asserted.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.AsField where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2 using (𝟘≢𝟙)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.Field using (Field)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo; is-zero8)
open import Substrate.Algebra.F2.Polynomial.Wedge.Inverse using (inv; inv-law)
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D

open F.Over F₂-CommRing using (Poly; nth)
open M.Over F₂-CommRing 7 m-lo using (oneC)
open Q.Over F₂-CommRing 7 m-lo using (Quotient-Ring; 𝟎C)

-- is-zero8 a ≡ true forces a to be the zero poly 𝟎C (= replicate 8 𝟘).
is-zero8-sound : (a : Poly 8) → is-zero8 a ≡ true → a ≡ 𝟎C
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []) h = refl
is-zero8-sound (F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ _) ()
is-zero8-sound (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ []) ()

-- bridge: the Field's propositional nonzero ⟹ the reflection's Bool nonzero.
nonzero-bridge : (a : Poly 8) → ¬ (a ≡ 𝟎C) → is-zero8 a ≡ false
nonzero-bridge a ¬z with is-zero8 a in eq
... | false = refl
... | true  = ⊥-elim (¬z (is-zero8-sound a eq))

-- AI-8 ★ THE KEYSTONE.
GF2⁸-Field : Field (Poly 8)
GF2⁸-Field = record
  { ring        = Quotient-Ring
  ; 0≢1         = λ eq → 𝟘≢𝟙 (cong (λ v → nth v 0) eq)
  ; mul-inv     = λ a _ → inv a
  ; mul-inv-law = λ a a≢0 → inv-law a (nonzero-bridge a a≢0)
  }
