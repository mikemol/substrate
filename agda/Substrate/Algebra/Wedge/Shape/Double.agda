------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Double
--
-- THE SHAPE-INDEXED STRUCTURE — over the quotient-sequence shape (`List (C D)`,
-- the quotients now carrier representatives, no longer a carrier-free `List ℕ`).
--
-- Since the quotient pivoted from a carrier-free ℕ count to a CARRIER element,
-- the shape is no longer comparable ACROSS carriers (List (C D₁) ≢ List (C D₂)
-- as types), and `shape` is no longer a strict bridge-INVARIANT — it is bridge-
-- NATURAL: `shape (transport-trace br t) ≡ map (translate br) (shape t)`
-- (Shape.Transport). So:
--   * VERTICAL — correspondences `Corr t₁ t₂ = shape t₁ ≡ shape t₂` are now
--     SAME-CARRIER (one DivStr D); a GROUPOID (refl / sym / trans).
--   * SQUARE   — `square`: ONE bridge carries corresponding traces to
--     corresponding traces (the NATURALITY of shape under transport). The old
--     two-independent-bridges square held only because shape was bridge-
--     invariant; under carrier-representative quotients a bridge RELABELS the
--     quotients (via `map ∘ translate`), so two different bridges give different
--     shapes — the heterogeneous square is no longer valid, the single-bridge
--     naturality square is.
--
-- Cross-carrier correspondence (the genuinely heterogeneous double category) now
-- requires a bridge MEDIATING the comparison (compare `map (translate br) (shape
-- t₁)` with `shape t₂`), not a carrier-free shape — deferred to the bridge-
-- mediated form.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Double where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Wedge using (DivStr; Trace)
open import Substrate.Algebra.Wedge.Shape using (Corresponds)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; transport-trace)
open import Substrate.Algebra.Wedge.Shape.Transport using (shape-transport; mapL)

------------------------------------------------------------------------
-- 1. Vertical: the correspondence groupoid (shape-equality, same carrier).
------------------------------------------------------------------------

Corr : {C : Set} {D : DivStr C} {a₁ b₁ g₁ a₂ b₂ g₂ : C} →
       Trace D a₁ b₁ g₁ → Trace D a₂ b₂ g₂ → Set
Corr = Corresponds

corr-id : {C : Set} {D : DivStr C} {a b g : C} (t : Trace D a b g) → Corr t t
corr-id _ = refl

corr-sym : {C : Set} {D : DivStr C} {a₁ b₁ g₁ a₂ b₂ g₂ : C}
           {t₁ : Trace D a₁ b₁ g₁} {t₂ : Trace D a₂ b₂ g₂} →
           Corr t₁ t₂ → Corr t₂ t₁
corr-sym = sym

corr-∘ : {C : Set} {D : DivStr C}
         {a₁ b₁ g₁ a₂ b₂ g₂ a₃ b₃ g₃ : C}
         {t₁ : Trace D a₁ b₁ g₁} {t₂ : Trace D a₂ b₂ g₂} {t₃ : Trace D a₃ b₃ g₃} →
         Corr t₂ t₃ → Corr t₁ t₂ → Corr t₁ t₃
corr-∘ q p = trans p q

------------------------------------------------------------------------
-- 2. The naturality square: ONE bridge maps corresponding traces to
--    corresponding traces (shape is natural — it relabels by `map ∘ translate`,
--    so both sides shift identically and the correspondence is preserved).
--
--        t₁ ──corr──── t₂
--        │ br          │ br        (the SAME bridge on both legs)
--        ▼             ▼
--   br·t₁ ──corr──── br·t₂
------------------------------------------------------------------------

square : {C C′ : Set} {D : DivStr C} {D′ : DivStr C′} (br : Bridge D D′)
         {a₁ b₁ g₁ a₂ b₂ g₂ : C}
         (t₁ : Trace D a₁ b₁ g₁) (t₂ : Trace D a₂ b₂ g₂) →
         Corr t₁ t₂ → Corr (transport-trace br t₁) (transport-trace br t₂)
square br t₁ t₂ c =
  trans (shape-transport br t₁)
        (trans (cong (mapL (translate br)) c) (sym (shape-transport br t₂)))
