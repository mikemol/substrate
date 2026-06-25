------------------------------------------------------------------------
-- Substrate.Category.FreeUniversalProperty.PackageComm
--
-- THE STRATEGY-SELECTION LICENSE — `package-comm`. Any two packagings of the
-- free object on the SAME basis B (same AlgebraClass A) are UNIQUELY isomorphic.
-- This is the precise form of the user's intuition that "extend+uniqueness feels
-- like a group with packaging-transitions as actions, and the invariant licenses
-- on-the-fly strategy selection":
--
--   • The packagings form a CONTRACTIBLE groupoid: between any two free objects
--     there is a UNIQUE comparison iso (`compare`, `compare-unique`). The
--     automorphism "group" of a single packaging is therefore TRIVIAL — the
--     ∃!-uniqueness clause kills the loops. That triviality IS the license:
--     compute in whichever packaging is cheap, transport along the canonical
--     iso, GUARANTEED to agree (path-independence of a contractible groupoid).
--   • Basis-agnostic: `FreeUP`'s basis is `B : Set`, so this subsumes the Fin-
--     bound packaging (FreeLinearizationR / FreeBasisUniversal) AND any arbitrary
--     -basis one — they are the same object up to the unique `compare`.
--
-- The genuine (non-trivial) group content lives one level up — in Aut(B), the
-- BASIS symmetry (e.g. S_{n+1} on faces, or the V₄ = ⟨†, bar⟩ of Wedge.StarV4) —
-- and that action is packaging-independent precisely BECAUSE `compare` is unique.
--
-- Hypotheses: that A's structure-preservation is a CATEGORY (identity preserves,
-- composition preserves) — the only facts beyond the FreeUP record the proof needs.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeUniversalProperty.PackageComm where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Category.FreeOverBasis
  using (AlgebraClass; Has-structure; Hom-preserves)
open import Substrate.Category.FreeUniversalProperty using (FreeUP)
open FreeUP

module _
  {A : AlgebraClass} {B : Set}
  -- A's structure-preservation forms a category:
  (id-pres : {M : Set} (hM : Has-structure A M) →
             Hom-preserves A hM hM (λ x → x))
  (∘-pres  : {M N P : Set}
             (hM : Has-structure A M) (hN : Has-structure A N) (hP : Has-structure A P)
             (g : N → P) (f : M → N) →
             Hom-preserves A hN hP g → Hom-preserves A hM hN f →
             Hom-preserves A hM hP (λ x → g (f x)))
  {F F′ : Set} (fr : FreeUP A B F) (fr′ : FreeUP A B F′)
  where

  ------------------------------------------------------------------------
  -- The comparison maps: each extends the other's unit.
  ------------------------------------------------------------------------

  compare : F → F′
  compare = extend fr (free-has fr′) (unit fr′)

  compare⁻¹ : F′ → F
  compare⁻¹ = extend fr′ (free-has fr) (unit fr)

  -- both are structure-preserving (FreeUP.extend-preserves).
  private
    compare-pres : Hom-preserves A (free-has fr) (free-has fr′) compare
    compare-pres = extend-preserves fr (free-has fr′) (unit fr′)

    compare⁻¹-pres : Hom-preserves A (free-has fr′) (free-has fr) compare⁻¹
    compare⁻¹-pres = extend-preserves fr′ (free-has fr) (unit fr)

  ------------------------------------------------------------------------
  -- The round trips are the identity — by extend-unique (both the round trip
  -- and id extend `unit` along itself, and the extension is unique).
  ------------------------------------------------------------------------

  compare-invˡ : (x : F) → compare⁻¹ (compare x) ≡ x
  compare-invˡ x = trans (round x) (sym (idy x))
    where
      on-unit : (b : B) → compare⁻¹ (compare (unit fr b)) ≡ unit fr b
      on-unit b = trans (cong compare⁻¹ (extend-extends fr (free-has fr′) (unit fr′) b))
                        (extend-extends fr′ (free-has fr) (unit fr) b)
      rt-pres : Hom-preserves A (free-has fr) (free-has fr) (λ x → compare⁻¹ (compare x))
      rt-pres = ∘-pres (free-has fr) (free-has fr′) (free-has fr)
                       compare⁻¹ compare compare⁻¹-pres compare-pres
      round : (x : F) → compare⁻¹ (compare x) ≡ extend fr (free-has fr) (unit fr) x
      round = extend-unique fr (free-has fr) (unit fr)
                (λ x → compare⁻¹ (compare x)) rt-pres on-unit
      idy : (x : F) → x ≡ extend fr (free-has fr) (unit fr) x
      idy = extend-unique fr (free-has fr) (unit fr)
              (λ x → x) (id-pres (free-has fr)) (λ b → refl)

  compare-invʳ : (y : F′) → compare (compare⁻¹ y) ≡ y
  compare-invʳ y = trans (round y) (sym (idy y))
    where
      on-unit : (b : B) → compare (compare⁻¹ (unit fr′ b)) ≡ unit fr′ b
      on-unit b = trans (cong compare (extend-extends fr′ (free-has fr) (unit fr) b))
                        (extend-extends fr (free-has fr′) (unit fr′) b)
      rt-pres : Hom-preserves A (free-has fr′) (free-has fr′) (λ y → compare (compare⁻¹ y))
      rt-pres = ∘-pres (free-has fr′) (free-has fr) (free-has fr′)
                       compare compare⁻¹ compare-pres compare⁻¹-pres
      round : (y : F′) → compare (compare⁻¹ y) ≡ extend fr′ (free-has fr′) (unit fr′) y
      round = extend-unique fr′ (free-has fr′) (unit fr′)
                (λ y → compare (compare⁻¹ y)) rt-pres on-unit
      idy : (y : F′) → y ≡ extend fr′ (free-has fr′) (unit fr′) y
      idy = extend-unique fr′ (free-has fr′) (unit fr′)
              (λ y → y) (id-pres (free-has fr′)) (λ b → refl)

  ------------------------------------------------------------------------
  -- THE ISO IS UNIQUE: any structure-preserving h commuting with the units
  -- IS `compare`. This is the contractibility — the loop-killing clause that
  -- makes strategy selection canonical.
  ------------------------------------------------------------------------

  compare-unique :
    (h : F → F′) → Hom-preserves A (free-has fr) (free-has fr′) h →
    ((b : B) → h (unit fr b) ≡ unit fr′ b) →
    (x : F) → h x ≡ compare x
  compare-unique h h-pres h-unit =
    extend-unique fr (free-has fr′) (unit fr′) h h-pres h-unit
