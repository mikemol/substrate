{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceNuAbstractLimit — ⟡nu-abstract-limit-postfp: the
-- ABSTRACT descending-chain limit as a post-fixed-point, UNDER an explicit ω-
-- continuity hypothesis. The complement of ADD 164 (the CONSTRUCTIVE ν via divide,
-- which needs NO hypothesis): here we prove Limit ⊑ Φ-step Limit for the ABSTRACT
-- Limit (whose step is an EXISTENTIAL Σ w. Φⁿ⊤), which DOES need the wedge to be
-- determinate across stages.
--
-- THE HYPOTHESIS (honest, and it is the exact ω-continuity condition): wrem-uniq —
-- any two wedges a→b have equal rem. This is FALSE for unconstrained wedges
-- (a = q·b + r has many solutions without smallness r < b), so it captures the
-- CERTIFIED/SMALL-wedge restriction (recon-bounded-unique for ℕ-div). Plus deq
-- (decidable carrier equality) to decide the done case. UNDER these, Limit is a
-- post-fixed-point, hence (with coalg-below-limit, ADD 162) the GREATEST fixed
-- point: Limit = νΦ-step. This isolates EXACTLY what the abstract limit needs — the
-- residue naming why the constructive path (divide, a function, ADD 164) needs none.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceNuAbstractLimit where

open import Substrate.Foundation.Eq  using (_≡_; refl; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Wedge using (DivStr; z; rem) renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_; iterate)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; step-refinement)
open import Substrate.Algebra.Wedge.TraceNuColimit using (⊤-fam; Limit; coalg-below-limit)

-- a Dec of a product from two Decs (for the done? decision).
dec-× : {A B : Set} → Dec A → Dec B → Dec (A × B)
dec-× (yes a) (yes b) = yes (a , b)
dec-× (yes a) (no ¬b) = no (λ ab → ¬b (proj₂ ab))
dec-× (no ¬a) _       = no (λ ab → ¬a (proj₁ ab))

module _ {C : Set} (D : DivStr C)
         (deq : (x y : C) → Dec (x ≡ y))
         (wrem-uniq : {a b : C} (w w' : Wedge⟦478f66a6⟧ D a b) → rem w ≡ rem w') where

  -- decide the done case at an index (b ≡ z × g ≡ a) from decidable equality.
  done? : (i : Idx D) → Dec ((proj₁ (proj₂ i) ≡ z D) × (proj₂ (proj₂ i) ≡ proj₁ i))
  done? (a , b , g) = dec-× (deq b (z D)) (deq g a)

  ------------------------------------------------------------------------
  -- THE ABSTRACT LIMIT IS A POST-FIXED-POINT (under deq + wrem-uniq). At each index:
  -- decide done; if done, emit inj₁; else every stage-witness is a step (inj₁ would
  -- contradict ¬done), extract its wedge, and wrem-uniq reconciles the per-stage
  -- wedges to ONE canonical w so the residual sits in Limit at (b, rem w, g).
  ------------------------------------------------------------------------
  abstract-limit-postfp : Limit D ⊑ᶠ Φ-step D (Limit D)
  abstract-limit-postfp (a , b , g) l with done? (a , b , g)
  ... | yes (b≡z , g≡a) = inj₁ (b≡z , g≡a)
  ... | no ¬done        = inj₂ (w₁ , residual)
    where
      -- every stage m gives a step-witness (inj₁ contradicts ¬done): the wedge + the
      -- residual membership at THAT wedge's rem.
      step-at : (m : ℕ) →
        Σ (Wedge⟦478f66a6⟧ D a b) (λ w → iterate (step-refinement D) m (⊤-fam D) (b , rem w , g))
      step-at m with l (suc m)
      ... | inj₁ dp       = ⊥-elim (¬done dp)
      ... | inj₂ (w , y)  = w , y
      -- the canonical wedge from stage 0, and the residual limit at its rem —
      -- transporting each stage's witness along wrem-uniq (rem is determinate).
      w₁ : Wedge⟦478f66a6⟧ D a b
      w₁ = proj₁ (step-at zero)
      residual : Limit D (b , rem w₁ , g)
      residual m =
        subst (λ r → iterate (step-refinement D) m (⊤-fam D) (b , r , g))
              (wrem-uniq (proj₁ (step-at m)) w₁)
              (proj₂ (step-at m))

  ------------------------------------------------------------------------
  -- HENCE Limit = νΦ-step: it is a post-fixed-point (a coalgebra, above), and by
  -- coalg-below-limit (ADD 162) every coalgebra is below it — so it is the GREATEST
  -- fixed point. Both directions of "Limit is the terminal coalgebra" hold under
  -- the ω-continuity hypothesis.
  ------------------------------------------------------------------------
  -- the limit is itself a coalgebra (post-fixed-point):
  limit-coalgebra : Limit D ⊑ᶠ Φ-step D (Limit D)
  limit-coalgebra = abstract-limit-postfp

  -- and it is above every coalgebra (162) — so Limit is the greatest fixed point.
  limit-greatest : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) → X ⊑ᶠ Limit D
  limit-greatest = coalg-below-limit D

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the abstract limit-postfp, HONESTLY conditional):
-- under wrem-uniq (rem-uniqueness) + deq (decidable equality), the ABSTRACT
-- descending-chain Limit ⋂ₙ Φⁿ⊤ IS a post-fixed-point (Limit ⊑ Φ-step Limit), hence
-- (with coalg-below-limit, 162) the GREATEST fixed point: Limit = νΦ-step. The proof:
-- decide done (deq); if done emit inj₁; else extract the per-stage step-wedges (inj₁
-- contradicts ¬done) and RECONCILE them via wrem-uniq to one canonical w (the residual
-- then sits in Limit at (b, rem w, g)). THE HYPOTHESIS IS THE ω-CONTINUITY CONDITION,
-- and it needs SMALLNESS: wrem-uniq is FALSE for unconstrained wedges (a = q·b+r has
-- many rems), TRUE for certified/small wedges (recon-bounded-unique, ℕ-div). So this
-- is the CERTIFIED-wedge restriction. The either/or "abstract limit is/isn't a post-
-- fp" dissolves: it IS, exactly under wedge-determinacy (ω-continuity) — which the
-- CONSTRUCTIVE ν (divide, a FUNCTION, ADD 164) SATISFIES STRUCTURALLY (no hypothesis).
-- 164 (constructive, no hypothesis) + here (abstract, under ω-continuity) are the two
-- honest faces of the ν greatest-fixed-point; together the ν-half is complete.
------------------------------------------------------------------------
