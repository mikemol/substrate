------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Quotient  (AI-17 B3)
--
-- `R[y]/(f) : CommutativeRing` over ANY `CommutativeRing R`, for any monic
-- `f` (given by its low part `f-lo : Poly (suc d)`, with y^(suc d) ≡ f-lo).
--
-- The carrier is the reduced representatives `Poly (suc d)`, which are
-- ALL-CANONICAL (`reduce-idempotent : reduce p ≡ p`), so `≡` is already the
-- right equality — no quotient subtype / Hedberg needed (the Σ-subtype +
-- `reduced-≈⇒≡` bypass is ℚ's, where `*ℚ` is fixed-carrier; the polynomial
-- `*P` is GRADED, so the quotient ring is inherently `reduce ∘ *P`).
--
-- `_*Q_ a b = reduce-mod-f (a *P b)`; the ring laws are `_*P_`'s graded laws
-- (B1) PULLED THROUGH the `reduce` homomorphism (B2d: reduce-*-hom / reduce-+P
-- / reduce-idempotent). The additive group needs genuine negation (`-P`, from
-- the coefficient ring's inverse — `FromCommRing.neg`), since char-2's
-- `inv = id` is not available generically. Generic port of GF256 §AI-6e/6f.
--
-- `(F₂, m)` re-derives GF(2⁸); `(GF(2⁸), y⁴+1)` is the MixColumns column ring.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.Quotient where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Ring using (Ring)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  -- ⟡public-policy: bind Graded's API at ITS source. `Mod` no longer re-exports what it
  -- does not define (*P-comm/*P-assoc/*P-distribʳ/ˡ/neg/+-inverse* are Graded's, not Mod's).
  open F.Over CR
  open M.Over CR d f-lo

  private variable n m : ℕ

  𝟎C : Poly (suc d)
  𝟎C = replicate (suc d) 𝟘

  -- 1. additive abelian group on Poly (suc d): +P-assoc/comm + genuine negation.
  +P-comm : (u v : Poly n) → u +P v ≡ v +P u
  +P-comm []      []      = refl
  +P-comm (x ∷ u) (y ∷ v) = cong₂ _∷_ (+-comm x y) (+P-comm u v)

  +P-assoc : (u v w : Poly n) → (u +P v) +P w ≡ u +P (v +P w)
  +P-assoc []      []      []      = refl
  +P-assoc (x ∷ u) (y ∷ v) (z ∷ w) = cong₂ _∷_ (+-assoc x y z) (+P-assoc u v w)

  -P : Poly n → Poly n
  -P []      = []
  -P (x ∷ v) = neg x ∷ -P v

  +P-inverseˡ : (v : Poly n) → (-P v) +P v ≡ replicate n 𝟘
  +P-inverseˡ []      = refl
  +P-inverseˡ (x ∷ v) = cong₂ _∷_ (+-inverseˡ x) (+P-inverseˡ v)

  +P-inverseʳ : (v : Poly n) → v +P (-P v) ≡ replicate n 𝟘
  +P-inverseʳ []      = refl
  +P-inverseʳ (x ∷ v) = cong₂ _∷_ (+-inverseʳ x) (+P-inverseʳ v)

  -- 2. multiplicative helpers (port of GF256 §Mul: hsum at 𝟘 / 𝟙).
  ·c-identityˡ : (v : Poly n) → 𝟙 ·c v ≡ v
  ·c-identityˡ []      = refl
  ·c-identityˡ (x ∷ v) = cong₂ _∷_ (*-identityˡ x) (·c-identityˡ v)

  hsum-zero : (r : Poly (suc d)) → hsum (replicate n 𝟘) r ≡ 𝟎C
  hsum-zero {zero}  r = refl
  hsum-zero {suc n} r =
    trans (cong₂ _+P_ (·c-absorbˡ r) (hsum-zero {n} (ytime r))) (+P-identityˡ 𝟎C)

  hsum-zeroʳ : (p : Poly n) → hsum p 𝟎C ≡ 𝟎C
  hsum-zeroʳ []      = refl
  hsum-zeroʳ (a ∷ p) =
    trans (cong₂ _+P_ (·c-zeroʳ a) (trans (cong (hsum p) ytime-zero) (hsum-zeroʳ p)))
          (+P-identityˡ 𝟎C)

  hsum-one-id : (r : Poly (suc d)) → hsum oneC r ≡ r
  hsum-one-id r =
    trans (cong₂ _+P_ (·c-identityˡ r) (hsum-zero {d} (ytime r))) (+P-identityʳ r)

  -- 3. the quotient multiplication + its 8 ring laws (pulled through reduce).
  infixl 7 _*Q_
  _*Q_ : Poly (suc d) → Poly (suc d) → Poly (suc d)
  a *Q b = reduce-mod-f (a *P b)

  *Q-comm : (a b : Poly (suc d)) → a *Q b ≡ b *Q a
  *Q-comm a b =
    trans (cong reduce-mod-f (*P-comm a b)) (reduce-subst (+ℕ-comm (suc d) (suc d)) (b *P a))

  *Q-distribˡ : (a b c : Poly (suc d)) → a *Q (b +P c) ≡ (a *Q b) +P (a *Q c)
  *Q-distribˡ a b c =
    trans (cong reduce-mod-f (*P-distribˡ a b c)) (reduce-+P (a *P b) (a *P c))

  *Q-distribʳ : (a b c : Poly (suc d)) → (a +P b) *Q c ≡ (a *Q c) +P (b *Q c)
  *Q-distribʳ a b c =
    trans (cong reduce-mod-f (*P-distribʳ a b c)) (reduce-+P (a *P c) (b *P c))

  *Q-identityˡ : (b : Poly (suc d)) → oneC *Q b ≡ b
  *Q-identityˡ b =
    trans (reduce-*P-expand oneC b) (trans (hsum-one-id (reduce-mod-f b)) (reduce-idempotent b))

  *Q-identityʳ : (b : Poly (suc d)) → b *Q oneC ≡ b
  *Q-identityʳ b = trans (*Q-comm b oneC) (*Q-identityˡ b)

  *Q-zeroˡ : (b : Poly (suc d)) → 𝟎C *Q b ≡ 𝟎C
  *Q-zeroˡ b = trans (reduce-*P-expand 𝟎C b) (hsum-zero {suc d} (reduce-mod-f b))

  *Q-zeroʳ : (b : Poly (suc d)) → b *Q 𝟎C ≡ 𝟎C
  *Q-zeroʳ b =
    trans (reduce-*P-expand b 𝟎C) (trans (cong (hsum b) (reduce-𝟎P {suc d})) (hsum-zeroʳ b))

  reduce-*-homˡ : (p : Poly n) (q : Poly m)
                → reduce-mod-f (reduce-mod-f p *P q) ≡ reduce-mod-f (p *P q)
  reduce-*-homˡ {n} {m} p q =
    trans (cong reduce-mod-f (*P-comm (reduce-mod-f p) q))
    (trans (reduce-subst (+ℕ-comm m (suc d)) (q *P reduce-mod-f p))
    (trans (sym (reduce-*-hom q p))
    (trans (cong reduce-mod-f (*P-comm q p)) (reduce-subst (+ℕ-comm n m) (p *P q)))))

  *Q-assoc : (a b c : Poly (suc d)) → (a *Q b) *Q c ≡ a *Q (b *Q c)
  *Q-assoc a b c =
    trans (reduce-*-homˡ (a *P b) c)
    (trans (sym (reduce-subst (+ℕ-assoc (suc d) (suc d) (suc d)) ((a *P b) *P c)))
    (trans (cong reduce-mod-f (*P-assoc a b c)) (reduce-*-hom a (b *P c))))

  -- 4. climb the ladder: CommutativeRing (Poly (suc d)). ONE additive monoid is
  --    shared by the semiring AND the abelian group ⇒ +-coherent = refl.
  +P-monoid : Monoid (Poly (suc d))
  +P-monoid = record
    { semigroup = record { magma = record { _·_ = _+P_ } ; ·-assoc = +P-assoc }
    ; ε = 𝟎C ; ε-left = +P-identityˡ ; ε-right = +P-identityʳ }

  +P-abelian : AbelianGroup (Poly (suc d))
  +P-abelian = record
    { group = record { monoid = +P-monoid ; inv = -P
                     ; inv-left = +P-inverseˡ ; inv-right = +P-inverseʳ }
    ; ·-comm = +P-comm }

  *Q-monoid : Monoid (Poly (suc d))
  *Q-monoid = record
    { semigroup = record { magma = record { _·_ = _*Q_ } ; ·-assoc = *Q-assoc }
    ; ε = oneC ; ε-left = *Q-identityˡ ; ε-right = *Q-identityʳ }

  Quotient-Semiring : Semiring (Poly (suc d))
  Quotient-Semiring = record
    { +-monoid = +P-monoid ; *-monoid = *Q-monoid
    ; distrib-left = *Q-distribˡ ; distrib-right = *Q-distribʳ
    ; zero-absorb-left = *Q-zeroˡ ; zero-absorb-right = *Q-zeroʳ }

  Quotient-Ring : Ring (Poly (suc d))
  Quotient-Ring = record
    { semiring = Quotient-Semiring ; +-abelian = +P-abelian ; +-coherent = refl }

  Quotient-CommRing : CommutativeRing (Poly (suc d))
  Quotient-CommRing = record { ring = Quotient-Ring ; *-comm = *Q-comm }
