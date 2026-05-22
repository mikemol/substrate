------------------------------------------------------------------------
-- Substrate.Algebra.F2.Code
--
-- M-4 of the Cocycles structural-migration plan. F₂-linear codes as
-- the image (generator-matrix form) or kernel (parity-check form) of
-- F₂-linear maps.
--
-- Two complementary records:
--   * ImageCode k n  : codewords = image of G : Vec F₂ k → Vec F₂ n
--                      (generator matrix; codewords easily enumerated).
--   * KernelCode n p : codewords = ker (H : Vec F₂ n → Vec F₂ p)
--                      (parity-check matrix; membership easily tested).
--
-- Both describe the same kind of object — a linear subspace of
-- Vec F₂ n — just with different constructive entry-points. The
-- bridge between them (for k + p = n in non-degenerate cases) is a
-- separate slice (M-4.5 or part of the dual-code module).
--
-- This file's scope is the two records, membership predicates, and
-- basic structural facts (closure under + and *ₛ).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Code where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

------------------------------------------------------------------------
-- ImageCode: codewords = image of the generator linear map.
--
-- A vector v : Vector n is a codeword iff there exists u : Vector k
-- with apply generator u ≡ v.
------------------------------------------------------------------------

record ImageCode (k n : ℕ) : Set where
  field
    generator : Linear k n

open ImageCode public

-- Membership.
In-Image : ∀ {k n} → ImageCode k n → Vector n → Set
In-Image {k} C v = Σ (Vector k) (λ u → apply (generator C) u ≡ v)

-- The zero vector is always a codeword (apply at 𝟎ⱽ).
𝟎-in-image : ∀ {k n} (C : ImageCode k n) → In-Image C 𝟎ⱽ
𝟎-in-image C = 𝟎ⱽ , preserves-𝟎 (generator C)

-- Codewords are closed under +ⱽ.
+ⱽ-in-image :
  ∀ {k n} (C : ImageCode k n) (v w : Vector n) →
  In-Image C v → In-Image C w → In-Image C (v +ⱽ w)
+ⱽ-in-image C v w (u₁ , eq₁) (u₂ , eq₂) =
  u₁ +ⱽ u₂ ,
  trans (preserves-+ (generator C) u₁ u₂) (cong₂ _+ⱽ_ eq₁ eq₂)

-- Codewords are closed under scalar multiplication.
*ₛ-in-image :
  ∀ {k n} (C : ImageCode k n) (c : F₂) (v : Vector n) →
  In-Image C v → In-Image C (c *ₛ v)
*ₛ-in-image C c v (u , eq) =
  c *ₛ u ,
  trans (preserves-*ₛ (generator C) c u)
        (cong (c *ₛ_) eq)

------------------------------------------------------------------------
-- KernelCode: codewords = kernel of the parity-check linear map.
--
-- A vector v : Vector n is a codeword iff apply parity-check v ≡ 𝟎ⱽ.
------------------------------------------------------------------------

record KernelCode (n p : ℕ) : Set where
  field
    parity-check : Linear n p

open KernelCode public

-- Membership.
In-Kernel : ∀ {n p} → KernelCode n p → Vector n → Set
In-Kernel C v = apply (parity-check C) v ≡ 𝟎ⱽ

-- The zero vector is in the kernel.
𝟎-in-kernel : ∀ {n p} (C : KernelCode n p) → In-Kernel C 𝟎ⱽ
𝟎-in-kernel C = preserves-𝟎 (parity-check C)

-- Codewords closed under +ⱽ.
+ⱽ-in-kernel :
  ∀ {n p} (C : KernelCode n p) (v w : Vector n) →
  In-Kernel C v → In-Kernel C w → In-Kernel C (v +ⱽ w)
+ⱽ-in-kernel C v w v-in w-in =
  trans (preserves-+ (parity-check C) v w)
  (trans (cong₂ _+ⱽ_ v-in w-in)
         (+ⱽ-identityˡ 𝟎ⱽ))

-- Codewords closed under scalar multiplication.
*ₛ-in-kernel :
  ∀ {n p} (C : KernelCode n p) (c : F₂) (v : Vector n) →
  In-Kernel C v → In-Kernel C (c *ₛ v)
*ₛ-in-kernel C c v v-in =
  trans (preserves-*ₛ (parity-check C) c v)
  (trans (cong (c *ₛ_) v-in)
         (*ₛ-𝟎-is-𝟎 c))
  where
    *ₛ-𝟎-is-𝟎 : ∀ {n} (c : F₂) → (c *ₛ (𝟎ⱽ {n})) ≡ 𝟎ⱽ
    *ₛ-𝟎-is-𝟎 𝟘 = *ₛ-absorbˡ 𝟎ⱽ
    *ₛ-𝟎-is-𝟎 𝟙 = *ₛ-identityˡ 𝟎ⱽ

------------------------------------------------------------------------
-- Categorical retrofit — In-Kernel as an Equalizer-At-Constant instance.
--
-- Per `feedback_categorical_name_first` and the
-- Substrate.Category.Primitives roadmap: `In-Kernel C v` is precisely
-- the equalizer of (apply (parity-check C)) and the constant-𝟎ⱽ
-- function at v. The two definitions are definitionally compatible
-- (both reduce to `apply (parity-check C) v ≡ 𝟎ⱽ`); the bridge below
-- wraps each direction explicitly so downstream code can cite the
-- categorical handle.
------------------------------------------------------------------------

open import Substrate.Category.Equalizer
  using (IsEqualised; equal; Kernel-At)

In-Kernel→Kernel-At :
  ∀ {n p} (C : KernelCode n p) (v : Vector n) →
  In-Kernel C v → Kernel-At (apply (parity-check C)) 𝟎ⱽ v
In-Kernel→Kernel-At C v in-ker = record { equal = in-ker }

Kernel-At→In-Kernel :
  ∀ {n p} (C : KernelCode n p) (v : Vector n) →
  Kernel-At (apply (parity-check C)) 𝟎ⱽ v → In-Kernel C v
Kernel-At→In-Kernel C v ker-at = equal ker-at
