{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.OrbitBoundary — the boundary-of-a-boundary
-- structure over the space of admissible detectors (operator: Agda does not
-- verify the Python; it COMPILES the ∂∂ measure over the space of admissible
-- structures, WITHIN which the Python is confined).
--
-- This makes explicit what was implicit in OrbitComplete.completeness: the
-- admissibility conditions are a BOUNDARY OPERATOR ∂ on detectors, and the
-- coinductive coherence that lets completeness close is ∂∂ = 0 — the boundary
-- of the boundary vanishes. That vanishing is exactly what makes "admissible on
-- the closed set" a well-defined CLASS (a cycle, not an arbitrary sample), and
-- the confinement region the Python lives in.
--
--   ∂  (the boundary):  a detector's admissibility DEFECT at each state — the
--       pair (head-defect, tail-defect). ∂ h s = 0 ⟺ the two squares hold at s.
--   ∂∂ (boundary of boundary): the coherence that the tail-defect at s, stepped,
--       feeds the head-defect at next s. On a step-closed P this obstruction
--       VANISHES (the coinduction closes) — ∂∂ = 0. That IS completeness.
--   CONFINEMENT: ker ∂ (the admissible detectors) on a closed P is a single
--       ~-class (all agree, = cover). The Python, projected into ker ∂, is
--       CONFINED to that class — Agda compiled the region; it need not run it.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.OrbitBoundary where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)
open import Substrate.Algebra.R.Trace.OrbitUniversality using (module OrbitCover)
open import Substrate.Algebra.R.Trace.OrbitComplete using (module ClosedControls)

module Boundary
  (S : Set) (next : S → S) (obs : S → ℕ)
  (P : S → Set) (P-closed : (s : S) → P s → P (next s))
  where
  open OrbitCover S next obs using (cover)
  open ClosedControls S next obs P P-closed using (AdmissibleOn; completeness)

  ------------------------------------------------------------------------
  -- ∂ — the boundary operator. A detector h has a DEFECT at s: the head-defect
  -- (does head (h s) equal obs s?) and the tail-defect (does tail (h s) equal
  -- h (next s)?). We record ∂ as the PROPOSITION that both defects vanish at s
  -- (∂ h s ≡ 0); its conjunction over the closed set is AdmissibleOn.
  ------------------------------------------------------------------------
  ∂-head-vanishes : (S → RealTrace) → (s : S) → P s → Set
  ∂-head-vanishes h s _ = head (h s) ≡ obs s

  ∂-tail-vanishes : (S → RealTrace) → (s : S) → P s → Set
  ∂-tail-vanishes h s _ = tail (h s) ≡ h (next s)

  -- ∂ h = 0 on P  ⟺  AdmissibleOn h. The boundary vanishes = admissible.
  ∂-vanishes : (S → RealTrace) → Set
  ∂-vanishes h = ((s : S) (ps : P s) → ∂-head-vanishes h s ps)
               × ((s : S) (ps : P s) → ∂-tail-vanishes h s ps)

  -- ∂-vanishes IS AdmissibleOn (same two squares) — the boundary operator's
  -- kernel is the admissible space, definitionally.
  ∂-is-admissible : (h : S → RealTrace) → ∂-vanishes h → AdmissibleOn h
  ∂-is-admissible h (hh , ht) = (λ s ps → hh s ps) , (λ s ps → ht s ps)

  ------------------------------------------------------------------------
  -- ∂∂ = 0 — the boundary of the boundary. The tail-defect at s vanishing
  -- means tail (h s) ≡ h (next s); for the boundary to COHERE, the head-defect
  -- must then vanish at next s, and its tail-defect feeds next² s, ... The
  -- obstruction to this closing is what P-closed kills: closure keeps every
  -- stepped state in P, so the boundary condition is available at every reachable
  -- state. ∂∂ = 0 is precisely that the coinductive chain closes — witnessed by
  -- `completeness` producing h s ~ cover s from ∂-vanishes.
  ------------------------------------------------------------------------
  ∂∂-vanishes : (h : S → RealTrace) → ∂-vanishes h → (s : S) → P s → h s ~ cover s
  ∂∂-vanishes h dv s ps = completeness h (∂-is-admissible h dv) s ps

  ------------------------------------------------------------------------
  -- CONFINEMENT. ker ∂ on the closed P is a SINGLE ~-class: any two detectors
  -- with vanishing boundary agree. A structure (the Python, projected into
  -- ker ∂) is CONFINED to that class — it need not be run, only shown to have
  -- vanishing boundary, and ∂∂ = 0 places it in the cover's class.
  ------------------------------------------------------------------------
  confinement : (h₁ h₂ : S → RealTrace)
              → ∂-vanishes h₁ → ∂-vanishes h₂
              → (s : S) → P s → h₁ s ~ h₂ s
  confinement h₁ h₂ d₁ d₂ s ps =
    ~trans (∂∂-vanishes h₁ d₁ s ps) (~sym (∂∂-vanishes h₂ d₂ s ps))
    where
      ~sym : {x y : RealTrace} → x ~ y → y ~ x
      head~ (~sym p) rewrite head~ p = refl
      tail~ (~sym p) = ~sym (tail~ p)
      ~trans : {x y z : RealTrace} → x ~ y → y ~ z → x ~ z
      head~ (~trans p q) rewrite head~ p = head~ q
      tail~ (~trans p q) = ~trans (tail~ p) (tail~ q)
