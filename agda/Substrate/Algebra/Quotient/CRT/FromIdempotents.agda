------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.FromIdempotents
--
-- The CRT combine — the wedge for two moduli. Given the IDEMPOTENTS
-- e₁,e₂ : ℕ (the local solutions: e₁ ≡ 1 mod (suc m), ≡ 0 mod (suc n);
-- e₂ the mirror), the reconstruction map combine(a₁,a₂) = a₁·e₁ + a₂·e₂
-- glues the two local truths into the global one, AND its correctness is
-- exactly the modular ring-homomorphism bridge in action (mod-add-hom +
-- mod-mult-hom). This builds a full CRT-Witness — the glue is the content.
--
-- (Deriving e₁,e₂ from a coprimality/Bézout witness — the ℤ→ℕ residue
-- extraction — is the separable follow-on that feeds this map.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.FromIdempotents where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityʳ; *-zeroʳ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-id; mod-suc-bound)
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-add-hom; mod-mult-hom)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness)
open import Substrate.Algebra.Quotient.CRT.Idempotents using (CRTIdempotents)

------------------------------------------------------------------------
-- 1. mod is idempotent (its output is already reduced).
------------------------------------------------------------------------

mod-idempotent : (a m : ℕ) → (a mod-suc m) mod-suc m ≡ a mod-suc m
mod-idempotent a m = mod-suc-id (a mod-suc m) m (mod-suc-bound a m)

-- multiplying by an idempotent ≡ 1 (mod M) is identity (mod M).
mult-idem-1 : (x e mm : ℕ) → e mod-suc mm ≡ 1 → (x * e) mod-suc mm ≡ x mod-suc mm
mult-idem-1 x e mm e≡1 =
  trans (mod-mult-hom x e mm)
  (trans (cong (λ z → ((x mod-suc mm) * z) mod-suc mm) e≡1)
  (trans (cong (_mod-suc mm) (*-identityʳ (x mod-suc mm)))
         (mod-idempotent x mm)))

-- multiplying by an idempotent ≡ 0 (mod M) is 0 (mod M).
mult-idem-0 : (x e mm : ℕ) → e mod-suc mm ≡ 0 → (x * e) mod-suc mm ≡ 0
mult-idem-0 x e mm e≡0 =
  trans (mod-mult-hom x e mm)
  (trans (cong (λ z → ((x mod-suc mm) * z) mod-suc mm) e≡0)
         (cong (_mod-suc mm) (*-zeroʳ (x mod-suc mm))))

------------------------------------------------------------------------
-- 3. The CRT combine: glue the local solutions, proved correct.
------------------------------------------------------------------------

crt-witness : {m n : ℕ} → CRTIdempotents m n → CRT-Witness m n
crt-witness {m} {n} idem = record
  { combine       = λ p → proj₁ p * e₁ + proj₂ p * e₂
  ; combine-mod-m = cmm
  ; combine-mod-n = cmn
  }
  where
    open CRTIdempotents idem
    cmm : (a₁ a₂ : ℕ) → (a₁ * e₁ + a₂ * e₂) mod-suc m ≡ a₁ mod-suc m
    cmm a₁ a₂ =
      trans (mod-add-hom (a₁ * e₁) (a₂ * e₂) m)
      (trans (cong₂ (λ u v → (u + v) mod-suc m)
                    (mult-idem-1 a₁ e₁ m e₁-mod-m)
                    (mult-idem-0 a₂ e₂ m e₂-mod-m))
      (trans (cong (_mod-suc m) (+-identityʳ (a₁ mod-suc m)))
             (mod-idempotent a₁ m)))
    cmn : (a₁ a₂ : ℕ) → (a₁ * e₁ + a₂ * e₂) mod-suc n ≡ a₂ mod-suc n
    cmn a₁ a₂ =
      trans (mod-add-hom (a₁ * e₁) (a₂ * e₂) n)
      (trans (cong₂ (λ u v → (u + v) mod-suc n)
                    (mult-idem-0 a₁ e₁ n e₁-mod-n)
                    (mult-idem-1 a₂ e₂ n e₂-mod-n))
             (mod-idempotent a₂ n))
