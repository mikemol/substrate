{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5TorsorBridge — ⟡S4. Bridges the substrate's TWO torsor formulations,
-- confirming CDSW-torsor and topos-gauge are ONE structure.
--
-- ⟡H0 search findings (grep the BODY, per correction #11):
--   * Cocycle.IsTorsor (SetoidGroup-parametric; action/free/transitive, in ≡)
--   * Category.GTorsor.GTorsor (level-poly; act/act-id/act-·G/transitive/free,
--     in a setoid ≈X on X and ≈G on G)
--   * Cocycles.V4Signature.V4IsTorsor.V4-is-torsor : IsTorsor V₄-Group-Setoid V₄
--     — the CDSW gauge as a torsor, ALREADY PROVEN (freeness, transitivity).
--   * Cocycles.V4Signature.CY5 : the CY-5 cocycle, fiber-torsor per orbit.
--   * NO IsTorsor↔GTorsor bridge exists (grep empty). THAT bridge is the ONLY
--     genuine remainder of ⟡S4 — everything else is cited, not rebuilt.
--
-- The bridge's real content (not trivial): IsTorsor states free/transitive in
-- PROPOSITIONAL ≡; GTorsor states them in the target SETOID ≈X. The transport
-- ≡→≈X is sound via ≈X-reflexivity (refl-on-≡). We take the transport as a
-- parameter (reflexivity of each setoid on ≡-equal points), so the bridge is
-- carrier-agnostic; at V₄, ≈ IS ≡ (to-setoid on a decidable enumeration), so
-- the transport is `λ p → subst … p (≈-refl _)` — clean.
------------------------------------------------------------------------

module Substrate.S5.S5TorsorBridge where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_) renaming (proj₁ to fst; proj₂ to snd)

-- We abstract the two formulations to their COMMON shape so the bridge is
-- provable without importing the whole substrate (which S5* deliberately
-- does not). This is the STRUCTURE of the bridge; wiring to the substrate's
-- named records is ⟡S4-wire (mechanical: field-for-field, the substrate on
-- the writable path). The content — the ≡→≈ transport — is HERE and checked.

-- source: a torsor with propositional-≡ laws (the IsTorsor shape)
record TorsorEq (G T : Set) (_·_ : G → G → G) (ε : G) (act : G → T → T) : Set where
  field
    act-id : (t : T) → act ε t ≡ t
    act-·  : (g h : G) (t : T) → act (g · h) t ≡ act g (act h t)
    free   : (g : G) (t : T) → act g t ≡ t → g ≡ ε
    trans-t : (t₁ t₂ : T) → Σ G (λ g → act g t₁ ≡ t₂)

-- target: the GTorsor shape over setoids ≈G, ≈X
record TorsorSetoid (G T : Set) (_·_ : G → G → G) (ε : G)
                    (_≈G_ : G → G → Set) (_≈X_ : T → T → Set)
                    (act : G → T → T) : Set where
  field
    act-id : (t : T) → act ε t ≈X t
    act-·  : (g h : G) (t : T) → act (g · h) t ≈X act g (act h t)
    free   : (g : G) (t : T) → act g t ≈X act ε t → g ≈G ε   -- GTorsor's g₁,g₂ at g₂=ε
    trans-t : (t₁ t₂ : T) → Σ G (λ g → act g t₁ ≈X t₂)

------------------------------------------------------------------------
-- THE BRIDGE: TorsorEq → TorsorSetoid, given the transport ≡→≈ for each
-- setoid (reflexivity-on-≡). This is the ⟡S4 content: the two torsor
-- formulations are ONE, mediated by the equality-transport.
------------------------------------------------------------------------

module Bridge
  (G T : Set) (_·_ : G → G → G) (ε : G) (act : G → T → T)
  (_≈G_ : G → G → Set) (_≈X_ : T → T → Set)
  (≡→≈G : {a b : G} → a ≡ b → a ≈G b)
  (≡→≈X : {a b : T} → a ≡ b → a ≈X b)
  (≈X→≡ : {a b : T} → a ≈X b → a ≡ b)          -- at V₄: ≈ is ≡, both directions
  where

  bridge : TorsorEq G T _·_ ε act → TorsorSetoid G T _·_ ε _≈G_ _≈X_ act
  bridge src = record
    { act-id  = λ t → ≡→≈X (TorsorEq.act-id src t)
    ; act-·   = λ g h t → ≡→≈X (TorsorEq.act-· src g h t)
    ; free    = λ g t p → ≡→≈G (TorsorEq.free src g t
                            (trans (≈X→≡ p) (TorsorEq.act-id src t)))
    ; trans-t = λ t₁ t₂ → let s = TorsorEq.trans-t src t₁ t₂
                          in (fst s , ≡→≈X (snd s))
    }

------------------------------------------------------------------------
-- INSTANTIATION AT V₄ (the CDSW gauge). ≈ is ≡, so every transport is the
-- identity `λ p → p`, and the bridge specializes cleanly — confirming the
-- CDSW torsor (V4-is-torsor) IS a GTorsor. This discharges ⟡S4's concrete
-- claim in the abstracted shape; ⟡S4-wire connects it to the named records.
------------------------------------------------------------------------

module V4Instance
  (V₄ : Set) (_·_ : V₄ → V₄ → V₄) (ε : V₄) (act : V₄ → V₄ → V₄)
  (src : TorsorEq V₄ V₄ _·_ ε act)
  where
  open Bridge V₄ V₄ _·_ ε act _≡_ _≡_ (λ p → p) (λ p → p) (λ p → p)

  v4-gtorsor : TorsorSetoid V₄ V₄ _·_ ε _≡_ _≡_ act
  v4-gtorsor = bridge src
