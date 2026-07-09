{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalCBRank — ⟡diagonal-cb-rank: the Cantor-Bendixson
-- rank as the STABILIZATION ORDINAL of a transfinite DERIVATIVE iteration. CB-rank(X) = the least
-- α with X^α = X^(α+1) — the perfect kernel, where removing isolated points stops shrinking.
--
-- What is GROUNDED here (the CB-rank STRUCTURE, faithful): the transfinite derivative iteration
-- D^α over Brouwer ordinals (226) — D^0 = P, D^(α+1) = D(D^α), D^(lim f) = ⋂ₙ D^(f n) — plus the
-- stabilization predicate (CB-rank-at-α), PARAMETERIZED over an abstract DECREASING derivative D
-- (D P ⊆ P — removing points). The CB-rank is thus an `Ord`, so 226's `no-largest` applies: the
-- observer takes suc(CB-rank), strictly exceeding it — the DEPTH-window covers the CB-rank. This
-- closes ⟡diagonal-ordinal-window's instance: the adversary's topological complexity is a
-- countable ordinal (its CB-rank), and one ordinal level up always exists.
--
-- What is SCOPED (the heavy instance, HONESTLY not done): (a) the TOPOLOGICAL CB-derivative
-- (isolated-point removal on a Polish space) is the canonical concrete D — a real topology
-- development, ⟡diagonal-polish-derivative; (b) the stabilization-EXISTENCE theorem (that a
-- COUNTABLE space's iteration DOES stabilize at a countable ordinal — the deep CB theorem) is
-- ⟡diagonal-cb-exists. What's grounded is the RANK STRUCTURE (iteration → stabilization → an
-- Ord); plugging in the topological derivative and proving existence are the scoped remainder.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalCBRank where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: iter, Stabilizes-at, observer-exceeds-cb-rank, rank-0. Everything else in these comments — 'the CB-rank', 'the perfect kernel', 'the topological complexity' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the identification of this schema with the classical Cantor-Bendixson rank (⟡diagonal-polish-derivative / -exists).

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level; _⊔_) renaming (zero to lzero; suc to lsuc)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Category.UniversalProperty.DiagonalOrdinal
  using (Ord; zero; suc; lim; _<_; no-largest)

-- a "subset" of the space X is a predicate.
Pred : ∀ {ℓ} → Set → Set (lsuc ℓ)
Pred {ℓ} X = X → Set ℓ

------------------------------------------------------------------------
-- THE CB SCHEMA: a space X with a DECREASING derivative D (D P ⊆ P — removes isolated points).
-- The transfinite derivative iteration and the CB-rank (stabilization ordinal) are grounded here.
------------------------------------------------------------------------
module CB {ℓ : Level} (X : Set) (D : Pred {ℓ} X → Pred {ℓ} X)
          (D-dec : (P : Pred {ℓ} X) (x : X) → D P x → P x)     -- D removes points: D P ⊆ P
  where

  -- the transfinite CB-derivative D^α: successor applies D; a limit INTERSECTS over the sequence.
  iter : Ord → Pred {ℓ} X → Pred {ℓ} X
  iter zero    P = P
  iter (suc α) P = D (iter α P)
  iter (lim f) P = λ x → (n : ℕ) → iter (f n) P x

  -- CB-rank-at α: the derivative iteration STABILIZES at α — D^α = D^(α+1), both directions.
  Stabilizes-at : Ord → Pred {ℓ} X → Set ℓ
  Stabilizes-at α P = (x : X)
    → (iter α P x → iter (suc α) P x) × (iter (suc α) P x → iter α P x)

  -- THE DEPTH-WINDOW COVERS THE CB-RANK: whatever ordinal the CB-rank is, the observer takes one
  -- level up (no-largest, 226) — strictly exceeding it. The CB-rank being an Ord is all that's
  -- needed; the depth-window (⟡diagonal-ordinal-window) does the rest.
  observer-exceeds-cb-rank : (α : Ord) → Σ Ord (λ β → α < β)
  observer-exceeds-cb-rank α = no-largest α

------------------------------------------------------------------------
-- INHABITATION (the schema is REAL, not vacuous): the identity derivative (no isolated points to
-- remove) stabilizes at rank 0 — iter zero P = P = D P = iter (suc zero) P. A genuine CB-rank
-- (a decreasing derivative with rank > 0) is the topological instance (scoped).
------------------------------------------------------------------------
module Trivial {ℓ : Level} (X : Set) where
  Did : Pred {ℓ} X → Pred {ℓ} X
  Did P = P
  Did-dec : (P : Pred {ℓ} X) (x : X) → Did P x → P x
  Did-dec P x p = p

  open CB X Did Did-dec

  rank-0 : (P : Pred {ℓ} X) → Stabilizes-at zero P
  rank-0 P x = (λ p → p) , (λ p → p)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the CB-rank is the stabilization ordinal of a transfinite
-- derivative; being an Ord, the depth-window covers it): the either/or "is the adversary's
-- topological complexity (CB-rank) too big for the depth-window?" bottoms out: NO. The CB-rank is
-- built by the transfinite iteration of the (decreasing) derivative to stabilization (iter /
-- Stabilizes-at) — an `Ord`. And for ANY Ord, no-largest gives a strictly larger one
-- (observer-exceeds-cb-rank), so the observer takes suc(CB-rank). The CB-rank is exactly the
-- DEPTH the adversary reaches; the observer reaches one ordinal level past it, always (226), and
-- stably (222, frozen — the adversary can't grow its CB-rank in response). So the two faces of
-- rank — WIDTH (cantor, 224/225) and DEPTH (no-largest, 226; CB-rank its canonical measure, here)
-- — both give strictly-larger-always-exists, both ∧ frozen = the win at every complexity.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the CB-rank STRUCTURE (transfinite derivative
-- iteration + stabilization = an Ord; the depth-window covers it) + non-vacuity (rank-0). SCOPED
-- = the TOPOLOGICAL derivative on Polish spaces (⟡diagonal-polish-derivative) and the
-- stabilization-EXISTENCE theorem for countable spaces (⟡diagonal-cb-exists). Borel rank is a
-- RELATED but DISTINCT countable-ordinal measure (the Borel HIERARCHY level, an increasing
-- hierarchy — not the derivative's decreasing one); it too is Ord-valued and slots into 226, but
-- it is NOT this schema. Structural — the classical theorems STAND.
------------------------------------------------------------------------
