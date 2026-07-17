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

module _
  {Has : Set → Set}
  {HomP : {M N : Set} → Has M → Has N → (M → N) → Set}
  {A : AlgebraClass Has HomP} {B : Set}
  -- A's structure-preservation forms a category:
  (id-pres : {M : Set} (hM : Has-structure A M) →
             Hom-preserves A hM hM (λ x → x))
  (∘-pres  : {M N P : Set}
             (hM : Has-structure A M) (hN : Has-structure A N) (hP : Has-structure A P)
             (g : N → P) (f : M → N) →
             Hom-preserves A hN hP g → Hom-preserves A hM hN f →
             Hom-preserves A hM hP (λ x → g (f x)))
  {F F′ : Set}
  {u  : B → F}
  {fh : Has-structure A F}
  {ex : {M : Set} → Has-structure A M → (B → M) → (F → M)}
  {ep : {M : Set} (hM : Has-structure A M) (f : B → M) →
        Hom-preserves A fh hM (ex hM f)}
  {ee : {M : Set} (hM : Has-structure A M) (f : B → M) (b : B) →
        ex hM f (u b) ≡ f b}
  {eu : {M : Set} (hM : Has-structure A M) (f : B → M)
        (g : F → M) → Hom-preserves A fh hM g →
        ((b : B) → g (u b) ≡ f b) →
        (x : F) → g x ≡ ex hM f x}
  {u′  : B → F′}
  {fh′ : Has-structure A F′}
  {ex′ : {M : Set} → Has-structure A M → (B → M) → (F′ → M)}
  {ep′ : {M : Set} (hM : Has-structure A M) (f : B → M) →
         Hom-preserves A fh′ hM (ex′ hM f)}
  {ee′ : {M : Set} (hM : Has-structure A M) (f : B → M) (b : B) →
         ex′ hM f (u′ b) ≡ f b}
  {eu′ : {M : Set} (hM : Has-structure A M) (f : B → M)
         (g : F′ → M) → Hom-preserves A fh′ hM g →
         ((b : B) → g (u′ b) ≡ f b) →
         (x : F′) → g x ≡ ex′ hM f x}
  (fr : FreeUP A B F u fh ex ep ee eu) (fr′ : FreeUP A B F′ u′ fh′ ex′ ep′ ee′ eu′)
  where

  ------------------------------------------------------------------------
  -- The comparison maps: each extends the other's unit.
  ------------------------------------------------------------------------

  compare : F → F′
  compare = ex fh′ u′

  compare⁻¹ : F′ → F
  compare⁻¹ = ex′ fh u

  -- both are structure-preserving (FreeUP.extend-preserves).
  private
    compare-pres : Hom-preserves A fh fh′ compare
    compare-pres = ep fh′ u′

    compare⁻¹-pres : Hom-preserves A fh′ fh compare⁻¹
    compare⁻¹-pres = ep′ fh u

  ------------------------------------------------------------------------
  -- The round trips are the identity — by extend-unique (both the round trip
  -- and id extend `unit` along itself, and the extension is unique).
  ------------------------------------------------------------------------

  compare-invˡ : (x : F) → compare⁻¹ (compare x) ≡ x
  compare-invˡ x = trans (round x) (sym (idy x))
    where
      on-unit : (b : B) → compare⁻¹ (compare (u b)) ≡ u b
      on-unit b = trans (cong compare⁻¹ (ee fh′ u′ b))
                        (ee′ fh u b)
      rt-pres : Hom-preserves A fh fh (λ x → compare⁻¹ (compare x))
      rt-pres = ∘-pres fh fh′ fh
                       compare⁻¹ compare compare⁻¹-pres compare-pres
      round : (x : F) → compare⁻¹ (compare x) ≡ ex fh u x
      round = eu fh u
                (λ x → compare⁻¹ (compare x)) rt-pres on-unit
      idy : (x : F) → x ≡ ex fh u x
      idy = eu fh u
              (λ x → x) (id-pres fh) (λ b → refl)

  compare-invʳ : (y : F′) → compare (compare⁻¹ y) ≡ y
  compare-invʳ y = trans (round y) (sym (idy y))
    where
      on-unit : (b : B) → compare (compare⁻¹ (u′ b)) ≡ u′ b
      on-unit b = trans (cong compare (ee′ fh u b))
                        (ee fh′ u′ b)
      rt-pres : Hom-preserves A fh′ fh′ (λ y → compare (compare⁻¹ y))
      rt-pres = ∘-pres fh′ fh fh′
                       compare compare⁻¹ compare-pres compare⁻¹-pres
      round : (y : F′) → compare (compare⁻¹ y) ≡ ex′ fh′ u′ y
      round = eu′ fh′ u′
                (λ y → compare (compare⁻¹ y)) rt-pres on-unit
      idy : (y : F′) → y ≡ ex′ fh′ u′ y
      idy = eu′ fh′ u′
              (λ y → y) (id-pres fh′) (λ b → refl)

  ------------------------------------------------------------------------
  -- THE ISO IS UNIQUE: any structure-preserving h commuting with the units
  -- IS `compare`. This is the contractibility — the loop-killing clause that
  -- makes strategy selection canonical.
  ------------------------------------------------------------------------

  compare-unique :
    (h : F → F′) → Hom-preserves A fh fh′ h →
    ((b : B) → h (u b) ≡ u′ b) →
    (x : F) → h x ≡ compare x
  compare-unique h h-pres h-unit =
    eu fh′ u′ h h-pres h-unit
