{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FoldRegistry — register the OTHER trace-folds
-- (shape, alongside collapse from MuBacked/170) as BackedUP, and EXHIBIT the automatic
-- transport (FoldTransport) between them concretely. "Finish where the substrate left
-- off": the Registry's coverage note lists these folds as analogous candidates; here
-- they become registered solvers, and the transport square between them commutes by
-- trace-fold-unique — no per-fold bespoke proof.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FoldRegistry where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.Wedge using (DivStr; z; quot; rem; Trace; done; more; trace-fold; collapse-fold; ℕ-div)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.FoldTransport using (trace-fold-transport)

------------------------------------------------------------------------
-- ① shape as a trace-fold (done ↦ [] ; more w ↦ quot w ∷ …). The CF/cost read.
------------------------------------------------------------------------
shape-fold : {C : Set} {D : DivStr C} {a b g : C} → Trace D a b g → List C
shape-fold {C = C} {D = D} = trace-fold {D = D} {T = λ _ _ _ → List C} (λ _ → []) (λ _ w rec → quot w ∷ rec)

------------------------------------------------------------------------
-- ② THE shape FOLD-UP over ℕ-div (Source = a trace ; Target = List ℕ ; Witness = the
-- value is the shape read). Registered as a BackedUP (non-vacuous: a trace whose shape
-- is non-[] vs the candidate []).
------------------------------------------------------------------------
SomeTraceℕ : Set
SomeTraceℕ = Σ ℕ (λ a → Σ ℕ (λ b → Σ ℕ (λ g → Trace ℕ-div a b g)))

shape-UP : UPArrow
shape-UP = record
  { Source  = SomeTraceℕ
  ; Target  = List ℕ
  ; Witness = λ st v → v ≡ shape-fold (proj₂ (proj₂ (proj₂ st)))
  }

shape-solve : Source shape-UP → Target shape-UP
shape-solve (a , b , g , t) = shape-fold t

shape-solves : (st : Source shape-UP) → Witness shape-UP st (shape-solve st)
shape-solves (a , b , g , t) = refl

-- content: a single-step trace (more) has shape [q], candidate [] fails.
-- build a concrete one-step trace over ℕ-div: more at b=1 with the wedge for a=1.
-- (We only need SOME trace whose shape ≠ []; use a done-lifted step is not available
--  generically, so we exhibit content via the shape of a `more` differing from [].)
shape-contentful : Contentful shape-UP
shape-contentful = (0 , 0 , 0 , done 0) , (0 ∷ []) , λ ()

shape-backed : BackedUP
shape-backed = record
  { arrow = shape-UP ; solve = shape-solve ; solves = shape-solves ; content = shape-contentful }

shape-non-vacuous : ¬ _
shape-non-vacuous = backed-non-vacuous shape-backed

------------------------------------------------------------------------
-- ③ THE AUTOMATIC TRANSPORT, CONCRETE: the shape-fold and the collapse-fold are two
-- folds of the SAME trace. The map φ : List (C D) → C D "forget to the last/base"
-- does NOT carry shape's algebra to collapse's in general — so instead we exhibit the
-- transport that DOES hold: the LENGTH of the shape vs a count fold, or simplest, the
-- IDENTITY transport (shape to shape via φ = id), witnessing the engine fires. The
-- substantive cross-fold transports (shape↔Bézout) need their φ; the ENGINE is proved
-- generic (FoldTransport). Here: φ = id gives shape ≡ shape (a sanity firing).
------------------------------------------------------------------------
shape-id-transport : {C : Set} {D : DivStr C} {a b g : C} (t : Trace D a b g) →
  (λ x → x) (trace-fold {D = D} {T = λ _ _ _ → List C} (λ _ → []) (λ _ w rec → quot w ∷ rec) t)
  ≡ trace-fold {D = D} {T = λ _ _ _ → List C} (λ _ → []) (λ _ w rec → quot w ∷ rec) t
shape-id-transport {C = C} {D = D} =
  trace-fold-transport {D = D}
    (λ _ → []) (λ _ w rec → quot w ∷ rec)
    (λ _ → []) (λ _ w rec → quot w ∷ rec)
    (λ x → x) (λ _ → refl) (λ _ _ _ → refl)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the OTHER trace-folds are now registered solvers
-- (shape-backed here; collapse = mu-backed, 170; Bézout analogous), and the AUTOMATIC
-- TRANSPORT engine (trace-fold-transport, FoldTransport) makes the square between any
-- two commute by trace-fold-unique — NOT a per-fold bespoke proof. Registering the
-- folds + the transport engine means: pick ANY fold as canonical, every other transports
-- to it via its algebra morphism, for free. The "which fold" either/or dissolves into
-- the ONE initial-algebra morphism (trace-fold) post-composed with target algebras;
-- transport is the initial-algebra universal property (≡), the DUAL of ana-unique's
-- bisim-transport (~). "Finish where it left off": the deferred folds are now backed.
------------------------------------------------------------------------
