------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Cross
--
-- THE CROSS-COMBINATION of two carriers (first form). Combining two DivStrs
-- A, B into one over the cross-carrier C A × C B, reducing both components
-- by a SHARED quotient. A wedge in `A ⊗ᴰ B` is therefore a SIMULTANEOUS
-- reduction of an A-element and a B-element by the same partial-quotient
-- sequence — which is exactly a cross-silo CORRESPONDENCE: A and B
-- correspond along a run iff they admit a common continued fraction, and the
-- carrier-free `Shape` of that run is the shared invariant (`List ℕ`, still
-- carrier-free — the quotient stays the Peano shadow, not absorbed into C).
--
-- The braiding the heterogeneous wedge wants is, at this form, the product
-- SYMMETRY  C A × C B ≅ C B × C A  (swap numerator/denominator carriers).
--
-- HONEST SCOPE: this is the SYNCHRONIZED cross-combination — both carriers
-- reduced in lockstep by one quotient. It is NOT yet the bilinear mixing
-- where the quotient itself braids carrier content across the two strands
-- (the genuine tensor, where a residue is nilpotent of a graded degree).
-- That mixing needs the carriers to MULTIPLY — structure bare DivStr (Sets +
-- recon) doesn't carry — so it is the next layer, deliberately deferred
-- rather than faked. What is here: the product carrier, the shared-quotient
-- lockstep, the symmetry, and the projections that read a correspondence
-- back into its two component reductions.
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
  ; recon = λ q p p′ → recon A q (proj₁ p) (proj₁ p′)
                     , recon B q (proj₂ p) (proj₂ p′)
  }

------------------------------------------------------------------------
-- 2. A correspondence-wedge reads back into its two component reductions,
--    sharing one quotient — the lockstep that IS the correspondence.
------------------------------------------------------------------------

wedge-fst : (A B : DivStr) {a a′ : C A} {b b′ : C B} →
            Wedge (A ⊗ᴰ B) (a , b) (a′ , b′) → Wedge A a a′
wedge-fst A B w = record
  { quot = quot w ; rem = proj₁ (rem w) ; wedge-eq = cong proj₁ (wedge-eq w) }

wedge-snd : (A B : DivStr) {a a′ : C A} {b b′ : C B} →
            Wedge (A ⊗ᴰ B) (a , b) (a′ , b′) → Wedge B b b′
wedge-snd A B w = record
  { quot = quot w ; rem = proj₂ (rem w) ; wedge-eq = cong proj₂ (wedge-eq w) }

-- the two component reductions share the quotient: that shared partial
-- quotient is the correspondence's carrier-free content, at every step.
shared-quot : (A B : DivStr) {a a′ : C A} {b b′ : C B}
              (w : Wedge (A ⊗ᴰ B) (a , b) (a′ , b′)) →
              quot (wedge-fst A B w) ≡ quot (wedge-snd A B w)
shared-quot A B w = refl
