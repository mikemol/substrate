------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.ModZero  (B-EEA-INV, crux)
--
-- The modulus reduces to zero: `reduce-mod-f b-poly ≡ 𝟎C`, over any
-- CommutativeRing.  b-poly = y^(suc d) − f-lo is the divisor; modulo itself it
-- is 0.  This is the key fact behind reading the inverse off a Bézout identity
-- (B-EEA-INV → AI-8): in `s·a + t·m = 1`, the `t·m` term vanishes mod m, so
-- `reduce(s·a) = 1`.
--
-- Proof: split b-poly = y^(suc d) +P snoc(−f-lo)𝟘; the monomial reduces to f-lo
-- (the defining modulus relation `reduce-y-shift` + `ytime` on the monomial),
-- the snoc-𝟘 part reduces to −f-lo (`reduce` ignores trailing zeros), and
-- f-lo +P −f-lo ≡ 𝟎C (`+P-inverseʳ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.ModZero where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.Div as D

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open D.Over CR d f-lo

  private variable n : ℕ

  -- vlast / vinit of a snoc.
  vlast-snoc : (w : Poly n) (x : A) → vlast (snoc w x) ≡ x
  vlast-snoc []      x = refl
  vlast-snoc (a ∷ w) x = vlast-snoc w x

  vinit-snoc : (w : Poly n) (x : A) → vinit (snoc w x) ≡ w
  vinit-snoc []      x = refl
  vinit-snoc (a ∷ w) x = cong (a ∷_) (vinit-snoc w x)

  -- reduce ignores a trailing zero.
  reduce-snoc-zero : (w : Poly n) → reduce-mod-f (snoc w 𝟘) ≡ reduce-mod-f w
  reduce-snoc-zero []      = trans (reduce-y-shift []) ytime-zero
  reduce-snoc-zero (a ∷ w) =
    cong (λ z → (a ∷ replicate d 𝟘) +P ytime z) (reduce-snoc-zero w)

  -- the monomial y^(suc d) reduces to f-lo (the defining modulus relation).
  monomial : Poly (suc (suc d))
  monomial = snoc (replicate (suc d) 𝟘) 𝟙

  reduce-monomial : reduce-mod-f monomial ≡ f-lo
  reduce-monomial =
    trans (reduce-y-shift (snoc (replicate d 𝟘) 𝟙))
    (trans (cong ytime (reduce-idempotent (snoc (replicate d 𝟘) 𝟙)))
           ytime-M')
    where
      ytime-M' : ytime (snoc (replicate d 𝟘) 𝟙) ≡ f-lo
      ytime-M' =
        trans (cong₂ _+P_ (cong (𝟘 ∷_) (vinit-snoc (replicate d 𝟘) 𝟙))
                          (cong (_·c f-lo) (vlast-snoc (replicate d 𝟘) 𝟙)))
        (trans (cong ((𝟘 ∷ replicate d 𝟘) +P_) (·c-identityˡ f-lo))
               (+P-identityˡ f-lo))

  -- THE CRUX: the modulus b-poly reduces to 0.
  reduce-modulus-zero : reduce-mod-f b-poly ≡ replicate (suc d) 𝟘
  reduce-modulus-zero =
    trans (cong reduce-mod-f bp≡)
    (trans (reduce-+P monomial (snoc (-P f-lo) 𝟘))
    (trans (cong₂ _+P_ reduce-monomial
                       (trans (reduce-snoc-zero (-P f-lo)) (reduce-idempotent (-P f-lo))))
           (+P-inverseʳ f-lo)))
    where
      bp≡ : b-poly ≡ monomial +P snoc (-P f-lo) 𝟘
      bp≡ = sym (trans (snoc-+P (replicate (suc d) 𝟘) (-P f-lo) 𝟙 𝟘)
                       (cong₂ snoc (+P-identityˡ (-P f-lo)) (+-identityʳ 𝟙)))
