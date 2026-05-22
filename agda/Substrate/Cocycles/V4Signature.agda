------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature
--
-- The CY-5 V_4-signature cocycle as an `IsomorphicCocycleStructure`
-- instance (the catalog's strong discipline, rule 11 strong).
--
-- Under this discipline:
--   * Invariant = OrbitKey = Pairing × Chirality  (6 elements)
--   * Fiber over each orbit is V_4 itself, acting on itself by left
--     translation. Each fiber is a V_4-torsor: free transitive
--     V_4-action, no canonical origin baked into the type.
--   * TotalSpace = Σ OrbitKey (λ _ → V₄) — the 24 "signatures" are
--     DERIVED as (orbit_key, v4_position) pairs.
--
-- Notice what is NOT here:
--   * No primitive `Signature` record (no source/sink/witness fields
--     baked in).
--   * No `project` function (the projection is the Σ-fst).
--   * No `canonical-in-orbit` / `lex-min` / `v4_delta-from-canonical`
--     — these are not expressible because the type structure has no
--     place for a canonical-relative coordinate to live.
--
-- The current substrate's Signature record + v4_delta encoding is
-- recoverable as a WeakCocycleStructure via the Downcast module of
-- Substrate.Cocycle (provided one supplies a section of the
-- TotalSpace ↠ Invariant projection — i.e., a canonical choice).
-- But the canonical choice would have to be advertised explicitly;
-- the type system doesn't let it sneak in.
--
-- See: catalog/cocycles.md § CY-5 and § Isomorphic storage.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature where

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; ∃; -,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; cong)

open import Substrate.Cocycle
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ; V₄-Group)
open import Substrate.Algebra.Group.ToSetoid using (to-setoid)

V₄-Group-Setoid = to-setoid V₄-Group

------------------------------------------------------------------------
-- The orbit_key components.
--
-- Pairing: which V_4 partition of AXES the orbit corresponds to.
--   α-pair = {D,C}|{S,W}; β-pair = {D,S}|{C,W}; γ-pair = {D,W}|{C,S}
-- Chirality: which coset of A_4 in S_4 (even = A_4, odd = S_4 \ A_4).
------------------------------------------------------------------------

data Pairing : Set where
  α-pair β-pair γ-pair : Pairing

------------------------------------------------------------------------
-- V₄ → Pairing total relationship. V₄'s α/β/γ each induce an axis-pair
-- partition (the corresponding Pairing ctor); V₄'s identity element e
-- does NOT induce a Pairing — there's no axis-swap for the identity.
-- The detector's cross-type signal V₄→Pairing (3-of-4 fanout, missing
-- 'e-pair') is structurally true: Pairing = V₄/⟨e⟩ as a set quotient.
--
-- We expose two names to make the absence first-class:
--
--   V₄→Pairing   : (v : V₄) → v ≢ e → Pairing
--                  the partial function with the e-case absurd.
--
--   e-pair       : ⊥ → Pairing
--                  the named "constructor" for the absent case, body
--                  absurd-via-⊥. Documents the missing-by-design ctor
--                  so the cross-type stem-match has a target.
------------------------------------------------------------------------

_≢_ : V₄ → V₄ → Set
v ≢ w = (v ≡ w) → ⊥

V₄→Pairing : (v : V₄) → v ≢ e → Pairing
V₄→Pairing e v≢e = ⊥-elim (v≢e refl)
V₄→Pairing α _   = α-pair
V₄→Pairing β _   = β-pair
V₄→Pairing γ _   = γ-pair

e-pair : ⊥ → Pairing
e-pair ()

data Chirality : Set where
  even odd : Chirality

OrbitKey : Set
OrbitKey = Pairing × Chirality

------------------------------------------------------------------------
-- The fiber: V_4 acting on itself by left translation.
--
-- This is the regular representation; well-known to be a torsor:
--   * Free: g · t = t implies g = e (left cancellation in groups).
--   * Transitive: for any t₁, t₂, take g = t₂ · t₁⁻¹ (here t₁⁻¹ = t₁
--     since V_4 elements are self-inverse).
--
-- We use V_4 as the carrier; the torsor axioms ensure no consumer
-- can depend on which element is the V_4 identity, so the "canonical
-- baseline" question doesn't arise at the type level.
------------------------------------------------------------------------

V4-acts-on-itself : Action V₄-Group-Setoid V₄
V4-acts-on-itself = record
  { act    = V4._·_
  ; act-id = V4.ε-left                  -- e · b ≡ b (algebraic via V4-Generic)
  ; act-∙  = λ g h b → V4.·-assoc g h b -- (g · h) · b ≡ g · (h · b)
  }

-- Left cancellation in V_4: needed for the freeness proof.
-- Stated and proved here (provable from V_4 being a group).
V4-left-cancel : (g h : V₄) → g V4.· h ≡ h → g ≡ e
V4-left-cancel e h _ = refl
V4-left-cancel α e p = p               -- α · e = α, so p : α ≡ e — return p directly
V4-left-cancel α α p = sym p           -- α · α = e, so p : e ≡ α — flip to α ≡ e
V4-left-cancel α β ()                  -- α · β = γ ≠ β
V4-left-cancel α γ ()                  -- α · γ = β ≠ γ
V4-left-cancel β e p = p               -- β · e = β, so p : β ≡ e
V4-left-cancel β α ()                  -- β · α = γ ≠ α
V4-left-cancel β β p = sym p           -- β · β = e, so p : e ≡ β — flip to β ≡ e
V4-left-cancel β γ ()                  -- β · γ = α ≠ γ
V4-left-cancel γ e p = p               -- γ · e = γ, so p : γ ≡ e
V4-left-cancel γ α ()                  -- γ · α = β ≠ α
V4-left-cancel γ β ()                  -- γ · β = α ≠ β
V4-left-cancel γ γ p = sym p           -- γ · γ = e, so p : e ≡ γ — flip to γ ≡ e

-- Transitivity: from t₁ to t₂ in V_4 (as a torsor on itself).
-- The group element doing the work is t₂ · t₁ (since V_4 is
-- self-inverse, t₁⁻¹ = t₁).
V4-transitive : (t₁ t₂ : V₄) → ∃ λ g → g V4.· t₁ ≡ t₂
V4-transitive e t₂ = t₂ , V4.ε-right t₂
V4-transitive α t₂ = (t₂ V4.· α) , aux
  where
    aux : (t₂ V4.· α) V4.· α ≡ t₂
    aux rewrite V4.·-assoc t₂ α α = V4.ε-right t₂
V4-transitive β t₂ = (t₂ V4.· β) , aux
  where
    aux : (t₂ V4.· β) V4.· β ≡ t₂
    aux rewrite V4.·-assoc t₂ β β = V4.ε-right t₂
V4-transitive γ t₂ = (t₂ V4.· γ) , aux
  where
    aux : (t₂ V4.· γ) V4.· γ ≡ t₂
    aux rewrite V4.·-assoc t₂ γ γ = V4.ε-right t₂

V4-is-torsor : IsTorsor V₄-Group-Setoid V₄
V4-is-torsor = record
  { action     = V4-acts-on-itself
  ; free       = V4-left-cancel
  ; transitive = V4-transitive
  }

------------------------------------------------------------------------
-- The Fiber: every orbit has V_4 as its torsor carrier.
--
-- This is the constant function `λ _ → V₄`. In the strong-discipline
-- formulation, this captures that every orbit has the same internal
-- structure (V_4-torsor) — the orbit_key distinguishes WHICH orbit;
-- within an orbit, the elements form a V_4-torsor with no canonical
-- baseline.
------------------------------------------------------------------------

Fiber : OrbitKey → Set
Fiber _ = V₄

fiber-torsor : (i : OrbitKey) → IsTorsor V₄-Group-Setoid (Fiber i)
fiber-torsor _ = V4-is-torsor

------------------------------------------------------------------------
-- The CY-5 cocycle, as an IsomorphicCocycleStructure.
------------------------------------------------------------------------

CY5-V4Signature : IsomorphicCocycleStructure
CY5-V4Signature = record
  { Invariant    = OrbitKey
  ; Gauge        = V₄-Group-Setoid
  ; Fiber        = Fiber
  ; fiber-torsor = fiber-torsor
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. There are 6 × 4 = 24 elements in TotalSpace = Σ OrbitKey Fiber.
--    These are the "24 signatures" the catalog refers to. They are
--    DERIVED from the orbit-key/torsor structure, not declared
--    primitively. The catalog's combinatorial reading (4P3 = 24) and
--    its Hodge-dual reading (Λ³ ↔ Λ¹ in dim 4) are alternative ways
--    of CONSTRUCTING the same 24 — different routes to the same
--    isomorphic-storage carrier.
--
-- 2. The catalog's CY-5 Type-D rigidification (lex-min in v4_delta
--    content-addressing) cannot be encoded here. v4_delta-from-
--    lex-min would require:
--      * picking a canonical element in V_4 (e.g., e),
--      * then encoding each fiber element as "offset from canonical."
--    Neither step exists in this formulation. The type structure
--    refuses the rigidification.
--
-- 3. Future work — a `Substrate.Bijections.S4-vs-Total` module
--    proving TotalSpace ≃ S_4 (matching the catalog's "the 24 ARE
--    S_4" identification). Deferred.
--
-- 4. Future work — bijection between this IsomorphicCocycleStructure
--    and the current substrate's (Signature record + v4_delta) shape
--    via the Downcast module + a chosen canonical. This makes the
--    backwards-compatibility explicit while keeping the current
--    substrate isolated in the WeakCocycleStructure layer.
------------------------------------------------------------------------
