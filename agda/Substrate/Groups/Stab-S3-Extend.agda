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
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
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
-- Helper proofs that chain SFin.inv-l / SFin.inv-r via captured p.
--
-- inv-l-helper: given SFin.apply s i ≡ j (captured from `with`),
-- derives that fin3-to-non-anchor anchor (SFin.invₐ s j) equals
-- fin3-to-non-anchor anchor i.
------------------------------------------------------------------------

inv-l-helper :
  (anchor : Axis) (s : SFin.Permutation 3) (i j : Fin 3) →
  SFin.apply s i ≡ j →
  fin3-to-non-anchor anchor (SFin.invₐ s j)
  ≡ fin3-to-non-anchor anchor i
inv-l-helper anchor s i j p =
  cong (fin3-to-non-anchor anchor)
       (trans (cong (SFin.invₐ s) (sym p)) (SFin.inv-l s i))

inv-r-helper :
  (anchor : Axis) (s : SFin.Permutation 3) (i j : Fin 3) →
  SFin.invₐ s i ≡ j →
  fin3-to-non-anchor anchor (SFin.apply s j)
  ≡ fin3-to-non-anchor anchor i
inv-r-helper anchor s i j p =
  cong (fin3-to-non-anchor anchor)
       (trans (cong (SFin.apply s) (sym p)) (SFin.inv-r s i))

------------------------------------------------------------------------
-- Round-trip proofs.
------------------------------------------------------------------------

extend-inv-l :
  (anchor : Axis) (s : SFin.Permutation 3) (x : Axis) →
  extend-invₐ anchor s (extend-apply anchor s x) ≡ x
extend-inv-l D s D = refl
extend-inv-l D s C with SFin.apply s zero in p
... | zero           = inv-l-helper D s zero zero p
... | ₁       = inv-l-helper D s zero ₁ p
... | ₂ = inv-l-helper D s zero ₂ p
extend-inv-l D s S with SFin.apply s ₁ in p
... | zero           = inv-l-helper D s ₁ zero p
... | ₁       = inv-l-helper D s ₁ ₁ p
... | ₂ = inv-l-helper D s ₁ ₂ p
extend-inv-l D s W with SFin.apply s ₂ in p
... | zero           = inv-l-helper D s ₂ zero p
... | ₁       = inv-l-helper D s ₂ ₁ p
... | ₂ = inv-l-helper D s ₂ ₂ p
extend-inv-l C s D with SFin.apply s zero in p
... | zero           = inv-l-helper C s zero zero p
... | ₁       = inv-l-helper C s zero ₁ p
... | ₂ = inv-l-helper C s zero ₂ p
extend-inv-l C s C = refl
extend-inv-l C s S with SFin.apply s ₁ in p
... | zero           = inv-l-helper C s ₁ zero p
... | ₁       = inv-l-helper C s ₁ ₁ p
... | ₂ = inv-l-helper C s ₁ ₂ p
extend-inv-l C s W with SFin.apply s ₂ in p
... | zero           = inv-l-helper C s ₂ zero p
... | ₁       = inv-l-helper C s ₂ ₁ p
... | ₂ = inv-l-helper C s ₂ ₂ p
extend-inv-l S s D with SFin.apply s zero in p
... | zero           = inv-l-helper S s zero zero p
... | ₁       = inv-l-helper S s zero ₁ p
... | ₂ = inv-l-helper S s zero ₂ p
extend-inv-l S s C with SFin.apply s ₁ in p
... | zero           = inv-l-helper S s ₁ zero p
... | ₁       = inv-l-helper S s ₁ ₁ p
... | ₂ = inv-l-helper S s ₁ ₂ p
extend-inv-l S s S = refl
extend-inv-l S s W with SFin.apply s ₂ in p
... | zero           = inv-l-helper S s ₂ zero p
... | ₁       = inv-l-helper S s ₂ ₁ p
... | ₂ = inv-l-helper S s ₂ ₂ p
extend-inv-l W s D with SFin.apply s zero in p
... | zero           = inv-l-helper W s zero zero p
... | ₁       = inv-l-helper W s zero ₁ p
... | ₂ = inv-l-helper W s zero ₂ p
extend-inv-l W s C with SFin.apply s ₁ in p
... | zero           = inv-l-helper W s ₁ zero p
... | ₁       = inv-l-helper W s ₁ ₁ p
... | ₂ = inv-l-helper W s ₁ ₂ p
extend-inv-l W s S with SFin.apply s ₂ in p
... | zero           = inv-l-helper W s ₂ zero p
... | ₁       = inv-l-helper W s ₂ ₁ p
... | ₂ = inv-l-helper W s ₂ ₂ p
extend-inv-l W s W = refl

extend-inv-r :
  (anchor : Axis) (s : SFin.Permutation 3) (x : Axis) →
  extend-apply anchor s (extend-invₐ anchor s x) ≡ x
extend-inv-r D s D = refl
extend-inv-r D s C with SFin.invₐ s zero in p
... | zero           = inv-r-helper D s zero zero p
... | ₁       = inv-r-helper D s zero ₁ p
... | ₂ = inv-r-helper D s zero ₂ p
extend-inv-r D s S with SFin.invₐ s ₁ in p
... | zero           = inv-r-helper D s ₁ zero p
... | ₁       = inv-r-helper D s ₁ ₁ p
... | ₂ = inv-r-helper D s ₁ ₂ p
extend-inv-r D s W with SFin.invₐ s ₂ in p
... | zero           = inv-r-helper D s ₂ zero p
... | ₁       = inv-r-helper D s ₂ ₁ p
... | ₂ = inv-r-helper D s ₂ ₂ p
extend-inv-r C s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper C s zero zero p
... | ₁       = inv-r-helper C s zero ₁ p
... | ₂ = inv-r-helper C s zero ₂ p
extend-inv-r C s C = refl
extend-inv-r C s S with SFin.invₐ s ₁ in p
... | zero           = inv-r-helper C s ₁ zero p
... | ₁       = inv-r-helper C s ₁ ₁ p
... | ₂ = inv-r-helper C s ₁ ₂ p
extend-inv-r C s W with SFin.invₐ s ₂ in p
... | zero           = inv-r-helper C s ₂ zero p
... | ₁       = inv-r-helper C s ₂ ₁ p
... | ₂ = inv-r-helper C s ₂ ₂ p
extend-inv-r S s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper S s zero zero p
... | ₁       = inv-r-helper S s zero ₁ p
... | ₂ = inv-r-helper S s zero ₂ p
extend-inv-r S s C with SFin.invₐ s ₁ in p
... | zero           = inv-r-helper S s ₁ zero p
... | ₁       = inv-r-helper S s ₁ ₁ p
... | ₂ = inv-r-helper S s ₁ ₂ p
extend-inv-r S s S = refl
extend-inv-r S s W with SFin.invₐ s ₂ in p
... | zero           = inv-r-helper S s ₂ zero p
... | ₁       = inv-r-helper S s ₂ ₁ p
... | ₂ = inv-r-helper S s ₂ ₂ p
extend-inv-r W s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper W s zero zero p
... | ₁       = inv-r-helper W s zero ₁ p
... | ₂ = inv-r-helper W s zero ₂ p
extend-inv-r W s C with SFin.invₐ s ₁ in p
... | zero           = inv-r-helper W s ₁ zero p
... | ₁       = inv-r-helper W s ₁ ₁ p
... | ₂ = inv-r-helper W s ₁ ₂ p
extend-inv-r W s S with SFin.invₐ s ₂ in p
... | zero           = inv-r-helper W s ₂ zero p
... | ₁       = inv-r-helper W s ₂ ₁ p
... | ₂ = inv-r-helper W s ₂ ₂ p
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
