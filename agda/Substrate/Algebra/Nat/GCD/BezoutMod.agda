------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.BezoutMod
--
-- The EEA fold INTO ℤ/(suc mm) — "change the type EEA operates on" to the
-- modular target. Same EEATrace, coefficients are ℕ residues, the
-- back-substitution s := t', t := s' − t'·q is done MODULARLY (via negmod).
-- Stays in ℕ throughout (no ℤ→ℕ residue), using only the modular ring-
-- homomorphism (mod-add-hom/mod-mult-hom) ℕ+ negmod-inverse. Yields
-- (s·a ℕ+ t·b) ≡ g (mod M); at a coprime top (M,N,1) the coefficient of N
-- is N⁻¹ mod M — exactly the CRT inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.BezoutMod where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-distribˡ-+; *-distribʳ-+)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-add-hom; mod-mult-hom; mod-+-left)
open import Substrate.Algebra.Z.Residue using (negmod; negmod-inverse)
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; wedge-eq) renaming (Wedge-GCD to Wedge-GCD)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.Nat.GCD.Wedge

module _ (mm : ℕ) where

  BezoutMod : ℕ → ℕ → ℕ → Set
  BezoutMod a b g =
    Σ ℕ (λ s → Σ ℕ (λ t → (s * a ℕ+ t * b) mod-suc mm ≡ g mod-suc mm))

  mod-idem : (a : ℕ) → (a mod-suc mm) mod-suc mm ≡ a mod-suc mm
  mod-idem a = mod-suc-id (a mod-suc mm) mm (mod-suc-bound a mm)

  -- a summand that is 0 mod M drops out (mod M).
  drop-zero : (A Z : ℕ) → Z mod-suc mm ≡ 0 → (A ℕ+ Z) mod-suc mm ≡ A mod-suc mm
  drop-zero A Z z0 =
    trans (mod-add-hom A Z mm)
    (trans (cong (λ w → ((A mod-suc mm) ℕ+ w) mod-suc mm) z0)
    (trans (cong (_mod-suc mm) (+ℕ-identityʳ (A mod-suc mm))) (mod-idem A)))

  -- (A+B)ℕ+(C+D) ≡ (B+C)ℕ+(A+D).
  reorder4 : (A B C D : ℕ) → ((A ℕ+ B) ℕ+ (C ℕ+ D)) ≡ ((B ℕ+ C) ℕ+ (A ℕ+ D))
  reorder4 A B C D =
    trans (+ℕ-assoc A B (C ℕ+ D))
    (trans (cong (A ℕ+_) (sym (+ℕ-assoc B C D)))
    (trans (cong (A ℕ+_) (+ℕ-comm (B ℕ+ C) D))
    (trans (sym (+ℕ-assoc A D (B ℕ+ C))) (+ℕ-comm (A ℕ+ D) (B ℕ+ C)))))

  base-bm : (a : ℕ) → BezoutMod a 0 a
  base-bm a = 1 , 0 , cong (_mod-suc mm) (trans (+ℕ-identityʳ (a ℕ+ 0)) (+ℕ-identityʳ a))

  step-bm : {a g : ℕ} (b : ℕ) (w : Wedge-GCD a (suc b)) →
            BezoutMod (suc b) (remainder w) g → BezoutMod a (suc b) g
  step-bm {a} {g} b w (s' , t' , eq') =
    t' , (s' ℕ+ negmod (t' * q) mm) , proof
    where
      b' = suc b
      q  = quotient w
      r  = remainder w
      ng = negmod (t' * q) mm
      group-zero : (((t' * q) * b') ℕ+ (ng * b')) mod-suc mm ≡ 0
      group-zero =
        trans (cong (_mod-suc mm) (sym (*-distribʳ-+ b' (t' * q) ng)))
        (trans (mod-mult-hom ((t' * q) ℕ+ ng) b' mm)
               (cong (λ z → (z * (b' mod-suc mm)) mod-suc mm)
                     (trans (sym (mod-+-left (t' * q) ng mm))
                            (negmod-inverse (t' * q) mm))))
      rearr : (t' * (q * b' ℕ+ r)) ℕ+ ((s' ℕ+ ng) * b')
            ≡ ((t' * r) ℕ+ (s' * b')) ℕ+ (((t' * q) * b') ℕ+ (ng * b'))
      rearr =
        trans (cong₂ _ℕ+_ (*-distribˡ-+ t' (q * b') r) (*-distribʳ-+ b' s' ng))
        (trans (cong (λ z → (z ℕ+ (t' * r)) ℕ+ ((s' * b') ℕ+ (ng * b'))) (sym (*-assoc t' q b')))
               (reorder4 ((t' * q) * b') (t' * r) (s' * b') (ng * b')))
      proof : (t' * a ℕ+ (s' ℕ+ ng) * b') mod-suc mm ≡ g mod-suc mm
      proof =
        trans (cong (λ A → (t' * A ℕ+ (s' ℕ+ ng) * b') mod-suc mm) (wedge-eq w))
        (trans (cong (_mod-suc mm) rearr)
        (trans (drop-zero ((t' * r) ℕ+ (s' * b')) (((t' * q) * b') ℕ+ (ng * b')) group-zero)
        (trans (cong (_mod-suc mm) (+ℕ-comm (t' * r) (s' * b'))) eq')))

  bezout-mod : {a b g : ℕ} → EEATrace a b g → BezoutMod a b g
  bezout-mod (base a)            = base-bm a
  bezout-mod (step {a} {g} b w sub) = step-bm {g = g} b w (bezout-mod {g = g} sub)
