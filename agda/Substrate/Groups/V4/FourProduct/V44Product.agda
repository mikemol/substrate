------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct.V44Product
--
-- Defines: V₄-4-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.FourProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct.V44Product where

open import Substrate.Groups.V4.Operations
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bundle
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Groups.V4.FourProduct.Private
open import Substrate.Groups.V4.FourProduct.ToCInjective
open import Substrate.Groups.V4.FourProduct.NeqTo
open import Substrate.Groups.V4.FourProduct.ToC



------------------------------------------------------------------------
-- V₄-4-product: four pairwise-distinct V₄ elements multiply to ε.
------------------------------------------------------------------------

V₄-4-product :
  (a b c d : V₄) →
  a ≢ b → a ≢ c → a ≢ d → b ≢ c → b ≢ d → c ≢ d →
  (a ·₄ b) ·₄ (c ·₄ d) ≡ ε
V₄-4-product a b c d a≢b a≢c a≢d b≢c b≢d c≢d =
  to-c-injective ((a ·₄ b) ·₄ (c ·₄ d)) e bridge
  where
    coxeter-result :
      ((to-c a C.· to-c b) C.· (to-c c C.· to-c d)) C.≈ []
    coxeter-result =
      C.V₄-4-product (to-c a) (to-c b) (to-c c) (to-c d)
        (≢→≉ a≢b) (≢→≉ a≢c) (≢→≉ a≢d)
        (≢→≉ b≢c) (≢→≉ b≢d) (≢→≉ c≢d)

    bridge : to-c ((a ·₄ b) ·₄ (c ·₄ d)) ≡ []
    bridge =
      trans (to-c-· (a ·₄ b) (c ·₄ d))
      (cong-trans (λ x → C.normalize (x ++ to-c (c ·₄ d)))
                  (to-c-· a b)
      (cong-trans (λ x → C.normalize ((to-c a C.· to-c b) ++ x))
                  (to-c-· c d)
      (sym-trans (C.normalize-idem
                    ((to-c a C.· to-c b) ++ (to-c c C.· to-c d)))
                 coxeter-result)))
