{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Base
--
-- The THIN carrier layer of the graded polynomial ring: just the coefficient
-- vector `Poly n = Vec A n` and its accessor `nth`, parameterised over the
-- coefficient type A and its zero 𝟘 ONLY (no ring ops, no laws). A consumer
-- that needs only the polynomial TYPE (an AES byte table, an S-box column)
-- deserialises this thin base instead of the whole `Graded.Div` ring tower —
-- the load-bound floor closure (a). `Substrate.Algebra.Polynomial.Graded`
-- opens `Base.Over 𝟘 public`, so the ring development sees `Poly`/`nth` as
-- single-source (`ε(+M) ≡ 𝟘` makes the two `nth`s the same neutral).
-- --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.Polynomial.Graded.Base where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)

module Over {A : Set} (𝟘 : A) where

  private variable n : ℕ

  Poly : ℕ → Set
  Poly n = Vec A n

  nth : Poly n → ℕ → A
  nth []      _       = 𝟘
  nth (x ∷ _) zero    = x
  nth (_ ∷ v) (suc i) = nth v i
