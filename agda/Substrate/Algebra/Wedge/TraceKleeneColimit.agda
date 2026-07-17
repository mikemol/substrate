{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceKleeneColimit — ⟡trace-kleene-colimit: the KLEENE
-- colimit μΦ = ⋃ₙ Φⁿ⊥ ≅ Trace, completing the μ-half of Refinement's frontier
-- BEYOND the initial-algebra characterization (ADD 157/158).
--
-- ADD 158 built the wedge-step Φ (Φ-step) and proved Trace is its FIXED POINT
-- (Lambek); with trace-fold-unique (157) Trace is the INITIAL Φ-algebra = μΦ in the
-- initial-algebra sense. This module closes the OTHER characterization: the KLEENE
-- ascending chain from ⊥. Φⁿ⊥ = the traces of bounded depth < n; the colimit
-- ⋃ₙ Φⁿ⊥ = all finite traces = Trace. Both directions proven ⟹ Colim ≅ Trace, so
-- the Kleene colimit IS Trace IS μΦ (via 157/158). The μ-half is now closed in BOTH
-- senses (initial algebra AND Kleene colimit); the ν-half (RealTrace ≅ νΦ) remains.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceKleeneColimit where

open import Substrate.Foundation.Eq  using (_≡_; refl; subst; sym)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Wedge using (DivStr; z; rem; Trace; done; more)
open import Substrate.Category.Allegory.Refinement using (_⊑ᶠ_; iterate)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; step-refinement; TraceF)

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE BOTTOM family ⊥ and the KLEENE COLIMIT ⋃ₙ Φⁿ⊥. Colim i = "i is present
  -- at SOME stage n" = the ascending-chain union. (Φⁿ⊥ = bounded-depth traces.)
  ------------------------------------------------------------------------
  ⊥-fam : Idx D → Set
  ⊥-fam _ = ⊥

  Colim : Idx D → Set
  Colim i = Σ ℕ (λ n → iterate (step-refinement D) n ⊥-fam i)

  ------------------------------------------------------------------------
  -- ② TRACE ⊑ COLIM: every trace is present at some stage (its structural depth).
  -- done at stage 1 (Φ¹⊥ has the terminal case); more at stage (suc n) if its
  -- sub-trace is at stage n. This is "every finite trace has bounded depth".
  ------------------------------------------------------------------------
  trace→colim : TraceF D ⊑ᶠ Colim
  trace→colim (a , .(z D) , .a) (done .a) =
    suc zero , inj₁ (refl , refl)                       -- done: stage 1, terminal case
  trace→colim (a , b , g) (more .b w tr) with trace→colim (b , rem w , g) tr
  ... | n , at-n = suc n , inj₂ (w , at-n)              -- more: stage (suc n), step case

  ------------------------------------------------------------------------
  -- ③ COLIM ⊑ TRACE: every colimit element (present at some stage n) rolls up to a
  -- trace. By induction on the stage n — stage 0 is ⊥ (vacuous), stage (suc m)
  -- is a Φ-layer over stage m, rolled by the constructors.
  ------------------------------------------------------------------------
  stage→trace : (n : ℕ) → iterate (step-refinement D) n ⊥-fam ⊑ᶠ TraceF D
  stage→trace zero    i          ()                     -- stage 0 = ⊥: vacuous
  stage→trace (suc m) (a , b , g) (inj₁ (b≡z , g≡a)) =  -- terminal → done (transported)
    subst (λ b′ → Trace D a b′ g)         (sym b≡z)
      (subst (λ g′ → Trace D a (z D) g′)  (sym g≡a) (done a))
  stage→trace (suc m) (a , b , g) (inj₂ (w , y)) =      -- step → more, IH on stage m
    more b w (stage→trace m (b , rem w , g) y)

  colim→trace : Colim ⊑ᶠ TraceF D
  colim→trace i (n , at-n) = stage→trace n i at-n

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the μ-half closed in the Kleene sense): the
-- KLEENE colimit ⋃ₙ Φⁿ⊥ (Colim) is iso to Trace — trace→colim (every finite trace
-- has bounded depth, at its own stage) and colim→trace (every bounded-depth element
-- rolls to a trace). Φⁿ⊥ is the traces of depth < n; the union is all finite
-- traces = Trace. Combined with ADD 158 (Trace is a fixed point of Φ-step) and ADD
-- 157 (Trace is the initial Φ-algebra), the μ-half is now closed in BOTH senses:
-- the INITIAL ALGEBRA (157/158) AND the KLEENE COLIMIT (here) — μΦ = Trace = ⋃ Φⁿ⊥.
-- The "initial-algebra μ vs Kleene-colimit μ" either/or dissolves: they are the SAME
-- least fixed point, and Trace realises both. The ν-half (RealTrace ≅ νΦ, the dual
-- greatest fixed point via the DESCENDING chain from ⊤) remains the scoped frontier.
------------------------------------------------------------------------
