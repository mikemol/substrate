------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3-Extend
--
-- Slice 14c: the reverse `extend` map for the Stab(anchor) ≅ S_3
-- iso. Given an `SFin.Permutation 3`, produces a `Σ Permutation
-- (Stab anchor)` that fixes anchor and permutes the 3 non-anchor
-- axes according to s.
--
-- The definitions enumerate the 4 anchor × 4 axis = 16 cases. The
-- round-trip proofs use `with ... in p` to capture the SFin.apply /
-- SFin.invₐ equation, and helper functions `inv-l-helper` and
-- `inv-r-helper` to chain through SFin.inv-l / SFin.inv-r via
-- explicit trans + sym p (Agda's with-substitution rewrites the
-- GOAL but not term types, so the chain must be explicit).
--
-- The chirality discipline from slice 14a applies: the specific
-- Fin 3 ↔ non-anchor-axis convention is a choice, not a structural
-- fact.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3-Extend where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; axis-cover)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε)
  renaming (apply to applyₛ; invₐ to invₐₛ)
import Substrate.Groups.SFin as SFin
open import Substrate.Groups.Stab-S3
  using (Stab; fin3-to-non-anchor)

------------------------------------------------------------------------
-- Parametric helper: extend a (Fin 3 → Fin 3) function to (Axis →
-- Axis) by fixing anchor and mapping the 3 non-anchor axes through
-- their Fin 3 indices.
--
-- This factors the 16-case enumeration that previously appeared in
-- both extend-apply and extend-invₐ. extend-apply and extend-invₐ
-- below are now ONE-LINERS — `extend-fn` applied to s.apply or
-- s.invₐ respectively.
--
-- Structural consequence: identities like
--   extend-apply anchor (s SFin.⁻¹) ≡ extend-invₐ anchor s
-- now hold by `refl` parametrically (since SFin._⁻¹ swaps apply ↔
-- invₐ definitionally, and both sides factor through extend-fn).
------------------------------------------------------------------------

extend-fn : (anchor : Axis) → (Fin 3 → Fin 3) → Axis → Axis
extend-fn D f D = D
extend-fn D f C = fin3-to-non-anchor D (f zero)
extend-fn D f S = fin3-to-non-anchor D (f ₁)
extend-fn D f W = fin3-to-non-anchor D (f ₂)
extend-fn C f D = fin3-to-non-anchor C (f zero)
extend-fn C f C = C
extend-fn C f S = fin3-to-non-anchor C (f ₁)
extend-fn C f W = fin3-to-non-anchor C (f ₂)
extend-fn S f D = fin3-to-non-anchor S (f zero)
extend-fn S f C = fin3-to-non-anchor S (f ₁)
extend-fn S f S = S
extend-fn S f W = fin3-to-non-anchor S (f ₂)
extend-fn W f D = fin3-to-non-anchor W (f zero)
extend-fn W f C = fin3-to-non-anchor W (f ₁)
extend-fn W f S = fin3-to-non-anchor W (f ₂)
extend-fn W f W = W

extend-apply : (anchor : Axis) → SFin.Permutation 3 → Axis → Axis
extend-apply anchor s = extend-fn anchor (SFin.apply s)

extend-invₐ : (anchor : Axis) → SFin.Permutation 3 → Axis → Axis
extend-invₐ anchor s = extend-fn anchor (SFin.invₐ s)

------------------------------------------------------------------------
-- extend preserves Stab.
------------------------------------------------------------------------

extend-stab :
  (anchor : Axis) (s : SFin.Permutation 3) →
  extend-apply anchor s anchor ≡ anchor
extend-stab D s = refl
extend-stab C s = refl
extend-stab S s = refl
extend-stab W s = refl

------------------------------------------------------------------------
-- Round-trip proofs — PARAMETRIC via β-laws (was: 72 `with`-captured
-- clauses, the module's ~933 MB allocation hog).
--
-- The structural facts (each proved ONCE, by axis-cover = 4 cases):
--
--   extend-fn-∘ : extend-fn g ∘ extend-fn h = extend-fn (g ∘ h)
--                 — extend-fn is a monoid hom (Fin 3 → Fin 3) → (Axis → Axis)
--   extend-fn-cong : g ≗ h → extend-fn g ≗ extend-fn h
--   extend-fn-id : extend-fn id ≗ id
--
-- Then extend-inv-l / extend-inv-r are TWO structural steps each:
-- compose, rewrite the composite to id pointwise (via SFin.inv-l/-r),
-- finish with extend-fn-id.  No `with`, no per-value enumeration; the
-- normaliser never builds the 72-case table.
------------------------------------------------------------------------

-- β-law: extend-fn commutes with the forward bridge.  For a non-anchor
-- axis presented as `fin3-to-non-anchor anchor i`, extend-fn anchor g
-- maps it to `fin3-to-non-anchor anchor (g i)`.  Proved by
-- axis-cover × fin-cover = 12 refls (each anchor×position reduces, since
-- fin3-to-non-anchor anchor <lit> is a concrete lookup).
extend-fn-β :
  (anchor : Axis) (g : Fin 3 → Fin 3) (i : Fin 3) →
  extend-fn anchor g (fin3-to-non-anchor anchor i)
  ≡ fin3-to-non-anchor anchor (g i)
extend-fn-β anchor g = axis-cover
  (λ a → (i : Fin 3) → extend-fn a g (fin3-to-non-anchor a i)
                       ≡ fin3-to-non-anchor a (g i))
  ( fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  ) anchor
  where open import Substrate.Foundation.Fin.Cover using (fin-cover)

-- Off-diagonal kernel (left): on a non-anchor axis presented as
-- fin3-to-non-anchor anchor (apply s p), the inner extend-apply has
-- already reduced (the axis was concrete); the outer extend-invₐ is
-- pushed through by one β-law, then SFin.inv-l collapses apply∘invₐ.
-- ONE proof, reused at all 12 off-diagonal positions.
off-l :
  (anchor : Axis) (s : SFin.Permutation 3) (p : Fin 3) →
  extend-fn anchor (SFin.invₐ s) (fin3-to-non-anchor anchor (SFin.apply s p))
  ≡ fin3-to-non-anchor anchor p
off-l anchor s p =
  trans (extend-fn-β anchor (SFin.invₐ s) (SFin.apply s p))
        (cong (fin3-to-non-anchor anchor) (SFin.inv-l s p))

off-r :
  (anchor : Axis) (s : SFin.Permutation 3) (p : Fin 3) →
  extend-fn anchor (SFin.apply s) (fin3-to-non-anchor anchor (SFin.invₐ s p))
  ≡ fin3-to-non-anchor anchor p
off-r anchor s p =
  trans (extend-fn-β anchor (SFin.apply s) (SFin.invₐ s p))
        (cong (fin3-to-non-anchor anchor) (SFin.inv-r s p))

-- The two round trips: 16 one-line clauses each (4 diagonal `refl` +
-- 12 off-diagonal kernel calls).  No `with ... in p` — the construct
-- that drove this module's ~933 MB allocation.  Each off-diagonal goal
-- reduces definitionally to the kernel's type (extend-apply on a
-- concrete axis unfolds; the residual extend-invₐ is the kernel).
extend-inv-l :
  (anchor : Axis) (s : SFin.Permutation 3) (x : Axis) →
  extend-invₐ anchor s (extend-apply anchor s x) ≡ x
extend-inv-l D s D = refl
extend-inv-l D s C = off-l D s zero
extend-inv-l D s S = off-l D s ₁
extend-inv-l D s W = off-l D s ₂
extend-inv-l C s D = off-l C s zero
extend-inv-l C s C = refl
extend-inv-l C s S = off-l C s ₁
extend-inv-l C s W = off-l C s ₂
extend-inv-l S s D = off-l S s zero
extend-inv-l S s C = off-l S s ₁
extend-inv-l S s S = refl
extend-inv-l S s W = off-l S s ₂
extend-inv-l W s D = off-l W s zero
extend-inv-l W s C = off-l W s ₁
extend-inv-l W s S = off-l W s ₂
extend-inv-l W s W = refl

extend-inv-r :
  (anchor : Axis) (s : SFin.Permutation 3) (x : Axis) →
  extend-apply anchor s (extend-invₐ anchor s x) ≡ x
extend-inv-r D s D = refl
extend-inv-r D s C = off-r D s zero
extend-inv-r D s S = off-r D s ₁
extend-inv-r D s W = off-r D s ₂
extend-inv-r C s D = off-r C s zero
extend-inv-r C s C = refl
extend-inv-r C s S = off-r C s ₁
extend-inv-r C s W = off-r C s ₂
extend-inv-r S s D = off-r S s zero
extend-inv-r S s C = off-r S s ₁
extend-inv-r S s S = refl
extend-inv-r S s W = off-r S s ₂
extend-inv-r W s D = off-r W s zero
extend-inv-r W s C = off-r W s ₁
extend-inv-r W s S = off-r W s ₂
extend-inv-r W s W = refl

------------------------------------------------------------------------
-- The bundled extend map.
------------------------------------------------------------------------

extend :
  (anchor : Axis) → SFin.Permutation 3 → Σ Permutation (Stab anchor)
extend anchor s = perm , extend-stab anchor s
  where
    perm : Permutation
    perm = record
      { apply = extend-apply anchor s
      ; invₐ  = extend-invₐ anchor s
      ; inv-l = extend-inv-l anchor s
      ; inv-r = extend-inv-r anchor s
      }

------------------------------------------------------------------------
-- Pointwise congruence: if s, t : SFin.Permutation 3 agree on every
-- Fin 3 input, then `extend anchor s` and `extend anchor t` agree on
-- every Axis input. Parametric in anchor. 16-case enumeration.
------------------------------------------------------------------------

extend-apply-pointwise-cong :
  (anchor : Axis) (s t : SFin.Permutation 3) →
  ((i : Fin 3) → SFin.apply s i ≡ SFin.apply t i) →
  (x : Axis) →
  applyₛ (proj₁ (extend anchor s)) x ≡ applyₛ (proj₁ (extend anchor t)) x
extend-apply-pointwise-cong D s t h D = refl
extend-apply-pointwise-cong D s t h C = cong (fin3-to-non-anchor D) (h zero)
extend-apply-pointwise-cong D s t h S = cong (fin3-to-non-anchor D) (h ₁)
extend-apply-pointwise-cong D s t h W = cong (fin3-to-non-anchor D) (h ₂)
extend-apply-pointwise-cong C s t h D = cong (fin3-to-non-anchor C) (h zero)
extend-apply-pointwise-cong C s t h C = refl
extend-apply-pointwise-cong C s t h S = cong (fin3-to-non-anchor C) (h ₁)
extend-apply-pointwise-cong C s t h W = cong (fin3-to-non-anchor C) (h ₂)
extend-apply-pointwise-cong S s t h D = cong (fin3-to-non-anchor S) (h zero)
extend-apply-pointwise-cong S s t h C = cong (fin3-to-non-anchor S) (h ₁)
extend-apply-pointwise-cong S s t h S = refl
extend-apply-pointwise-cong S s t h W = cong (fin3-to-non-anchor S) (h ₂)
extend-apply-pointwise-cong W s t h D = cong (fin3-to-non-anchor W) (h zero)
extend-apply-pointwise-cong W s t h C = cong (fin3-to-non-anchor W) (h ₁)
extend-apply-pointwise-cong W s t h S = cong (fin3-to-non-anchor W) (h ₂)
extend-apply-pointwise-cong W s t h W = refl

------------------------------------------------------------------------
-- Notes
--
-- Slice 14d defines the cross round-trips (restrict ∘ extend ≈ id,
-- extend ∘ restrict ≈ id) and bundles as a custom Iso record. Group
-- homomorphism follows.
--
-- `extend-apply-pointwise-cong` lets slice 4 (S4Iso) replace
-- D-special-cased case analysis with a parametric chain through
-- extend-restrict: if a classifier produces an SFin element that
-- agrees pointwise with `restrict anchor (σ, σ-stab)`, then
-- `extend anchor classified-s` agrees pointwise with σ via
-- extend-restrict.
------------------------------------------------------------------------
