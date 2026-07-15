------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedGradedStencil — ⟡C2g-retire-part2 P1b: the µ⊣ν
-- uniqueness picture as ONE record. Instantiates the generic `UniquenessStencil`
-- (UniquenessStencilAbstract — "the generic uniqueness stencil over ANY Lawvere fixed-point") with
-- the graded ν wedge-coalgebra's OWN fold⊣unfold, so the three uniqueness layers (µ ≡-unconditional,
-- ν-step ≡-bounded, ν-whole ~-bisimulation) are unified in a single Set₀ inhabitant.
--
-- The carriers are POLYMORPHIC in the stencil (CrossMul cospan, never unified): the two ≡ layers over
-- the wedge (ℕ×ℕ, the (a,b)/(q,r) pairs), the ~ layer over the coalgebra (QState/RealTrace). Every
-- layer proof is a tier-free witness-tower engine, NOT a re-port of the flat Set₁ solver-unique:
--   µ-fold  : the unconditional corner — the graded backing's witness IS functional equality, so the
--             per-source layer is `λ s t _ w → w` (the functional witness is the equality).
--   ν-step  : nu-step-uniqueᴳ (← recon-bounded-unique ← divmod-unique), the r<b bounded uniqueness,
--             tied to nu-solve via its own wedge-eq + the mod-suc-bound smallness (both definitional
--             through fromℕ-Wedge/construct-wedge). b=0 ⇒ the bound r<0 is uninhabited (vacuous).
--   ν-whole : shape-is-canonical ℕ-coalg (= ana-unique), the terminal-coalgebra bisimulation.
--
-- Zero postulates, --safe --without-K --guardedness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.BackedGradedStencil where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Wedge using (recon; ℕ-div; rem; wedge-eq)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide)
open import Substrate.Algebra.Nat.Mod using (mod-suc-bound)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_)
open import Substrate.Algebra.Wedge.NuShapeIso
  using (QState; quotient-coalg; shape-stream; shape-is-canonical)
open import Substrate.Category.UniversalProperty.NuBackedGraded using (nu-solve; ℕ-coalg)
open import Substrate.Category.UniversalProperty.BackedGradedUnique using (nu-step-uniqueᴳ)
open import Substrate.Category.UniversalProperty.UniquenessStencilAbstract
  using (UniquenessStencil; PerSource; MapLevel)

------------------------------------------------------------------------
-- The predicate slots (the CrossMul "coherence" gates + witness specs).
------------------------------------------------------------------------

Admμ : ℕ × ℕ → ℕ × ℕ → Set
Admμ _ _ = ⊤

Witμ : ℕ × ℕ → ℕ × ℕ → Set
Witμ s t = t ≡ nu-solve s

Admνs : ℕ × ℕ → ℕ × ℕ → Set
Admνs (a , b) (q , r) = r < b

Witνs : ℕ × ℕ → ℕ × ℕ → Set
Witνs (a , b) (q , r) = a ≡ recon ℕ-div q b r

Agreeᴺ : (QState → RealTrace) → Set
Agreeᴺ h = (∀ s → head (h s) ≡ proj₁ (quotient-coalg ℕ-coalg s))
         × (∀ s → tail (h s) ≡ h (proj₂ (quotient-coalg ℕ-coalg s)))

------------------------------------------------------------------------
-- The two ν-step helpers: nu-solve's own smallness + wedge witness at (a, suc b') — both definitional
-- (nu-solve reads quot/rem off `divide ℕ-coalg`, which at suc b' is `fromℕ-Wedge (construct-wedge a b')`
-- whose rem = a mod-suc b' and wedge-eq is the construct-wedge witness).
------------------------------------------------------------------------

nu-solve-small : (a b' : ℕ) → proj₂ (nu-solve (a , suc b')) < suc b'
nu-solve-small a b' = mod-suc-bound a b'

nu-solve-wit : (a b' : ℕ) →
  a ≡ recon ℕ-div (proj₁ (nu-solve (a , suc b'))) (suc b') (proj₂ (nu-solve (a , suc b')))
nu-solve-wit a b' = wedge-eq (divide ℕ-coalg a (suc b'))

------------------------------------------------------------------------
-- THE UNIFIED µ⊣ν STENCIL: the wedge coalgebra's fold⊣unfold uniqueness as ONE Set₀ record.
------------------------------------------------------------------------

graded-uniqueness :
  UniquenessStencil (ℕ × ℕ) (ℕ × ℕ) QState RealTrace
                    _≡_ _~_
                    nu-solve Admμ Witμ
                    nu-solve Admνs Witνs
                    (shape-stream ℕ-coalg) Agreeᴺ
graded-uniqueness = record
  { μ-fold  = λ s t _ w → w
  ; ν-step  = ν-step-proof
  ; ν-whole = λ h agree s → shape-is-canonical ℕ-coalg h (proj₁ agree) (proj₂ agree) s
  }
  where
    ν-step-proof : PerSource _≡_ nu-solve Admνs Witνs
    ν-step-proof (a , zero)   (q , r) () _
    ν-step-proof (a , suc b') (q , r) r<sb wit =
      nu-step-uniqueᴳ a b' (q , r) (nu-solve (a , suc b'))
                      r<sb (nu-solve-small a b') wit (nu-solve-wit a b')
