{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Nerve — ⟡S2 BRIDGE (corrected). The repo ALREADY proves the general
-- simplicial machinery; this file must NOT re-derive it. Reachable-gate
-- findings (grep, before writing):
--   * WitnessTower.SimplicialBoundary.simplicial : the GENERAL-LENGTH face
--     identity  delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs)  (i ≤ j),
--     by list induction. (⟡S2-ind was NOT owed — already done.)
--   * CayleyDickson.Coboundary.d²-zero : δ³(δ²φ) ≡ false, the generic d²=0
--     over F₂ for every 2-cochain. (⟡S2-Z core was NOT owed — already done.)
--   * NO `nerve` of a monoid exists anywhere (grep empty). So the ONLY new
--     content of ⟡S2 is the NERVE's COMPOSE-FACE — the inner face d_i that
--     uses the monoid multiplication, which `delAt` (drop-only) cannot
--     express. That single fact = ASSOCIATIVITY. This file proves exactly
--     that and nothing the repo already has.
--
-- The ε-tower (window composition: assoc + ε unit, S5TwoFuel.T-compose) is
-- a monoid; its nerve's DROP-faces are the repo's `delAt` (inheriting
-- `simplicial`), and its COMPOSE-face is `mul` below (the new bit). Over F₂
-- the boundary cancellation is the repo's `d²-zero`. So the ε-tower is
-- simplicial by INSTANTIATION of existing machine-checked results + this one
-- associativity bridge.
------------------------------------------------------------------------

module Substrate.S5.S5Nerve where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong)

-- the window monoid (the structure T-compose checks for the runner). PINNED as
-- MonoidR: bundled M/_∙_/ε/laws — a distinct shape from Semigroup-based Algebra.Monoid.
record MonoidR : Set₁ where
  field
    M      : Set
    _∙_    : M → M → M
    ε      : M
    assoc  : (x y z : M) → ((x ∙ y) ∙ z) ≡ (x ∙ (y ∙ z))
    unitˡ  : (x : M) → (ε ∙ x) ≡ x
    unitʳ  : (x : M) → (x ∙ ε) ≡ x

module NerveComposeFace (Mon : MonoidR) where
  open MonoidR Mon

  -- The nerve's INNER (compose) face at an adjacent pair. `delAt` handles the
  -- OUTER faces (drop-first, drop-last) and the repo's `simplicial` gives
  -- their identity; this is the ONE face `delAt` cannot express.
  mul : M → M → M
  mul a b = a ∙ b

  -- THE ⟡S2 CONTENT: the compose-face simplicial coincidence = associativity.
  -- Two nested inner faces on [a,b,c] reach the fully-composed 0-face by two
  -- routes; they agree iff the monoid is associative. This is the exact
  -- content `delAt`'s drop-only identity omits, and it is the whole reason
  -- the ε-tower's nerve is simplicial.
  compose-face-id : (a b c : M) → mul (mul a b) c ≡ mul a (mul b c)
  compose-face-id = assoc

  -- ε is the degeneracy's inserted unit (both adjacencies), from the unit laws.
  degen-collapseˡ : (x : M) → mul ε x ≡ x
  degen-collapseˡ = unitˡ

  degen-collapseʳ : (x : M) → mul x ε ≡ x
  degen-collapseʳ = unitʳ
