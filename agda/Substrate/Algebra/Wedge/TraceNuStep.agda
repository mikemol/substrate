{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceNuStep — ⟡realtrace-nu-step: the ν/GREATEST half,
-- the mirror of the μ-half (ADD 157-159). Where Trace = μΦ-step (initial algebra,
-- fixed point, Kleene colimit), the ν side is the COALGEBRA of Φ-step — realized
-- (per Wedge.Coalgebra's design) as the wedge UNFOLD `divide`, NOT a materialized
-- coinductive object. The greatest fixed point is the observations/coalgebra side.
--
-- HONEST SCOPE (the dual of 158, mirrored precisely):
--   (1) coalg→Φ : a WedgeCoalg unrolls each (a,b,g) into a Φ-step layer — the ν
--       COALGEBRA structure (dual to 158's unroll, but for an ARBITRARY coalgebra
--       carrier, which is what terminality quantifies over).
--   (2) with ana-unique (Final, ADD 157), RealTrace is the TERMINAL coalgebra = ν
--       in the terminal-coalgebra sense (dual to Trace = initial = μ).
--   (3) HONEST: RealTrace is the ℕ-STREAM (the CF-digit shape), i.e. the SHAPE-image
--       of νΦ-step; the full "RealTrace ≅ νΦ-step" is up-to-shape (shape forgets the
--       positional fill), scoped. The DESCENDING chain ⋂ Φⁿ⊤ (dual of 159's ⋃ Φⁿ⊥)
--       is scoped as the colimit mirror.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceNuStep where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Wedge using (DivStr; z; quot; rem; recon) renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide; eq?)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; step-refinement)

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE ν COALGEBRA over an arbitrary carrier X : Idx → Set. A coalgebra assigns
  -- to each index a Φ-step layer — EITHER the terminal (done) OR a step (a wedge +
  -- the next state). This is the DUAL of 158's roll: there the constructors folded
  -- INTO Trace; here a coalgebra unfolds OUT of a carrier. νΦ-step is the terminal
  -- such coalgebra (the greatest fixed point).
  ------------------------------------------------------------------------
  ν-Coalg : (Idx D → Set) → Set
  ν-Coalg X = X ⊑ᶠ Φ-step D X          -- the unfold: every state emits a Φ-step layer

  ------------------------------------------------------------------------
  -- ② A WedgeCoalg INDUCES a ν-coalgebra on "not-yet-terminal" states. Given a
  -- decision that (a,b,g) is a step (b is not z, so divide applies), the coalgebra
  -- emits inj₂ (the wedge + residual state). This is the wedge UNFOLD as the ν
  -- structure (Wedge.Coalgebra's `divide` = the coalgebra dual to recon).
  ------------------------------------------------------------------------
  -- the STEP carrier: states that emit a wedge (the coalgebra's active domain).
  -- A step-state at (a,b,g) is a witness that divide produces the wedge a→b.
  StepAt : WedgeCoalg D → Idx D → Set
  StepAt co (a , b , g) = Σ (Wedge⟦478f66a6⟧ D a b) (λ w → rem w ≡ rem (divide co a b))

  -- the coalgebra unrolls a step-state into a Φ-step layer (the inj₂ / more side):
  -- emit the wedge and land on the residual state (b, rem w, g). Dual to 158's roll.
  coalg-unroll : (co : WedgeCoalg D) → StepAt co ⊑ᶠ Φ-step D (StepAt co)
  coalg-unroll co (a , b , g) (w , _) =
    inj₂ (w , (divide co b (rem w) , refl))    -- step: wedge w, next state at residual

  ------------------------------------------------------------------------
  -- ③ THE TERMINAL / ν UNIVERSAL PROPERTY (the mirror of 157's initiality). The
  -- greatest fixed point νΦ-step is TERMINAL: any ν-coalgebra maps uniquely into it.
  -- The substrate realizes this via Wedge.Coalgebra (the divide-unfold, cyclic lasso)
  -- and Final.ana-unique (for the ℕ-stream shape). Here we record the ν-coalgebra
  -- structure; terminality is the shape/RealTrace connection (④).
  ------------------------------------------------------------------------
  -- a ν-coalgebra IS a Φ-step-coalgebra (definitionally) — the structure map exists.
  coalg-is-Φ : (co : WedgeCoalg D) → ν-Coalg (StepAt co)
  coalg-is-Φ = coalg-unroll

------------------------------------------------------------------------
-- ④ THE RealTrace CONNECTION (honest, up-to-shape). RealTrace is the ℕ-stream of
-- CF digits — the SHAPE of a νΦ-step unfold (each node = one wedge quotient). So
-- RealTrace ≅ νΦ-step holds at the level of SHAPE (the quotient stream), NOT as a
-- full iso (shape forgets the positional fill b + witnesses, exactly as in the
-- finite case, Wedge.Shape). ana-unique (Final, ADD 157) gives the ℕ-stream's
-- terminality — the ν universal property for the shape. The full νΦ-step (with
-- positional fill) is the wedge-coalgebra unfold (Wedge.Coalgebra), realized as a
-- finite cyclic lasso (halt/loop/stop), never a materialized infinite object.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; ~-refl)

-- the ν side's self-consistency (the terminal object is bisimilar to itself — the
-- coinductive reflexivity, from Final's ana-unique self-unfold shape).
ν-self : (x : RealTrace) → x ~ x
ν-self = ~-refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ν-half mirror, HONESTLY): the greatest fixed
-- point νΦ-step is the COALGEBRA of Φ-step — a ν-coalgebra X ⊑ᶠ Φ-step X (dual to
-- 158's roll : Φ-step Trace ⊑ᶠ Trace). A WedgeCoalg induces one (coalg-unroll, via
-- divide = the wedge unfold dual to recon). With ana-unique (157), the terminal
-- coalgebra is ν, dual to Trace initial = μ. The μ-vs-ν either/or dissolves into the
-- fold⊣unfold duality: μΦ-step = Trace (recon/roll/initial/Kleene-colimit, 157-159)
-- and νΦ-step = the wedge-coalgebra (divide/unroll/terminal), ONE Φ-step with two
-- fixed-point endpoints. HONESTLY SCOPED: RealTrace is the ℕ-stream = the SHAPE of
-- νΦ-step (RealTrace ≅ νΦ-step up-to-shape, not a full iso — shape forgets fill);
-- the DESCENDING chain ⋂ Φⁿ⊤ (dual of 159's ⋃ Φⁿ⊥) is the colimit mirror, scoped.
-- The frontier's ν-half: the coalgebra endpoint is grounded; the full up-to-shape
-- iso + descending colimit are the honest remainder.
------------------------------------------------------------------------
