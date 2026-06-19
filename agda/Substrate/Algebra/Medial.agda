------------------------------------------------------------------------
-- Substrate.Algebra.Medial  (Ⓜ)
--
-- The MEDIAL law (a.k.a. middle-four exchange / the interchange law of a
-- single commutative operation):
--
--     (w · x) · (y · z)  ≡  (w · y) · (x · z).
--
-- It is the commutative-semigroup law that lets two independent pairings be
-- regrouped. It follows from ASSOCIATIVITY + COMMUTATIVITY alone — identity
-- (and hence the full CommutativeMonoid record) is NOT needed — so the apex is
-- parameterized by exactly those two laws. Every carrier instantiates by
-- passing its own `·`/assoc/comm: F₂'s `+` (RingLaws.Distrib, GF256.Xtime,
-- Linear.ImagesProps), a graded ring's `+` (Polynomial.Graded), a free
-- F₂-module's `⊕` (FreeUniversalProperty.FreeF2Module) — each previously
-- re-proved this exact `trans/cong` chain.
--
-- (The categorical name is the medial law of the CommutativeMonoid in
-- Substrate.Category.CommutativeMonoid; this module is the law itself, with no
-- record bundling, so the loose-parameter carriers can instantiate it too.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Medial where

open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)

module _ {A : Set} (_·_ : A → A → A)
  (·-assoc : (a b c : A) → (a · b) · c ≡ a · (b · c))
  (·-comm  : (a b : A) → a · b ≡ b · a)
  where

  medial : (w x y z : A) → (w · x) · (y · z) ≡ (w · y) · (x · z)
  medial w x y z =
    trans (·-assoc w x (y · z))
    (trans (cong (w ·_) (sym (·-assoc x y z)))
    (trans (cong (λ t → w · (t · z)) (·-comm x y))
    (trans (cong (w ·_) (·-assoc y x z))
           (sym (·-assoc w y (x · z))))))
