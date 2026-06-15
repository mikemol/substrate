------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing
--
-- The adapter from the `CommutativeRing` RECORD to `Graded.Over`'s flat
-- bundle: it extracts the coefficient operations + laws from the record and
-- opens `Graded.Over` over them, so `open Over CR` gives the whole graded
-- polynomial ring R[y] for any `CR : CommutativeRing A`.
--
-- Only `+-comm` needs work: it lives on the Ring's additive AbelianGroup,
-- whose monoid is `+-coherent`-equal (not definitionally) to the Semiring's
-- `+-monoid`; we transport it onto the `+-monoid` operation once. Everything
-- else is a direct projection (definitionally the operation `Over` expects).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.FromCommRing where

open import Substrate.Foundation.Eq using (_≡_; cong; subst)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group; ·-comm)
open import Substrate.Algebra.Semiring using (Semiring; +-monoid; *-monoid;
  distrib-left; zero-absorb-left; zero-absorb-right)
open import Substrate.Algebra.Ring using (Ring; semiring; +-abelian; +-coherent)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing; ring)
import Substrate.Algebra.Polynomial.Graded as G

module Over {A : Set} (CR : CommutativeRing A) where
  private
    R  = ring CR
    SR = semiring R
    +M = +-monoid SR
    *M = *-monoid SR
    opOf : Monoid A → (A → A → A)
    opOf M = Magma._·_ (magma (semigroup M))
    _+_ = opOf +M
    _*_ = opOf *M
    -- +-comm lives on the abelian group; transport it onto the +-monoid op
    -- via +-coherent (refl for coherently-built rings, e.g. GF256-Ring).
    +-comm : (a b : A) → _+_ a b ≡ _+_ b a
    +-comm = subst (λ op → (a b : A) → op a b ≡ op b a)
                   (cong opOf (+-coherent R))
                   (·-comm (+-abelian R))

  open G.Over _+_ _*_ (ε +M) (ε *M)
    (·-assoc (semigroup +M)) +-comm (ε-left +M) (ε-right +M)
    (·-assoc (semigroup *M)) (CommutativeRing.*-comm CR) (ε-left *M)
    (distrib-left SR) (zero-absorb-left SR) (zero-absorb-right SR)
    public
