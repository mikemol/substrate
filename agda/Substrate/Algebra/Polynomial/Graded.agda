------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded
--
-- R[y], the graded polynomial ring over an arbitrary COMMUTATIVE RING,
-- parameterised over the coefficient operations + laws (a flat bundle so the
-- proofs are free of Ring-record coherence friction; a `CommutativeRing R`
-- adapter supplies them). `Poly n = Vec A n`; `_*P_` is the length-additive
-- convolution (outer ∘ anti-diag-sum), exactly the F₂ construction with F₂
-- swapped for the parameters. This is the generic home of which the F₂
-- `Polynomial.RingLaws` development is the `A = F₂` instance.
--
-- FOUNDATION (this file): coefficient calculus `nth`, the convolution bridge
-- `nth-*P`, observation-equality `nth-ext`. Distributivity / commutativity /
-- associativity / identity are built on top (lifted via FreeModuleExtensionality).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)

-- R[y] over the coefficient operations + commutative-ring laws (flat bundle).
-- Instantiate `open Over (+) (*) 𝟘 𝟙 …laws…` at A = F₂ (re-derives F₂[x]) or
-- A = GF(2⁸) (the AES column ring's coefficient level).
module Over {A : Set}
  (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A)
  (+-assoc     : (a b c : A) → (a + b) + c ≡ a + (b + c))
  (+-comm      : (a b : A) → a + b ≡ b + a)
  (+-identityˡ : (a : A) → 𝟘 + a ≡ a)
  (+-identityʳ : (a : A) → a + 𝟘 ≡ a)
  (*-assoc     : (a b c : A) → (a * b) * c ≡ a * (b * c))
  (*-comm      : (a b : A) → a * b ≡ b * a)
  (*-identityˡ : (a : A) → 𝟙 * a ≡ a)
  (*-distribˡ  : (a b c : A) → a * (b + c) ≡ (a * b) + (a * c))
  (*-absorbˡ   : (a : A) → 𝟘 * a ≡ 𝟘)
  (*-absorbʳ   : (a : A) → a * 𝟘 ≡ 𝟘)
  where

  private variable n m : ℕ

  -- 1. The graded polynomial type and its operations (no laws needed).
  Poly : ℕ → Set
  Poly n = Vec A n

  infixl 6 _+P_
  _+P_ : Poly n → Poly n → Poly n
  []      +P []      = []
  (x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)

  infixl 7 _·c_
  _·c_ : A → Poly n → Poly n
  a ·c []      = []
  a ·c (x ∷ p) = (a * x) ∷ (a ·c p)

  x-shift : Poly n → Poly (suc n)
  x-shift p = 𝟘 ∷ p

  pad-end : (k : ℕ) → Poly n → Poly (n ℕ+ k)
  pad-end k []      = replicate k 𝟘
  pad-end k (x ∷ p) = x ∷ pad-end k p

  shift-to-suc-on-left : ∀ {n'} → Poly (m ℕ+ suc n') → Poly (suc n' ℕ+ m)
  shift-to-suc-on-left {m} {n'} p = subst Poly (+ℕ-comm m (suc n')) p

  outer : Poly n → Poly m → Vec (Poly m) n
  outer []      q = []
  outer (a ∷ p) q = (a ·c q) ∷ outer p q

  anti-diag-sum : Vec (Poly m) n → Poly (n ℕ+ m)
  anti-diag-sum {m} {zero}   []           = replicate m 𝟘
  anti-diag-sum {m} {suc n'} (row ∷ rows) =
    shift-to-suc-on-left (pad-end (suc n') row) +P x-shift (anti-diag-sum rows)

  infixl 7 _*P_
  _*P_ : Poly n → Poly m → Poly (n ℕ+ m)
  p *P q = anti-diag-sum (outer p q)

  -- 2. Coefficient extraction `nth` and its homomorphism lemmas.
  nth : Poly n → ℕ → A
  nth []      _       = 𝟘
  nth (x ∷ _) zero    = x
  nth (_ ∷ v) (suc i) = nth v i

  nth-replicate : (k i : ℕ) → nth (replicate k 𝟘) i ≡ 𝟘
  nth-replicate zero    _       = refl
  nth-replicate (suc _) zero    = refl
  nth-replicate (suc k) (suc i) = nth-replicate k i

  nth-subst : ∀ {a b} (eq : a ≡ b) (v : Poly a) (i : ℕ)
            → nth (subst Poly eq v) i ≡ nth v i
  nth-subst refl v i = refl

  nth-pad-end : (k : ℕ) (v : Poly n) (i : ℕ) → nth (pad-end k v) i ≡ nth v i
  nth-pad-end k []      i       = nth-replicate k i
  nth-pad-end k (x ∷ v) zero    = refl
  nth-pad-end k (x ∷ v) (suc i) = nth-pad-end k v i

  nth-x-shift-zero : (v : Poly n) → nth (x-shift v) zero ≡ 𝟘
  nth-x-shift-zero v = refl
  nth-x-shift-suc : (v : Poly n) (i : ℕ) → nth (x-shift v) (suc i) ≡ nth v i
  nth-x-shift-suc v i = refl

  nth-+P : (u v : Poly n) (i : ℕ) → nth (u +P v) i ≡ nth u i + nth v i
  nth-+P []      []      i       = sym (+-identityˡ 𝟘)
  nth-+P (x ∷ u) (y ∷ v) zero    = refl
  nth-+P (x ∷ u) (y ∷ v) (suc i) = nth-+P u v i

  nth-·c : (a : A) (v : Poly n) (i : ℕ) → nth (a ·c v) i ≡ a * nth v i
  nth-·c a []      i       = sym (*-absorbʳ a)
  nth-·c a (x ∷ v) zero    = refl
  nth-·c a (x ∷ v) (suc i) = nth-·c a v i

  -- 3. The convolution coefficient and the bridge `nth-*P` (the method).
  convCoeff : Poly n → Poly m → ℕ → A
  convCoeff []      q k       = 𝟘
  convCoeff (a ∷ p) q zero    = a * nth q zero
  convCoeff (a ∷ p) q (suc k) = (a * nth q (suc k)) + convCoeff p q k

  nth-*P : (p : Poly n) (q : Poly m) (k : ℕ) → nth (p *P q) k ≡ convCoeff p q k
  nth-*P {n = zero}  {m = m} []      q k       = nth-replicate m k
  nth-*P {n = suc n} {m = m} (a ∷ p) q zero    =
    trans (nth-+P lo hi zero)
          (trans (cong₂ _+_
                    (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) zero)
                           (trans (nth-pad-end (suc n) (a ·c q) zero) (nth-·c a q zero)))
                    (nth-x-shift-zero (p *P q)))
                 (+-identityʳ (a * nth q zero)))
    where
      lo : Poly (suc n ℕ+ m)
      lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
      hi : Poly (suc n ℕ+ m)
      hi = x-shift (p *P q)
  nth-*P {n = suc n} {m = m} (a ∷ p) q (suc k) =
    trans (nth-+P lo hi (suc k))
          (cong₂ _+_
             (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) (suc k))
                    (trans (nth-pad-end (suc n) (a ·c q) (suc k)) (nth-·c a q (suc k))))
             (trans (nth-x-shift-suc (p *P q) k) (nth-*P p q k)))
    where
      lo : Poly (suc n ℕ+ m)
      lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
      hi : Poly (suc n ℕ+ m)
      hi = x-shift (p *P q)

  nth-ext : (u v : Poly n) → (∀ k → nth u k ≡ nth v k) → u ≡ v
  nth-ext []      []      _  = refl
  nth-ext (x ∷ u) (y ∷ v) eq = cong₂ _∷_ (eq zero) (nth-ext u v (λ k → eq (suc k)))
