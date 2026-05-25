------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct
--
-- V₄-4-product: four pairwise-distinct V₄ elements multiply to ε.
-- Delegated to V4-Coxeter's V₄-4-product via the bijection.
--
-- Consumed by Substrate.Groups.V4-Normality (`case-any-no-fix`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; _≢_; sym-trans; cong-trans)

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word using ([])

open import Substrate.Groups.V4.Bundle public

------------------------------------------------------------------------
-- Bijection injectivity + inequality lift.
------------------------------------------------------------------------

private
  -- to-c is injective: distinct V₄ ctors map to distinct canonical Words.
  to-c-injective : (x y : V₄) → to-c x ≡ to-c y → x ≡ y
  to-c-injective e e _  = refl
  to-c-injective α α _  = refl
  to-c-injective β β _  = refl
  to-c-injective γ γ _  = refl
  to-c-injective e α ()
  to-c-injective e β ()
  to-c-injective e γ ()
  to-c-injective α e ()
  to-c-injective α β ()
  to-c-injective α γ ()
  to-c-injective β e ()
  to-c-injective β α ()
  to-c-injective β γ ()
  to-c-injective γ e ()
  to-c-injective γ α ()
  to-c-injective γ β ()

  -- Lift V₄ inequality to canonical-Word inequality via to-c.
  ≢→≉ : {x y : V₄} → x ≢ y → to-c x C.≉ to-c y
  ≢→≉ {x} {y} ineq normalize-eq =
    ineq (to-c-injective x y
            (sym-trans (C.canonical-is-fixed-V4 (to-c-canonical x))
                       (trans normalize-eq
                              (C.canonical-is-fixed-V4 (to-c-canonical y)))))

  -- Bridge: to-c (a · b) ≡ to-c a C.· to-c b.
  to-c-· : (a b : V₄) → to-c (a · b) ≡ to-c a C.· to-c b
  to-c-· a b =
    trans (to-from-canonical
            (C.normalize-canonical (to-c a C.· to-c b)))
          (C.normalize-idem (to-c a C.++ to-c b))

------------------------------------------------------------------------
-- V₄-4-product: four pairwise-distinct V₄ elements multiply to ε.
------------------------------------------------------------------------

V₄-4-product :
  (a b c d : V₄) →
  a ≢ b → a ≢ c → a ≢ d → b ≢ c → b ≢ d → c ≢ d →
  (a · b) · (c · d) ≡ ε
V₄-4-product a b c d a≢b a≢c a≢d b≢c b≢d c≢d =
  to-c-injective ((a · b) · (c · d)) e bridge
  where
    coxeter-result :
      ((to-c a C.· to-c b) C.· (to-c c C.· to-c d)) C.≈ []
    coxeter-result =
      C.V₄-4-product (to-c a) (to-c b) (to-c c) (to-c d)
        (≢→≉ a≢b) (≢→≉ a≢c) (≢→≉ a≢d)
        (≢→≉ b≢c) (≢→≉ b≢d) (≢→≉ c≢d)

    bridge : to-c ((a · b) · (c · d)) ≡ []
    bridge =
      trans (to-c-· (a · b) (c · d))
      (cong-trans (λ x → C.normalize (x C.++ to-c (c · d)))
                  (to-c-· a b)
      (cong-trans (λ x → C.normalize ((to-c a C.· to-c b) C.++ x))
                  (to-c-· c d)
      (sym-trans (C.normalize-idem
                    ((to-c a C.· to-c b) C.++ (to-c c C.· to-c d)))
                 coxeter-result)))
