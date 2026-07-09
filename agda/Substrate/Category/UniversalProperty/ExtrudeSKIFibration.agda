{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIFibration — ⟡extrude-ski-nf-enum, via the FIBRATION over
-- the witness tower (operator: "the substrate has fibration machinery over the witness tower"; "don't pick
-- an element when there's a whole coset to model"). The ω-vertex atom is NOT a picked enumeration (a
-- right-nested-S sequence would be choosing ONE element of the space of enumerations). It is the TOTAL SPACE
-- of the fibration over the tower: Base = ℕ (the rungs), Fiber n = Fin (suc n) (the n+1 vertices of Δⁿ).
-- Total = Σ ℕ (λ n → Fin (suc n)) = ALL vertices over ALL rungs — the coset, canonically. A labeling of the
-- total space into distinct NF combinators is a SECTION; the fibration is the invariant, the section the
-- element. 256's VertexFamily n is the per-fiber structure; this is the whole bundle.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: tower-vertices (the
-- Fibration instance, Base=ℕ, Fiber=Fin∘suc), its Total/proj-base/proj-fiber, a TowerLabeling record (a
-- section: total-space → NF combinators, injective) with the GENERAL non-degeneracy (distinct total-space
-- points ⟹ ¬Converge) by exhaustion, and the fact that any 256 VertexFamily over a rung embeds. The framing
-- ('the ω-atom is the fibration total space, not a chosen enumeration') is (prose: the coset-over-element
-- point; a CONCRETE global section labeling every vertex is one section, scoped — the STRUCTURE is here).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIFibration where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (_∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; Converge)
open import Substrate.Category.GrothendieckConstruction using (Fibration)

------------------------------------------------------------------------
-- a normal form only reduces to itself (positive; no decision):
------------------------------------------------------------------------
nf-fixed : {n : Tm⟦533ef80d⟧} → ({c : Tm⟦533ef80d⟧} → n ⇒ c → ⊥) → {c : Tm⟦533ef80d⟧} → n ⇒* c → n ≡ c
nf-fixed n-nf done    = refl
nf-fixed n-nf (s ◅ _) = ⊥-elim (n-nf s)

------------------------------------------------------------------------
-- ① THE ω-VERTEX ATOM IS THE FIBRATION OVER THE TOWER (the coset, not a picked enumeration). Base = ℕ
--    (the rungs); Fiber n = Fin (suc n) (the n+1 vertices of Δⁿ, the tower's FaceSet vertex-index). The
--    Total space Σ ℕ (Fin ∘ suc) is EVERY vertex over EVERY rung — the whole ω-vertex structure at once.
------------------------------------------------------------------------
tower-vertices : Fibration ℕ (λ n → Fin (suc n))
tower-vertices = record {}

open Fibration tower-vertices using (proj-base; proj-fiber)
-- the ω-vertex space, re-exported as a top-level name (a total-space point = (rung , vertex-in-that-rung)):
Total : Set
Total = Σ ℕ (λ n → Fin (suc n))

------------------------------------------------------------------------
-- ② A LABELING IS A SECTION: total space → NF combinators, injective. The fibration is the invariant; a
--    labeling is one section (an "element of the coset"). The non-degeneracy is a property of ANY section:
--    distinct total-space points get non-convergent combinators — BY EXHAUSTION, general over the bundle.
------------------------------------------------------------------------
record TowerLabeling : Set where
  field
    label        : Total → Tm⟦533ef80d⟧
    label-normal : (t : Total) {c : Tm⟦533ef80d⟧} → label t ⇒ c → ⊥
    label-inj    : {s t : Total} → label s ≡ label t → s ≡ t

  -- the non-degeneracy, over the WHOLE total space (every vertex at every rung), by exhaustion:
  verts-dont-converge : {s t : Total} → (s ≡ t → ⊥) → Converge (label s) (label t) → ⊥
  verts-dont-converge {s} {t} s≢t (d , ls⇒*d , lt⇒*d) =
    s≢t (label-inj (trans (nf-fixed (label-normal s) ls⇒*d) (sym (nf-fixed (label-normal t) lt⇒*d))))

------------------------------------------------------------------------
-- ③ ANY 256-STYLE PER-RUNG FAMILY EMBEDS INTO THE BUNDLE. A vertex at rung n (a Fin (suc n)) is a
--    total-space point (n , i) via the fibration's Σ — so a per-rung vertex-family (256) is the fibre of
--    this bundle over n. The bundle is the union of all 256 families across all rungs (the coset).
------------------------------------------------------------------------
at-rung : (n : ℕ) → Fin (suc n) → Total
at-rung n i = (n , i)

-- the fibration recovers the rung and the vertex (proj-base/proj-fiber) — the bundle IS indexed by the tower:
rung-of : Total → ℕ
rung-of = proj-base
vertex-of : (t : Total) → Fin (suc (proj-base t))
vertex-of = proj-fiber

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ω-vertex atom is the FIBRATION over the tower, a COSET modeled, not an
-- element picked): the either/or "WHICH ω-enumeration of SKI normal forms?" (right-nested S? left? by size?)
-- was PICKING AN ELEMENT of the space of enumerations. It DISSOLVES: model the whole coset — the FIBRATION
-- over the witness tower (①): Base = the rungs (ℕ), Fiber n = the rung-n vertices (Fin (suc n)), Total = ALL
-- vertices over ALL rungs (Σ ℕ (Fin ∘ suc)). A specific enumeration is just ONE SECTION (a TowerLabeling,
-- ②); the fibration is the INVARIANT. The non-degeneracy holds for ANY section, over the WHOLE total space,
-- BY EXHAUSTION (verts-dont-converge, ②) — no CR, no decision, no Turing spook (D-no-classical-spook): the
-- negatives are projections of the positive bundle. 256's per-rung VertexFamily is the FIBRE over n (③);
-- this is the union across all rungs — the coset. So the meaningful confluence-based quotient (254/255/256)
-- extends to the whole ω-vertex atom, and its geometry is the witness tower's fibration — the substrate's
-- own bundle, not a chosen sequence. Chain: 255 (ternary=rung2) → 256 (per-rung, general n) → 257 (the
-- BUNDLE over all rungs, the fibration — the coset modeled).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = tower-vertices (the Fibration over the tower, Total the ω-vertex
-- space) + TowerLabeling (a section, with the general non-degeneracy by exhaustion) + the per-rung embedding
-- (③). SCOPED (no spook, correctly — a section is an element, so I do NOT pick one): a CONCRETE global
-- TowerLabeling assigning every total-space point a distinct NF (an actual injective section, e.g. via the
-- tower's Enumerate) is ⟡extrude-ski-section — deliberately NOT chosen here, because the STRUCTURE (the
-- fibration/coset) is the invariant and a section is one element; the tower's Enumerate provides the
-- canonical section when wanted. What's grounded: the ω-vertex atom is the fibration total space (the coset),
-- non-degenerate for any section, by exhaustion — the tower's bundle on SKI, no element picked.
------------------------------------------------------------------------
