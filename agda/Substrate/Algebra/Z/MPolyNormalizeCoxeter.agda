{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalizeCoxeter — ⟡normalize-via-coxeter.
--
-- RUNG 3a's polynomial `normalize` is an INSTANCE of the tower's carrier-
-- agnostic Coxeter normalizer `Groups.Coxeter.Core`. The multivariate-ℤ
-- monomial-COMBINING sorted-insert normal form satisfies the same
-- normalization-bearing-monoid interface as V₄'s abelian sorted words, so
-- instantiating `Core` at (MPoly, ++, isSortedB, normalize) inherits the whole
-- word-algebra — the monoid `_·_ = normalize (a ++ b)`, the quotient `_≈_`,
-- `normalize-idem`, the higher-arity/clash macros — and makes `normalize`
-- DISCOVERABLE as the generalized-Sₙ normalization it is, not a parallel
-- rebuild (`JacobianResidue`'s "HONEST DEBT" header).
--
-- `Core` is carrier-agnostic (`Word : Set` abstract), so there is NO
-- List↔Coxeter.Word bridge: `Word := MPoly` directly. Three of the four
-- obligations are discharged VERBATIM by RUNG 3a (normalize-sorted,
-- normalize-fixed) + `++-assoc`; the one new lemma `normalize-distrib` is a
-- one-shot `coeff-canonicity` argument — `normalize` is a monoid hom onto
-- sorted forms because `coeff` is additive over `++`.
------------------------------------------------------------------------

module Substrate.Algebra.Z.MPolyNormalizeCoxeter where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong₂)
open import Substrate.Foundation.List using ([]; _++_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.JacobianResidue using (MPoly; tt)
open import Substrate.Algebra.Z.MPolyNormalize using (isSortedB; normalize)
open import Substrate.Algebra.Z.MPolyNormalize.Properties
  using (normalize-sorted; normalize-fixed; coeff-normalize; coeff-++)
open import Substrate.Algebra.Z.MPolySemiring using (coeff-canonicity; ++-assoc)

-- The ONE new obligation: normalize is a monoid hom onto sorted forms.
normalize-distrib : (a b : MPoly) →
                    normalize (a ++ b) ≡ normalize (normalize a ++ normalize b)
normalize-distrib a b =
  coeff-canonicity (normalize (a ++ b)) (normalize (normalize a ++ normalize b))
    (normalize-sorted (a ++ b)) (normalize-sorted (normalize a ++ normalize b))
    (λ j → trans (coeff-normalize j (a ++ b))
           (trans (coeff-++ j a b)
           (trans (cong₂ _+ℤ_ (sym (coeff-normalize j a)) (sym (coeff-normalize j b)))
           (trans (sym (coeff-++ j (normalize a) (normalize b)))
                  (sym (coeff-normalize j (normalize a ++ normalize b)))))))

-- The Core instance: MPoly's normal form AS a Coxeter normalization-monoid.
-- Re-exports _·_ / _≈_ / _≉_ / ε / normalize-idem / higher-arity / clash.
open import Substrate.Groups.Coxeter.Core
  MPoly _++_ [] (λ a b c → ++-assoc a b c) (λ w → isSortedB w ≡ tt) normalize
  normalize-sorted (λ {w} → normalize-fixed w) normalize-distrib
  public
