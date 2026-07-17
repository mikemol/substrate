------------------------------------------------------------------------
-- Σ-SEAM-GLUE / M40 closure — AI-Q, brick 1.
--
-- WHAT THIS FILE PROVES (typechecked terms, nothing more):
--   * `compose`     — a concrete group law on ℤ₂ × V₄ × ℤ₃, transcribing
--                     scratch/spectral_view.py:a4z2_compose (PROVENANCE:
--                     transcription, checked by eye against that source —
--                     NOT verified by the typechecker; σ = the proven V₄
--                     3-cycle `rotate`, · = the proven V₄ op).
--   * `central-χ`   — the element χ = (odd, ε, z0) commutes with every g.
--
-- WHAT THIS FILE DOES *NOT* PROVE (PENDING — do not read the proof as
-- establishing these; they are not yet code):
--   * that this closure ≠ S₄  (PENDING brick B2: `no-order-4`).
--   * that χ being central = the universal "direct-product factor is
--     central"  (PENDING brick B3: exhibit `compose` as DirectProduct).
--   * gauge-invariance under even↔odd  (PENDING brick B4).
--
-- SEAM_GLUE_SPEC.md is a PROPOSAL, not a claim; its D₈/Sylow route is one
-- way to witness split-vs-non-split of 1→A₄→G→ℤ₂→1. This file pursues the
-- direct-product witness instead. Whether either fully discharges M2 is
-- decided by B2, not by this comment.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Closure where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ; _·_)
open import Substrate.Groups.V4.Axioms using (ε-left; ε-identity; inv-left)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (proj₂)

------------------------------------------------------------------------
-- ℤ₂ (chirality / sign) — even = +1, odd = −1.  The proven Chirality↔F₂
-- carrier; the group op is xor (sign multiplication).
------------------------------------------------------------------------

data Chir : Set where
  even odd : Chir

_*c_ : Chir → Chir → Chir
even *c y = y
odd  *c even = odd
odd  *c odd  = even

-- ℤ₂ is abelian (the sign-commutativity centrality needs).
*c-comm : (x y : Chir) → x *c y ≡ y *c x
*c-comm even even = refl
*c-comm even odd  = refl
*c-comm odd  even = refl
*c-comm odd  odd  = refl

-- associativity + units make (Chir, *c, even) a Monoid (even = +1 = identity).
*c-assoc : (x y z : Chir) → (x *c y) *c z ≡ x *c (y *c z)
*c-assoc even y    z    = refl
*c-assoc odd  even z    = refl
*c-assoc odd  odd  even = refl
*c-assoc odd  odd  odd  = refl

*c-identityʳ : (a : Chir) → a *c even ≡ a
*c-identityʳ even = refl
*c-identityʳ odd  = refl

------------------------------------------------------------------------
-- ONTO THE CATEGORICAL SPINE — the chirality factor ℤ₂ deloops to 𝐁(ℤ₂), a
-- CategoryOf (a typechecked Algebra→Category bridge, not a note). The full
-- A₄×ℤ₂ closure reaches the spine via WitnessTower.M40Group; this is the ℤ₂
-- sign-factor on its own.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)

Chir-Monoid : Monoid Chir
Chir-Monoid = record
  { semigroup = record { magma = record { _·_ = _*c_ } ; ·-assoc = *c-assoc }
  ; ε = even ; ε-left = λ a → refl ; ε-right = *c-identityʳ }

Chir-Category : CategoryOf ⊤ (λ _ _ → Chir)
Chir-Category = deloop Chir-Monoid

------------------------------------------------------------------------
-- ℤ₃ (the cycle position) and σ^j = rotate iterated.  z0 is the identity
-- (definitional left-identity); right-identity proved by 3 cases.
------------------------------------------------------------------------

data Z3 : Set where
  z0 z1 z2 : Z3

_+₃_ : Z3 → Z3 → Z3
z0 +₃ y = y
z1 +₃ z0 = z1
z1 +₃ z1 = z2
z1 +₃ z2 = z0
z2 +₃ z0 = z2
z2 +₃ z1 = z0
z2 +₃ z2 = z1

+₃-idʳ : (x : Z3) → x +₃ z0 ≡ x
+₃-idʳ z0 = refl
+₃-idʳ z1 = refl
+₃-idʳ z2 = refl

σ : Z3 → V₄ → V₄
σ z0 m = m
σ z1 m = rotate m
σ z2 m = rotate (rotate m)

-- σ fixes ε for every cycle power (rotate e = e definitionally).
σ-fixes-e : (j : Z3) → σ j e ≡ e
σ-fixes-e z0 = refl
σ-fixes-e z1 = refl
σ-fixes-e z2 = refl

------------------------------------------------------------------------
-- The closure carrier A₄ × ℤ₂ and its group law.
------------------------------------------------------------------------

record A4Z2 : Set where
  constructor mk
  field
    chir : Chir
    mask : V₄
    zee  : Z3

open A4Z2

compose : A4Z2 → A4Z2 → A4Z2
compose g h = mk (chir g *c chir h)
                 (mask g · σ (zee g) (mask h))
                 (zee g +₃ zee h)

-- componentwise equality of carrier elements.
a4z2-≡ : {c₁ c₂ : Chir} {m₁ m₂ : V₄} {z₁ z₂ : Z3} →
         c₁ ≡ c₂ → m₁ ≡ m₂ → z₁ ≡ z₂ → mk c₁ m₁ z₁ ≡ mk c₂ m₂ z₂
a4z2-≡ refl refl refl = refl

------------------------------------------------------------------------
-- L-CENTRALITY (M2): chirality χ = (odd, ε, z0) commutes with every g.
--   compose χ g .mask = ε · σ z0 (mask g) = ε · mask g = mask g
--   compose g χ .mask = mask g · σ (zee g) ε = mask g · ε = mask g
-- The sign factor commutes (ℤ₂); the cycle factor's identity laws agree.
------------------------------------------------------------------------

χ : A4Z2
χ = mk odd e z0

central-χ : (g : A4Z2) → compose χ g ≡ compose g χ
central-χ g =
  a4z2-≡
    (*c-comm odd (chir g))                                   -- ℤ₂: odd·s ≡ s·odd
    (trans (ε-left (mask g))                                  -- ε · m  ≡ m
           (trans (sym (proj₂ ε-identity (mask g)))           -- m      ≡ m · ε
                  (cong (mask g ·_) (sym (σ-fixes-e (zee g)))))) -- m · ε ≡ m · σ j ε
    (sym (+₃-idʳ (zee g)))                                    -- z0 + j ≡ j + z0   (both ≡ j)

------------------------------------------------------------------------
-- BRICK 2: NO ELEMENT HAS ORDER EXACTLY 4 (the decidable A₄×ℤ₂-vs-S₄
-- discriminator; faithful to spectral_view.verify_a4_z2_no_order_4_elements).
--
-- Stated as: g⁴ ≡ ι → g² ≡ ι.  (If the 4th power is trivial, the 2nd
-- already is — so the order never lands on exactly 4.)  Structural:
--   * g⁴ ≡ ι forces (zee g) ≡ z0   (ℤ₃: 4·j ≡ 0 ⟺ j ≡ 0), and
--   * with zee g ≡ z0, g² = (s·s , m·m , z0) = (even, ε, z0) = ι
--     by ℤ₂-square + V₄ exponent-2 (inv-left).
--
-- SCOPE (not overclaimed): this is the order-invariant of THIS group. The
-- formal ¬(G ≅ S₄) additionally needs order-preservation-under-iso + an
-- order-4 witness in S₄ — a separate brick, NOT proved here.
------------------------------------------------------------------------

ι : A4Z2
ι = mk even e z0

*c-sq : (s : Chir) → s *c s ≡ even
*c-sq even = refl
*c-sq odd  = refl

-- V₄ exponent-2: x · x ≡ ε  (inv x ≡ x definitionally, so inv-left applies).
·-sq : (x : V₄) → x · x ≡ V4.ε
·-sq x = inv-left x

sq : A4Z2 → A4Z2
sq g = compose g g

-- with cycle-component already trivial, the square is the identity.
sq-z0 : (s : Chir) (m : V₄) → sq (mk s m z0) ≡ ι
sq-z0 s m = a4z2-≡ (*c-sq s) (·-sq m) refl

-- ℤ₃: the 4th-power cycle component is z0 only when the element's is.
+4-z0 : (j : Z3) → ((j +₃ j) +₃ (j +₃ j)) ≡ z0 → j ≡ z0
+4-z0 z0 _  = refl
+4-z0 z1 ()
+4-z0 z2 ()

no-order-4 : (g : A4Z2) → sq (sq g) ≡ ι → sq g ≡ ι
no-order-4 (mk s m j) eq with +4-z0 j (cong zee eq)
... | refl = sq-z0 s m
