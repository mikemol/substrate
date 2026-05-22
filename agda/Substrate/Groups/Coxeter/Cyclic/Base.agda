------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base
--
-- Foundation layer: Gen, power, Canonical (Fin-indexed), canonical-cover,
-- bijection to/from Fin, σ permutation, σ-HasOrderPerm, Word-level insert.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (Dec; yes; no)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)

module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where

------------------------------------------------------------------------
-- 1. Gen: single generator.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

------------------------------------------------------------------------
-- 2. power k = aᵏ as a Word.
------------------------------------------------------------------------

power : ℕ → Word Gen
power zero    = []
power (suc k) = a ∷ power k

length-power : (k : ℕ) → length (power k) ≡ k
length-power zero    = refl
length-power (suc k) = cong suc (length-power k)

------------------------------------------------------------------------
-- 3. Canonical w k — length-indexed.
------------------------------------------------------------------------

data Canonical : Word Gen → Fin (suc n) → Set where
  c-here : (k : Fin (suc n)) → Canonical (power (toℕ k)) k

------------------------------------------------------------------------
-- 4. canonical-cover — Fin-indexed dispatch.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w k} → Canonical w k → Set ℓ) →
  ((k : Fin (suc n)) → P (c-here k)) →
  ∀ {w k} (c : Canonical w k) → P c
canonical-cover P f (c-here k) = f k

------------------------------------------------------------------------
-- 5. Bijection canonical-to-Fin / Fin-to-canonical.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w k} → Canonical w k → Fin (suc n)
canonical-to-Fin (c-here k) = k

Fin-to-canonical : (k : Fin (suc n)) → Canonical (power (toℕ k)) k
Fin-to-canonical k = c-here k

Fin-roundtrip : (k : Fin (suc n)) →
  canonical-to-Fin (Fin-to-canonical k) ≡ k
Fin-roundtrip _ = refl

------------------------------------------------------------------------
-- 6. σ = cyclic-suc {n}; σ-HasOrderPerm from Slice 4.
------------------------------------------------------------------------

σ : Fin (suc n) → Fin (suc n)
σ = cyclic-suc {n}

σ-HasOrderPerm : HasOrderPerm σ (suc n)
σ-HasOrderPerm = cyclic-suc-HasOrderPerm {n}

------------------------------------------------------------------------
-- 7. insert — cyclic Word-level shift.
--
-- For length w < n: prepend `a`. For length ≥ n: wrap to ε.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert g w with length w <? n
... | yes _ = g ∷ w
... | no  _ = []
