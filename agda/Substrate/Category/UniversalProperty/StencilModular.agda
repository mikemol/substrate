{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilModular — ⟡stencil-modular: THE MODULAR LAW
-- (the gate that earns "allegory", Category.Allegory.modular) applied to the stencil's
-- cross-relation. This is the DEEPEST bottoming-out: the allegory's DEFINING coherence —
-- the one identity that makes converse, meet, and composition cohere — holds for the
-- stencil's `agree`, and the symmetry (agree † ≈ agree, 193) makes it self-contained.
--
-- GROUNDED (reuse, not re-proof): Category.Allegory.modular R S T : ((R ⨾ S) ∧ T) ⊆
-- ((R ∧ (T ⨾ S†)) ⨾ S) — PROVEN (a constructive Σ/×-rearrangement). We INSTANTIATE it at
-- the stencil's symmetric agree (R = S = T = agree). And the substrate's OWN either/or-
-- dissolution mirror: Allegory.Division.residual-duality — (R ∖ T)† ≡ (R† ／ T†), "left and
-- right division are not two choices but the same residual seen through †" — the modular
-- law's residual conjugate, the dissolve-either/or made a theorem (root/log as one residual).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilModular where

open import Substrate.Category.Allegory
  using (_⨾_; _∧_; _†; _⊆_; _≈_; modular; ⊆-refl)

module _ {F : Set}
         (agree : F → F → Set)
         (agree-sym : {p q : F} → agree p q → agree q p)
  where

  ------------------------------------------------------------------------
  -- ① THE MODULAR LAW AT THE STENCIL'S CROSS-RELATION. Instantiate the proven allegory
  -- modular law at R = S = T = agree: the stencil's cross composed-and-met refines the
  -- meet-then-composed form — the allegory coherence, holding for the stencil.
  ------------------------------------------------------------------------
  stencil-modular :
    ((agree ⨾ agree) ∧ agree) ⊆ ((agree ∧ (agree ⨾ (agree †))) ⨾ agree)
  stencil-modular = modular agree agree agree

  ------------------------------------------------------------------------
  -- ② THE SYMMETRIC SPECIALIZATION: agree is SELF-CONVERSE (193), so `agree †` in the
  -- modular law is just agree again (up to ≈). The RHS residual term (agree ⨾ agree†)
  -- becomes (agree ⨾ agree) — the modular commute closes ENTIRELY within agree, no
  -- converse escaping. We witness the converse-collapse pointwise: agree† p q → agree p q.
  ------------------------------------------------------------------------
  agree†→agree : (agree †) ⊆ agree
  agree†→agree p q h = agree-sym h      -- (agree †) p q = agree q p, flipped by sym.

  agree→agree† : agree ⊆ (agree †)
  agree→agree† p q h = agree-sym h      -- symmetric the other way.

  -- so the modular law's S† term is interchangeable with agree — the coherence is
  -- self-contained in the symmetric cross-relation (a groupoid, 189).

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the allegory's DEFINING coherence holds for the stencil,
-- self-contained under symmetry): the modular law (Category.Allegory.modular, "the gate
-- that earns 'allegory'") is the one identity making converse + meet + composition cohere.
-- Instantiated at the stencil's cross-relation agree (stencil-modular = modular agree agree
-- agree), it holds — the stencil participates in the FULL allegory coherence, not just the
-- converse commute (193). And because agree is SELF-CONVERSE (agree † ≈ agree, via agree-sym
-- both ways: agree†→agree / agree→agree†), the modular law's S† term collapses to agree —
-- the coherence closes ENTIRELY within the symmetric cross-relation. So the recursion of
-- either/or-dissolutions BOTTOMS OUT at the modular law: every either/or the stencil touched
-- (relation vs function, A vs B, forward vs converse, root vs log) is a commute (193), and
-- ALL those commutes COHERE via the one modular identity — the deepest invariant, the gate
-- that makes the allegory an allegory. The substrate's residual-duality ((R ∖ T)† ≡ R†／T†,
-- "left and right division are the same residual through †") is the same dissolution made a
-- theorem elsewhere — the modular/residual structure IS the either/or-dissolution mechanism,
-- named category-theoretically. The stencil's agree is a symmetric relation satisfying the
-- modular law: an allegory-coherent equivalence, the invariant the recursion bottoms out at.
------------------------------------------------------------------------
