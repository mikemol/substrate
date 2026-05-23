------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3-Iso
--
-- Slice 14d: bundles the parametric Stab(anchor) ≅ S_3 iso. Two
-- round trips + custom Iso record.
--
-- Round trips:
--   restrict-extend : ∀ anchor s i, SFin.apply (restrict anchor
--                     (extend anchor s)) i ≡ SFin.apply s i.
--                     12 cases (4 anchor × 3 Fin 3).
--   extend-restrict : ∀ anchor σ σ-stab x, applyₛ (proj₁ (extend
--                     anchor (restrict anchor (σ, σ-stab)))) x
--                     ≡ applyₛ σ x.
--                     16 cases (4 anchor × 4 axis).
--
-- For non-anchor cases, the proofs use:
--   restrict-extend: non-anchor-to-fin3-cong + fin3-non-anchor-fin3.
--   extend-restrict: non-anchor-fin3-non-anchor (with the same
--     stab-preserves-≢ proof that restrict-apply's body uses).
--
-- For anchor cases (4 anchor-equal pairs):
--   extend-restrict: sym σ-stab (the identity component).
--
-- The bundle (`Stab≃S₃`) is a custom Iso record using pointwise _≡_
-- on each side (SFin.apply for Fin 3, applyₛ for Axis). Group
-- homomorphism (compositions / identity / inverse preserved) is
-- deferred to slice 14e if downstream theorems need it.
--
-- Chirality discipline (per slice 14a + memory feedback-ordering-is-
-- chirality-choice): the iso depends on the Fin 3 ↔ non-anchor-axis
-- convention. Any of the 6 valid orderings gives an iso differing by
-- an S_3 inner automorphism — the iso is unique only up to that.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3-Iso where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 as S4
  using (Permutation)
  renaming (apply to applyₛ)
import Substrate.Groups.SFin as SFin
open import Substrate.Groups.Stab-S3
  using (Stab; fin3-to-non-anchor; fin3-to-non-anchor-≢;
         non-anchor-to-fin3; non-anchor-fin3-non-anchor;
         fin3-non-anchor-fin3; stab-preserves-≢)
open import Substrate.Groups.Stab-S3-Restrict
  using (non-anchor-to-fin3-cong; restrict)
open import Substrate.Groups.Stab-S3-Extend using (extend)

------------------------------------------------------------------------
-- restrict-extend: round trip on the SFin.Permutation 3 side.
------------------------------------------------------------------------

restrict-extend :
  (anchor : Axis) (s : SFin.Permutation 3) (i : Fin 3) →
  SFin.apply (restrict anchor (extend anchor s)) i ≡ SFin.apply s i
restrict-extend D s zero =
  trans (non-anchor-to-fin3-cong D refl _
          (fin3-to-non-anchor-≢ D (SFin.apply s zero)))
        (fin3-non-anchor-fin3 D (SFin.apply s zero))
restrict-extend D s ₁ =
  trans (non-anchor-to-fin3-cong D refl _
          (fin3-to-non-anchor-≢ D (SFin.apply s ₁)))
        (fin3-non-anchor-fin3 D (SFin.apply s ₁))
restrict-extend D s ₂ =
  trans (non-anchor-to-fin3-cong D refl _
          (fin3-to-non-anchor-≢ D (SFin.apply s ₂)))
        (fin3-non-anchor-fin3 D (SFin.apply s ₂))
restrict-extend C s zero =
  trans (non-anchor-to-fin3-cong C refl _
          (fin3-to-non-anchor-≢ C (SFin.apply s zero)))
        (fin3-non-anchor-fin3 C (SFin.apply s zero))
restrict-extend C s ₁ =
  trans (non-anchor-to-fin3-cong C refl _
          (fin3-to-non-anchor-≢ C (SFin.apply s ₁)))
        (fin3-non-anchor-fin3 C (SFin.apply s ₁))
restrict-extend C s ₂ =
  trans (non-anchor-to-fin3-cong C refl _
          (fin3-to-non-anchor-≢ C (SFin.apply s ₂)))
        (fin3-non-anchor-fin3 C (SFin.apply s ₂))
restrict-extend S s zero =
  trans (non-anchor-to-fin3-cong S refl _
          (fin3-to-non-anchor-≢ S (SFin.apply s zero)))
        (fin3-non-anchor-fin3 S (SFin.apply s zero))
restrict-extend S s ₁ =
  trans (non-anchor-to-fin3-cong S refl _
          (fin3-to-non-anchor-≢ S (SFin.apply s ₁)))
        (fin3-non-anchor-fin3 S (SFin.apply s ₁))
restrict-extend S s ₂ =
  trans (non-anchor-to-fin3-cong S refl _
          (fin3-to-non-anchor-≢ S (SFin.apply s ₂)))
        (fin3-non-anchor-fin3 S (SFin.apply s ₂))
restrict-extend W s zero =
  trans (non-anchor-to-fin3-cong W refl _
          (fin3-to-non-anchor-≢ W (SFin.apply s zero)))
        (fin3-non-anchor-fin3 W (SFin.apply s zero))
restrict-extend W s ₁ =
  trans (non-anchor-to-fin3-cong W refl _
          (fin3-to-non-anchor-≢ W (SFin.apply s ₁)))
        (fin3-non-anchor-fin3 W (SFin.apply s ₁))
restrict-extend W s ₂ =
  trans (non-anchor-to-fin3-cong W refl _
          (fin3-to-non-anchor-≢ W (SFin.apply s ₂)))
        (fin3-non-anchor-fin3 W (SFin.apply s ₂))

------------------------------------------------------------------------
-- extend-restrict: round trip on the Σ Permutation (Stab anchor) side.
------------------------------------------------------------------------

extend-restrict :
  (anchor : Axis) (σ : Permutation) (σ-stab : Stab anchor σ) (x : Axis) →
  applyₛ (proj₁ (extend anchor (restrict anchor (σ , σ-stab)))) x
  ≡ applyₛ σ x
extend-restrict D σ σ-stab D = sym σ-stab
extend-restrict D σ σ-stab C =
  non-anchor-fin3-non-anchor D (applyₛ σ C)
    (stab-preserves-≢ D σ σ-stab C (fin3-to-non-anchor-≢ D zero))
extend-restrict D σ σ-stab S =
  non-anchor-fin3-non-anchor D (applyₛ σ S)
    (stab-preserves-≢ D σ σ-stab S (fin3-to-non-anchor-≢ D ₁))
extend-restrict D σ σ-stab W =
  non-anchor-fin3-non-anchor D (applyₛ σ W)
    (stab-preserves-≢ D σ σ-stab W (fin3-to-non-anchor-≢ D ₂))
extend-restrict C σ σ-stab D =
  non-anchor-fin3-non-anchor C (applyₛ σ D)
    (stab-preserves-≢ C σ σ-stab D (fin3-to-non-anchor-≢ C zero))
extend-restrict C σ σ-stab C = sym σ-stab
extend-restrict C σ σ-stab S =
  non-anchor-fin3-non-anchor C (applyₛ σ S)
    (stab-preserves-≢ C σ σ-stab S (fin3-to-non-anchor-≢ C ₁))
extend-restrict C σ σ-stab W =
  non-anchor-fin3-non-anchor C (applyₛ σ W)
    (stab-preserves-≢ C σ σ-stab W (fin3-to-non-anchor-≢ C ₂))
extend-restrict S σ σ-stab D =
  non-anchor-fin3-non-anchor S (applyₛ σ D)
    (stab-preserves-≢ S σ σ-stab D (fin3-to-non-anchor-≢ S zero))
extend-restrict S σ σ-stab C =
  non-anchor-fin3-non-anchor S (applyₛ σ C)
    (stab-preserves-≢ S σ σ-stab C (fin3-to-non-anchor-≢ S ₁))
extend-restrict S σ σ-stab S = sym σ-stab
extend-restrict S σ σ-stab W =
  non-anchor-fin3-non-anchor S (applyₛ σ W)
    (stab-preserves-≢ S σ σ-stab W (fin3-to-non-anchor-≢ S ₂))
extend-restrict W σ σ-stab D =
  non-anchor-fin3-non-anchor W (applyₛ σ D)
    (stab-preserves-≢ W σ σ-stab D (fin3-to-non-anchor-≢ W zero))
extend-restrict W σ σ-stab C =
  non-anchor-fin3-non-anchor W (applyₛ σ C)
    (stab-preserves-≢ W σ σ-stab C (fin3-to-non-anchor-≢ W ₁))
extend-restrict W σ σ-stab S =
  non-anchor-fin3-non-anchor W (applyₛ σ S)
    (stab-preserves-≢ W σ σ-stab S (fin3-to-non-anchor-≢ W ₂))
extend-restrict W σ σ-stab W = sym σ-stab

------------------------------------------------------------------------
-- The bundled iso.
------------------------------------------------------------------------

record Stab≃S₃ (anchor : Axis) : Set where
  field
    to       : Σ Permutation (Stab anchor) → SFin.Permutation 3
    from     : SFin.Permutation 3 → Σ Permutation (Stab anchor)
    to-from  : (s : SFin.Permutation 3) (i : Fin 3) →
               SFin.apply (to (from s)) i ≡ SFin.apply s i
    from-to  : (xy : Σ Permutation (Stab anchor)) (x : Axis) →
               applyₛ (proj₁ (from (to xy))) x ≡ applyₛ (proj₁ xy) x

stab≃s₃ : (anchor : Axis) → Stab≃S₃ anchor
stab≃s₃ anchor = record
  { to      = restrict anchor
  ; from    = extend anchor
  ; to-from = restrict-extend anchor
  ; from-to = λ { (σ , σ-stab) x → extend-restrict anchor σ σ-stab x }
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. The full iso closes parametric Stab(anchor) ≅ S_3 for every
--    anchor ∈ Axis. The catalog's V_4 ⋊ S_3 ≅ S_4 picture is now
--    closed at every relevant layer:
--    - Factorisation (slice 3): every σ = embed v · s with s ∈ Stab D.
--    - Normality (slices 9, 12): V_4 is normal in S_4.
--    - Coset bijection (slice 13): S_4/V_4 ↔ Stab(D) structurally.
--    - Stab ≅ S_3 (slice 14a-d): every Stab(anchor) is ≅ S_3 as a
--      set bijection with pointwise structure.
--
-- 2. Group homomorphism (composition / identity / inverse preserved
--    under the iso) is deferred to a slice 14e if needed. The
--    set-bijection here is the structural content of the catalog
--    claim; the homomorphism would lift it to a Group iso bundle.
--
-- 3. Chirality discipline: the iso depends on our Fin 3 ↔ non-anchor-
--    axis convention. Any of the 6 valid orderings gives an iso
--    differing by an S_3 inner automorphism. The iso is unique only
--    up to that S_3-action (per
--    [[feedback-ordering-is-chirality-choice]]).
--
-- 4. Cross-references:
--    * Slice 14a: parametric Stab + bridges.
--    * Slice 14b: bundled restrict + proof-irrelevance.
--    * Slice 14c: bundled extend.
--    * Slice 5: SFin.Permutation 3 — the S_3 carrier.
--    * Slice 3: Stab D (= Stab D in the parametric form).
------------------------------------------------------------------------
