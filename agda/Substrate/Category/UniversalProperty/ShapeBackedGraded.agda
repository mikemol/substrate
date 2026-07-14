------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ShapeBackedGraded — ⟡C2g-m-fold/shape (graded): the shape
-- trace-fold as a Set₀ graded backing.
--
-- Migrates the flat `shape-backed : BackedUP` (FoldRegistry.agda:59). solve = shape-fold (the CF/cost
-- read of a trace); `solves` (= refl) vanishes into `Contentfulᴳ`. Constant grade (Spec = λ _ →
-- SomeTraceℕ, Sol = λ _ → List ℕ); content = the trace `done 0` whose shape [] differs from the
-- candidate (0 ∷ []). Class A, CLEAN. (The `shape-id-transport` lemma stays in the flat FoldRegistry —
-- it is auxiliary, not part of the backing.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ShapeBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; quot; Trace; done; trace-fold; ℕ-div)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- shape as a trace-fold (done ↦ [] ; more w ↦ quot w ∷ …). The CF/cost read.
shape-fold : {C : Set} {D : DivStr C} {a b g : C} → Trace D a b g → List C
shape-fold {C = C} {D = D} = trace-fold {D = D} {T = λ _ _ _ → List C} (λ _ → []) (λ _ w rec → quot w ∷ rec)

SomeTraceℕ : Set
SomeTraceℕ = Σ ℕ (λ a → Σ ℕ (λ b → Σ ℕ (λ g → Trace ℕ-div a b g)))

shape-solve : SomeTraceℕ → List ℕ
shape-solve (a , b , g , t) = shape-fold t

shape-arrowᴳ : UPArrowᴳ (λ _ → SomeTraceℕ) (λ _ → List ℕ)
shape-arrowᴳ = mkUP shape-solve

shape-backedᴳ : BackedUPᴳ (λ _ → SomeTraceℕ) (λ _ → List ℕ)
shape-backedᴳ = record
  { arrowᴳ  = shape-arrowᴳ
  ; content = 0 , (0 , 0 , 0 , done 0) , (0 ∷ []) , λ ()
  }
