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

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)

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

  private variable n m k : ℕ

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

  -- 4. Bilinear distributivity (nth-ext + nth-*P + the per-coordinate identity).
  ·-distribʳ : (x y z : A) → (x + y) * z ≡ (x * z) + (y * z)
  ·-distribʳ x y z = trans (*-comm (x + y) z)
                     (trans (*-distribˡ z x y) (cong₂ _+_ (*-comm z x) (*-comm z y)))

  rearrange : (w x y z : A) → (w + x) + (y + z) ≡ (w + y) + (x + z)
  rearrange w x y z =
    trans (+-assoc w x (y + z))
    (trans (cong (w +_) (sym (+-assoc x y z)))
    (trans (cong (λ t → w + (t + z)) (+-comm x y))
    (trans (cong (w +_) (+-assoc y x z)) (sym (+-assoc w y (x + z))))))

  convCoeff-distrib : (p q : Poly n) (r : Poly m) (k : ℕ)
                    → convCoeff (p +P q) r k ≡ (convCoeff p r k) + (convCoeff q r k)
  convCoeff-distrib []      []      r k       = sym (+-identityˡ 𝟘)
  convCoeff-distrib (a ∷ p) (b ∷ q) r zero    = ·-distribʳ a b (nth r zero)
  convCoeff-distrib (a ∷ p) (b ∷ q) r (suc k) =
    trans (cong₂ _+_ (·-distribʳ a b (nth r (suc k))) (convCoeff-distrib p q r k))
          (rearrange (a * nth r (suc k)) (b * nth r (suc k)) (convCoeff p r k) (convCoeff q r k))

  *P-distribʳ : (p q : Poly n) (r : Poly m) → (p +P q) *P r ≡ (p *P r) +P (q *P r)
  *P-distribʳ p q r = nth-ext _ _ (λ k →
    trans (nth-*P (p +P q) r k)
    (trans (convCoeff-distrib p q r k)
    (trans (cong₂ _+_ (sym (nth-*P p r k)) (sym (nth-*P q r k)))
           (sym (nth-+P (p *P r) (q *P r) k)))))

  convCoeff-distribˡ : (r : Poly n) (p q : Poly m) (k : ℕ)
                     → convCoeff r (p +P q) k ≡ (convCoeff r p k) + (convCoeff r q k)
  convCoeff-distribˡ []      p q k       = sym (+-identityˡ 𝟘)
  convCoeff-distribˡ (a ∷ r) p q zero    =
    trans (cong (a *_) (nth-+P p q zero)) (*-distribˡ a (nth p zero) (nth q zero))
  convCoeff-distribˡ (a ∷ r) p q (suc k) =
    trans (cong₂ _+_ (trans (cong (a *_) (nth-+P p q (suc k)))
                            (*-distribˡ a (nth p (suc k)) (nth q (suc k))))
                     (convCoeff-distribˡ r p q k))
          (rearrange (a * nth p (suc k)) (a * nth q (suc k)) (convCoeff r p k) (convCoeff r q k))

  *P-distribˡ : (r : Poly n) (p q : Poly m) → r *P (p +P q) ≡ (r *P p) +P (r *P q)
  *P-distribˡ r p q = nth-ext _ _ (λ k →
    trans (nth-*P r (p +P q) k)
    (trans (convCoeff-distribˡ r p q k)
    (trans (cong₂ _+_ (sym (nth-*P r p k)) (sym (nth-*P r q k)))
           (sym (nth-+P (r *P p) (r *P q) k)))))

  -- 5. Scalar-linearity (preserves-·c in each argument) + subst-linearity.
  swap-· : (a c x : A) → a * (c * x) ≡ c * (a * x)
  swap-· a c x = trans (sym (*-assoc a c x)) (trans (cong (_* x) (*-comm a c)) (*-assoc c a x))

  convCoeff-scalarˡ : (c : A) (p : Poly n) (q : Poly m) (k : ℕ)
                    → convCoeff (c ·c p) q k ≡ c * convCoeff p q k
  convCoeff-scalarˡ c []      q k       = sym (*-absorbʳ c)
  convCoeff-scalarˡ c (a ∷ p) q zero    = *-assoc c a (nth q zero)
  convCoeff-scalarˡ c (a ∷ p) q (suc k) =
    trans (cong₂ _+_ (*-assoc c a (nth q (suc k))) (convCoeff-scalarˡ c p q k))
          (sym (*-distribˡ c (a * nth q (suc k)) (convCoeff p q k)))

  *P-scalarˡ : (c : A) (p : Poly n) (q : Poly m) → (c ·c p) *P q ≡ c ·c (p *P q)
  *P-scalarˡ c p q = nth-ext _ _ (λ k →
    trans (nth-*P (c ·c p) q k)
    (trans (convCoeff-scalarˡ c p q k)
    (trans (cong (c *_) (sym (nth-*P p q k))) (sym (nth-·c c (p *P q) k)))))

  convCoeff-scalarʳ : (c : A) (p : Poly n) (q : Poly m) (k : ℕ)
                    → convCoeff p (c ·c q) k ≡ c * convCoeff p q k
  convCoeff-scalarʳ c []      q k       = sym (*-absorbʳ c)
  convCoeff-scalarʳ c (a ∷ p) q zero    =
    trans (cong (a *_) (nth-·c c q zero)) (swap-· a c (nth q zero))
  convCoeff-scalarʳ c (a ∷ p) q (suc k) =
    trans (cong₂ _+_ (trans (cong (a *_) (nth-·c c q (suc k))) (swap-· a c (nth q (suc k))))
                     (convCoeff-scalarʳ c p q k))
          (sym (*-distribˡ c (a * nth q (suc k)) (convCoeff p q k)))

  *P-scalarʳ : (c : A) (p : Poly n) (q : Poly m) → p *P (c ·c q) ≡ c ·c (p *P q)
  *P-scalarʳ c p q = nth-ext _ _ (λ k →
    trans (nth-*P p (c ·c q) k)
    (trans (convCoeff-scalarʳ c p q k)
    (trans (cong (c *_) (sym (nth-*P p q k))) (sym (nth-·c c (p *P q) k)))))

  subst-+P : ∀ {a b} (eq : a ≡ b) (u v : Poly a)
           → subst Poly eq (u +P v) ≡ (subst Poly eq u) +P (subst Poly eq v)
  subst-+P refl u v = refl
  subst-·c : ∀ {a b} (eq : a ≡ b) (c : A) (v : Poly a)
           → subst Poly eq (c ·c v) ≡ c ·c (subst Poly eq v)
  subst-·c refl c v = refl

  -- 6. Basis machinery: canonical basis, Fin-indexed sums, basis-decomposition.
  basis : Fin n → Poly n
  basis {n} i = basis-vec {A} 𝟘 𝟙 {n} i

  -- the coefficient-level (A-valued) Fin sum, and its congruence / zero.
  sumA : (Fin n → A) → A
  sumA {zero}  _ = 𝟘
  sumA {suc _} g = g fz + sumA (λ i → g (fs i))

  sumA-cong : {g h : Fin n → A} → (∀ i → g i ≡ h i) → sumA g ≡ sumA h
  sumA-cong {zero}  _  = refl
  sumA-cong {suc _} eq = cong₂ _+_ (eq fz) (sumA-cong (λ i → eq (fs i)))

  sumA-zero : sumA {n} (λ _ → 𝟘) ≡ 𝟘
  sumA-zero {zero}   = refl
  sumA-zero {suc n'} = trans (cong (𝟘 +_) (sumA-zero {n'})) (+-identityˡ 𝟘)

  -- the polynomial-level Fin sum (fold +P), its congruence, and nth through it.
  sum : (Fin n → Poly m) → Poly m
  sum {zero}  {m} _ = replicate m 𝟘
  sum {suc _}     f = f fz +P sum (λ i → f (fs i))

  sum-cong : {f g : Fin n → Poly m} → (∀ i → f i ≡ g i) → sum f ≡ sum g
  sum-cong {zero}  _  = refl
  sum-cong {suc _} eq = cong₂ _+P_ (eq fz) (sum-cong (λ i → eq (fs i)))

  nth-sum : (f : Fin n → Poly m) (k : ℕ) → nth (sum f) k ≡ sumA (λ i → nth (f i) k)
  nth-sum {zero}  {m} f k = nth-replicate m k
  nth-sum {suc _}     f k =
    trans (nth-+P (f fz) (sum (λ i → f (fs i))) k)
          (cong (nth (f fz) k +_) (nth-sum (λ i → f (fs i)) k))

  -- basis i is the delta at toℕ i.
  nth-basis-same : (i : Fin n) → nth (basis i) (toℕ i) ≡ 𝟙
  nth-basis-same fz     = refl
  nth-basis-same (fs i) = nth-basis-same i

  nth-basis-other : (i : Fin n) (k : ℕ) → ¬ (k ≡ toℕ i) → nth (basis i) k ≡ 𝟘
  nth-basis-other fz       zero    neq = ⊥-elim (neq refl)
  nth-basis-other (fs i)   zero    _   = refl
  nth-basis-other {suc n'} fz (suc k) _   = nth-replicate n' k
  nth-basis-other (fs i)   (suc k) neq = nth-basis-other i k (λ e → neq (cong suc e))

  -- the one-hot collapse: Σᵢ (nth v (toℕ i))·(δ_{toℕ i})_k ≡ nth v k.
  basis-collapse : (v : Poly n) (k : ℕ) → sumA (λ (i : Fin n) → (nth v (toℕ i)) * nth (basis i) k) ≡ nth v k
  basis-collapse []      k       = refl
  basis-collapse {suc n'} (x ∷ v) zero =
    trans (cong₂ _+_ (trans (*-comm x 𝟙) (*-identityˡ x))
                     (trans (sumA-cong {n'} (λ i → *-absorbʳ (nth v (toℕ i)))) (sumA-zero {n'})))
          (+-identityʳ x)
  basis-collapse {suc n'} (x ∷ v) (suc k) =
    trans (cong₂ _+_ (trans (cong (x *_) (nth-replicate n' k)) (*-absorbʳ x))
                     (basis-collapse v k))
          (+-identityˡ (nth v k))

  -- every polynomial IS the sum of its scaled basis vectors.
  basis-decomp : (v : Poly n) → v ≡ sum (λ (i : Fin n) → nth v (toℕ i) ·c basis i)
  basis-decomp {n} v = nth-ext v (sum f) (λ k →
    sym (trans (nth-sum f k)
        (trans (sumA-cong {n} (λ i → nth-·c (nth v (toℕ i)) (basis {n} i) k))
               (basis-collapse {n} v k))))
    where f : Fin n → Poly n
          f i = nth v (toℕ i) ·c basis {n} i

  -- 7. The Linear record + linear-extensionality (the multilinear-extension bit
  --    that comm/assoc consume): two linear maps agreeing on the basis are equal.
  record Linear (d e : ℕ) : Set where
    field
      apply        : Poly d → Poly e
      preserves-+  : (u v : Poly d) → apply (u +P v) ≡ apply u +P apply v
      preserves-·c : (c : A) (v : Poly d) → apply (c ·c v) ≡ c ·c apply v
  open Linear public

  ·c-absorbˡ : (v : Poly n) → 𝟘 ·c v ≡ replicate n 𝟘
  ·c-absorbˡ []      = refl
  ·c-absorbˡ (x ∷ v) = cong₂ _∷_ (*-absorbˡ x) (·c-absorbˡ v)

  preserves-𝟎P : (L : Linear n m) → apply L (replicate n 𝟘) ≡ replicate m 𝟘
  preserves-𝟎P {n} L =
    trans (cong (apply L) (sym (·c-absorbˡ (replicate n 𝟘))))
          (trans (preserves-·c L 𝟘 (replicate n 𝟘))
                 (·c-absorbˡ (apply L (replicate n 𝟘))))

  preserves-sum : (L : Linear n m) (f : Fin k → Poly n)
                → apply L (sum f) ≡ sum (λ i → apply L (f i))
  preserves-sum {k = zero}  L f = preserves-𝟎P L
  preserves-sum {k = suc _} L f =
    trans (preserves-+ L (f fz) (sum (λ i → f (fs i))))
          (cong (apply L (f fz) +P_) (preserves-sum L (λ i → f (fs i))))

  linear-extensionality : (L M : Linear n m)
    → ((i : Fin n) → apply L (basis i) ≡ apply M (basis i))
    → (v : Poly n) → apply L v ≡ apply M v
  linear-extensionality {n} L M agree v =
    trans (cong (apply L) (basis-decomp v))
    (trans (preserves-sum L (λ (i : Fin n) → nth v (toℕ i) ·c basis i))
    (trans (sum-cong (λ (i : Fin n) → preserves-·c L (nth v (toℕ i)) (basis i)))
    (trans (sum-cong (λ (i : Fin n) → cong (nth v (toℕ i) ·c_) (agree i)))
    (trans (sum-cong (λ (i : Fin n) → sym (preserves-·c M (nth v (toℕ i)) (basis i))))
    (trans (sym (preserves-sum M (λ (i : Fin n) → nth v (toℕ i) ·c basis i)))
           (cong (apply M) (sym (basis-decomp v))))))))

  -- 8. Monomial facts: x-power (mult by xᵈ), basis = delta, basis-level commutativity.
  x-power : (d : ℕ) → Poly n → Poly (d ℕ+ n)
  x-power zero    q = q
  x-power (suc d) q = 𝟘 ∷ x-power d q

  nth-xpower-add : (d : ℕ) (q : Poly n) (k : ℕ) → nth (x-power d q) (d ℕ+ k) ≡ nth q k
  nth-xpower-add zero    q k = refl
  nth-xpower-add (suc d) q k = nth-xpower-add d q k

  convCoeff-𝟎P : (q : Poly m) (k : ℕ) → convCoeff (replicate n 𝟘) q k ≡ 𝟘
  convCoeff-𝟎P {n = zero}   q k       = refl
  convCoeff-𝟎P {n = suc n'} q zero    = *-absorbˡ (nth q zero)
  convCoeff-𝟎P {n = suc n'} q (suc k) =
    trans (cong₂ _+_ (*-absorbˡ (nth q (suc k))) (convCoeff-𝟎P {n = n'} q k)) (+-identityˡ 𝟘)

  convCoeff-basis-fz : (q : Poly m) (k : ℕ) → convCoeff (basis {suc n} fz) q k ≡ nth q k
  convCoeff-basis-fz         q zero    = *-identityˡ (nth q zero)
  convCoeff-basis-fz {n = n} q (suc k) =
    trans (cong₂ _+_ (*-identityˡ (nth q (suc k))) (convCoeff-𝟎P {n = n} q k)) (+-identityʳ (nth q (suc k)))

  convCoeff-basis-xpower : (i : Fin n) (q : Poly m) (k : ℕ)
                         → convCoeff (basis i) q k ≡ nth (x-power (toℕ i) q) k
  convCoeff-basis-xpower fz       q k       = convCoeff-basis-fz q k
  convCoeff-basis-xpower (fs i)   q zero    = *-absorbˡ (nth q zero)
  convCoeff-basis-xpower (fs i)   q (suc k) =
    trans (cong₂ _+_ (*-absorbˡ (nth q (suc k))) (convCoeff-basis-xpower i q k))
          (+-identityˡ (nth (x-power (toℕ i) q) k))

  nth-xpower-basis-peak : (d : ℕ) (j : Fin n) → nth (x-power d (basis j)) (d ℕ+ toℕ j) ≡ 𝟙
  nth-xpower-basis-peak d j = trans (nth-xpower-add d (basis j) (toℕ j)) (nth-basis-same j)

  nth-xpower-basis-off : (d : ℕ) (j : Fin n) (k : ℕ) → ¬ (k ≡ d ℕ+ toℕ j)
                       → nth (x-power d (basis j)) k ≡ 𝟘
  nth-xpower-basis-off zero    j k       neq = nth-basis-other j k neq
  nth-xpower-basis-off (suc d) j zero    _   = refl
  nth-xpower-basis-off (suc d) j (suc k) neq = nth-xpower-basis-off d j k (λ e → neq (cong suc e))

  -- the two monomials xⁱ·basis j and xʲ·basis i agree at every coefficient (both = δ at i+j).
  xpower-basis-symm : (i : Fin n) (j : Fin m) (k : ℕ)
                    → nth (x-power (toℕ i) (basis j)) k ≡ nth (x-power (toℕ j) (basis i)) k
  xpower-basis-symm i j k with k ≟ (toℕ i ℕ+ toℕ j)
  ... | yes eq = trans (subst (λ z → nth (x-power (toℕ i) (basis j)) z ≡ 𝟙) (sym eq)
                              (nth-xpower-basis-peak (toℕ i) j))
                       (sym (subst (λ z → nth (x-power (toℕ j) (basis i)) z ≡ 𝟙)
                              (sym (trans eq (+ℕ-comm (toℕ i) (toℕ j))))
                              (nth-xpower-basis-peak (toℕ j) i)))
  ... | no neq = trans (nth-xpower-basis-off (toℕ i) j k neq)
                       (sym (nth-xpower-basis-off (toℕ j) i k
                              (λ e → neq (trans e (+ℕ-comm (toℕ j) (toℕ i))))))

  -- basis-level commutativity of *P (coefficient form) — the bottom of *P-comm.
  convCoeff-basis-comm : (i : Fin n) (j : Fin m) (k : ℕ)
                       → convCoeff (basis i) (basis j) k ≡ convCoeff (basis j) (basis i) k
  convCoeff-basis-comm i j k =
    trans (convCoeff-basis-xpower i (basis j) k)
          (trans (xpower-basis-symm i j k) (sym (convCoeff-basis-xpower j (basis i) k)))

  -- multiplicative identity (graded / nth form): basis fz = the polynomial 1.
  *P-identityˡ-nth : ∀ {n m} (q : Poly m) (k : ℕ) → nth (basis {suc n} fz *P q) k ≡ nth q k
  *P-identityˡ-nth q k = trans (nth-*P (basis fz) q k) (convCoeff-basis-fz q k)

  -- 9. *P-comm via nested linear-extensionality, bottoming at convCoeff-basis-comm.
  --    `_*P q` and `subst ∘ (q *P_)` (same codomain via +ℕ-comm) as Linear maps, etc.
  Lq : ∀ {n m} (q : Poly m) → Linear n (n ℕ+ m)
  Lq q = record { apply = _*P q
                ; preserves-+  = λ u v → *P-distribʳ u v q
                ; preserves-·c = λ c v → *P-scalarˡ c v q }
  Mq : ∀ {n m} (q : Poly m) → Linear n (n ℕ+ m)
  Mq {n} {m} q = record
    { apply = λ p → subst Poly (+ℕ-comm m n) (q *P p)
    ; preserves-+  = λ u v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-distribˡ q u v))
                                   (subst-+P (+ℕ-comm m n) (q *P u) (q *P v))
    ; preserves-·c = λ c v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-scalarʳ c q v))
                                   (subst-·c (+ℕ-comm m n) c (q *P v)) }
  Li : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
  Li i = record { apply = λ q → basis i *P q
                ; preserves-+  = λ u v → *P-distribˡ (basis i) u v
                ; preserves-·c = λ c v → *P-scalarʳ c (basis i) v }
  Mi : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
  Mi {n} {m} i = record
    { apply = λ q → subst Poly (+ℕ-comm m n) (q *P basis i)
    ; preserves-+  = λ u v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-distribʳ u v (basis i)))
                                   (subst-+P (+ℕ-comm m n) (u *P basis i) (v *P basis i))
    ; preserves-·c = λ c v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-scalarˡ c v (basis i)))
                                   (subst-·c (+ℕ-comm m n) c (v *P basis i)) }

  agree-i : ∀ {n m} (i : Fin n) (q : Poly m)
          → basis i *P q ≡ subst Poly (+ℕ-comm m n) (q *P basis i)
  agree-i {n} {m} i q = linear-extensionality (Li i) (Mi i) basis-pair q
    where
      basis-pair : (j : Fin m) → basis i *P basis j ≡ subst Poly (+ℕ-comm m n) (basis j *P basis i)
      basis-pair j = nth-ext _ _ (λ k →
        trans (nth-*P (basis i) (basis j) k)
        (trans (convCoeff-basis-comm i j k)
        (trans (sym (nth-*P (basis j) (basis i) k))
               (sym (nth-subst (+ℕ-comm m n) (basis j *P basis i) k)))))

  *P-comm : ∀ {n m} (p : Poly n) (q : Poly m) → p *P q ≡ subst Poly (+ℕ-comm m n) (q *P p)
  *P-comm p q = linear-extensionality (Lq q) (Mq q) (λ i → agree-i i q) p

  -- 10. *P-assoc via 3× nested linear-extensionality, bottoming at mono-assoc (all-basis).
  convCoeff-comm : ∀ {n m} (p : Poly n) (q : Poly m) (d : ℕ) → convCoeff p q d ≡ convCoeff q p d
  convCoeff-comm {n} {m} p q d =
    trans (sym (nth-*P p q d))
    (trans (cong (λ z → nth z d) (*P-comm p q))
    (trans (nth-subst (+ℕ-comm m n) (q *P p) d) (nth-*P q p d)))

  convCoeff-basis-right : ∀ {n m} (p : Poly n) (k : Fin m) (d : ℕ)
                        → convCoeff p (basis k) d ≡ nth (x-power (toℕ k) p) d
  convCoeff-basis-right p k d = trans (convCoeff-comm p (basis k) d) (convCoeff-basis-xpower k p d)

  nth-xpower-off : ∀ a {m} (q : Poly m) (d : ℕ)
                 → (∀ b → d ≡ a ℕ+ b → nth q b ≡ 𝟘) → nth (x-power a q) d ≡ 𝟘
  nth-xpower-off zero    q d       h = h d refl
  nth-xpower-off (suc a) q zero    _ = refl
  nth-xpower-off (suc a) q (suc d) h = nth-xpower-off a q d (λ b e → h b (cong suc e))

  mono-assoc : ∀ {n m l} (i : Fin n) (j : Fin m) (k : Fin l)
             → subst Poly (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k)
               ≡ basis i *P (basis j *P basis k)
  mono-assoc {n} {m} {l} i j k = nth-ext _ _ (λ d →
    trans (nth-subst (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k) d) (coeff d))
    where
      P : ℕ
      P = toℕ i ℕ+ (toℕ j ℕ+ toℕ k)
      rk : toℕ k ℕ+ (toℕ i ℕ+ toℕ j) ≡ P
      rk = trans (+ℕ-comm (toℕ k) (toℕ i ℕ+ toℕ j)) (+ℕ-assoc (toℕ i) (toℕ j) (toℕ k))
      lhsV : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                     ≡ nth (x-power (toℕ k) (basis i *P basis j)) d
      lhsV d = trans (nth-*P (basis i *P basis j) (basis k) d)
                     (convCoeff-basis-right (basis i *P basis j) k d)
      rhsV : (d : ℕ) → nth (basis i *P (basis j *P basis k)) d
                     ≡ nth (x-power (toℕ i) (basis j *P basis k)) d
      rhsV d = trans (nth-*P (basis i) (basis j *P basis k) d)
                     (convCoeff-basis-xpower i (basis j *P basis k) d)
      ijV : (b : ℕ) → nth (basis i *P basis j) b ≡ nth (x-power (toℕ i) (basis j)) b
      ijV b = trans (nth-*P (basis i) (basis j) b) (convCoeff-basis-xpower i (basis j) b)
      jkV : (b : ℕ) → nth (basis j *P basis k) b ≡ nth (x-power (toℕ j) (basis k)) b
      jkV b = trans (nth-*P (basis j) (basis k) b) (convCoeff-basis-xpower j (basis k) b)
      coeff : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                      ≡ nth (basis i *P (basis j *P basis k)) d
      coeff d with d ≟ P
      ... | yes eq = trans lhs𝟙 (sym rhs𝟙)
        where
          rhs𝟙 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟙
          rhs𝟙 = subst (λ z → nth (basis i *P (basis j *P basis k)) z ≡ 𝟙) (sym eq)
                   (trans (rhsV P)
                    (trans (nth-xpower-add (toℕ i) (basis j *P basis k) (toℕ j ℕ+ toℕ k))
                     (trans (jkV (toℕ j ℕ+ toℕ k)) (nth-xpower-basis-peak (toℕ j) k))))
          lhs𝟙 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟙
          lhs𝟙 = subst (λ z → nth ((basis i *P basis j) *P basis k) z ≡ 𝟙) (sym eq)
                   (trans (lhsV P)
                    (subst (λ z → nth (x-power (toℕ k) (basis i *P basis j)) z ≡ 𝟙) rk
                      (trans (nth-xpower-add (toℕ k) (basis i *P basis j) (toℕ i ℕ+ toℕ j))
                       (trans (ijV (toℕ i ℕ+ toℕ j)) (nth-xpower-basis-peak (toℕ i) j)))))
      ... | no neq = trans lhs𝟘 (sym rhs𝟘)
        where
          rhs𝟘 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟘
          rhs𝟘 = trans (rhsV d)
                   (nth-xpower-off (toℕ i) (basis j *P basis k) d
                     (λ b e → trans (jkV b)
                       (nth-xpower-basis-off (toℕ j) k b
                         (λ b-eq → neq (trans e (cong (toℕ i ℕ+_) b-eq))))))
          lhs𝟘 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟘
          lhs𝟘 = trans (lhsV d)
                   (nth-xpower-off (toℕ k) (basis i *P basis j) d
                     (λ b e → trans (ijV b)
                       (nth-xpower-basis-off (toℕ i) j b
                         (λ b-eq → neq (trans (trans e (cong (toℕ k ℕ+_) b-eq)) rk)))))

  *P-assoc : ∀ {n m l} (p : Poly n) (q : Poly m) (r : Poly l)
           → subst Poly (+ℕ-assoc n m l) ((p *P q) *P r) ≡ p *P (q *P r)
  *P-assoc {n} {m} {l} p q r = linear-extensionality (Lp q r) (Rp q r) (λ i → agp i q r) p
    where
      ae : (n ℕ+ m) ℕ+ l ≡ n ℕ+ (m ℕ+ l)
      ae = +ℕ-assoc n m l
      S : Poly ((n ℕ+ m) ℕ+ l) → Poly (n ℕ+ (m ℕ+ l))
      S = subst Poly ae
      Lp : (q : Poly m) (r : Poly l) → Linear n (n ℕ+ (m ℕ+ l))
      Lp q r = record
        { apply = λ p → S ((p *P q) *P r)
        ; preserves-+  = λ u v → trans (cong S (trans (cong (_*P r) (*P-distribʳ u v q))
                                                      (*P-distribʳ (u *P q) (v *P q) r)))
                                      (subst-+P ae ((u *P q) *P r) ((v *P q) *P r))
        ; preserves-·c = λ c v → trans (cong S (trans (cong (_*P r) (*P-scalarˡ c v q))
                                                      (*P-scalarˡ c (v *P q) r)))
                                       (subst-·c ae c ((v *P q) *P r)) }
      Rp : (q : Poly m) (r : Poly l) → Linear n (n ℕ+ (m ℕ+ l))
      Rp q r = record
        { apply = λ p → p *P (q *P r)
        ; preserves-+  = λ u v → *P-distribʳ u v (q *P r)
        ; preserves-·c = λ c v → *P-scalarˡ c v (q *P r) }
      Lq' : (i : Fin n) (r : Poly l) → Linear m (n ℕ+ (m ℕ+ l))
      Lq' i r = record
        { apply = λ q → S ((basis i *P q) *P r)
        ; preserves-+  = λ u v → trans (cong S (trans (cong (_*P r) (*P-distribˡ (basis i) u v))
                                                      (*P-distribʳ (basis i *P u) (basis i *P v) r)))
                                      (subst-+P ae ((basis i *P u) *P r) ((basis i *P v) *P r))
        ; preserves-·c = λ c v → trans (cong S (trans (cong (_*P r) (*P-scalarʳ c (basis i) v))
                                                      (*P-scalarˡ c (basis i *P v) r)))
                                       (subst-·c ae c ((basis i *P v) *P r)) }
      Rq' : (i : Fin n) (r : Poly l) → Linear m (n ℕ+ (m ℕ+ l))
      Rq' i r = record
        { apply = λ q → basis i *P (q *P r)
        ; preserves-+  = λ u v → trans (cong (basis i *P_) (*P-distribʳ u v r))
                                      (*P-distribˡ (basis i) (u *P r) (v *P r))
        ; preserves-·c = λ c v → trans (cong (basis i *P_) (*P-scalarˡ c v r))
                                       (*P-scalarʳ c (basis i) (v *P r)) }
      Lr'' : (i : Fin n) (j : Fin m) → Linear l (n ℕ+ (m ℕ+ l))
      Lr'' i j = record
        { apply = λ r → S ((basis i *P basis j) *P r)
        ; preserves-+  = λ u v → trans (cong S (*P-distribˡ (basis i *P basis j) u v))
                                      (subst-+P ae ((basis i *P basis j) *P u) ((basis i *P basis j) *P v))
        ; preserves-·c = λ c v → trans (cong S (*P-scalarʳ c (basis i *P basis j) v))
                                       (subst-·c ae c ((basis i *P basis j) *P v)) }
      Rr'' : (i : Fin n) (j : Fin m) → Linear l (n ℕ+ (m ℕ+ l))
      Rr'' i j = record
        { apply = λ r → basis i *P (basis j *P r)
        ; preserves-+  = λ u v → trans (cong (basis i *P_) (*P-distribˡ (basis j) u v))
                                      (*P-distribˡ (basis i) (basis j *P u) (basis j *P v))
        ; preserves-·c = λ c v → trans (cong (basis i *P_) (*P-scalarʳ c (basis j) v))
                                       (*P-scalarʳ c (basis i) (basis j *P v)) }
      agq : (i : Fin n) (j : Fin m) (r : Poly l) → S ((basis i *P basis j) *P r) ≡ basis i *P (basis j *P r)
      agq i j r = linear-extensionality (Lr'' i j) (Rr'' i j) (λ k → mono-assoc i j k) r
      agp : (i : Fin n) (q : Poly m) (r : Poly l) → S ((basis i *P q) *P r) ≡ basis i *P (q *P r)
      agp i q r = linear-extensionality (Lq' i r) (Rq' i r) (λ j → agq i j r) q
