{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKINVertex — ⟡extrude-ski-nvertex: the GENERAL n-vertex form
-- of 255's ternary atom. The tower (WitnessTower.Core.WSimplex / FaceSet) builds n-vertex simplices
-- inductively; a VERTEX-FAMILY is an injective map (Fin n → Tm⟦533ef80d⟧) landing in NORMAL FORMS — the n vertices of
-- the rung-(n-1) simplex as distinct SKI combinators. The non-degeneracy (distinct vertices don't converge)
-- is the SIMPLICIAL vertex-distinctness at EVERY n, derived BY EXHAUSTION — 255's faces-dont-converge,
-- general. Positive object (the simplex) primary; the negatives its projections (no spook, D-no-classical).
--
-- The ternary atom (255, WitnessTower Z3, S/K/I) is the n=3 instance of THIS. The tower's inductive process
-- (WSimplex : ℕ → Set, base/witnessing; FaceSet's Face n = Vector (suc n)) is the geometry; this module
-- reuses its vertex-indexing (Fin) and lifts the non-degeneracy to all n.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY the VertexFamily record
-- (an injective NF-valued Fin n → Tm⟦533ef80d⟧) + nf-fixed + verts-dont-converge (distinct vertices ⟹ ¬Converge, by
-- exhaustion, general n) + the ternary instance (n=3, S/K/I). The framing ('the tower's simplicial geometry
-- at every n', 'every combinator NF a vertex') is (prose: the general form; a canonical enumeration of ALL
-- SKI NFs as an ω-vertex family is scoped — this gives the FINITE-n atom for any chosen NF-family).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKINVertex where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; Converge)

------------------------------------------------------------------------
-- a normal form only reduces to itself (positive; no decision):
------------------------------------------------------------------------
nf-fixed : {n : Tm⟦533ef80d⟧} → ({c : Tm⟦533ef80d⟧} → n ⇒ c → ⊥) → {c : Tm⟦533ef80d⟧} → n ⇒* c → n ≡ c
nf-fixed n-nf done    = refl
nf-fixed n-nf (s ◅ _) = ⊥-elim (n-nf s)

------------------------------------------------------------------------
-- ① THE n-VERTEX ATOM as a VERTEX-FAMILY: n vertices (Fin n), each projecting to a SKI term that is a
--    NORMAL FORM (vtx-normal) and the projection is INJECTIVE (vtx-inj — distinct vertices ⟹ distinct
--    terms). This is the rung-(n-1) simplex realized on SKI combinators (the tower's WSimplex vertices).
------------------------------------------------------------------------
record VertexFamily (n : ℕ) : Set where
  field
    vtx        : Fin n → Tm⟦533ef80d⟧
    vtx-normal : (i : Fin n) {c : Tm⟦533ef80d⟧} → vtx i ⇒ c → ⊥
    vtx-inj    : {i j : Fin n} → vtx i ≡ vtx j → i ≡ j

  -- ② THE NEGATIVES BY EXHAUSTION: distinct vertices DON'T CONVERGE — 255's lemma, general n. From NF-ness
  --    + injectivity; no CR, no decision, no spook. The non-degeneracy of the Converge-quotient at rung n.
  verts-dont-converge : {i j : Fin n} → (i ≡ j → ⊥) → Converge (vtx i) (vtx j) → ⊥
  verts-dont-converge {i} {j} i≢j (d , vi⇒*d , vj⇒*d) =
    i≢j (vtx-inj (trans (nf-fixed (vtx-normal i) vi⇒*d) (sym (nf-fixed (vtx-normal j) vj⇒*d))))

------------------------------------------------------------------------
-- ③ THE TERNARY ATOM (255) IS THE n=3 INSTANCE. vtx : Fin 3 → {S,K,I}. This exhibits 255 as rung 2 of the
--    general n-vertex process — the SKI observation quotient's non-degeneracy is the tower's simplicial
--    geometry, here at n=3, in general at every n.
------------------------------------------------------------------------
ski3 : VertexFamily 3
ski3 = record { vtx = v ; vtx-normal = v-nf ; vtx-inj = v-inj }
  where
    v : Fin 3 → Tm⟦533ef80d⟧
    v zero             = S
    v (suc zero)       = K
    v (suc (suc zero)) = I
    v-nf : (i : Fin 3) {c : Tm⟦533ef80d⟧} → v i ⇒ c → ⊥
    v-nf zero             ()
    v-nf (suc zero)       ()
    v-nf (suc (suc zero)) ()
    v-inj : {i j : Fin 3} → v i ≡ v j → i ≡ j
    v-inj {zero} {zero} _ = refl
    v-inj {suc zero} {suc zero} _ = refl
    v-inj {suc (suc zero)} {suc (suc zero)} _ = refl
    v-inj {zero} {suc zero} ()
    v-inj {zero} {suc (suc zero)} ()
    v-inj {suc zero} {zero} ()
    v-inj {suc zero} {suc (suc zero)} ()
    v-inj {suc (suc zero)} {zero} ()
    v-inj {suc (suc zero)} {suc zero} ()

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the SKI observation quotient's non-degeneracy is the tower's SIMPLICIAL
-- geometry at EVERY n: a vertex-family of distinct NF combinators is the rung-(n-1) simplex, and distinct
-- vertices don't converge BY EXHAUSTION — one lemma, all n): 255's ternary atom was rung 2; the either/or
-- "is the non-degeneracy a special 3-atom fact, or general?" bottoms out — GENERAL, and it is the tower's
-- INDUCTIVE n-vertex process (WSimplex/FaceSet) realized on SKI. A VertexFamily n (①) is n vertices as
-- distinct NF combinators; verts-dont-converge (②) derives ALL pairwise non-convergence at rung n BY
-- EXHAUSTION from NF-ness + injectivity — no CR, no decision, no Turing spook (D-no-classical-spook): the
-- negatives are projections of the ONE positive simplex. The ternary (③, ski3) is n=3. So the meaningful
-- confluence-based quotient (254/255) is non-degenerate on ANY finite NF-family, and its geometry is the
-- witness tower's — the substrate's own inductive atom, all the way up.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = VertexFamily n (the general n-vertex atom) + verts-dont-converge
-- (negatives by exhaustion, any n) + the ternary instance (ski3, n=3). SCOPED (no spook): a CANONICAL
-- ω-vertex enumeration of ALL SKI normal forms (every NF a vertex, the full tower colimit) — the general
-- form takes ANY finite NF-family; the specific enumeration + its injectivity is ⟡extrude-ski-nf-enum. The
-- literal WSimplex/FaceSet cone-indexing of the vertices (vs the Fin-index used here) is reused-in-spirit;
-- wiring vtx through FaceSet's Vector basis is ⟡extrude-ski-faceset. What's grounded: the non-degeneracy is
-- GENERAL (every n), by exhaustion, positive — the tower's simplicial geometry on SKI.
------------------------------------------------------------------------
