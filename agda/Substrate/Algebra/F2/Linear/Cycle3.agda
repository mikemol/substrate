------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Cycle3
--
-- Ⓕ.spectral — INTRODUCING the cycle operator (concretely, p = 3). Not a
-- wall: the operator was "absent" only because linear algebra is being
-- introduced. Here it is, built in FaceCount's architecture — small finite
-- space, term algebra reads the count at CHECK TIME (the obligations below
-- are `refl` or one finite case-split, never a computed dimension). p = 3 is
-- the BASE CASE; general p lifts by induction (the same shape as FaceCount's
-- cone-step lifting one rung to all rungs).
--
-- σ = the 3-cycle shift (a∷b∷c ↦ b∷c∷a), a coordinate permutation, so
-- F₂-linear by `refl`. Its cyclotomic operator Φ₃(σ) = id + σ + σ² is the
-- AUGMENTATION: every coordinate of Φ₃(σ)v is a+b+c. So
--   ker Φ₃(σ) = the even-weight subspace {v : a+b+c = 𝟘},
-- and `KernelDim Φσ 2` exhibits the iso F₂² ≅ ker — dimension 2 = degΦ₃ =
-- p−1. This grounds the per-p-cycle Φ_p-isotypic DIMENSION = degΦ_p — the
-- (p−1) factor in PhiMultiplicity.nullity2 = mult2·(p−1) (mult2 = the
-- FaceCount-fibered crossing COUNT, already proved; this is the per-factor
-- dimension, the spectral half).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Cycle3 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (_∷_; []; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans; sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Cyclotomic using (ΦL)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)

------------------------------------------------------------------------
-- The 3-cycle shift σ : rotate-left. Linearity is refl (componentwise).
------------------------------------------------------------------------

σ : Linear 3 3
σ = record
  { apply        = λ { (a ∷ b ∷ c ∷ []) → b ∷ c ∷ a ∷ [] }
  ; preserves-+  = λ { (a ∷ b ∷ c ∷ []) (d ∷ e ∷ f ∷ []) → refl }
  ; preserves-*ₛ = λ { s (a ∷ b ∷ c ∷ []) → refl }
  }

-- Φ₃(σ) = id + σ + σ²  (the cyclotomic operator at the orbit shift).
Φσ : Linear 3 3
Φσ = ΦL σ 3

------------------------------------------------------------------------
-- Membership in ker Φσ is `refl` — the augmentation collapses each
-- even-weight vector to 𝟎ⱽ by computation (the architecture test: no
-- proof, the term algebra reads it). These two are the supplied basis.
------------------------------------------------------------------------

ev : Fin 2 → Vector 3
ev zero       = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
ev (suc zero) = 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []

ev∈ker : (i : Fin 2) → inKer Φσ (ev i)
ev∈ker zero       = refl
ev∈ker (suc zero) = refl

------------------------------------------------------------------------
-- The dimension iso F₂² ≅ ker Φσ. `into` is the explicit span of `ev`
-- (columns ev₀, ev₁), `retract` projects coords 0,2 — both refl-linear up
-- to one F₂ rearrangement. Then dim (ker Φσ) = 2 = degΦ₃.
------------------------------------------------------------------------

-- F₂ middle-four interchange (the only non-refl bit of `into`'s linearity).
+-swap : (a b c d : F₂) → ((a + c) + (b + d)) ≡ ((a + b) + (c + d))
+-swap a b c d =
  trans (+-assoc a c (b + d))
  (trans (cong (a +_) (sym (+-assoc c b d)))
  (trans (cong (λ z → a + (z + d)) (+-comm c b))
  (trans (cong (a +_) (+-assoc b c d))
         (sym (+-assoc a b (c + d))))))

-- into (x₀∷x₁) = x₀·ev₀ + x₁·ev₁ = x₀ ∷ (x₀+x₁) ∷ x₁.
into : Linear 2 3
into = record
  { apply        = λ { (x₀ ∷ x₁ ∷ []) → x₀ ∷ (x₀ + x₁) ∷ x₁ ∷ [] }
  ; preserves-+  = λ { (x₀ ∷ x₁ ∷ []) (y₀ ∷ y₁ ∷ []) →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → +-swap x₀ x₁ y₀ y₁
                           ; (suc (suc zero)) → refl }) }
  ; preserves-*ₛ = λ { s (x₀ ∷ x₁ ∷ []) →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → sym (·-distribˡ-+ s x₀ x₁)
                           ; (suc (suc zero)) → refl }) }
  }

-- retract (a∷b∷c) = a ∷ c (drop the middle); refl-linear.
retr : Linear 3 2
retr = record
  { apply        = λ { (a ∷ b ∷ c ∷ []) → a ∷ c ∷ [] }
  ; preserves-+  = λ { (a ∷ b ∷ c ∷ []) (d ∷ e ∷ f ∷ []) → refl }
  ; preserves-*ₛ = λ { s (a ∷ b ∷ c ∷ []) → refl }
  }

-- The kernel condition (a+b)+c = 𝟘 forces b = a+c — the one F₂ fact `spans`
-- needs, read off by exhausting F₂³ (4 valid, 4 absurd).
b-eq : (a b c : F₂) → ((a + b) + c) ≡ 𝟘 → b ≡ (a + c)
b-eq 𝟘 𝟘 𝟘 _ = refl
b-eq 𝟘 𝟙 𝟙 _ = refl
b-eq 𝟙 𝟘 𝟙 _ = refl
b-eq 𝟙 𝟙 𝟘 _ = refl
b-eq 𝟘 𝟘 𝟙 ()
b-eq 𝟘 𝟙 𝟘 ()
b-eq 𝟙 𝟘 𝟘 ()
b-eq 𝟙 𝟙 𝟙 ()

dim2 : KernelDim Φσ 2
dim2 = record
  { into     = into
  ; retract  = retr
  ; into-ker = λ { (𝟘 ∷ 𝟘 ∷ []) → refl ; (𝟘 ∷ 𝟙 ∷ []) → refl
                 ; (𝟙 ∷ 𝟘 ∷ []) → refl ; (𝟙 ∷ 𝟙 ∷ []) → refl }
  ; indep    = λ { (x₀ ∷ x₁ ∷ []) → refl }
  ; spans    = λ { (a ∷ b ∷ c ∷ []) hyp →
      ≡-from-lookup _ _ (λ { zero → refl
                           ; (suc zero) → sym (b-eq a b c (cong (λ w → lookup w zero) hyp))
                           ; (suc (suc zero)) → refl }) }
  }
