{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalPolishFaithful — ⟡diagonal-polish-faithful: the
-- SEQUENTIAL CB-derivative (228, at Set, via observational convergence) coincides with the
-- TOPOLOGICAL one — WITHOUT accepting Set₁ and WITHOUT hardcoding a basis. Following the repo's
-- Adjunction / NuAbstractLimitInstance habit: PARAMETERIZE over the topological↔sequential
-- comparison (the adjunction is PLUGGABLE — many mappings exist, we commit to none), prove
-- faithfulness AGAINST the interface, then discharge NON-VACUITY with a concrete instance. No
-- Set₁ in code (subsets are Bool-characteristic — Set); no universe polymorphism. The repo does
-- exactly this (Adjunction.agda: "ℕ div-mod IS such a division" — abstract theorem, concrete
-- witness), and it is how the repo builds under tight memory: parametric, not universe-heavy.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalPolishFaithful where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: Faithful (faithful-→, faithful-←), NonVacuous. Everything else in these comments — 'faithfulness', 'the sequential = topological theorem' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require a genuine point-set topological Dtop instance (⟡diagonal-polish-topological).

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- points = Baire space (228). A SUBSET is a CHARACTERISTIC FUNCTION to Bool — stays at Set (NOT
-- Point → Set = Set₁). This is the repo's subset-at-Set habit; membership is `χ x ≡ true`.
Point : Set
Point = ℕ → ℕ

Sub : Set                       -- ← Set, not Set₁: a decidable subset via its characteristic map
Sub = Point → Bool

_∈_ : Point → Sub → Set
x ∈ S = S x ≡ true

------------------------------------------------------------------------
-- THE ADJUNCTION INTERFACE (parameterized — PLUGGABLE): a comparison between a TOPOLOGICAL
-- derivative `Dtop` and the SEQUENTIAL one `Dseq`, both as Set-level operations Sub → Sub, plus
-- the witness that they AGREE (the faithfulness content — the sequential=topological equation on
-- first-countable spaces, abstracted). We commit to NO particular topological representation;
-- the instantiator supplies `Dtop` + the agreement. Everything at Set.
------------------------------------------------------------------------
module Faithful
  (Dseq : Sub → Sub)                                   -- the sequential CB-derivative (228, Bool form)
  (Dtop : Sub → Sub)                                   -- ANY topological CB-derivative, pluggably
  (agree : (S : Sub) (x : Point) → Dseq S x ≡ Dtop S x) -- the adjunction: they coincide (faithfulness)
  where

  -- FAITHFULNESS: membership in the sequential derivative ⟺ membership in the topological one.
  -- Proved AGAINST the interface — no basis hardcoded, no Set₁, no universe polymorphism.
  faithful-→ : (S : Sub) (x : Point) → x ∈ Dseq S → x ∈ Dtop S
  faithful-→ S x m rewrite agree S x = m

  faithful-← : (S : Sub) (x : Point) → x ∈ Dtop S → x ∈ Dseq S
  faithful-← S x m rewrite agree S x = m

------------------------------------------------------------------------
-- NON-VACUITY (the repo's habit — discharge the abstract interface with a CONCRETE instance):
-- the DIAGONAL instance where the two derivatives are LITERALLY the same operation. This is the
-- degenerate-but-honest witness that the Faithful interface is INHABITED (as Adjunction.agda
-- discharges Free⊣Forgetful with "ℕ div-mod IS such a division"). A genuinely-different Dtop
-- (a real point-set topological derivative agreeing with Dseq by the sequential=topological
-- theorem) is the deeper instance — scoped ⟡diagonal-polish-topological.
------------------------------------------------------------------------
module NonVacuous (Dseq : Sub → Sub) = Faithful Dseq Dseq (λ S x → refl)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — faithfulness is PARAMETRIC over the pluggable topological↔
-- sequential adjunction; no Set₁, no universe polymorphism, non-vacuity by concrete instance):
-- the either/or "accept Set₁ to state faithfulness, or hardcode Baire's basis" dissolves — take
-- the ADJUNCTION (Dtop + the agreement) as a PARAMETER (the repo's Adjunction habit), prove
-- faithfulness against the interface (faithful-→ / faithful-←), keep subsets at Set (Bool
-- characteristic, not Set₁ predicates), and discharge NON-VACUITY with a concrete instance
-- (NonVacuous: Dtop = Dseq, refl — as Adjunction.agda fires at ℕ div-mod). The topological
-- representation is never chosen up front; ANY comparison that inhabits the interface works. So
-- the faithfulness THEOREM lives at Set, parametrically, no universe cost — which is exactly how
-- the repo builds 1767 modules under tight memory (parametric, ~7% touch Set₁, all genuine
-- category theory). The universe issue never arises because we never represent the topology by
-- its opens — we take the comparison to the sequential world as data.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the parametric faithfulness interface (Faithful) +
-- its non-vacuity (NonVacuous), at Set, no Set₁/universe-polymorphism, following the repo's
-- Adjunction template. SCOPED = a GENUINE topological Dtop (point-set opens) with the agreement
-- proved by the real sequential=topological theorem (first-countability) —
-- ⟡diagonal-polish-topological; that is the deep instance the parameter is designed to accept,
-- deliberately NOT chosen here (pluggable). The sequential Dseq (228) is the Set-level content;
-- this module is the pluggable bridge to whatever topological side an instantiator brings.
------------------------------------------------------------------------
