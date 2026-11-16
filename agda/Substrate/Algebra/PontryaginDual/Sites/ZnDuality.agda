------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.ZnDuality
--
-- ℤ/(suc n) AS AN LCA GROUP, AND THE DUALITY THEOREM AT THAT SITE.
--
-- `Sites/Zn` supplies the dual OPERATIONS; `Sites/ZnLaws` proves them an
-- AbelianGroup.  Those were the two things `LocallyCompactAbelian` needed and
-- did not have — its `abelian-group` field was UNINHABITABLE for this carrier
-- until the laws existed, which is why the site had a PontryaginDual instance
-- but no LCA instance.  Both land here.
--
-- ⚑ WHAT IS PROVED VS WHAT IS STRUCTURAL, STATED UP FRONT — because the
-- neighbouring site records exactly this overclaim as its own history.
-- `TopologicalGroup/Sites/V4.agda:9-16` documents that it once carried *"prose
-- OVERCLAIMING a TopologicalGroup bridge … while inhabiting nothing"*.  So, for
-- this module, precisely:
--
--   * `Zn-TopologicalGroup` is HONEST BUT CHEAP.  `TopologicalGroup`'s only
--     field is `group` (the topology is a documented marker, not data), so
--     inhabiting it is real but discharges no topological obligation.  The
--     discreteness of ℤ/n is asserted by the record's design, not proved here.
--     Same shape as `V4-TopologicalGroup`, deliberately.
--   * `Zn-LCA` is the SUBSTANTIVE one: its `abelian-group` field is
--     `Zn-AbelianGroup`, six discharged axioms, and it could not have been
--     written before them.
--   * `Zn-Self-Duality` is proved for the SELF-DUAL CHOICE of double-dual
--     carrier, and that choice is the theorem's PARAMETER, not a fact this
--     module establishes — see the note on it below.
--
-- ⚑ THE DUALITY THEOREM'S CONTENT HERE IS NARROWER THAN ITS NAME.
-- `PontryaginDualityTheorem` takes `DoubleDual` as a MODULE PARAMETER and asks
-- for a bijection `A ≅ DoubleDual`.  For ℤ/n the substrate identifies a
-- character with its frequency index (`Sites/Zn.agda:36-38`), so the double
-- dual carrier IS `Fin (suc n)` and the canonical evaluation pairing
-- `a ↦ (χ ↦ χ a)` becomes the identity on indices.  The roundtrips are
-- therefore `refl` — and that is not a triviality being dressed up: it is the
-- theorem's real content AT THIS INSTANTIATION, namely that the
-- index-identification is coherent.  What is NOT proved here is that this
-- carrier choice is forced; supplying `DoubleDual` is the consumer's job by
-- construction (⟡set1-paydown made it a parameter), so a different choice
-- would need a different witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.ZnDuality where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.TopologicalGroup
open import Substrate.Algebra.PontryaginDual
open import Substrate.Algebra.PontryaginDual.Sites.Zn
open import Substrate.Algebra.PontryaginDual.Sites.ZnLaws
open import Substrate.Foundation.Eq

------------------------------------------------------------------------
-- 1. ℤ/(suc n) as a topological group (discrete).
--
-- The group is the proved `Zn-Group`; the topology is the trivial discrete
-- marker.  Follows `TopologicalGroup/Sites/V4` exactly.
------------------------------------------------------------------------

Zn-TopologicalGroup : (n : ℕ) → TopologicalGroup (Fin (suc n))
Zn-TopologicalGroup n = record { group = Zn-Group n }

------------------------------------------------------------------------
-- 2. ℤ/(suc n) as a locally compact abelian group.
--
-- ⚑ THIS IS THE RUNG THAT WAS MISSING.  `LocallyCompactAbelian` needs BOTH an
-- `AbelianGroup` and a `TopologicalGroup`; the site had neither until Ⓩ1, so
-- `ℤ/n-as-Self-Dual` sat in the tree as a `PontryaginDual` whose underlying
-- group was never exhibited as LCA — the input the duality theorem takes.
------------------------------------------------------------------------

Zn-LCA : (n : ℕ) → LocallyCompactAbelian (Fin (suc n))
Zn-LCA n = record
  { abelian-group = Zn-AbelianGroup n
  ; topology      = Zn-TopologicalGroup n
  }

------------------------------------------------------------------------
-- 3. The duality theorem at the self-dual carrier.
--
-- Chars = DoubleDual = A = Fin (suc n): the substrate identifies a character
-- with its frequency index, so the evaluation pairing is the identity on
-- indices and both roundtrips hold definitionally.
------------------------------------------------------------------------

Zn-Self-Duality : (n : ℕ) →
                  PontryaginDualityTheorem
                    (Fin (suc n)) (Fin (suc n))
                    (Fin (suc n)) (Fin (suc n))
                    (Zn-LCA n) (ℤ/n-as-Self-Dual n)
Zn-Self-Duality n = record
  { to      = λ a → a
  ; from    = λ d → d
  ; to-from = λ _ → refl
  ; from-to = λ _ → refl
  }
