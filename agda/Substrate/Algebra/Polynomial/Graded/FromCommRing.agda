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

open import Substrate.Foundation.Eq using (_≡_; cong; subst; trans)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group using (Group; monoid; inv; inv-left)
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

  -- The coefficient ops + laws, exposed BY NAME (so consumers — B2 reduce-mod-f,
  -- B3, EEA — get 𝟘/_+_/… and the ring laws, not just the polynomial machinery).
  𝟘 𝟙 : A
  𝟘 = ε +M
  𝟙 = ε *M
  _+_ _*_ : A → A → A
  _+_ = opOf +M
  _*_ = opOf *M
  +-assoc     = ·-assoc (semigroup +M)
  +-identityˡ = ε-left +M
  +-identityʳ = ε-right +M
  *-assoc     = ·-assoc (semigroup *M)
  *-comm      = CommutativeRing.*-comm CR
  *-identityˡ = ε-left *M
  *-distribˡ  = distrib-left SR
  *-absorbˡ   = zero-absorb-left SR
  *-absorbʳ   = zero-absorb-right SR
  -- +-comm lives on the abelian group; transport it onto the +-monoid op
  -- via +-coherent (refl for coherently-built rings, e.g. GF256-Ring).
  +-comm : (a b : A) → a + b ≡ b + a
  +-comm = subst (λ op → (a b : A) → op a b ≡ op b a)
                 (cong opOf (+-coherent R))
                 (·-comm (+-abelian R))
  -- coefficient negation + its inverse laws (the additive abelian group of R[y]/(f)
  -- needs genuine negation — GF256's char-2 `inv = id` is not available generically).
  -- Transport inv-left from the group's monoid onto the +-monoid op/zero via +-coherent.
  neg : A → A
  neg = inv (group (+-abelian R))
  +-inverseˡ : (a : A) → neg a + a ≡ 𝟘
  +-inverseˡ = subst (λ M → (a : A) → opOf M (neg a) a ≡ ε M)
                     (+-coherent R) (inv-left (group (+-abelian R)))
  +-inverseʳ : (a : A) → a + neg a ≡ 𝟘
  +-inverseʳ a = trans (+-comm a (neg a)) (+-inverseˡ a)

  open G.Over _+_ _*_ 𝟘 𝟙
    +-assoc +-comm +-identityˡ +-identityʳ
    *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
    public
