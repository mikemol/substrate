------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Augmentation
--
-- Ⓕ.spectral (a) — GENERAL p, by the same structure Cycle3 proved at p=3.
--
-- The augmentation operator  A v = (Σ vᵢ) ·ₛ ones  IS Φ_p evaluated at the
-- p-cycle shift (Φ_p(σ_p) = id+σ+…+σ^{p-1}; summing all p rotations puts the
-- total in every coordinate). Cycle3 witnesses A = ΦL σ 3 at p=3 by reduction;
-- the general shift-sum identity (Φ_p(σ_p) = A) is the remaining connector.
-- This module proves the SPECTRAL HALF for all p:
--
--   ker A = the even-weight subspace {v : Σ vᵢ = 𝟘},  and
--   dim (ker A_{suc n}) = n = (suc n) − 1 = degΦ_{suc n}  (at prime p, p−1).
--
-- The dimension is read by a UNIFORM iso (no per-p enumeration, no Gaussian
-- elimination): F₂ⁿ ≅ ker A_{suc n} via  into rest = (Σ rest) ∷ rest  (prepend
-- the parity bit) and  retract (x ∷ rest) = rest  (drop it). Every KernelDim
-- obligation reduces; `spans` needs one F₂ fact (x = Σrest when Σv = 𝟘).
-- This is the (p−1) = degΦ_p factor of PhiMultiplicity.nullity2 = mult2·(p−1).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Augmentation where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (_∷_; []; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.AsModule using (*ₛ-distribʳ-+; *ₛ-assoc)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)

------------------------------------------------------------------------
-- total (Σ of the coordinates) and ones (all-𝟙), by recursion on length.
------------------------------------------------------------------------

total : ∀ {p} → Vector p → F₂
total []       = 𝟘
total (x ∷ xs) = x + total xs

ones : ∀ {p} → Vector p
ones {zero}  = []
ones {suc _} = 𝟙 ∷ ones

-- F₂ middle-four interchange (for total's additivity).
+swap4 : (a b c d : F₂) → ((a + b) + (c + d)) ≡ ((a + c) + (b + d))
+swap4 a b c d =
  trans (+-assoc a b (c + d))
  (trans (cong (a +_) (sym (+-assoc b c d)))
  (trans (cong (λ z → a + (z + d)) (+-comm b c))
  (trans (cong (a +_) (+-assoc c b d))
         (sym (+-assoc a c (b + d))))))

total-+ⱽ : ∀ {p} (u v : Vector p) → total (u +ⱽ v) ≡ (total u + total v)
total-+ⱽ []       []       = refl
total-+ⱽ (x ∷ xs) (y ∷ ys) =
  trans (cong ((x + y) +_) (total-+ⱽ xs ys)) (+swap4 x y (total xs) (total ys))

total-*ₛ : ∀ {p} (c : F₂) (v : Vector p) → total (c *ₛ v) ≡ (c · total v)
total-*ₛ c []       = sym (·-absorbʳ c)
total-*ₛ c (x ∷ xs) =
  trans (cong ((c · x) +_) (total-*ₛ c xs)) (sym (·-distribˡ-+ c x (total xs)))

------------------------------------------------------------------------
-- The augmentation operator A v = (total v) ·ₛ ones, F₂-linear.
------------------------------------------------------------------------

A : ∀ {p} → Linear p p
A = record
  { apply        = λ v → total v *ₛ ones
  ; preserves-+  = λ u v →
      trans (cong (_*ₛ ones) (total-+ⱽ u v)) (*ₛ-distribʳ-+ (total u) (total v) ones)
  ; preserves-*ₛ = λ c v →
      trans (cong (_*ₛ ones) (total-*ₛ c v)) (*ₛ-assoc c (total v) ones)
  }

------------------------------------------------------------------------
-- The dimension iso F₂ⁿ ≅ ker A_{suc n} : prepend the parity, drop the head.
------------------------------------------------------------------------

into : ∀ {n} → Linear n (suc n)
into = record
  { apply        = λ rest → total rest ∷ rest
  ; preserves-+  = λ u v → cong₂ _∷_ (total-+ⱽ u v) refl
  ; preserves-*ₛ = λ c v → cong₂ _∷_ (total-*ₛ c v) refl
  }

retr : ∀ {n} → Linear (suc n) n
retr = record
  { apply        = λ { (x ∷ rest) → rest }
  ; preserves-+  = λ { (x ∷ xs) (y ∷ ys) → refl }
  ; preserves-*ₛ = λ { c (x ∷ xs) → refl }
  }

-- Over F₂, a + b = 𝟘 forces b = a (the kernel condition reading x = Σrest).
sum0→eq : (a b : F₂) → (a + b) ≡ 𝟘 → b ≡ a
sum0→eq 𝟘 𝟘 _ = refl
sum0→eq 𝟙 𝟙 _ = refl
sum0→eq 𝟘 𝟙 ()
sum0→eq 𝟙 𝟘 ()

-- Σv = 𝟘 read off coordinate 0 of A v = 𝟎ⱽ (ones has a 𝟙 there).
tot0 : ∀ {n} (v : Vector (suc n)) → apply (A {suc n}) v ≡ 𝟎ⱽ → total v ≡ 𝟘
tot0 {n} v hyp =
  trans (sym (·-identityʳ (total v)))
  (trans (sym (lookup-*ₛ (total v) (ones {suc n}) (zero {n})))
  (trans (cong (λ w → lookup w (zero {n})) hyp) (lookup-𝟎 {suc n} (zero {n}))))

-- dim (ker A_{suc n}) = n = (suc n) − 1.
aug-dim : (n : ℕ) → KernelDim (A {suc n}) n
aug-dim n = record
  { into     = into
  ; retract  = retr
  ; into-ker = λ rest → trans (cong (_*ₛ ones) (+-self-inverse (total rest))) (*ₛ-absorbˡ ones)
  ; indep    = λ rest → refl
  ; spans    = λ { (x ∷ rest) hyp → cong (_∷ rest) (sum0→eq x (total rest) (tot0 (x ∷ rest) hyp)) }
  }
