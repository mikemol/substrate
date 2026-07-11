------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigInitial
--
-- ⟡rig-UP-alg-initiality — the Set₀ UNIVERSAL PROPERTY of the graded Lehmer rig, resolving
-- the G8 handoff residue ("is there a Set₀ rig-ALGEBRA initiality, distinct from the Set₁
-- categorical UP?"). ANSWER: YES, and it is pure ASSEMBLY of already-committed results — no
-- new grind. The Set₁ categorical UP (initiality among rig CATEGORIES) is NOT needed here.
--
-- A RigAlgebra is a graded carrier (C : ℕ → Set, each grade Set₀ — carrier a PARAMETER, never
-- a field, so this is Set NOT Set₁) with the ◂-tower structure (LehmerAlgebra: base, step) PLUS
-- the additive (⊕ᶜ) and multiplicative (⊗ᶜ) operations, together with their coherence laws (the
-- exact hypotheses fold-⊕ / fold-⊗ consume).
--
-- The UNIVERSAL PROPERTY: `fold` (the ◂-catamorphism) is THE UNIQUE map out of LehmerPath that
--   * respects (base, step)                       — and is UNIQUE among such (fold-unique), AND
--   * respects ⊕  (foldR-⊕ = fold-⊕),  respects ⊗ (foldR-⊗ = fold-⊗).
-- So the rig structure is CARRIED FOR FREE by the initial ◂-algebra map: uniqueness is pinned by
-- (base, step) alone, and the initial map automatically preserves ⊕ and ⊗. That is the Set₀
-- universal property — LehmerPath is the initial rig-carrying LehmerAlgebra.
--
-- (HONEST BOUNDARY: this is initiality where a hom respects the GENERATING op ◂. The strictly
-- stronger reading — initiality among rig-algebras whose homs respect ONLY ⊕/⊗/one, with ◂
-- DERIVED from them — is the free-symmetric-rig theorem and is the genuinely categorical/heavier
-- statement. Not claimed here; this Set₀ property is what the arc's committed lemmas already give.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigInitial where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural using (_⊗ˢ_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique; fold-⊕)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ; fold-⊗)

------------------------------------------------------------------------
-- 1. A RigAlgebra: the ◂-tower + ⊕/⊗ + the coherence laws fold-⊕/fold-⊗ consume. Carrier a
--    PARAMETER (Set, not Set₁). Each law field is exactly a fold-⊕ / fold-⊗ hypothesis.
------------------------------------------------------------------------

record RigAlgebra (C : ℕ → Set) : Set where
  field
    alg       : LehmerAlgebra C
    _⊕ᶜ_      : ∀ {i j} → C i → C j → C (i + j)
    ⊕ᶜ-base   : ∀ {n} (y : C n) → (base alg ⊕ᶜ y) ≡ y
    ⊕ᶜ-step   : ∀ {m n} (x : C m) (p : Fin (suc m)) (y : C n) →
                (step alg x p ⊕ᶜ y) ≡ step alg (x ⊕ᶜ y) (inject+ n p)
    _⊗ᶜ_      : ∀ {i j} → C i → C j → C (i * j)
    ⊗ᶜ-absorb : ∀ {n} (y : C n) → (base alg ⊗ᶜ y) ≡ base alg
    ⊗ᶜ-step   : ∀ {m n} (x : C m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
                replayᶜ alg p n l₂ (x ⊗ᶜ fold alg l₂) ≡ (step alg x p ⊗ᶜ fold alg l₂)

open RigAlgebra public

------------------------------------------------------------------------
-- 2. THE INITIAL MAP: fold on the RigAlgebra's underlying LehmerAlgebra.
------------------------------------------------------------------------

foldR : ∀ {C} (R : RigAlgebra C) → ∀ {n} → LehmerPath n → C n
foldR R = fold (alg R)

------------------------------------------------------------------------
-- 3. IT CARRIES THE RIG STRUCTURE: respects ⊕ and ⊗ (fold-⊕ / fold-⊗ on the fielded laws).
------------------------------------------------------------------------

foldR-⊕ : ∀ {C} (R : RigAlgebra C) {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
          foldR R (l₁ ⊕ l₂) ≡ (_⊕ᶜ_ R (foldR R l₁) (foldR R l₂))
foldR-⊕ R = fold-⊕ (alg R) (_⊕ᶜ_ R) (⊕ᶜ-base R) (⊕ᶜ-step R)

foldR-⊗ : ∀ {C} (R : RigAlgebra C) {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
          foldR R (l₁ ⊗ˢ l₂) ≡ (_⊗ᶜ_ R (foldR R l₁) (foldR R l₂))
foldR-⊗ R = fold-⊗ (alg R) (_⊗ᶜ_ R) (⊗ᶜ-absorb R) (⊗ᶜ-step R)

------------------------------------------------------------------------
-- 4. UNIVERSALITY: fold is THE UNIQUE map respecting (base, step) — pinned by the generating
--    ◂-structure ALONE. Any g that agrees on start and on ◂ IS foldR. So the initial
--    ◂-algebra map is unique, and (by §3) it carries the rig structure for free.
------------------------------------------------------------------------

foldR-initial : ∀ {C} (R : RigAlgebra C) (g : ∀ {n} → LehmerPath n → C n) →
                (g start ≡ base (alg R)) →
                (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
                   g (l ◂ p) ≡ step (alg R) (g l) p) →
                ∀ {n} (l : LehmerPath n) → g l ≡ foldR R l
foldR-initial R = fold-unique (alg R)
