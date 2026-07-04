{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedTransport — ⟡backed-transport: lift the
-- FOLD transport (176) to the REGISTERED BackedUP level. A BackedMorphism between two
-- BackedUPs is a pair (σ on Source, φ on Target) making the SOLVE square commute:
-- φ ∘ solve b₁ ≡ solve b₂ ∘ σ. For shared-Source fold-BackedUPs (σ = id), φ is the
-- algebra morphism between the fold targets and the square IS the fold-transport.
--
-- So the registered solvers are not isolated points — they are connected by transport
-- morphisms, and the fold-transport (trace-fold-transport, 172; shape→count, 176)
-- provides them. Concretely: shape-backed ⇒ count-backed via φ = length, the square =
-- 176's shape→count. The registered BackedUPs form a diagram, the morphisms free.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.BackedTransport where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.Wedge using (C; Trace; done; quot; rem; trace-fold; ℕ-div)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves; content; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.Registry using (registry)
open import Substrate.Category.UniversalProperty.FoldRegistry using (SomeTraceℕ; shape-fold; shape-backed)
open import Substrate.Category.UniversalProperty.FoldTransportInstances using (length; shape→count)

------------------------------------------------------------------------
-- ① A MORPHISM OF BackedUPs: (σ : Source b₁ → Source b₂, φ : Target b₁ → Target b₂)
-- making the solve square commute. This is transport at the registered-solver level.
------------------------------------------------------------------------
BackedMorphism : (b₁ b₂ : BackedUP) → Set
BackedMorphism b₁ b₂ =
  Σ (Source (arrow b₁) → Source (arrow b₂)) (λ σ →
  Σ (Target (arrow b₁) → Target (arrow b₂)) (λ φ →
    (s : Source (arrow b₁)) → φ (solve b₁ s) ≡ solve b₂ (σ s)))

------------------------------------------------------------------------
-- ② count-backed: the count/length fold registered as a BackedUP (Source = SomeTraceℕ,
-- the SAME Source as shape-backed; Target = ℕ; solve = count-fold).
------------------------------------------------------------------------
count-fold : {a b g : ℕ} → Trace ℕ-div a b g → ℕ
count-fold = trace-fold {ℕ-div} {T = λ _ _ _ → ℕ} (λ _ → 0) (λ _ _ rec → suc rec)

count-UP : UPArrow
count-UP = record
  { Source  = SomeTraceℕ
  ; Target  = ℕ
  ; Witness = λ st v → v ≡ count-fold (proj₂ (proj₂ (proj₂ st)))
  }

count-solve : Source count-UP → Target count-UP
count-solve (a , b , g , t) = count-fold t

count-solves : (st : Source count-UP) → Witness count-UP st (count-solve st)
count-solves (a , b , g , t) = refl

-- content: (done 0) has count 0; candidate 1 ≠ 0. Non-vacuous.
count-contentful : Contentful count-UP
count-contentful = (0 , 0 , 0 , done 0) , 1 , λ ()

count-backed : BackedUP
count-backed = record
  { arrow = count-UP ; solve = count-solve ; solves = count-solves ; content = count-contentful }

count-non-vacuous : ¬ _
count-non-vacuous = backed-non-vacuous count-backed

count-registry : List BackedUP
count-registry = count-backed ∷ registry

------------------------------------------------------------------------
-- ③ THE TRANSPORT MORPHISM shape-backed ⇒ count-backed. σ = id (shared Source), φ =
-- length (List ℕ → ℕ), and the square φ (shape-solve s) ≡ count-solve s IS 176's
-- shape→count (length ∘ shape-fold ≡ count-fold). The registered shape-solver transports
-- to the registered count-solver, for FREE, by the fold-transport.
------------------------------------------------------------------------
shape⇒count : BackedMorphism shape-backed count-backed
shape⇒count =
    (λ s → s)                                        -- σ = id (shared SomeTraceℕ)
  , length                                            -- φ = length : List ℕ → ℕ
  , (λ { (a , b , g , t) → shape→count t })           -- the square = 176's shape→count

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — transport at the registered-solver level): the
-- registered fold-BackedUPs are NOT isolated points — a BackedMorphism (σ, φ) connects
-- two of them by making the SOLVE square commute (φ ∘ solve b₁ ≡ solve b₂ ∘ σ), and for
-- shared-Source folds this square IS the fold-transport (176). shape-backed ⇒ count-
-- backed via φ = length is the witness: the registered shape-solver transports to the
-- registered count-solver by 176's shape→count, no new proof. So the whole registered-
-- fold family forms a DIAGRAM whose morphisms are the algebra morphisms between targets,
-- lifted through solve — the initial-algebra universal property (trace-fold-unique)
-- supplying every arrow. The "isolated registered solvers vs a connected family" either/
-- or dissolves: registration certifies each solver (existence + non-vacuity), and the
-- fold-transport certifies the morphisms between them — the Registry is a DIAGRAM, not a
-- list. (count-backed also registered here; count-registry cons's it.)
------------------------------------------------------------------------
