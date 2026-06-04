------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.IntParityBridge
--
-- ℤ ↠ F₂ — the parity bridge on the ℤ root, completing the parity story
-- (Algebra.Wedge.ParityBridge gave ℕ ↠ F₂; ℤ ⊃ ℕ, so this extends it). A
-- genuine cross-root wedge bridge that RAISES the bridge-degree of the founded
-- roots beyond the ℕ-centric star: ℤ-div and F₂-div each gain an edge that does
-- not route through ℕ.
--
-- parity-ℤ is SIGN-BLIND: −x ≡ x (mod 2), so the negative branch -suc n maps to
-- parity (suc n) — the magnitude's parity. The ring-hom laws (respects recon)
-- reduce to the ℕ parity laws (reused from ParityBridge) plus two F₂
-- rearrangements that hold by 4-case refl (F₂ is the decidable carrier where
-- the cancellation is computational — the LEM-faithful flip again).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.IntParityBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; +-comm; +-identityʳ)
  renaming (_+_ to _+₂_)
open import Substrate.Algebra.F2.Wedge using (F₂-div; scale)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; 0ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_; _⊖_)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
open import Substrate.Algebra.Wedge.ParityBridge using (parity; parity-+; parity-scale)

------------------------------------------------------------------------
-- 1. parity on ℤ — sign-blind (magnitude's parity).
------------------------------------------------------------------------

parity-ℤ : ℤ → F₂
parity-ℤ (+ n)    = parity n
parity-ℤ (-suc n) = parity (suc n)

------------------------------------------------------------------------
-- 2. F₂ rearrangements (4-case refl — the decidable cancellation).
------------------------------------------------------------------------

-- x + y = (𝟙+x) + (𝟙+y): the two units cancel.
f2-shift : (x y : F₂) → x +₂ y ≡ (𝟙 +₂ x) +₂ (𝟙 +₂ y)
f2-shift 𝟘 𝟘 = refl
f2-shift 𝟘 𝟙 = refl
f2-shift 𝟙 𝟘 = refl
f2-shift 𝟙 𝟙 = refl

-- 𝟙+(𝟙+(x+y)) = (𝟙+x)+(𝟙+y): the same cancellation, for the both-negative case.
f2-both : (x y : F₂) → 𝟙 +₂ (𝟙 +₂ (x +₂ y)) ≡ (𝟙 +₂ x) +₂ (𝟙 +₂ y)
f2-both 𝟘 𝟘 = refl
f2-both 𝟘 𝟙 = refl
f2-both 𝟙 𝟘 = refl
f2-both 𝟙 𝟙 = refl

------------------------------------------------------------------------
-- 3. parity of the truncated difference: m ⊖ n ≡ m + n (mod 2).
------------------------------------------------------------------------

parity-⊖ : (m n : ℕ) → parity-ℤ (m ⊖ n) ≡ parity m +₂ parity n
parity-⊖ m       zero    = sym (+-identityʳ (parity m))
parity-⊖ zero    (suc n) = refl
parity-⊖ (suc m) (suc n) = trans (parity-⊖ m n) (f2-shift (parity m) (parity n))

------------------------------------------------------------------------
-- 4. parity-ℤ is additive: parity-ℤ (x +ℤ y) ≡ parity-ℤ x + parity-ℤ y.
------------------------------------------------------------------------

parity-ℤ-+ : (x y : ℤ) → parity-ℤ (x +ℤ y) ≡ parity-ℤ x +₂ parity-ℤ y
parity-ℤ-+ (+ m)    (+ n)    = parity-+ m n
parity-ℤ-+ (+ m)    (-suc n) = parity-⊖ m (suc n)
parity-ℤ-+ (-suc m) (+ n)    =
  trans (parity-⊖ n (suc m)) (+-comm (parity n) (parity (suc m)))
parity-ℤ-+ (-suc m) (-suc n) =
  trans (cong (λ w → 𝟙 +₂ (𝟙 +₂ w)) (parity-+ m n)) (f2-both (parity m) (parity n))

------------------------------------------------------------------------
-- 5. parity-ℤ kills the sign: parity-ℤ (-ℤ (+ k)) ≡ parity k.
------------------------------------------------------------------------

parity-negPos : (k : ℕ) → parity-ℤ (-ℤ (+ k)) ≡ parity k
parity-negPos zero    = refl
parity-negPos (suc k) = refl

------------------------------------------------------------------------
-- 6. parity-ℤ respects the ℕ-scaling (+ q) *ℤ b.
------------------------------------------------------------------------

parity-ℤ-scale : (q : ℕ) (b : ℤ) → parity-ℤ ((+ q) *ℤ b) ≡ scale q (parity-ℤ b)
parity-ℤ-scale q (+ n)    = parity-scale q n
parity-ℤ-scale q (-suc n) =
  trans (parity-negPos (q * suc n)) (parity-scale q (suc n))

------------------------------------------------------------------------
-- 7. THE BRIDGE: ℤ-div ↠ F₂-div (the mod-2 ring homomorphism).
------------------------------------------------------------------------

int-parity-bridge : Bridge ℤ-div F₂-div
int-parity-bridge = record
  { translate = parity-ℤ
  ; respects  = λ q b r →
      trans (parity-ℤ-+ ((+ q) *ℤ b) r)
            (cong (_+₂ parity-ℤ r) (parity-ℤ-scale q b))
  ; z-pres    = refl
  }
