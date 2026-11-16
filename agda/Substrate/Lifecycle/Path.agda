------------------------------------------------------------------------
-- Substrate.Lifecycle.Path
--
-- Defines: LifecyclePath, _◂_, origin
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Path where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin

infixl 5 _◂_


------------------------------------------------------------------------
-- THE LIFECYCLE PATH: a datum's climb through the stage boundaries, with
-- the ORIENTATION recorded at each step.
--
-- ⚑ THIS IS `LehmerPath`'s SHAPE, DELIBERATELY (`WitnessTower.LehmerPath`:
-- `start` / `_◂_ : LehmerPath k → Fin (suc k) → LehmerPath (suc k)`). The
-- repo arrives at cons-list-indexed-by-position under four spellings —
-- `Chain` (ε/_▷_), `Pipe` ([]/_∷_), `LehmerPath` (start/_◂_), and the actor
-- chain — and this is that structure, not a fifth invention.
--
-- ⚑ THE DIGIT IS BOUNDED, AND THE BOUND IS THE CONTENT. At boundary k there
-- are `suc k` positions an actor may hold: it has drawn from upstream and
-- released some prefix downstream, so its residue ranges over `Fin (suc k)`.
-- Boundedness is exactly what `CertifiedWedge`'s `small : rem < b` bundles,
-- and what makes the decomposition UNIQUE (`recon-bounded-unique`) — hence
-- canonical, hence extractable.
--
-- ⚑ AND `insert-at` IS ORDER-SENSITIVE, SO NOTHING COMMUTES HERE. That is
-- the FREE side of the adjunction (`WitnessTower.Wedge.Simplicial` §2): each
-- step records a CHOICE, distinct choices give distinct results, and the
-- non-commutation IS the permutohedron. Forgetting the digits gives the
-- nerve, where the simplicial identities hold; the wedge hands them back.
-- A lifecycle path is the free side — the ordering of who released what,
-- when, is precisely what must not be forgotten.
------------------------------------------------------------------------

data LifecyclePath : ℕ → Set where
  origin : LifecyclePath zero
  _◂_    : ∀ {k} → LifecyclePath k → Fin (suc k) → LifecyclePath (suc k)
