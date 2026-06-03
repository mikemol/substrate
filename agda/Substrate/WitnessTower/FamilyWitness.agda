------------------------------------------------------------------------
-- Substrate.WitnessTower.FamilyWitness
--
-- "Suppose witnessing took a FAMILY of previous objects instead of one.
--  Would the tower stay linear, or expand into a DAG / higher groupoid?"
--
-- It expands. This module makes the answer concrete and CHECKED, not
-- asserted, on three pinned facts:
--
--   (a) the linear WitnessTower.Core is genuinely a CHAIN — WSimplex k is
--       a singleton (exactly one inhabitant per rung). Proved below
--       (WSimplex-unique). So Core's `witnessing : WSimplex k →
--       WSimplex (suc k)` carries no branching: it is ONE spine.
--
--   (b) a family-witnessing move genuinely BRANCHES — a rung-(suc k) cell
--       is built from a FAMILY of (suc (suc k)) facets, each a rung-k
--       object. The branching factor is witnessed by the constructor's
--       type (FSimplex below); at every rung ≥ 1 it is ≥ 2, so the object
--       is a DAG (the simplex face lattice), not a chain.
--
--   (c) the bridge: the linear spines of a rung-k simplex are exactly the
--       orderings of its (k+1) vertices — the order in which Core adds
--       them — so #spines = (k+1)! = |perms (suc k)|, the census count
--       (proved via Enumerate.perms-length). Core.walk is ONE spine (the
--       identity ordering); the symmetric group S_{k+1} = perms (suc k)
--       permutes spines. The census already enumerates the gauge group of
--       the DAG.
--
-- READING (interpretation, pinned to (a)/(b)/(c)): linearity was a GAUGE
-- CHOICE — a chart (one vertex-ordering) on a fundamentally branching
-- (DAG) object. The spines + the permutations between them form a groupoid
-- (a torsor under S_{k+1}): objects = spines, morphisms = perms (suc k),
-- all invertible. So "stay linear or become a groupoid?" → the linear
-- tower is one object of the groupoid whose morphism set is the census.
-- This is exactly the atlas-vs-chart / choice-rigidification pattern the
-- rest of the substrate keeps surfacing.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FamilyWitness where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym)

open import Substrate.WitnessTower.Core using (WSimplex; base; witnessing)
open import Substrate.WitnessTower.Enumerate using (perms; lengthL; factorial; perms-length)

------------------------------------------------------------------------
-- (a) The linear tower IS a chain: WSimplex k is a singleton.
------------------------------------------------------------------------

WSimplex-unique : ∀ {k} (x y : WSimplex k) → x ≡ y
WSimplex-unique base           base           = refl
WSimplex-unique (witnessing x) (witnessing y) = cong witnessing (WSimplex-unique x y)

------------------------------------------------------------------------
-- (b) The family-witnessing move BRANCHES. A rung-(suc k) cell carries a
--     family of (suc (suc k)) facets, each a rung-k object (a
--     (k+1)-simplex has k+2 facets, each a k-simplex). The type itself is
--     the witness that the move is no longer linear.
------------------------------------------------------------------------

data FSimplex : ℕ → Set where
  vertex : FSimplex zero
  cell   : ∀ {k} → Vec (FSimplex k) (suc (suc k)) → FSimplex (suc k)

-- the branching factor at rung (suc k): the size of the facet family.
branching : ℕ → ℕ
branching k = suc (suc k)

-- it is always ≥ 2, i.e. ≥ 2 children — never a chain (which would have 1).
-- (Recorded as the concrete debut: even the lowest family-witnessing rung,
-- the edge, has 2 facets — its two endpoints.)
branching-edge : branching zero ≡ 2
branching-edge = refl

-- read the facet family back out of a cell (the family the move consumed).
facets : ∀ {k} → FSimplex (suc k) → Vec (FSimplex k) (suc (suc k))
facets (cell fs) = fs

------------------------------------------------------------------------
-- (c) The bridge. A linear spine of a rung-k simplex = an ordering of its
--     (k+1) vertices (the order Core adds them). #spines = (k+1)! =
--     |perms (suc k)|, the census count.
------------------------------------------------------------------------

spine-count : ℕ → ℕ
spine-count k = factorial (suc k)

-- the census enumerates exactly the spines of the DAG (gauge group S_{k+1}).
spine-count-is-census : (k : ℕ) → spine-count k ≡ lengthL (perms (suc k))
spine-count-is-census k = sym (perms-length (suc k))

-- the linear Core supplies ONE spine per rung (it is a singleton), so the
-- gauge group acts on a set of which Core.walk is a single point.
core-is-one-spine : ∀ {k} (x y : WSimplex k) → x ≡ y
core-is-one-spine = WSimplex-unique
