{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolySemiring — ⟡jac-poly-semiring (RUNG 3b).
--
-- The normalized multivariate polynomial ring `NormPoly` (sorted, combined,
-- no-zero-coeff MPoly over ℤ) IS a `Semiring` — the carrier RUNG 3c's native
-- Leibniz determinant needs (`Det`/`WithSign` require a full `Semiring A`).
--
-- Load-bearing content: (i) `coeff-canonicity` (two sorted polys with equal
-- coeff-functions are ≡) makes `coeff` a faithful semantics, so every Semiring
-- law reduces to a coeff equation; (ii) the convolution linearity — coeff is
-- invariant under normalizing either factor of `*P` (`*P-normalizeˡ` via
-- insertT-surgery on the left factor, `*P-normalizeʳ` via the shifted-coeff
-- formula on the right) — discharges the multiplicative laws that raw `++`
-- cannot; (iii) `*P` is associative ON THE NOSE, so `coeff-*P-assoc` is
-- `cong (coeff m) *P-assoc`. Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.MPolySemiring where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; Σ-≡,≡→≡)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Hedberg using (DecidableEquality; Decidable⇒UIP)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; -ℤ_; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-assoc; +ℤ-comm; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseˡ)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-identityˡ; *ℤ-identityʳ; *ℤ-zeroˡ; *ℤ-zeroʳ; *ℤ-distribˡ-+; *ℤ-distribʳ-+)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Semiring.Instances using (mk-monoid)
open import Substrate.Algebra.Semiring.Instances.Z using (mul-sign-computes)
open import Substrate.Algebra.Z.MonoCommMonoid using (addM-assoc; addM-idˡ; addM-idʳ)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; 𝔹; tt; ff; and;
         addM; mulT; scaleT; _*P_; 𝟙P; kP; X; Y)
open import Substrate.Algebra.Z.MPolyNormalize
  using (isSortedB; ltMᵇ; nzB; minB; normalize; insertT; consNZ; Bcase; triM; ltM; eqM≡; gtM)
open import Substrate.Algebra.Z.MPolyNormalize.Properties
  using (normalize-sorted; coeff-normalize; coeff-++; coeff-cons; coeff-cons-tt; coeff-cons-ff;
         eqM-refl; ltMᵇ→eqMff; <M→ltMᵇ; minB-trans; sorted-nz; sorted-tail; sorted-min; nzB-ff)

------------------------------------------------------------------------
-- 0. Boolean + ℤ helpers.
------------------------------------------------------------------------

ff≢tt : ff ≡ tt → ⊥
ff≢tt ()

and-r-ff : (x : 𝔹) → and x ff ≡ ff
and-r-ff tt = refl
and-r-ff ff = refl

interchange : (A B C D : ℤ) → (A +ℤ B) +ℤ (C +ℤ D) ≡ (A +ℤ C) +ℤ (B +ℤ D)
interchange A B C D =
  trans (+ℤ-assoc A B (C +ℤ D))
  (trans (cong (A +ℤ_) (trans (sym (+ℤ-assoc B C D))
                        (trans (cong (_+ℤ D) (+ℤ-comm B C)) (+ℤ-assoc C B D))))
         (sym (+ℤ-assoc A C (B +ℤ D))))

+ℤ-cancelˡ : (a b c : ℤ) → a +ℤ b ≡ a +ℤ c → b ≡ c
+ℤ-cancelˡ a b c e =
  trans (sym (+ℤ-identityˡ b))
  (trans (cong (_+ℤ b) (sym (+ℤ-inverseˡ a)))
  (trans (+ℤ-assoc (-ℤ a) a b)
  (trans (cong (-ℤ a +ℤ_) e)
  (trans (sym (+ℤ-assoc (-ℤ a) a c))
  (trans (cong (_+ℤ c) (+ℤ-inverseˡ a)) (+ℤ-identityˡ c))))))

------------------------------------------------------------------------
-- 1. NormPoly Σ-subtype h-prop.
------------------------------------------------------------------------

NormPoly : Set
NormPoly = Σ MPoly (λ p → isSortedB p ≡ tt)

_≟𝔹_ : DecidableEquality 𝔹
tt ≟𝔹 tt = yes refl
ff ≟𝔹 ff = yes refl
tt ≟𝔹 ff = no (λ ())
ff ≟𝔹 tt = no (λ ())

𝔹-UIP : {x y : 𝔹} (p q : x ≡ y) → p ≡ q
𝔹-UIP = Decidable⇒UIP _≟𝔹_

NormPoly-≡ : {a b : NormPoly} → proj₁ a ≡ proj₁ b → a ≡ b
NormPoly-≡ {p , sp} {q , sq} e =
  Σ-≡,≡→≡ (e , 𝔹-UIP (subst (λ r → isSortedB r ≡ tt) e sp) sq)

------------------------------------------------------------------------
-- 2. *P is associative ON THE NOSE (raw MPoly ≡). ⇒ coeff-*P-assoc is a cong.
------------------------------------------------------------------------

scaleT-++ : (t : Term) (b c : MPoly) → scaleT t (b ++ c) ≡ scaleT t b ++ scaleT t c
scaleT-++ t []       c = refl
scaleT-++ t (u ∷ b') c = cong (mulT t u ∷_) (scaleT-++ t b' c)

++-assoc : {A : Set} (xs ys zs : List A) → (xs ++ ys) ++ zs ≡ xs ++ (ys ++ zs)
++-assoc []       ys zs = refl
++-assoc (x ∷ xs) ys zs = cong (x ∷_) (++-assoc xs ys zs)

mulT-assoc : (t u w : Term) → mulT t (mulT u w) ≡ mulT (mulT t u) w
mulT-assoc (term p x) (term q y) (term r z) =
  cong₂ term (sym (addM-assoc p q r)) (sym (*ℤ-assoc x y z))

scaleT-scaleT : (t u : Term) (c : MPoly) → scaleT t (scaleT u c) ≡ scaleT (mulT t u) c
scaleT-scaleT t u []       = refl
scaleT-scaleT t u (w ∷ c') = cong₂ _∷_ (mulT-assoc t u w) (scaleT-scaleT t u c')

scaleT-*P : (t : Term) (b c : MPoly) → scaleT t (b *P c) ≡ (scaleT t b) *P c
scaleT-*P t []       c = refl
scaleT-*P t (u ∷ b') c =
  trans (scaleT-++ t (scaleT u c) (b' *P c))
        (cong₂ _++_ (scaleT-scaleT t u c) (scaleT-*P t b' c))

*P-++-distˡ : (p q c : MPoly) → (p ++ q) *P c ≡ (p *P c) ++ (q *P c)
*P-++-distˡ []       q c = refl
*P-++-distˡ (t ∷ p') q c =
  trans (cong (scaleT t c ++_) (*P-++-distˡ p' q c))
        (sym (++-assoc (scaleT t c) (p' *P c) (q *P c)))

*P-assoc : (a b c : MPoly) → (a *P b) *P c ≡ a *P (b *P c)
*P-assoc []       b c = refl
*P-assoc (t ∷ a') b c =
  trans (*P-++-distˡ (scaleT t b) (a' *P b) c)
        (cong₂ _++_ (sym (scaleT-*P t b c)) (*P-assoc a' b c))

coeff-*P-assoc : (m : Mono) (a b c : MPoly) → coeff m ((a *P b) *P c) ≡ coeff m (a *P (b *P c))
coeff-*P-assoc m a b c = cong (coeff m) (*P-assoc a b c)

------------------------------------------------------------------------
-- 3. coeff-linearity of *P in each argument (feeds distributivity).
------------------------------------------------------------------------

coeff-*P-distˡ : (m : Mono) (a b c : MPoly) →
                 coeff m ((a ++ b) *P c) ≡ coeff m (a *P c) +ℤ coeff m (b *P c)
coeff-*P-distˡ m []       b c = sym (+ℤ-identityˡ (coeff m (b *P c)))
coeff-*P-distˡ m (t ∷ a') b c =
  trans (coeff-++ m (scaleT t c) ((a' ++ b) *P c))
  (trans (cong (coeff m (scaleT t c) +ℤ_) (coeff-*P-distˡ m a' b c))
  (trans (sym (+ℤ-assoc (coeff m (scaleT t c)) (coeff m (a' *P c)) (coeff m (b *P c))))
         (cong (_+ℤ coeff m (b *P c)) (sym (coeff-++ m (scaleT t c) (a' *P c))))))

coeff-*P-distʳ : (m : Mono) (a b c : MPoly) →
                 coeff m (a *P (b ++ c)) ≡ coeff m (a *P b) +ℤ coeff m (a *P c)
coeff-*P-distʳ m []       b c = sym (+ℤ-identityˡ 0ℤ)
coeff-*P-distʳ m (t ∷ a') b c =
  trans (coeff-++ m (scaleT t (b ++ c)) (a' *P (b ++ c)))
  (trans (cong₂ _+ℤ_
            (trans (cong (coeff m) (scaleT-++ t b c)) (coeff-++ m (scaleT t b) (scaleT t c)))
            (coeff-*P-distʳ m a' b c))
  (trans (interchange (coeff m (scaleT t b)) (coeff m (scaleT t c)) (coeff m (a' *P b)) (coeff m (a' *P c)))
         (sym (cong₂ _+ℤ_ (coeff-++ m (scaleT t b) (a' *P b)) (coeff-++ m (scaleT t c) (a' *P c))))))

coeff-*P-nilʳ : (m : Mono) (p : MPoly) → coeff m (p *P []) ≡ 0ℤ
coeff-*P-nilʳ m []       = refl
coeff-*P-nilʳ m (t ∷ p') = coeff-*P-nilʳ m p'

------------------------------------------------------------------------
-- 4. LEFT normalize-congruence: coeff m (normalize x *P q) ≡ coeff m (x *P q).
--    (insertT surgery on the left factor.)
------------------------------------------------------------------------

scaleT-0 : (k : Mono) (q : MPoly) (m : Mono) → coeff m (scaleT (term k 0ℤ) q) ≡ 0ℤ
scaleT-0 k []              m = refl
scaleT-0 k (term u e ∷ q') m =
  trans (coeff-cons m (addM k u) (0ℤ *ℤ e) (scaleT (term k 0ℤ) q')) st
  where
    st : Bcase (eqM m (addM k u)) ((0ℤ *ℤ e) +ℤ coeff m (scaleT (term k 0ℤ) q')) (coeff m (scaleT (term k 0ℤ) q')) ≡ 0ℤ
    st with eqM m (addM k u)
    ... | tt = trans (cong₂ _+ℤ_ (*ℤ-zeroˡ e) (scaleT-0 k q' m)) (+ℤ-identityˡ 0ℤ)
    ... | ff = scaleT-0 k q' m

scaleT-+coeff : (k : Mono) (c d : ℤ) (q : MPoly) (m : Mono) →
                coeff m (scaleT (term k (c +ℤ d)) q)
                  ≡ coeff m (scaleT (term k c) q) +ℤ coeff m (scaleT (term k d) q)
scaleT-+coeff k c d []              m = sym (+ℤ-identityˡ 0ℤ)
scaleT-+coeff k c d (term u e ∷ q') m =
  trans (coeff-cons m (addM k u) ((c +ℤ d) *ℤ e) (scaleT (term k (c +ℤ d)) q'))
  (trans st
  (sym (cong₂ _+ℤ_ (coeff-cons m (addM k u) (c *ℤ e) (scaleT (term k c) q'))
                   (coeff-cons m (addM k u) (d *ℤ e) (scaleT (term k d) q')))))
  where
    Lc = coeff m (scaleT (term k c) q')
    Ld = coeff m (scaleT (term k d) q')
    st : Bcase (eqM m (addM k u)) (((c +ℤ d) *ℤ e) +ℤ coeff m (scaleT (term k (c +ℤ d)) q')) (coeff m (scaleT (term k (c +ℤ d)) q'))
       ≡ Bcase (eqM m (addM k u)) ((c *ℤ e) +ℤ Lc) Lc +ℤ Bcase (eqM m (addM k u)) ((d *ℤ e) +ℤ Ld) Ld
    st rewrite scaleT-+coeff k c d q' m with eqM m (addM k u)
    ... | tt = trans (cong (_+ℤ (Lc +ℤ Ld)) (*ℤ-distribʳ-+ c d e))
                     (interchange (c *ℤ e) (d *ℤ e) Lc Ld)
    ... | ff = refl

consNZ-*P : (k : Mono) (c : ℤ) (zs q : MPoly) (m : Mono) →
            coeff m (consNZ k c zs *P q) ≡ coeff m (scaleT (term k c) q) +ℤ coeff m (zs *P q)
consNZ-*P k c zs q m with c ≟ℤ 0ℤ
... | yes c≡0 = sym (trans (cong (_+ℤ coeff m (zs *P q)) sc0) (+ℤ-identityˡ (coeff m (zs *P q))))
  where sc0 : coeff m (scaleT (term k c) q) ≡ 0ℤ
        sc0 = trans (cong (λ cc → coeff m (scaleT (term k cc) q)) c≡0) (scaleT-0 k q m)
... | no  _ = coeff-++ m (scaleT (term k c) q) (zs *P q)

insertT-*P : (k : Mono) (c : ℤ) (ys q : MPoly) (m : Mono) →
             coeff m (insertT k c ys *P q) ≡ coeff m (scaleT (term k c) q) +ℤ coeff m (ys *P q)
insertT-*P k c []              q m = consNZ-*P k c [] q m
insertT-*P k c (term n d ∷ ys') q m with triM k n
... | ltM _   = consNZ-*P k c (term n d ∷ ys') q m
... | eqM≡ refl =
      trans (consNZ-*P k (c +ℤ d) ys' q m)
      (trans (cong (_+ℤ coeff m (ys' *P q)) (scaleT-+coeff k c d q m))
      (trans (+ℤ-assoc (coeff m (scaleT (term k c) q)) (coeff m (scaleT (term k d) q)) (coeff m (ys' *P q)))
             (cong (coeff m (scaleT (term k c) q) +ℤ_) (sym (coeff-++ m (scaleT (term k d) q) (ys' *P q))))))
... | gtM _   =
      trans (coeff-++ m (scaleT (term n d) q) (insertT k c ys' *P q))
      (trans (cong (coeff m (scaleT (term n d) q) +ℤ_) (insertT-*P k c ys' q m))
      (trans swap
             (cong (coeff m (scaleT (term k c) q) +ℤ_) (sym (coeff-++ m (scaleT (term n d) q) (ys' *P q))))))
  where
    D  = coeff m (scaleT (term n d) q)
    Sc = coeff m (scaleT (term k c) q)
    Yq = coeff m (ys' *P q)
    swap : D +ℤ (Sc +ℤ Yq) ≡ Sc +ℤ (D +ℤ Yq)
    swap = trans (sym (+ℤ-assoc D Sc Yq)) (trans (cong (_+ℤ Yq) (+ℤ-comm D Sc)) (+ℤ-assoc Sc D Yq))

*P-normalizeˡ : (x q : MPoly) (m : Mono) → coeff m (normalize x *P q) ≡ coeff m (x *P q)
*P-normalizeˡ []              q m = refl
*P-normalizeˡ (term k c ∷ x') q m =
  trans (insertT-*P k c (normalize x') q m)
  (trans (cong (coeff m (scaleT (term k c) q) +ℤ_) (*P-normalizeˡ x' q m))
         (sym (coeff-++ m (scaleT (term k c) q) (x' *P q))))

------------------------------------------------------------------------
-- 5. RIGHT normalize-congruence: coeff m (x *P normalize y) ≡ coeff m (x *P y).
--    coeff m (scaleT (term k c) y) = c *ℤ coeff (m ∸ k) y, gated m ≥ k.
------------------------------------------------------------------------

geqℕ : ℕ → ℕ → 𝔹                      -- a ≥ b
geqℕ a       zero    = tt
geqℕ zero    (suc _) = ff
geqℕ (suc a) (suc b) = geqℕ a b

geqM : Mono → Mono → 𝔹
geqM (mono a b c) (mono d e f) = and (geqℕ a d) (and (geqℕ b e) (geqℕ c f))

subM : Mono → Mono → Mono
subM (mono a b c) (mono d e f) = mono (a ∸ d) (b ∸ e) (c ∸ f)

-- a = k + u  ⟺  a ≥ k ∧ (a ∸ k) = u
eqℕ-add-decompose : (a k u : ℕ) → eqℕ a (k + u) ≡ and (geqℕ a k) (eqℕ (a ∸ k) u)
eqℕ-add-decompose a       zero    u = refl
eqℕ-add-decompose zero    (suc k) u = refl
eqℕ-add-decompose (suc a) (suc k) u = eqℕ-add-decompose a k u

reshuffle4 : (gB sB gC sC : 𝔹) → and (and gB sB) (and gC sC) ≡ and (and gB gC) (and sB sC)
reshuffle4 ff sB gC sC = refl
reshuffle4 tt ff gC sC = sym (and-r-ff gC)
reshuffle4 tt tt gC sC = refl

reshuffle6 : (gA sA gB sB gC sC : 𝔹) →
  and (and gA sA) (and (and gB sB) (and gC sC)) ≡ and (and gA (and gB gC)) (and sA (and sB sC))
reshuffle6 ff sA gB sB gC sC = refl
reshuffle6 tt ff gB sB gC sC = sym (and-r-ff (and gB gC))
reshuffle6 tt tt gB sB gC sC = reshuffle4 gB sB gC sC

eqM-addM-decompose : (m k u : Mono) → eqM m (addM k u) ≡ and (geqM m k) (eqM (subM m k) u)
eqM-addM-decompose (mono a b c) (mono kx ky kz) (mono ux uy uz)
  rewrite eqℕ-add-decompose a kx ux
        | eqℕ-add-decompose b ky uy
        | eqℕ-add-decompose c kz uz
  = reshuffle6 (geqℕ a kx) (eqℕ (a ∸ kx) ux) (geqℕ b ky) (eqℕ (b ∸ ky) uy) (geqℕ c kz) (eqℕ (c ∸ kz) uz)

coeff-scaleT-full : (k : Mono) (c : ℤ) (y : MPoly) (m : Mono) →
                    coeff m (scaleT (term k c) y) ≡ Bcase (geqM m k) (c *ℤ coeff (subM m k) y) 0ℤ
coeff-scaleT-full k c []              m with geqM m k
... | tt = sym (*ℤ-zeroʳ c)
... | ff = refl
coeff-scaleT-full k c (term u e ∷ y') m =
  trans (coeff-cons m (addM k u) (c *ℤ e) (scaleT (term k c) y'))
  (trans (cong (λ b → Bcase b ((c *ℤ e) +ℤ R) R) (eqM-addM-decompose m k u)) body)
  where
    R = coeff m (scaleT (term k c) y')
    P = coeff (subM m k) y'
    body : Bcase (and (geqM m k) (eqM (subM m k) u)) ((c *ℤ e) +ℤ R) R
         ≡ Bcase (geqM m k) (c *ℤ coeff (subM m k) (term u e ∷ y')) 0ℤ
    body rewrite coeff-cons (subM m k) u e y' | coeff-scaleT-full k c y' m
      with geqM m k | eqM (subM m k) u
    ... | tt | tt = sym (*ℤ-distribˡ-+ c e P)
    ... | tt | ff = refl
    ... | ff | _  = refl

scaleT-cong : (k : Mono) (c : ℤ) (y1 y2 : MPoly) → ((j : Mono) → coeff j y1 ≡ coeff j y2) →
              (m : Mono) → coeff m (scaleT (term k c) y1) ≡ coeff m (scaleT (term k c) y2)
scaleT-cong k c y1 y2 hyp m =
  trans (coeff-scaleT-full k c y1 m)
  (trans (cong (λ z → Bcase (geqM m k) (c *ℤ z) 0ℤ) (hyp (subM m k)))
         (sym (coeff-scaleT-full k c y2 m)))

*P-right-cong : (x y1 y2 : MPoly) → ((j : Mono) → coeff j y1 ≡ coeff j y2) →
                (m : Mono) → coeff m (x *P y1) ≡ coeff m (x *P y2)
*P-right-cong []             y1 y2 hyp m = refl
*P-right-cong (term k c ∷ x') y1 y2 hyp m =
  trans (coeff-++ m (scaleT (term k c) y1) (x' *P y1))
  (trans (cong₂ _+ℤ_ (scaleT-cong k c y1 y2 hyp m) (*P-right-cong x' y1 y2 hyp m))
         (sym (coeff-++ m (scaleT (term k c) y2) (x' *P y2))))

*P-normalizeʳ : (x y : MPoly) (m : Mono) → coeff m (x *P normalize y) ≡ coeff m (x *P y)
*P-normalizeʳ x y m = *P-right-cong x (normalize y) y (λ j → coeff-normalize j y) m

------------------------------------------------------------------------
-- 6. coeff-canonicity — two sorted polys with equal coeffs are ≡ (the slog).
------------------------------------------------------------------------

nz→≢0 : {k : ℤ} → nzB k ≡ tt → ¬ (k ≡ 0ℤ)
nz→≢0 {k} nz k≡0 = ff≢tt (trans (sym (nzB-ff k≡0)) nz)

coeff-below : (m : Mono) (p : MPoly) → isSortedB p ≡ tt → minB m p ≡ tt → coeff m p ≡ 0ℤ
coeff-below m []              _  _   = refl
coeff-below m (term n d ∷ p') sp m<n =
  trans (coeff-cons-ff m n d p' (ltMᵇ→eqMff m n m<n))
        (coeff-below m p' (sorted-tail n d p' sp) (minB-trans m n p' m<n (sorted-min n d p' sp)))

coeff-head : (m : Mono) (k : ℤ) (p : MPoly) → isSortedB (term m k ∷ p) ≡ tt → coeff m (term m k ∷ p) ≡ k
coeff-head m k p sp =
  trans (coeff-cons-tt m m k p (eqM-refl m))
  (trans (cong (k +ℤ_) (coeff-below m p (sorted-tail m k p sp) (sorted-min m k p sp)))
         (+ℤ-identityʳ k))

coeff-canonicity : (p q : MPoly) → isSortedB p ≡ tt → isSortedB q ≡ tt →
                   ((m : Mono) → coeff m p ≡ coeff m q) → p ≡ q
coeff-canonicity []              []                sp sq h = refl
coeff-canonicity []              (term n d ∷ q')   sp sq h =
  ⊥-elim (nz→≢0 (sorted-nz n d q' sq) (sym (trans (h n) (coeff-head n d q' sq))))
coeff-canonicity (term m k ∷ p') []               sp sq h =
  ⊥-elim (nz→≢0 (sorted-nz m k p' sp) (trans (sym (coeff-head m k p' sp)) (h m)))
coeff-canonicity (term m k ∷ p') (term n d ∷ q')  sp sq h with triM m n
... | ltM m<n = ⊥-elim (nz→≢0 (sorted-nz m k p' sp)
      (trans (sym (coeff-head m k p' sp))
             (trans (h m) (coeff-below m (term n d ∷ q') sq (<M→ltMᵇ m<n)))))
... | gtM n<m = ⊥-elim (nz→≢0 (sorted-nz n d q' sq)
      (trans (sym (coeff-head n d q' sq))
             (trans (sym (h n)) (coeff-below n (term m k ∷ p') sp (<M→ltMᵇ n<m)))))
... | eqM≡ refl = cong₂ (λ kk pp → term m kk ∷ pp) k≡d
                        (coeff-canonicity p' q' (sorted-tail m k p' sp) (sorted-tail m d q' sq) h')
  where
    k≡d : k ≡ d
    k≡d = trans (sym (coeff-head m k p' sp)) (trans (h m) (coeff-head m d q' sq))
    h' : (x : Mono) → coeff x p' ≡ coeff x q'
    h' x with eqM x m in e
    ... | tt = +ℤ-cancelˡ k (coeff x p') (coeff x q')
               (trans (sym (coeff-cons-tt x m k p' e))
               (trans (h x)
               (trans (coeff-cons-tt x m d q' e) (cong (_+ℤ coeff x q') (sym k≡d)))))
    ... | ff = trans (sym (coeff-cons-ff x m k p' e))
               (trans (h x) (coeff-cons-ff x m d q' e))

------------------------------------------------------------------------
-- 7. Assemble the Semiring.
------------------------------------------------------------------------

NormPoly⟨_⟩ : (p : MPoly) → isSortedB p ≡ tt → NormPoly
NormPoly⟨ p ⟩ sp = (p , sp)

0P : NormPoly
0P = ([] , refl)

1P : NormPoly
1P = (normalize 𝟙P , normalize-sorted 𝟙P)

_⊕_ : NormPoly → NormPoly → NormPoly
a ⊕ b = (normalize (proj₁ a ++ proj₁ b) , normalize-sorted (proj₁ a ++ proj₁ b))

_⊗_ : NormPoly → NormPoly → NormPoly
a ⊗ b = (normalize (proj₁ a *P proj₁ b) , normalize-sorted (proj₁ a *P proj₁ b))

law-≡ : (a b : NormPoly) → ((m : Mono) → coeff m (proj₁ a) ≡ coeff m (proj₁ b)) → a ≡ b
law-≡ a b hyp = NormPoly-≡ (coeff-canonicity (proj₁ a) (proj₁ b) (proj₂ a) (proj₂ b) hyp)

coeff⊕ : (a b : NormPoly) (m : Mono) → coeff m (proj₁ (a ⊕ b)) ≡ coeff m (proj₁ a) +ℤ coeff m (proj₁ b)
coeff⊕ a b m = trans (coeff-normalize m (proj₁ a ++ proj₁ b)) (coeff-++ m (proj₁ a) (proj₁ b))

coeff⊗ : (a b : NormPoly) (m : Mono) → coeff m (proj₁ (a ⊗ b)) ≡ coeff m (proj₁ a *P proj₁ b)
coeff⊗ a b m = coeff-normalize m (proj₁ a *P proj₁ b)

⊕-assoc : (a b c : NormPoly) → (a ⊕ b) ⊕ c ≡ a ⊕ (b ⊕ c)
⊕-assoc a b c = law-≡ _ _ λ m →
  trans (coeff⊕ (a ⊕ b) c m)
  (trans (cong (_+ℤ coeff m (proj₁ c)) (coeff⊕ a b m))
  (trans (+ℤ-assoc (coeff m (proj₁ a)) (coeff m (proj₁ b)) (coeff m (proj₁ c)))
  (trans (cong (coeff m (proj₁ a) +ℤ_) (sym (coeff⊕ b c m)))
         (sym (coeff⊕ a (b ⊕ c) m)))))

⊕-idˡ : (a : NormPoly) → 0P ⊕ a ≡ a
⊕-idˡ a = law-≡ _ _ λ m → trans (coeff⊕ 0P a m) (+ℤ-identityˡ (coeff m (proj₁ a)))

⊕-idʳ : (a : NormPoly) → a ⊕ 0P ≡ a
⊕-idʳ a = law-≡ _ _ λ m → trans (coeff⊕ a 0P m) (+ℤ-identityʳ (coeff m (proj₁ a)))

⊗-assoc : (a b c : NormPoly) → (a ⊗ b) ⊗ c ≡ a ⊗ (b ⊗ c)
⊗-assoc a b c = law-≡ _ _ λ m →
  trans (coeff⊗ (a ⊗ b) c m)
  (trans (*P-normalizeˡ (proj₁ a *P proj₁ b) (proj₁ c) m)
  (trans (coeff-*P-assoc m (proj₁ a) (proj₁ b) (proj₁ c))
  (trans (sym (*P-normalizeʳ (proj₁ a) (proj₁ b *P proj₁ c) m))
         (sym (coeff⊗ a (b ⊗ c) m)))))

-- 𝟙P is a left/right unit for coeff∘*P.
mul-𝟙ˡ : (p : MPoly) (m : Mono) → coeff m (𝟙P *P p) ≡ coeff m p
mul-𝟙ˡ p m = trans (coeff-++ m (scaleT (term (mono 0 0 0) 1ℤ) p) []) e
  where
    s1 : (p : MPoly) (m : Mono) → coeff m (scaleT (term (mono 0 0 0) 1ℤ) p) ≡ coeff m p
    s1 []             m = refl
    s1 (term u d ∷ p') m rewrite addM-idˡ u =
      trans (coeff-cons m u (1ℤ *ℤ d) (scaleT (term (mono 0 0 0) 1ℤ) p'))
      (trans st (sym (coeff-cons m u d p')))
      where
        st : Bcase (eqM m u) ((1ℤ *ℤ d) +ℤ coeff m (scaleT (term (mono 0 0 0) 1ℤ) p')) (coeff m (scaleT (term (mono 0 0 0) 1ℤ) p'))
           ≡ Bcase (eqM m u) (d +ℤ coeff m p') (coeff m p')
        st rewrite s1 p' m with eqM m u
        ... | tt = cong (_+ℤ coeff m p') (*ℤ-identityˡ d)
        ... | ff = refl
    e : coeff m (scaleT (term (mono 0 0 0) 1ℤ) p) +ℤ coeff m [] ≡ coeff m p
    e = trans (+ℤ-identityʳ (coeff m (scaleT (term (mono 0 0 0) 1ℤ) p))) (s1 p m)

mul-𝟙ʳ : (p : MPoly) (m : Mono) → coeff m (p *P 𝟙P) ≡ coeff m p
mul-𝟙ʳ []             m = refl
mul-𝟙ʳ (term k c ∷ p') m =
  trans (coeff-++ m (scaleT (term k c) 𝟙P) (p' *P 𝟙P))
  (trans (cong₂ _+ℤ_ scHead (mul-𝟙ʳ p' m))
  (trans bridge (sym (coeff-cons m k c p'))))
  where
    -- scaleT (term k c) 𝟙P = term (addM k (mono 0 0 0)) (c *ℤ 1ℤ) ∷ []
    scHead : coeff m (scaleT (term k c) 𝟙P) ≡ Bcase (eqM m k) c 0ℤ
    scHead rewrite addM-idʳ k =
      trans (coeff-cons m k (c *ℤ 1ℤ) [])
            (cong (λ z → Bcase (eqM m k) z 0ℤ)
                  (trans (+ℤ-identityʳ (c *ℤ 1ℤ)) (*ℤ-identityʳ c)))
    bridge : Bcase (eqM m k) c 0ℤ +ℤ coeff m p' ≡ Bcase (eqM m k) (c +ℤ coeff m p') (coeff m p')
    bridge with eqM m k
    ... | tt = refl
    ... | ff = +ℤ-identityˡ (coeff m p')
    -- Then coeff m ((term k c ∷ p') *P 𝟙P) = Bcase (eqM m k) c 0ℤ +ℤ coeff m p'
    --   vs coeff m (term k c ∷ p') = Bcase (eqM m k) (c +ℤ coeff m p') (coeff m p')

⊗-idˡ : (a : NormPoly) → 1P ⊗ a ≡ a
⊗-idˡ a = law-≡ _ _ λ m →
  trans (coeff⊗ 1P a m) (trans (*P-normalizeˡ 𝟙P (proj₁ a) m) (mul-𝟙ˡ (proj₁ a) m))

⊗-idʳ : (a : NormPoly) → a ⊗ 1P ≡ a
⊗-idʳ a = law-≡ _ _ λ m →
  trans (coeff⊗ a 1P m) (trans (*P-normalizeʳ (proj₁ a) 𝟙P m) (mul-𝟙ʳ (proj₁ a) m))

distribL : (a b c : NormPoly) → a ⊗ (b ⊕ c) ≡ (a ⊗ b) ⊕ (a ⊗ c)
distribL a b c = law-≡ _ _ λ m →
  trans (coeff⊗ a (b ⊕ c) m)
  (trans (*P-normalizeʳ (proj₁ a) (proj₁ b ++ proj₁ c) m)
  (trans (coeff-*P-distʳ m (proj₁ a) (proj₁ b) (proj₁ c))
  (trans (sym (cong₂ _+ℤ_ (coeff⊗ a b m) (coeff⊗ a c m)))
         (sym (coeff⊕ (a ⊗ b) (a ⊗ c) m)))))

distribR : (a b c : NormPoly) → (a ⊕ b) ⊗ c ≡ (a ⊗ c) ⊕ (b ⊗ c)
distribR a b c = law-≡ _ _ λ m →
  trans (coeff⊗ (a ⊕ b) c m)
  (trans (*P-normalizeˡ (proj₁ a ++ proj₁ b) (proj₁ c) m)
  (trans (coeff-*P-distˡ m (proj₁ a) (proj₁ b) (proj₁ c))
  (trans (sym (cong₂ _+ℤ_ (coeff⊗ a c m) (coeff⊗ b c m)))
         (sym (coeff⊕ (a ⊗ c) (b ⊗ c) m)))))

zabsL : (a : NormPoly) → 0P ⊗ a ≡ 0P
zabsL a = law-≡ _ _ λ m → refl

zabsR : (a : NormPoly) → a ⊗ 0P ≡ 0P
zabsR a = law-≡ _ _ λ m → trans (coeff⊗ a 0P m) (coeff-*P-nilʳ m (proj₁ a))

NormPoly-Semiring : Semiring NormPoly
NormPoly-Semiring = record
  { +-monoid          = mk-monoid _⊕_ 0P ⊕-assoc ⊕-idˡ ⊕-idʳ
  ; *-monoid          = mk-monoid _⊗_ 1P ⊗-assoc ⊗-idˡ ⊗-idʳ
  ; distrib-left      = distribL
  ; distrib-right     = distribR
  ; zero-absorb-left  = zabsL
  ; zero-absorb-right = zabsR
  }

------------------------------------------------------------------------
-- 8. ε₂ and ε₂-sq (for RUNG 3c's WithSign), + a non-vacuity pole.
------------------------------------------------------------------------

ε₂ : NormPoly
ε₂ = (normalize (kP (-suc 0)) , normalize-sorted (kP (-suc 0)))

ε₂-sq : ε₂ ⊗ ε₂ ≡ 1P
ε₂-sq = law-≡ _ _ λ m →
  trans (coeff⊗ ε₂ ε₂ m)
  (trans (*P-normalizeˡ (kP (-suc 0)) (normalize (kP (-suc 0))) m)
  (trans (*P-normalizeʳ (kP (-suc 0)) (kP (-suc 0)) m)
  (trans (cong (λ z → coeff m (term (mono 0 0 0) z ∷ [])) mul-sign-computes)
         (sym (coeff-normalize m 𝟙P)))))

-- POLE: normalization actually combines like terms — (X ⊕ Y)⊗(X ⊕ Y) has its
-- xy cross terms MERGED to coefficient 2, which raw *P (unmerged ++) does not.
X∷ Y∷ : NormPoly
X∷ = (normalize X , normalize-sorted X)
Y∷ = (normalize Y , normalize-sorted Y)

poly-⊗-reorders : coeff (mono 1 1 0) (proj₁ ((X∷ ⊕ Y∷) ⊗ (X∷ ⊕ Y∷))) ≡ + 2
poly-⊗-reorders = refl
