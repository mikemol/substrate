------------------------------------------------------------------------
-- Substrate.WitnessTower.FaithfulnessBridge
--
-- A DISCOVERABILITY BRIDGE with LOAD-BEARING content. "A permutation /
-- group element is DETERMINED BY ITS ACTION" (faithfulness) is proven in
-- several places under names that don't cross-reference; this author kept
-- re-proving it locally before finding each pre-existing copy. This file is
-- the search anchor: search "faithful" / "determined by action" / "row-inj"
-- / "apply-injective" / "extract-s inverts" and land here.
--
-- The witnesses it bridges:
--   (T) Tower, EVERY rung:  SnGroup.apply-injective
--         {n} → (∀ i → apply σ i ≡ apply τ i) → σ ≡ τ.   [Vec rep, all n]
--   (S) Symmetric setoid:   Groups.Symmetric._≈_ IS (∀ x → apply σ x ≡
--         apply τ x) by DEFINITION — determinacy is the setoid relation.
--   (X) S4-Iso recovery:    Groups.S4-Iso.Extract.extract-s-from is the
--         INVERSE of the canonical S₃-on-V₄ action: reading the action on
--         α,β and running extract-s-from returns the canonical element.
--   (R) this author's row-inj (Actions.S3-on-V4.CanonicalFaithful): the six
--         canonical S₃ rows separated by their action on {α,β}. Its content
--         IS (X): "separated by action" = "extract-s recovers the element".
--
-- The load-bearing lemmas below (all `refl`) prove (X): extract-s-from
-- inverts act-on-canonical on each of the six canonical rows. That is the
-- machine-checked "these are the same machinery" — my row-inj's separation
-- and S4-Iso's extract-s recovery are one fact, computing definitionally.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FaithfulnessBridge where

open import Substrate.Groups.Z2.Gen
open import Substrate.Groups.Z3.Gen
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.SnGroup using (apply; apply-injective)

open import Substrate.Groups.V4.Bijection using (α; β)
open import Substrate.Groups.Z2.A
open import Substrate.Groups.Z3.A
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)


open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.S4-Iso.Extract using (extract-s-from)
open import Substrate.Axes.AxisOfV using (axis-of-v)

------------------------------------------------------------------------
-- (T) The concept, named once at rung n: determined-by-action ⇒ equal.
-- This IS apply-injective, re-exported under a searchable name.
------------------------------------------------------------------------

DeterminedByAction : {n : ℕ} → Perm n → Perm n → Set
DeterminedByAction {n} σ τ = (i : Fin n) → apply σ i ≡ apply τ i

faithful-tower : {n : ℕ} {σ τ : Perm n} → DeterminedByAction σ τ → σ ≡ τ
faithful-tower = apply-injective

------------------------------------------------------------------------
-- (X) The LOAD-BEARING bridge: extract-s-from (S4-Iso's recovery) is the
-- inverse of the canonical S₃-on-V₄ action. Reading act-on-canonical on the
-- two involutions α,β and recovering via extract-s-from returns the original
-- canonical (Z₃-word, Z₂-word). Proven for all six canonical rows, each by
-- refl (definitional). This identifies row-inj's "separated by action" with
-- S4-Iso's "extract-s recovers" — the same faithfulness, computing.
------------------------------------------------------------------------

recover : Word Gen₃ → Word Gen₂ → _
recover n h = extract-s-from (axis-of-v (act-on-canonical n h α))
                             (axis-of-v (act-on-canonical n h β))

extract-inverts-id  : recover [] [] ≡ ([] , [])
extract-inverts-id  = refl

extract-inverts-r   : recover (a₃ ∷ []) [] ≡ (a₃ ∷ [] , [])
extract-inverts-r   = refl

extract-inverts-r²  : recover (a₃ ∷ a₃ ∷ []) [] ≡ (a₃ ∷ a₃ ∷ [] , [])
extract-inverts-r²  = refl

extract-inverts-s   : recover [] (a₂ ∷ []) ≡ ([] , a₂ ∷ [])
extract-inverts-s   = refl

extract-inverts-sr  : recover (a₃ ∷ []) (a₂ ∷ []) ≡ (a₃ ∷ [] , a₂ ∷ [])
extract-inverts-sr  = refl

extract-inverts-sr² : recover (a₃ ∷ a₃ ∷ []) (a₂ ∷ []) ≡ (a₃ ∷ a₃ ∷ [] , a₂ ∷ [])
extract-inverts-sr² = refl
