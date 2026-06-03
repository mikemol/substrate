------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.BezoutMod
--
-- The EEA fold INTO ℤ/(suc mm) — "change the type EEA operates on" to the
-- modular target. Same EEATrace, coefficients are ℕ residues, the
-- back-substitution s := t', t := s' − t'·q is done MODULARLY (via negmod).
-- Stays in ℕ throughout (no ℤ→ℕ residue), using only the modular ring-
-- homomorphism (mod-add-hom/mod-mult-hom) + negmod-inverse. Yields
-- (s·a + t·b) ≡ g (mod M); at a coprime top (M,N,1) the coefficient of N
-- is N⁻¹ mod M — exactly the CRT inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.BezoutMod where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm; +-assoc; +-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-distribˡ-+; *-distribʳ-+)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-id; mod-suc-bound)
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-add-hom; mod-mult-hom; mod-+-left)
open import Substrate.Algebra.Z.Residue using (negmod; negmod-inverse)
open import Substrate.Algebra.Nat.GCD.Wedge using (Wedge; quotient; remainder; wedge-eq)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)

module _ (mm : ℕ) where

  BezoutMod : ℕ → ℕ → ℕ → Set
  BezoutMod a b g =
    Σ ℕ (λ s → Σ ℕ (λ t → (s * a + t * b) mod-suc mm ≡ g mod-suc mm))

  mod-idem : (a : ℕ) → (a mod-suc mm) mod-suc mm ≡ a mod-suc mm
  mod-idem a = mod-suc-id (a mod-suc mm) mm (mod-suc-bound a mm)

  -- a summand that is 0 mod M drops out (mod M).
  drop-zero : (A Z : ℕ) → Z mod-suc mm ≡ 0 → (A + Z) mod-suc mm ≡ A mod-suc mm
  drop-zero A Z z0 =
    trans (mod-add-hom A Z mm)
    (trans (cong (λ w → ((A mod-suc mm) + w) mod-suc mm) z0)
    (trans (cong (_mod-suc mm) (+-identityʳ (A mod-suc mm))) (mod-idem A)))

  -- (A+B)+(C+D) ≡ (B+C)+(A+D).
  reorder4 : (A B C D : ℕ) → ((A + B) + (C + D)) ≡ ((B + C) + (A + D))
  reorder4 A B C D =
    trans (+-assoc A B (C + D))
    (trans (cong (A +_) (sym (+-assoc B C D)))
    (trans (cong (A +_) (+-comm (B + C) D))
    (trans (sym (+-assoc A D (B + C))) (+-comm (A + D) (B + C)))))

  base-bm : (a : ℕ) → BezoutMod a 0 a
  base-bm a = 1 , 0 , cong (_mod-suc mm) (trans (+-identityʳ (a + 0)) (+-identityʳ a))

  step-bm : {a g : ℕ} (b : ℕ) (w : Wedge a (suc b)) →
            BezoutMod (suc b) (remainder w) g → BezoutMod a (suc b) g
  step-bm {a} {g} b w (s' , t' , eq') =
    t' , (s' + negmod (t' * q) mm) , proof
    where
      b' = suc b
      q  = quotient w
      r  = remainder w
      ng = negmod (t' * q) mm
      group-zero : (((t' * q) * b') + (ng * b')) mod-suc mm ≡ 0
      group-zero =
        trans (cong (_mod-suc mm) (sym (*-distribʳ-+ b' (t' * q) ng)))
        (trans (mod-mult-hom ((t' * q) + ng) b' mm)
               (cong (λ z → (z * (b' mod-suc mm)) mod-suc mm)
                     (trans (sym (mod-+-left (t' * q) ng mm))
                            (negmod-inverse (t' * q) mm))))
      rearr : (t' * (q * b' + r)) + ((s' + ng) * b')
            ≡ ((t' * r) + (s' * b')) + (((t' * q) * b') + (ng * b'))
      rearr =
        trans (cong₂ _+_ (*-distribˡ-+ t' (q * b') r) (*-distribʳ-+ b' s' ng))
        (trans (cong (λ z → (z + (t' * r)) + ((s' * b') + (ng * b'))) (sym (*-assoc t' q b')))
               (reorder4 ((t' * q) * b') (t' * r) (s' * b') (ng * b')))
      proof : (t' * a + (s' + ng) * b') mod-suc mm ≡ g mod-suc mm
      proof =
        trans (cong (λ A → (t' * A + (s' + ng) * b') mod-suc mm) (wedge-eq w))
        (trans (cong (_mod-suc mm) rearr)
        (trans (drop-zero ((t' * r) + (s' * b')) (((t' * q) * b') + (ng * b')) group-zero)
        (trans (cong (_mod-suc mm) (+-comm (t' * r) (s' * b'))) eq')))

  bezout-mod : {a b g : ℕ} → EEATrace a b g → BezoutMod a b g
  bezout-mod (base a)            = base-bm a
  bezout-mod (step {a} {g} b w sub) = step-bm {g = g} b w (bezout-mod {g = g} sub)
