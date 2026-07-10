------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Compose
--
-- THE WEDGE CATEGORY'S COMPOSITION — the keystone both the arrow category
-- and the twisted arrow category sit on. A wedge `a = recon q b r` is an
-- arrow `b ⟶ a`; this module gives the category structure:
--
--   * identity = the (1, z) corner: `a = recon 1 a z = a` (ReconUnit), the
--     same corner that makes `=` the (1,z) read (Adjunction/Iso/Bridge);
--   * composition: from `a = q·b + r` and `b = q'·c + r'`,
--       a = recon q (recon q' c r') r = recon (q*q') c (recon q r' r)
--     — the RECON-LINEARITY law (ReconLinear).
--
-- The composition LITERALLY exhibits the wedge's two roles as its two legs:
--   * `quot w₁ ⊗ quot w₂`  — quotient — QUANTIFY (multiplicities multiply, via
--     the carrier's own multiplication `_⊗_`, the quotient being a carrier rep);
--   * `recon (quot w₁) (rem w₂) (rem w₁)` — carrier — EXCHANGE (the
--     residue handed downstream, exactly the EEA step).
-- This is the carrier-side content; quotienting by the carrier (Shape.agda)
-- projects composition to concatenation of the quotient sequences.
--
-- The laws are PREDICATES on a DivStr (a carrier needs to be ring-like to
-- satisfy ReconLinear). ℕ-div satisfies both — Compose.Laws — assembled from
-- the existing Foundation.Nat distributivity/associativity lemmas (the
-- identity was already implicit; this is its assembly, not new theory).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Compose where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Wedge
  using (DivStr; z; recon; quot; rem; wedge-eq)
  renaming (Wedge to Wedge⟦478f66a6⟧)   -- specialize the colliding name by shape

------------------------------------------------------------------------
-- 1. The two laws a carrier needs to host the wedge category.
--    The quotient is now a CARRIER element, so "multiplicities multiply" is the
--    carrier's OWN multiplication `_⊗_` and the identity quotient is `one : C D`
--    (these were ℕ's `_*_` and `1` when the quotient was a baked count).
------------------------------------------------------------------------

-- composition: recon distributes over its own remainder (ring-linearity).
ReconLinear : {C : Set} (D : DivStr C) → (C → C → C) → Set
ReconLinear D _⊗_ = ∀ q q′ c r′ r →
  recon D q (recon D q′ c r′) r ≡ recon D (q ⊗ q′) c (recon D q r′ r)

-- identity: the (one, z) corner reconstructs the element unchanged.
ReconUnit : {C : Set} (D : DivStr C) → C → Set
ReconUnit D one = ∀ x → recon D one x (z D) ≡ x

------------------------------------------------------------------------
-- 2. The category structure: identity (1,z) and composition.
------------------------------------------------------------------------

-- composition of wedges: quotients multiply (quantify), remainders
-- accumulate through recon (exchange).
wedge-∘ : {C : Set} {D : DivStr C} {_⊗_ : C → C → C} → ReconLinear D _⊗_ → {a b c : C} →
          Wedge⟦478f66a6⟧ D a b → Wedge⟦478f66a6⟧ D b c → Wedge⟦478f66a6⟧ D a c
wedge-∘ {D = D} {_⊗_ = _⊗_} lin {c = c} w₁ w₂ = record
  { quot     = quot w₁ ⊗ quot w₂
  ; rem      = recon D (quot w₁) (rem w₂) (rem w₁)
  ; wedge-eq =
      trans (wedge-eq w₁)
      (trans (cong (λ b′ → recon D (quot w₁) b′ (rem w₁)) (wedge-eq w₂))
             (lin (quot w₁) (quot w₂) c (rem w₂) (rem w₁)))
  }

-- the identity wedge a ⟶ a: the (one, z) corner.
wedge-id : {C : Set} {D : DivStr C} {one : C} → ReconUnit D one → (a : C) → Wedge⟦478f66a6⟧ D a a
wedge-id {D = D} {one = one} unit a =
  record { quot = one ; rem = z D ; wedge-eq = sym (unit a) }
