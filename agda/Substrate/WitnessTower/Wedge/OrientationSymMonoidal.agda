------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSymMonoidal
--
-- ⟡rig-UP-cat (the Set₀ capstone) — ⊕ and ⊗ as the TWO INSTANCES of ONE GradedSymMonoidal
-- bundle. The endpoint of the whole lift arc: every decomposition-free invariant we built
-- (GradedProductOver, its associator, GradedBraid, GradedBraidNatural, GradedBifunctor)
-- collects into a single "graded symmetric monoidal structure" record, and the additive and
-- multiplicative halves of the graded Lehmer rig differ ONLY in the grading monoid —
-- (ℕ,+,0) on the code side (LehmerPath, readout lookup∘decode) vs (ℕ,·,1) on the vector
-- side (Perm, readout lookup).
--
--   ⊕-symmon : GradedSymMonoidal _+_ 0 LehmerPath +-assoc (lookup ∘ decode)
--   ⊗-symmon : GradedSymMonoidal _*_ 1 Perm       *-assoc  lookup
--
-- Both are pure ASSEMBLY of already-proven values — the capstone certifies, in one object,
-- that the orientation rig has the full symmetric-monoidal structure on each fibre.
--
-- SCOPE (honest): this bundles the two MONOIDAL structures. The full RIG additionally carries
-- the distributor δ and the 5 Laplaza coherences (OrientationDistributor / DistributorAssoc,
-- proven + numpy-verified this arc) — a further pure-assembly step. NOT here, and NOT the
-- Set₁ categorical universal property (initiality among symmetric rig categories, which
-- quantifies over category-targets — a grade-collapse the mission refuses), nor the deep
-- Set₀ wreath-initiality (the unique map coupling fold with the Coxeter-word hom).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSymMonoidal where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; decode)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedSymMonoidal)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties
  using (⊕-over; ⊗-over; ⊕-assoc-over; ⊗-assoc-over;
         ⊕-braid; ⊗-braid; ⊕-braid-nat; ⊗-braid-nat)
open import Substrate.WitnessTower.Wedge.OrientationBifunctor using (⊕-bifunctor; ⊗-bifunctor)

-- ⊕: the additive graded symmetric monoidal structure (code side, LehmerPath).
⊕-symmon : GradedSymMonoidal _+_ 0 LehmerPath +-assoc (λ l → lookup (decode l))
⊕-symmon = record
  { product   = ⊕-over
  ; prodAssoc = ⊕-assoc-over
  ; braiding  = ⊕-braid
  ; braidNat  = ⊕-braid-nat
  ; bifunctor = ⊕-bifunctor
  }

-- ⊗: the multiplicative graded symmetric monoidal structure (vector side, Perm).
⊗-symmon : GradedSymMonoidal _*_ 1 Perm *-assoc lookup
⊗-symmon = record
  { product   = ⊗-over
  ; prodAssoc = ⊗-assoc-over
  ; braiding  = ⊗-braid
  ; braidNat  = ⊗-braid-nat
  ; bifunctor = ⊗-bifunctor
  }
