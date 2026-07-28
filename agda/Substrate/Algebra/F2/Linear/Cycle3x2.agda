------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Cycle3x2
--
-- Ⓕ.tower-F₂ (base case) — the MULTIPLICITY composes. Two disjoint 3-cycles
-- on F₂⁶ (the simplest multiplicity-2 instance, built the efficient way:
-- a permutation operator whose Φ_p-kernel READS off by reduction, like (a)).
--
--   σ₆ = (0 1 2)(3 4 5) — two p-cycle blocks (p=3), so Φ₃(σ₆) is BLOCKWISE
--   augmentation (each coord = its block's total), ker = blockwise even-weight,
--   and `dim2x : KernelDim Φσ₆ 4` — dim ker Φ₃(σ₆) = 4 = 2·(3−1) = 2·degΦ₃.
--
-- This WITNESSES the per-factor degΦ_p (a) composing into the multiplicity: m
-- p-cycle blocks ⟹ dim ker Φ_p = m·degΦ_p (here m=2). The general m (= mult2/2,
-- the cotype's crossing count) is the inductive generalization (RemQuot block
-- structure), the same shape (a) took: Cycle3 base → Augmentation general.
-- Reuses Cycle3's `+-swap`/`b-eq`; every KernelDim obligation reduces.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Cycle3x2 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (_∷_; []; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (ΦL)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.Cycle3 using (+-swap; b-eq)

------------------------------------------------------------------------
-- σ₆ = two disjoint 3-cycles (rotate each block of 3); refl-linear.
------------------------------------------------------------------------

σ₆ : Linear 6 6
σ₆ = record
  { apply        = λ { (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) → b ∷ c ∷ a ∷ e ∷ f ∷ d ∷ [] }
  ; preserves-+  = λ { (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (g ∷ h ∷ i ∷ j ∷ k ∷ l ∷ []) → refl }
  ; preserves-*ₛ = λ { s (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) → refl }
  }

Φσ₆ : Linear 6 6
Φσ₆ = ΦL σ₆ 3

------------------------------------------------------------------------
-- F₂⁴ ≅ ker Φσ₆ : per block, prepend the parity; drop the middle. (Two copies
-- of Cycle3's even-weight iso, side by side.)
------------------------------------------------------------------------

into : Linear 4 6
into = record
  { apply        = λ { (a ∷ b ∷ c ∷ d ∷ []) → a ∷ (a + b) ∷ b ∷ c ∷ (c + d) ∷ d ∷ [] }
  ; preserves-+  = λ { (a ∷ b ∷ c ∷ d ∷ []) (g ∷ h ∷ i ∷ j ∷ []) →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → +-swap a b g h
                           ; (suc (suc zero)) → refl
                           ; (suc (suc (suc zero))) → refl
                           ; (suc (suc (suc (suc zero)))) → +-swap c d i j
                           ; (suc (suc (suc (suc (suc zero))))) → refl }) }
  ; preserves-*ₛ = λ { s (a ∷ b ∷ c ∷ d ∷ []) →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → sym (·-distribˡ-+ s a b)
                           ; (suc (suc zero)) → refl
                           ; (suc (suc (suc zero))) → refl
                           ; (suc (suc (suc (suc zero)))) → sym (·-distribˡ-+ s c d)
                           ; (suc (suc (suc (suc (suc zero))))) → refl }) }
  }

retr : Linear 6 4
retr = record
  { apply        = λ { (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) → a ∷ c ∷ d ∷ f ∷ [] }
  ; preserves-+  = λ { (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (g ∷ h ∷ i ∷ j ∷ k ∷ l ∷ []) → refl }
  ; preserves-*ₛ = λ { s (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) → refl }
  }

------------------------------------------------------------------------
-- dim ker Φ₃(σ₆) = 4 = 2·degΦ₃ — the multiplicity (2 blocks) composes.
------------------------------------------------------------------------

dim2x : KernelDim Φσ₆ 4
dim2x = record
  { into     = into
  ; retract  = retr
  ; into-ker = λ { (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) → refl ; (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) → refl
                 ; (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) → refl ; (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) → refl
                 ; (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) → refl ; (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) → refl
                 ; (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) → refl ; (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) → refl
                 ; (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) → refl ; (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) → refl
                 ; (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) → refl ; (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) → refl
                 ; (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) → refl ; (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) → refl
                 ; (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) → refl ; (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) → refl }
  ; indep    = λ { (a ∷ b ∷ c ∷ d ∷ []) → refl }
  ; spans    = λ { (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) hyp →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → sym (b-eq a b c (cong (λ w → lookup w zero) hyp))
                           ; (suc (suc zero)) → refl
                           ; (suc (suc (suc zero))) → refl
                           ; (suc (suc (suc (suc zero)))) →
                               sym (b-eq d e f (cong (λ w → lookup w (suc (suc (suc zero)))) hyp))
                           ; (suc (suc (suc (suc (suc zero))))) → refl }) }
  }
