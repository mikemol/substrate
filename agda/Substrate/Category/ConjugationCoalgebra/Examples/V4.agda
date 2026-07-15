------------------------------------------------------------------------
-- Substrate.Category.ConjugationCoalgebra.Examples.V4
--
-- First concrete instantiation of the simplicity recognizer: the Klein
-- four-group V₄ is NOT simple, proved generically by exhibiting a
-- NonSimplicityWitness (the subgroup ⟨α⟩ = {e, α}).  The group itself
-- is REUSED from Substrate.Groups.V4 — the coalgebra is a thin wrapper,
-- not a fresh carrier.
--
-- This is the "reject" leg of the recognizer.  V₄ is abelian, so
-- conjugation is trivial and every conjugacy class is a singleton.
--
-- The "accept" leg (proving a group SIMPLE) is deliberately NOT done
-- here: `IsSimple` quantifies over ALL normal subgroups, so discharging
-- it for a concrete group needs an enumeration of normal subgroups
-- (which `WithOrbits.Finite` reduces to decidable membership for every
-- N, but does not itself provide).  That is a separate arc; see the
-- note at the foot.  Per [[chirality-pair-completeness]] the pair is
-- acknowledged, with the accept leg's cost named rather than faked.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConjugationCoalgebra.Examples.V4 where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Product using (∃-syntax; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong₂; subst)
open import Substrate.Groups.V4
  using (V₄; e; α; β; γ; _·_; ε; inv; v4-cover; v4×v4-cover)
open import Substrate.Category.ConjugationCoalgebra using (ConjugationCoalgebra)
open import Substrate.Category.ConjugationCoalgebra.Simplicity using (module Recognizer)

------------------------------------------------------------------------
-- V₄ is abelian and exponent-2, so conjugation is the identity:
--   (g · h) · g⁻¹ ≡ h         (here g⁻¹ = inv g = g)
-- proved by the 4×4 cover (each cell reduces definitionally).
------------------------------------------------------------------------

conj-trivial : (g h : V₄) → (g · h) · inv g ≡ h
conj-trivial = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- The conjugation coalgebra: classes are singletons (Class = V₄,
-- rep = id, in-class c h = c ≡ h).
------------------------------------------------------------------------

V4-coalg : ConjugationCoalgebra V₄ _·_ ε inv V₄ (λ c → c) (λ c h → c ≡ h)
V4-coalg = record
  { in-class-rep = λ c → refl
  ; conjugation-respects-class =
      λ g c h c≡h → trans c≡h (sym (conj-trivial g h))
  }

open Recognizer V4-coalg (λ x y → x ≡ y)

------------------------------------------------------------------------
-- The normal subgroup ⟨α⟩ = {e, α}.
------------------------------------------------------------------------

mem-α : V₄ → Set
mem-α x = (x ≡ e) ⊎ (x ≡ α)

-- Closure under the operation: the {e,α} block multiplies into itself
-- (e·e=e, e·α=α, α·e=α, α·α=e), so the products land back in {e,α}.
mem-α-· : {a b : V₄} → mem-α a → mem-α b → mem-α (a · b)
mem-α-· (inj₁ a≡e) (inj₁ b≡e) = inj₁ (cong₂ _·_ a≡e b≡e)
mem-α-· (inj₁ a≡e) (inj₂ b≡α) = inj₂ (cong₂ _·_ a≡e b≡α)
mem-α-· (inj₂ a≡α) (inj₁ b≡e) = inj₂ (cong₂ _·_ a≡α b≡e)
mem-α-· (inj₂ a≡α) (inj₂ b≡α) = inj₁ (cong₂ _·_ a≡α b≡α)

-- ⟡set1-paydown: `member` is now a parameter of NormalSubgroup, so the type
-- is `NormalSubgroup mem-α` and the record literal drops the `member` field.
⟨α⟩ : NormalSubgroup mem-α
⟨α⟩ = record
  { member-resp = λ a≡b m → subst mem-α a≡b m
  ; member-ε    = inj₁ refl
  ; member-·    = mem-α-·
  ; member-⁻¹   = λ m → m                       -- inv a = a definitionally
  ; member-conj = λ g {h} m → subst mem-α (sym (conj-trivial g h)) m
  }

------------------------------------------------------------------------
-- The reject: ⟨α⟩ is proper (β ∉) and nontrivial (α ∈, α ≢ e), so it
-- is a NonSimplicityWitness — hence V₄ is not simple.  PROVEN.
------------------------------------------------------------------------

V4-witness : NonSimplicityWitness mem-α
V4-witness = record
  { N         = ⟨α⟩
  ; wit-ntriv = α
  ; ntriv-∈   = inj₂ refl
  ; ntriv-≉ε  = λ ()
  ; wit-prop  = β
  ; prop-∉    = λ { (inj₁ ()) ; (inj₂ ()) }
  }

V4-not-simple : IsSimple → ⊥
V4-not-simple = witness→¬simple V4-witness

------------------------------------------------------------------------
-- The trace bridge instantiates too: orbit picks g = e (since classes
-- are singletons, every element is its own conjugacy orbit).  This
-- gives `WithOrbits.saturated` for V₄ — trivial here because classes
-- are singletons, but it shows the machinery composes on a real group.
------------------------------------------------------------------------

conj-e : (c : V₄) → (e · c) · inv e ≡ c
conj-e = v4-cover _ (refl , refl , refl , refl)

V4-orbit : (c h : V₄) → c ≡ h → ∃[ g ] (((g · c) · inv g) ≡ h)
V4-orbit c h c≡h = e , trans (conj-e c) c≡h

open WithOrbits V4-orbit using (saturated)

------------------------------------------------------------------------
-- Toward the accept leg (separate arc):
--
-- To prove a group SIMPLE through this recognizer one must inhabit
-- `IsSimple = (N : NormalSubgroup) → IsTrivial N ⊎ IsWhole N`, a
-- universal over all normal subgroups.  For a concrete finite group
-- that means: (1) enumerate the normal subgroups (e.g. V₄ has five:
-- {e}, ⟨α⟩, ⟨β⟩, ⟨γ⟩, V₄), (2) classify each.  V₄ fails at ⟨α⟩, as
-- proved above.  A simple group (Zₚ, Aₙ for n ≥ 5) would pass — but
-- the enumeration step is the remaining work; `Finite` only discharges
-- the per-N decision machinery, not the quantifier over N.
------------------------------------------------------------------------
