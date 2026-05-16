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

open import Level using (0ℓ)
open import Data.Empty using (⊥; ⊥-elim)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε)
  renaming (apply to applyₛ; invₐ to invₐₛ)
import Substrate.Groups.SFin as SFin
open import Substrate.Groups.Stab-S3
  using (Stab; fin3-to-non-anchor)

------------------------------------------------------------------------
-- extend-apply, extend-invₐ: 16-case enumerations.
------------------------------------------------------------------------

extend-apply : (anchor : Axis) → SFin.Permutation 3 → Axis → Axis
extend-apply D s D = D
extend-apply D s C = fin3-to-non-anchor D (SFin.apply s zero)
extend-apply D s S = fin3-to-non-anchor D (SFin.apply s (suc zero))
extend-apply D s W = fin3-to-non-anchor D (SFin.apply s (suc (suc zero)))
extend-apply C s D = fin3-to-non-anchor C (SFin.apply s zero)
extend-apply C s C = C
extend-apply C s S = fin3-to-non-anchor C (SFin.apply s (suc zero))
extend-apply C s W = fin3-to-non-anchor C (SFin.apply s (suc (suc zero)))
extend-apply S s D = fin3-to-non-anchor S (SFin.apply s zero)
extend-apply S s C = fin3-to-non-anchor S (SFin.apply s (suc zero))
extend-apply S s S = S
extend-apply S s W = fin3-to-non-anchor S (SFin.apply s (suc (suc zero)))
extend-apply W s D = fin3-to-non-anchor W (SFin.apply s zero)
extend-apply W s C = fin3-to-non-anchor W (SFin.apply s (suc zero))
extend-apply W s S = fin3-to-non-anchor W (SFin.apply s (suc (suc zero)))
extend-apply W s W = W

extend-invₐ : (anchor : Axis) → SFin.Permutation 3 → Axis → Axis
extend-invₐ D s D = D
extend-invₐ D s C = fin3-to-non-anchor D (SFin.invₐ s zero)
extend-invₐ D s S = fin3-to-non-anchor D (SFin.invₐ s (suc zero))
extend-invₐ D s W = fin3-to-non-anchor D (SFin.invₐ s (suc (suc zero)))
extend-invₐ C s D = fin3-to-non-anchor C (SFin.invₐ s zero)
extend-invₐ C s C = C
extend-invₐ C s S = fin3-to-non-anchor C (SFin.invₐ s (suc zero))
extend-invₐ C s W = fin3-to-non-anchor C (SFin.invₐ s (suc (suc zero)))
extend-invₐ S s D = fin3-to-non-anchor S (SFin.invₐ s zero)
extend-invₐ S s C = fin3-to-non-anchor S (SFin.invₐ s (suc zero))
extend-invₐ S s S = S
extend-invₐ S s W = fin3-to-non-anchor S (SFin.invₐ s (suc (suc zero)))
extend-invₐ W s D = fin3-to-non-anchor W (SFin.invₐ s zero)
extend-invₐ W s C = fin3-to-non-anchor W (SFin.invₐ s (suc zero))
extend-invₐ W s S = fin3-to-non-anchor W (SFin.invₐ s (suc (suc zero)))
extend-invₐ W s W = W

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
... | suc zero       = inv-l-helper D s zero (suc zero) p
... | suc (suc zero) = inv-l-helper D s zero (suc (suc zero)) p
extend-inv-l D s S with SFin.apply s (suc zero) in p
... | zero           = inv-l-helper D s (suc zero) zero p
... | suc zero       = inv-l-helper D s (suc zero) (suc zero) p
... | suc (suc zero) = inv-l-helper D s (suc zero) (suc (suc zero)) p
extend-inv-l D s W with SFin.apply s (suc (suc zero)) in p
... | zero           = inv-l-helper D s (suc (suc zero)) zero p
... | suc zero       = inv-l-helper D s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-l-helper D s (suc (suc zero)) (suc (suc zero)) p
extend-inv-l C s D with SFin.apply s zero in p
... | zero           = inv-l-helper C s zero zero p
... | suc zero       = inv-l-helper C s zero (suc zero) p
... | suc (suc zero) = inv-l-helper C s zero (suc (suc zero)) p
extend-inv-l C s C = refl
extend-inv-l C s S with SFin.apply s (suc zero) in p
... | zero           = inv-l-helper C s (suc zero) zero p
... | suc zero       = inv-l-helper C s (suc zero) (suc zero) p
... | suc (suc zero) = inv-l-helper C s (suc zero) (suc (suc zero)) p
extend-inv-l C s W with SFin.apply s (suc (suc zero)) in p
... | zero           = inv-l-helper C s (suc (suc zero)) zero p
... | suc zero       = inv-l-helper C s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-l-helper C s (suc (suc zero)) (suc (suc zero)) p
extend-inv-l S s D with SFin.apply s zero in p
... | zero           = inv-l-helper S s zero zero p
... | suc zero       = inv-l-helper S s zero (suc zero) p
... | suc (suc zero) = inv-l-helper S s zero (suc (suc zero)) p
extend-inv-l S s C with SFin.apply s (suc zero) in p
... | zero           = inv-l-helper S s (suc zero) zero p
... | suc zero       = inv-l-helper S s (suc zero) (suc zero) p
... | suc (suc zero) = inv-l-helper S s (suc zero) (suc (suc zero)) p
extend-inv-l S s S = refl
extend-inv-l S s W with SFin.apply s (suc (suc zero)) in p
... | zero           = inv-l-helper S s (suc (suc zero)) zero p
... | suc zero       = inv-l-helper S s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-l-helper S s (suc (suc zero)) (suc (suc zero)) p
extend-inv-l W s D with SFin.apply s zero in p
... | zero           = inv-l-helper W s zero zero p
... | suc zero       = inv-l-helper W s zero (suc zero) p
... | suc (suc zero) = inv-l-helper W s zero (suc (suc zero)) p
extend-inv-l W s C with SFin.apply s (suc zero) in p
... | zero           = inv-l-helper W s (suc zero) zero p
... | suc zero       = inv-l-helper W s (suc zero) (suc zero) p
... | suc (suc zero) = inv-l-helper W s (suc zero) (suc (suc zero)) p
extend-inv-l W s S with SFin.apply s (suc (suc zero)) in p
... | zero           = inv-l-helper W s (suc (suc zero)) zero p
... | suc zero       = inv-l-helper W s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-l-helper W s (suc (suc zero)) (suc (suc zero)) p
extend-inv-l W s W = refl

extend-inv-r :
  (anchor : Axis) (s : SFin.Permutation 3) (x : Axis) →
  extend-apply anchor s (extend-invₐ anchor s x) ≡ x
extend-inv-r D s D = refl
extend-inv-r D s C with SFin.invₐ s zero in p
... | zero           = inv-r-helper D s zero zero p
... | suc zero       = inv-r-helper D s zero (suc zero) p
... | suc (suc zero) = inv-r-helper D s zero (suc (suc zero)) p
extend-inv-r D s S with SFin.invₐ s (suc zero) in p
... | zero           = inv-r-helper D s (suc zero) zero p
... | suc zero       = inv-r-helper D s (suc zero) (suc zero) p
... | suc (suc zero) = inv-r-helper D s (suc zero) (suc (suc zero)) p
extend-inv-r D s W with SFin.invₐ s (suc (suc zero)) in p
... | zero           = inv-r-helper D s (suc (suc zero)) zero p
... | suc zero       = inv-r-helper D s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-r-helper D s (suc (suc zero)) (suc (suc zero)) p
extend-inv-r C s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper C s zero zero p
... | suc zero       = inv-r-helper C s zero (suc zero) p
... | suc (suc zero) = inv-r-helper C s zero (suc (suc zero)) p
extend-inv-r C s C = refl
extend-inv-r C s S with SFin.invₐ s (suc zero) in p
... | zero           = inv-r-helper C s (suc zero) zero p
... | suc zero       = inv-r-helper C s (suc zero) (suc zero) p
... | suc (suc zero) = inv-r-helper C s (suc zero) (suc (suc zero)) p
extend-inv-r C s W with SFin.invₐ s (suc (suc zero)) in p
... | zero           = inv-r-helper C s (suc (suc zero)) zero p
... | suc zero       = inv-r-helper C s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-r-helper C s (suc (suc zero)) (suc (suc zero)) p
extend-inv-r S s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper S s zero zero p
... | suc zero       = inv-r-helper S s zero (suc zero) p
... | suc (suc zero) = inv-r-helper S s zero (suc (suc zero)) p
extend-inv-r S s C with SFin.invₐ s (suc zero) in p
... | zero           = inv-r-helper S s (suc zero) zero p
... | suc zero       = inv-r-helper S s (suc zero) (suc zero) p
... | suc (suc zero) = inv-r-helper S s (suc zero) (suc (suc zero)) p
extend-inv-r S s S = refl
extend-inv-r S s W with SFin.invₐ s (suc (suc zero)) in p
... | zero           = inv-r-helper S s (suc (suc zero)) zero p
... | suc zero       = inv-r-helper S s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-r-helper S s (suc (suc zero)) (suc (suc zero)) p
extend-inv-r W s D with SFin.invₐ s zero in p
... | zero           = inv-r-helper W s zero zero p
... | suc zero       = inv-r-helper W s zero (suc zero) p
... | suc (suc zero) = inv-r-helper W s zero (suc (suc zero)) p
extend-inv-r W s C with SFin.invₐ s (suc zero) in p
... | zero           = inv-r-helper W s (suc zero) zero p
... | suc zero       = inv-r-helper W s (suc zero) (suc zero) p
... | suc (suc zero) = inv-r-helper W s (suc zero) (suc (suc zero)) p
extend-inv-r W s S with SFin.invₐ s (suc (suc zero)) in p
... | zero           = inv-r-helper W s (suc (suc zero)) zero p
... | suc zero       = inv-r-helper W s (suc (suc zero)) (suc zero) p
... | suc (suc zero) = inv-r-helper W s (suc (suc zero)) (suc (suc zero)) p
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
-- Notes
--
-- Slice 14d will define the cross round-trips (restrict ∘ extend ≈
-- id, extend ∘ restrict ≈ id) and bundle as a custom Iso record.
-- Group homomorphism follows.
------------------------------------------------------------------------
