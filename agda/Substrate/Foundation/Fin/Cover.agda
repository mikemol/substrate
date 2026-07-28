------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Cover
--
-- Cover combinators for Fin n: dispatch a per-position payload across
-- a finite index set.
--
-- THREE layers (per [[feedback-expose-generator-not-orbit-applies]]):
--
-- 1. `dep-Pow P` — dependent tuple over `Fin n → Set ℓ`. A right-
--    nested product whose i-th component has type P i. Replaces
--    n-fold hand-spelled types like `P 0 × P 1 × P 2 × P 3` and
--    handles non-uniform P (each position has its own type),
--    extending the user's `Substrate.Groups.Coxeter.CanonicalCover.Pow`
--    to the dependent case.
--
-- 2. `fin-cover` — single n parametric, ONE definition that covers
--    every Fin n via dep-Pow. The n-ctor enumeration is structurally
--    eliminated by induction on n.
--
-- 3. `fin×fin-cover` — N × M Cayley table as the atlas-of-charts
--    tensor of two fin-cover applications. One line.
--
-- The substrate-honest "Cayley-table payload" is the dep-Pow tuple
-- supplied to the cover. Each refl literal in the tuple unifies its
-- own implicit {x} at use site (so heterogeneous outputs work too).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Cover where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Function using (_∘_)

------------------------------------------------------------------------
-- dep-Pow P — dependent product over Fin n as a right-nested tuple.
-- For n = 0 the result is ⊥-elim'd land (no Fin 0 inhabitants), so
-- the dep-Pow there is just ⊥ → ⊥, expressed compactly as ⊥ (no
-- proof obligation). Callers use n ≥ 1.
------------------------------------------------------------------------

dep-Pow : ∀ {ℓ n} → (Fin n → Set ℓ) → Set ℓ
dep-Pow {ℓ} {n = zero}        _ = Lift⊥
  where
    -- A level-polymorphic ⊥ placeholder (callers use n ≥ 1).
    data Lift⊥ : Set ℓ where
dep-Pow {n = suc zero}        P = P zero
dep-Pow {n = suc (suc n)}     P = P zero × dep-Pow {n = suc n} (P ∘ suc)

------------------------------------------------------------------------
-- fin-cover — single n-parametric cover.
------------------------------------------------------------------------

fin-cover :
  ∀ {ℓ n} (P : Fin n → Set ℓ) →
  dep-Pow P → ∀ i → P i
fin-cover {n = suc zero}    P p          zero    = p
fin-cover {n = suc (suc n)} P (p₀ , _)   zero    = p₀
fin-cover {n = suc (suc n)} P (_  , ps) (suc i) =
  fin-cover {n = suc n} (P ∘ suc) ps i

------------------------------------------------------------------------
-- tabulate — the inverse of fin-cover. Mirror of `copies` / `n-refls`
-- from Substrate.Groups.Coxeter.CanonicalCover, but on the dependent
-- (heterogeneous-position) side: given a per-position function, pack
-- it into a dep-Pow payload. Restricted to n ≥ 1.
--
-- The uniform-payload special case `tabulate _ (λ _ → v)` mirrors
-- `copies n v`; the all-refl case `tabulate _ (λ _ → refl)` mirrors
-- `n-refls n`. NOTE: the all-refl version requires the predicate to
-- be UNIFORM at each position (same `x ≡ x` after reduction). For
-- heterogeneous-position-equality predicates (e.g. bivector
-- symmetric), Agda's higher-order unification cannot promote the
-- single `refl` literal to depend on the lambda-bound position;
-- those sites need per-position refls (hand-written or via a
-- reflection macro).
------------------------------------------------------------------------

tabulate :
  ∀ {ℓ n} (P : Fin (suc n) → Set ℓ) →
  (∀ i → P i) → dep-Pow {n = suc n} P
tabulate {n = zero}    P f = f zero
tabulate {n = suc n'}  P f = f zero , tabulate (P ∘ suc) (f ∘ suc)

------------------------------------------------------------------------
-- fin×fin-cover — N × M Cayley table via the product of two fin-cover.
------------------------------------------------------------------------

fin×fin-cover :
  ∀ {ℓ n m} (P : Fin n → Fin m → Set ℓ) →
  dep-Pow (λ i → dep-Pow (P i)) →
  ∀ i j → P i j
fin×fin-cover P rows i j =
  fin-cover (P i)
    (fin-cover (λ i' → dep-Pow (P i')) rows i)
    j

------------------------------------------------------------------------
-- F₂ⁿ binary fan-out covers.
--
-- For carriers with a binary-product decomposition (V₄ ≅ F₂², so a
-- 4×4 Cayley = (F₂×F₂)×(F₂×F₂) = F₂⁴), the cover composes 2-element
-- fin2-cover applications via the binary product structure. Same
-- leaves as a 4×4 dep-Pow but with the F₂-grading exposed.
--
-- `fin-cover-2² P` covers Fin 2 × Fin 2 (4 cells) via two fin2-cover
-- compositions. `fin-cover-2⁴ P` covers (Fin 2 × Fin 2) × (Fin 2 ×
-- Fin 2) (16 cells) via four fin2-cover compositions — matching the
-- 2⁴-refls binary nesting from CanonicalCover.
------------------------------------------------------------------------

fin-cover-2² :
  ∀ {ℓ} (P : Fin 2 → Fin 2 → Set ℓ) →
  dep-Pow (λ i → dep-Pow (P i)) →
  ∀ i j → P i j
fin-cover-2² = fin×fin-cover

fin-cover-2⁴ :
  ∀ {ℓ} (P : Fin 2 → Fin 2 → Fin 2 → Fin 2 → Set ℓ) →
  dep-Pow (λ i₁ → dep-Pow (λ i₂ → dep-Pow (λ j₁ → dep-Pow (P i₁ i₂ j₁)))) →
  ∀ i₁ i₂ j₁ j₂ → P i₁ i₂ j₁ j₂
fin-cover-2⁴ P table i₁ i₂ j₁ j₂ =
  fin-cover (P i₁ i₂ j₁)
    (fin-cover (λ j₁' → dep-Pow (P i₁ i₂ j₁'))
      (fin-cover (λ i₂' → dep-Pow (λ j₁' → dep-Pow (P i₁ i₂' j₁')))
        (fin-cover
          (λ i₁' → dep-Pow (λ i₂' → dep-Pow (λ j₁' → dep-Pow (P i₁' i₂' j₁'))))
          table i₁)
        i₂)
      j₁)
    j₂
