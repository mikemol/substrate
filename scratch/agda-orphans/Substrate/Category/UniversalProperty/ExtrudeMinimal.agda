{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeMinimal.Properties.Properties — ⟡extrude-minimal: the extruder's irreducible core,
-- MINIMISATION (μ) as a least-cost search, structured as the wedge-coalgebra unfold (Algebra.Wedge.
-- Coalgebra — the study of ADD 264: divide UNFOLDS, the residue IS the next state, close-cycle = the μ
-- fixed point found; halt/loop/stop). The extruder synthesizes a MINIMAL SKI program meeting a spec: over a
-- candidate enumeration (the grounded vertex/section geometry, 258/260), μ finds the LEAST-COST (SKIShed-
-- Duality.cost) term satisfying a DECIDABLE spec. μ is a FIXED POINT (Lawvere-positive — it EXISTS, no
-- spook); its collapse-to-construction case is extrude-fixpoint = Y-of (248/249).
--
-- THIS MODULE grounds the μ CORE: least-cost selection over a finite candidate list against a decidable
-- spec, with the two universal properties — SOUNDNESS (the result satisfies the spec) and MINIMALITY (the
-- result is cost-≤ every spec-satisfying candidate in the list) — plus the fixed-point collapse (Y-of). The
-- search IS the wedge-coalgebra unfold (halt = found the minimal witness); the full SPPF cycle-closing over
-- an infinite candidate stream is Wedge.Coalgebra.run, reused-in-spirit at this bounded specialization.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: μ-search (least-cost
-- spec-satisfying selection over a list) returning MinResult (a sound + minimal witness, or a no-satisfier
-- certificate), and μ-fixpoint (the collapse case = Y-of converges). The framing ('μ is the extruder's
-- irreducible core, a Lawvere-positive fixed point; the search is the wedge-coalgebra unfold') is (prose:
-- the thesis + the 264 study; the infinite-stream SPPF unfold + the self-interp synthesis are scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeMinimal where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; subst)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s; _≤?_)
open import Substrate.Foundation.Nat.Properties.Order using (≤-refl; ≤-trans; <→≤)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (cost; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; Converge)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- list membership (a candidate is drawn from the enumeration xs):
------------------------------------------------------------------------
Mem : Tm⟦533ef80d⟧ → List Tm⟦533ef80d⟧ → Set
Mem t []       = ⊥
Mem t (x ∷ xs) = (t ≡ x) ⊎ Mem t xs

-- ≤-total-ish: for costs, either m ≤ n or n ≤ m (from _≤?_ via the order):
≤-or : (m n : ℕ) → (m ≤ n) ⊎ (n ≤ m)
≤-or m n with m ≤? n
... | yes p = inj₁ p
... | no ¬p = inj₂ (not≤→≥ m n ¬p)
  where
    not≤→≥ : (m n : ℕ) → ¬ (m ≤ n) → n ≤ m
    not≤→≥ zero    n       ¬p = ⊥-elim (¬p z≤n)
    not≤→≥ (suc m) zero    ¬p = z≤n
    not≤→≥ (suc m) (suc n) ¬p = s≤s (not≤→≥ m n (λ p → ¬p (s≤s p)))

------------------------------------------------------------------------
-- ① THE μ RESULT: a least-cost spec-satisfying witness (sound + minimal), OR a no-satisfier certificate.
------------------------------------------------------------------------
data MinResult (P : Tm⟦533ef80d⟧ → Set) (xs : List Tm⟦533ef80d⟧) : Set where
  found :
    (best : Tm⟦533ef80d⟧) → P best →
    ((t : Tm⟦533ef80d⟧) → P t → Mem t xs → cost best ≤ cost t) →   -- MINIMAL among spec-satisfiers in xs
    MinResult P xs
  none  :
    ((t : Tm⟦533ef80d⟧) → Mem t xs → ¬ P t) →                       -- no candidate satisfies P
    MinResult P xs

------------------------------------------------------------------------
-- ② THE μ SEARCH: bounded minimisation over the candidate list. Decidable spec P?; returns the least-cost
--    satisfier with its universal properties, or the no-satisfier certificate. This IS the extruder's μ —
--    the wedge-coalgebra unfold specialized to a finite candidate list (halt = found the minimal witness).
------------------------------------------------------------------------
μ-search : (P : Tm⟦533ef80d⟧ → Set) → ((t : Tm⟦533ef80d⟧) → Dec (P t)) → (xs : List Tm⟦533ef80d⟧) → MinResult P xs
μ-search P P? [] = none (λ t ())
μ-search P P? (x ∷ xs) with P? x | μ-search P P? xs
-- x satisfies P; combine with the best of the tail:
... | yes px | found b pb mb =
      -- pick the cheaper of x and the tail-best b:
      combine (≤-or (cost x) (cost b))
  where
    combine : (cost x ≤ cost b) ⊎ (cost b ≤ cost x) → MinResult P (x ∷ xs)
    combine (inj₁ x≤b) = found x px min
      where min : (t : Tm⟦533ef80d⟧) → P t → Mem t (x ∷ xs) → cost x ≤ cost t
            min t pt (inj₁ t≡x) = subst (λ z → cost x ≤ cost z) (sym t≡x) (≤-refl _)
            min t pt (inj₂ tin) = ≤-trans x≤b (mb t pt tin)
    combine (inj₂ b≤x) = found b pb min
      where min : (t : Tm⟦533ef80d⟧) → P t → Mem t (x ∷ xs) → cost b ≤ cost t
            min t pt (inj₁ t≡x) = subst (λ z → cost b ≤ cost z) (sym t≡x) b≤x
            min t pt (inj₂ tin) = mb t pt tin
... | yes px | none notail = found x px min
      where min : (t : Tm⟦533ef80d⟧) → P t → Mem t (x ∷ xs) → cost x ≤ cost t
            min t pt (inj₁ t≡x) = subst (λ z → cost x ≤ cost z) (sym t≡x) (≤-refl _)
            min t pt (inj₂ tin) = ⊥-elim (notail t tin pt)
-- x fails P; defer to the tail:
... | no ¬px | found b pb mb = found b pb min
      where min : (t : Tm⟦533ef80d⟧) → P t → Mem t (x ∷ xs) → cost b ≤ cost t
            min t pt (inj₁ t≡x) = ⊥-elim (¬px (subst P t≡x pt))
            min t pt (inj₂ tin) = mb t pt tin
... | no ¬px | none notail = none min
      where min : (t : Tm⟦533ef80d⟧) → Mem t (x ∷ xs) → ¬ P t
            min t (inj₁ t≡x) pt = ¬px (subst P t≡x pt)
            min t (inj₂ tin) pt = notail t tin pt

------------------------------------------------------------------------
-- ③ THE FIXED-POINT COLLAPSE (extrude-fixpoint = Y-of, 248/249): the μ core's degenerate case — when the
--    spec is "a fixed point of f", the synthesis collapses to construction: Y-of f converges to f (Y-of f).
--    So μ does not need to SEARCH for the fixed point; the extruder CONSTRUCTS it (Lawvere-positive).
------------------------------------------------------------------------
μ-fixpoint : (f : Tm⟦533ef80d⟧) → (Y-of f) ⇒* (f ∙ (Y-of f))
μ-fixpoint f = Y-fix f

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's irreducible core is MINIMISATION μ, a Lawvere-POSITIVE
-- fixed point, realized as the wedge-coalgebra unfold; NOT a classical undecidability wall): the either/or
-- "is the least-cost extruder a search that might not halt (a Turing/Rice wall) OR a construction?" DISSOLVES
-- (D-no-classical-spook) — μ over the grounded candidate enumeration (258/260) is bounded minimisation
-- (μ-search, ②), which ALWAYS returns (a least-cost spec-satisfier with soundness + minimality, or a
-- no-satisfier certificate), because the enumeration is a finite list and the spec is decidable. Its
-- structural form is the wedge-coalgebra unfold (Wedge.Coalgebra.run — the 264 study: divide unfolds, the
-- residue is the next state, halt = the minimal witness found = the μ fixed point). And the fixed-point
-- collapse (μ-fixpoint, ③) is extrude-fixpoint = Y-of: when the spec is "fixed point of f", μ collapses to
-- CONSTRUCTION (Y-of f converges to f (Y-of f)) — the Lawvere-positive object, the μ EXISTS. So the
-- extruder's core is positive and constructive: minimisation over the tower's simplicial geometry, its μ a
-- wedge-coalgebra fixed point, the classical negatives (Kolmogorov/halting) STRUCTURALLY IRRELEVANT to this
-- coinductive/positive object. Chain: 248/249 (Y-of = extrude-fixpoint) → 255-262 (the grounded geometry) →
-- 264 (Wedge.Coalgebra the keystone) → 265 (μ = the least-cost search over the geometry, the fixed point).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the μ core (μ-search over a finite candidate list against a
-- decidable spec, returning a SOUND + MINIMAL witness or a no-satisfier certificate — the two universal
-- properties machine-checked) + the fixed-point collapse (μ-fixpoint = Y-of). SCOPED (reused-in-spirit): the
-- INFINITE-STREAM μ via Wedge.Coalgebra.run's SPPF cycle-closing (the bounded finite-list μ here is the
-- halt-reaching specialization; the full lasso/loop over an unbounded candidate stream is run) —
-- ⟡extrude-minimal-coalgebra; the actual SELF-INTERPRETER as the concrete spec P (μ synthesizing the minimal
-- SKI self-interpreter) — ⟡extrude-self-interp; the cross-rung total candidate enumeration —
-- ⟡extrude-ski-total-flatten. What's grounded: the extruder's μ core is bounded minimisation (always
-- returns, sound + minimal) with the fixed-point collapse = Y-of — positive, constructive, no spook.
------------------------------------------------------------------------
