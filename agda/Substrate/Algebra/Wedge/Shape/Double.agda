------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Double
--
-- THE SHAPE-INDEXED DOUBLE CATEGORY — the symmetric structure your two
-- fiberings name, built where it is CLEAN: over the carrier-free shape
-- (`List ℕ`), whose equality is decidable, so the morphism-equality wall
-- (`Bridge`/`Wedge` proof fields under `--without-K`) never appears.
--
-- Both species of arrow live over the shape as their common base:
--   * HORIZONTAL — bridges, acting by `transport-trace`, shape-preserving
--     (`shape-transport`). Composition/identity from Bridge `⊚`/`id-bridge`.
--   * VERTICAL  — correspondences, `Corr t₁ t₂ = shape t₁ ≡ shape t₂`, a
--     GROUPOID (refl / sym / trans) — every correspondence is invertible.
--   * SQUARE    — `square`: independent bridges top and bottom plus a
--     correspondence on the left yield a correspondence on the right; it
--     commutes because both bridges preserve shape. This is the genuine
--     2-cell (top ≠ bottom allowed — the cross-carrier correspondence is what
--     frees it from the single-bridge `transport-wedge` diagonal).
--
-- So the structure fibers over the shape in BOTH directions; the transpose
-- (swap horizontal ↔ vertical) fixes the shape — the Möbius — and its seam is
-- the diagonal where a bridge is an iso and a correspondence is `refl`.
--
-- SCOPE: this is the double-category DATA (objects-as-shaped-traces, the two
-- arrow species, the square). The coherence laws (vertical groupoid laws,
-- interchange) are inherited from `trans`/`sym`/`cong` on `List ℕ` `≡`; the
-- groupoid ops are given here, the full interchange is the next layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Double where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace)
open import Substrate.Algebra.Wedge.Shape using (Corresponds)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)
open import Substrate.Algebra.Wedge.Shape.Transport using (shape-transport)

------------------------------------------------------------------------
-- 1. Vertical: the correspondence groupoid (shape-equality, cross-carrier).
------------------------------------------------------------------------

Corr : {D₁ D₂ : DivStr} {a₁ b₁ g₁ : C D₁} {a₂ b₂ g₂ : C D₂} →
       Trace D₁ a₁ b₁ g₁ → Trace D₂ a₂ b₂ g₂ → Set
Corr = Corresponds

corr-id : {D : DivStr} {a b g : C D} (t : Trace D a b g) → Corr t t
corr-id _ = refl

corr-sym : {D₁ D₂ : DivStr} {a₁ b₁ g₁ : C D₁} {a₂ b₂ g₂ : C D₂}
           {t₁ : Trace D₁ a₁ b₁ g₁} {t₂ : Trace D₂ a₂ b₂ g₂} →
           Corr t₁ t₂ → Corr t₂ t₁
corr-sym = sym

corr-∘ : {D₁ D₂ D₃ : DivStr}
         {a₁ b₁ g₁ : C D₁} {a₂ b₂ g₂ : C D₂} {a₃ b₃ g₃ : C D₃}
         {t₁ : Trace D₁ a₁ b₁ g₁} {t₂ : Trace D₂ a₂ b₂ g₂} {t₃ : Trace D₃ a₃ b₃ g₃} →
         Corr t₂ t₃ → Corr t₁ t₂ → Corr t₁ t₃
corr-∘ q p = trans p q

------------------------------------------------------------------------
-- 2. The square: independent bridges + a correspondence commute (both
--    bridges preserve shape, so the right correspondence is forced).
--
--        t₁ ──corr──── t₂
--        │br₁          │br₂
--        ▼             ▼
--   br₁·t₁ ──corr── br₂·t₂
------------------------------------------------------------------------

square : {D₁ D₁′ D₂ D₂′ : DivStr}
         (br₁ : Bridge D₁ D₁′) (br₂ : Bridge D₂ D₂′)
         {a₁ b₁ g₁ : C D₁} {a₂ b₂ g₂ : C D₂}
         (t₁ : Trace D₁ a₁ b₁ g₁) (t₂ : Trace D₂ a₂ b₂ g₂) →
         Corr t₁ t₂ → Corr (transport-trace br₁ t₁) (transport-trace br₂ t₂)
square br₁ br₂ t₁ t₂ c =
  trans (shape-transport br₁ t₁) (trans c (sym (shape-transport br₂ t₂)))
