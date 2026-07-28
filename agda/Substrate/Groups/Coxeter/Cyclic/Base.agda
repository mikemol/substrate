------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base
--
-- Foundation layer: Gen, power, Canonical-at (Fin-indexed), canonical-cover,
-- bijection to/from Fin, σ permutation, σ-HasOrderPerm, Word-level insert.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (Dec; yes; no)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Foundation.Fin.Iterate
  using (HasOrderPerm; OrderOf; seal-order)
open import Substrate.Algebra.Nat.CyclicSuc
  using (cyclic-suc; cyclic-suc-HasOrderPerm)

module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where

------------------------------------------------------------------------
-- 1. Gen: single generator.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

-- Decidable equality on Gen. Identical across every Z_n-Coxeter
-- instance because Gen is the single-generator type; previously
-- re-declared verbatim in Z2/Z3/Z4/Z5/Z7-Coxeter.
gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

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
-- 3. Canonical-at w k — length-indexed.
------------------------------------------------------------------------

data Canonical-at : Word Gen → Fin (suc n) → Set where      -- ⟦shape:421aa4ad c-here⟧
  c-here : (k : Fin (suc n)) → Canonical-at (power (toℕ k)) k

------------------------------------------------------------------------
-- 4. canonical-cover — Fin-indexed dispatch.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w k} → Canonical-at w k → Set ℓ) →
  ((k : Fin (suc n)) → P (c-here k)) →
  ∀ {w k} (c : Canonical-at w k) → P c
canonical-cover P f (c-here k) = f k

------------------------------------------------------------------------
-- 5. Bijection canonical-to-Fin / Fin-to-canonical.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w k} → Canonical-at w k → Fin (suc n)
canonical-to-Fin (c-here k) = k

Fin-to-canonical : (k : Fin (suc n)) → Canonical-at (power (toℕ k)) k
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

-- ⟡cap-384: the ABSTRACT-σ seal (n is a module param → cyclic-suc {n} abstract →
-- cheap, no iterate normalization). Rides the `public` re-export chain to every
-- Zn-Coxeter-Fin; the capability field consumes THIS (a non-reducing token) so a
-- concrete cap-Zₙ record never re-normalizes `iterate n (cyclic-suc)`.
σ-OrderOf : OrderOf σ (suc n)
σ-OrderOf = seal-order σ-HasOrderPerm

------------------------------------------------------------------------
-- 7. insert — cyclic Word-level shift.
--
-- For length w < n: prepend `a`. For length ≥ n: wrap to ε.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert g w with length w <? n
... | yes _ = g ∷ w
... | no  _ = []
