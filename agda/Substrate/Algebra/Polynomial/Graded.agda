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
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Negation using (¬_)
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
