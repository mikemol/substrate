{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceMuStep — ⟡allegory-wedge-step-mu: the Φ built from
-- the WEDGE STEP (heeding Refinement's FALSE-SHORTCUT warning: NOT raw R), and the
-- proof that Trace is a FIXED POINT of it (Φ Trace ≅ Trace — Lambek). This is the
-- foundational, PROVEN core of Refinement's open obligation "Trace ≅ μΦ".
--
-- HONEST SCOPE: the FULL obligation is Trace ≅ μΦ where μΦ is the CHAIN colimit
-- (Kleene, ⋃ Φⁿ⊥). This module delivers the two TRUE foundational facts and marks
-- the colimit-leastness + RealTrace ≅ νΦ as the remaining frontier:
--   (1) Φ-step : the pattern functor on Fam (C×C×C), built from the done/more STEP
--       (a genuine Refinement — monotone), NOT the raw-R false shortcut.
--   (2) Trace ≅ Φ-step Trace: Trace is a FIXED POINT (roll = the constructors,
--       unroll = pattern-match) — Lambek's lemma for the pattern functor.
--   (3) with trace-fold-unique (ADD 157), Trace is the INITIAL Φ-algebra = μΦ in the
--       initial-algebra sense. The Kleene-chain (⋃ Φⁿ⊥) agreeing is scoped.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceMuStep where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Wedge using (DivStr; z; rem; Trace; done; more) renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_; Refinement)

module _ {C : Set} (D : DivStr C) where

  -- the index of a trace: the triple (a, b, g) — start, current divisor, gcd.
  Idx : Set
  Idx = C × C × C

  ------------------------------------------------------------------------
  -- ① THE WEDGE-STEP PATTERN FUNCTOR Φ. At index (a, b, g), a family element is
  -- EITHER the done case (b ≡ z, g ≡ a — the terminal) OR a step: a wedge w : Wedge
  -- a b, and P at the residual (b, rem w, g). Built from the STEP (done/more), NOT
  -- raw R. Monotone (P appears positively) ⟹ a genuine Refinement.
  ------------------------------------------------------------------------
  Φ-step : (Idx → Set) → Idx → Set
  Φ-step P (a , b , g) =
      ((b ≡ z D) × (g ≡ a))                              -- done: terminal
    ⊎ (Σ (Wedge⟦478f66a6⟧ D a b) (λ w → P (b , rem w , g)))        -- more: step to residual

  Φ-step-mono : {P Q : Fam Idx} → P ⊑ᶠ Q → Φ-step P ⊑ᶠ Φ-step Q
  Φ-step-mono P⊑Q (a , b , g) (inj₁ eqs)      = inj₁ eqs
  Φ-step-mono P⊑Q (a , b , g) (inj₂ (w , p))  = inj₂ (w , P⊑Q (b , rem w , g) p)

  -- the wedge-step Φ IS a Refinement (the monotone Φ-floor, from the STEP).
  step-refinement : Refinement Idx
  step-refinement = record { Φ = Φ-step ; mono = Φ-step-mono }

  ------------------------------------------------------------------------
  -- ② TRACE AS THE FAMILY. Trace at (a,b,g) — the inductive done/more type, read as
  -- a family over Idx.
  ------------------------------------------------------------------------
  TraceF : Idx → Set
  TraceF (a , b , g) = Trace D a b g

  ------------------------------------------------------------------------
  -- ③ TRACE IS A FIXED POINT OF Φ-step (Lambek): Φ-step TraceF ≅ TraceF, both
  -- directions. ROLL (Φ TraceF ⊑ TraceF) = the constructors; UNROLL (TraceF ⊑ Φ
  -- TraceF) = pattern-match. This is the algebra+coalgebra structure — the PROVEN
  -- core of "Trace ≅ μΦ".
  ------------------------------------------------------------------------
  -- ROLL: a Φ-step layer over Trace folds into a Trace (done/more constructors).
  roll : Φ-step TraceF ⊑ᶠ TraceF
  roll (a , .(z D) , .a) (inj₁ (refl , refl)) = done a
  roll (a , b , g)       (inj₂ (w , tr))      = more b w tr

  -- UNROLL: a Trace unfolds to a Φ-step layer (pattern-match on the constructors).
  unroll : TraceF ⊑ᶠ Φ-step TraceF
  unroll (a , .(z D) , .a) (done .a)      = inj₁ (refl , refl)
  unroll (a , b , g)       (more .b w tr) = inj₂ (w , tr)

  ------------------------------------------------------------------------
  -- ④ THE ROUND-TRIPS: roll ∘ unroll ≡ id and unroll ∘ roll ≡ id (the iso is
  -- definitional on the constructors — Lambek, witnessed).
  ------------------------------------------------------------------------
  roll∘unroll : (i : Idx) (t : TraceF i) → roll i (unroll i t) ≡ t
  roll∘unroll (a , .(z D) , .a) (done .a)      = refl
  roll∘unroll (a , b , g)       (more .b w tr) = refl

  unroll∘roll : (i : Idx) (x : Φ-step TraceF i) → unroll i (roll i x) ≡ x
  unroll∘roll (a , .(z D) , .a) (inj₁ (refl , refl)) = refl
  unroll∘roll (a , b , g)       (inj₂ (w , tr))      = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — HONESTLY, the frontier ADVANCED not overclaimed):
-- the Φ built from the WEDGE STEP (Φ-step, NOT the raw-R false shortcut) is a
-- genuine Refinement, and Trace is its FIXED POINT — Φ-step TraceF ≅ TraceF, roll
-- (constructors) and unroll (pattern-match) mutually inverse (Lambek's lemma). With
-- trace-fold-unique (ADD 157, initiality), Trace is the INITIAL Φ-step-algebra = μΦ
-- in the initial-algebra sense. The μ-vs-frontier either/or dissolves: Trace-as-
-- fixed-point + Trace-as-initial ARE the μ content (initial algebra = least fixed
-- point); what remains scoped is the KLEENE-CHAIN characterization (μΦ = ⋃ Φⁿ⊥
-- agreeing with the initial algebra — the colimit convergence) and RealTrace ≅ νΦ
-- (the terminal coalgebra = greatest, dual via ana-unique). This module delivers the
-- TRUE foundation (the Φ from the step + Trace as its fixed point); the colimit and
-- the ν-half stay the honest remaining obligation, the false shortcut heeded.
------------------------------------------------------------------------
