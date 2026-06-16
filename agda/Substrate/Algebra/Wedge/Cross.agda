------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Cross
--
-- THE CROSS-COMBINATION of two carriers (first form). Combining two DivStrs
-- A, B into one over the cross-carrier C A × C B. Since the quotient is now a
-- CARRIER REPRESENTATIVE (recon : C → C → C → C), the product carrier's quotient
-- is a PAIR (qₐ , q_b) — each strand reduced by its OWN representative. A wedge
-- in `A ⊗ᴰ B` is thus the free product reduction of an A-element and a
-- B-element. This is the cross-silo correspondence structure; its carrier-free
-- `Shape` of a run is the per-strand quotient sequence (now `List (C D)`).
--
-- The braiding the heterogeneous wedge wants is, at this form, the product
-- SYMMETRY  C A × C B ≅ C B × C A  (swap numerator/denominator carriers).
--
-- HONEST SCOPE: the SYNCHRONIZED/lockstep correspondence — both strands reduced
-- by ONE shared quotient — was an artifact of the old baked ℕ quotient (one ℕ
-- drove both). Under carrier-representative quotients the two strands live in
-- different carriers, so a genuinely shared quotient must live in a COMMON
-- carrier with bridges to each strand: that is `CrossMul`'s cospan A → R ← B
-- (the bilinear mixing, where the residue is nilpotent of a graded degree).
-- `shared-quot` below is therefore now the DIAGONAL condition, not automatic.
-- What is here: the product carrier, the free per-strand reduction, the
-- symmetry, and the projections that read a correspondence into its components.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Cross where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge
  using (DivStr; C; z; recon; Wedge; quot; rem; wedge-eq)

------------------------------------------------------------------------
-- 1. The product DivStr: cross-carrier, shared quotient.
------------------------------------------------------------------------

_⊗ᴰ_ : DivStr → DivStr → DivStr
A ⊗ᴰ B = record
  { C     = C A × C B
  ; z     = z A , z B
  ; recon = λ q p p′ → recon A (proj₁ q) (proj₁ p) (proj₁ p′)
                     , recon B (proj₂ q) (proj₂ p) (proj₂ p′)
  }

------------------------------------------------------------------------
-- 2. A correspondence-wedge reads back into its two component reductions,
--    sharing one quotient — the lockstep that IS the correspondence.
------------------------------------------------------------------------

wedge-fst : (A B : DivStr) {a a′ : C A} {b b′ : C B} →
            Wedge (A ⊗ᴰ B) (a , b) (a′ , b′) → Wedge A a a′
wedge-fst A B w = record
  { quot = proj₁ (quot w) ; rem = proj₁ (rem w) ; wedge-eq = cong proj₁ (wedge-eq w) }

wedge-snd : (A B : DivStr) {a a′ : C A} {b b′ : C B} →
            Wedge (A ⊗ᴰ B) (a , b) (a′ , b′) → Wedge B b b′
wedge-snd A B w = record
  { quot = proj₂ (quot w) ; rem = proj₂ (rem w) ; wedge-eq = cong proj₂ (wedge-eq w) }

-- the quotient is now a PAIR: the two component reads recover its two
-- projections, and pairing them back reconstructs the product quotient (η).
-- Lockstep (one shared quotient driving both strands) is the DIAGONAL of this
-- pair — no longer automatic; the unconditional shared quotient lives in
-- CrossMul's common carrier R (the cospan A → R ← B).
quot-is-pair : (A B : DivStr) {a a′ : C A} {b b′ : C B}
               (w : Wedge (A ⊗ᴰ B) (a , b) (a′ , b′)) →
               (quot (wedge-fst A B w) , quot (wedge-snd A B w)) ≡ quot w
quot-is-pair A B w = refl
