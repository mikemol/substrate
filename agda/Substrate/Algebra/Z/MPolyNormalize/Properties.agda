{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties — ⟡jac-poly-normalize (RUNG 3a), PROOFS.
--
-- The proof layer over `MPolyNormalize`'s definitions: the coeff-homomorphism
-- core (`coeff` invariant under `normalize`, `++`), the ordering foundation
-- (`_<M_` transitivity via ℕ's `<-trans`, bridged to boolean `ltMᵇ` — the
-- shared ordering machinery RUNG 3b's `coeff-canonicity` also consumes), and
-- the sortedness/idempotence of `normalize` — culminating in the reuse witness
-- `normalize-Canonical = idem-Canonical normalize normalize-idem`.
--
-- Separated from the definition module so the datatype-exporting
-- `MPolyNormalize` keeps a proof-free import closure (def/proof-separation
-- gate). Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.MPolyNormalize.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (<-irrefl; ≤-<-trans; <→≤)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ; 1ℤ; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-assoc; +ℤ-identityˡ)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; 𝔹; tt; ff; and)
open import Substrate.Algebra.Quotient
  using (Quotient; ker-Quotient; idem-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)
open import Substrate.Algebra.Z.MPolyNormalize

------------------------------------------------------------------------
-- eqM ↔ ≡.
------------------------------------------------------------------------

private
  eqℕ-refl : (n : ℕ) → eqℕ n n ≡ tt
  eqℕ-refl zero    = refl
  eqℕ-refl (suc n) = eqℕ-refl n

  eqℕ-sound : {p q : ℕ} → eqℕ p q ≡ tt → p ≡ q
  eqℕ-sound {zero}  {zero}  _ = refl
  eqℕ-sound {suc p} {suc q} e = cong suc (eqℕ-sound e)

eqM-refl : (m : Mono) → eqM m m ≡ tt
eqM-refl (mono a b c) rewrite eqℕ-refl a | eqℕ-refl b | eqℕ-refl c = refl

eqM-sound : {m n : Mono} → eqM m n ≡ tt → m ≡ n
eqM-sound {mono a b c} {mono d e f} h =
  cong₃ mono (eqℕ-sound (and-l {eqℕ a d} h))
             (eqℕ-sound (and-l {eqℕ b e} (and-r {eqℕ a d} h)))
             (eqℕ-sound (and-r {eqℕ b e} (and-r {eqℕ a d} h)))

------------------------------------------------------------------------
-- ℕ / Mono order lemmas.
------------------------------------------------------------------------

<→≢ : {a b : ℕ} → a < b → ¬ (a ≡ b)
<→≢ {a} lt refl = <-irrefl a lt

<-trans : {a b c : ℕ} → a < b → b < c → a < c
<-trans a<b b<c = ≤-<-trans (<→≤ a<b) b<c

<M-trans : {m n o : Mono} → m <M n → n <M o → m <M o
<M-trans (<x a<d) (<x d<h) = <x (<-trans a<d d<h)
<M-trans (<x a<d) (<y _)   = <x a<d
<M-trans (<x a<d) (<z _)   = <x a<d
<M-trans (<y _)   (<x a<h) = <x a<h
<M-trans (<y b<e) (<y e<i) = <y (<-trans b<e e<i)
<M-trans (<y b<e) (<z _)   = <y b<e
<M-trans (<z _)   (<x a<h) = <x a<h
<M-trans (<z _)   (<y b<i) = <y b<i
<M-trans (<z c<g) (<z g<j) = <z (<-trans c<g g<j)

-- irreflexivity by PROJECTING the differing coordinate (m, n stay
-- independent ⇒ no `a = a` self-equation ⇒ --without-K-safe).
<M→≢ : {m n : Mono} → m <M n → ¬ (m ≡ n)
<M→≢ (<x a<d) eq = <→≢ a<d (cong fst₃ eq)
<M→≢ (<y b<e) eq = <→≢ b<e (cong snd₃ eq)
<M→≢ (<z c<f) eq = <→≢ c<f (cong thd₃ eq)

<M-irrefl : {m : Mono} → m <M m → ⊥
<M-irrefl m<m = <M→≢ m<m refl

<M→ltMᵇ : {m n : Mono} → m <M n → ltMᵇ m n ≡ tt
<M→ltMᵇ (<x {a}{b}{c}{d}{e}{f} a<d) with triℕ a d | triℕ b e | triℕ c f
... | ltN _   | _        | _       = refl
... | eqN a≡d | _        | _       = ⊥-elim (<→≢ a<d a≡d)
... | gtN d<a | _        | _       = ⊥-elim (<-irrefl a (<-trans a<d d<a))
<M→ltMᵇ (<y {a}{b}{c}{e}{f} b<e) with triℕ a a | triℕ b e | triℕ c f
... | ltN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | gtN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | eqN _   | ltN _    | _       = refl
... | eqN _   | eqN b≡e  | _       = ⊥-elim (<→≢ b<e b≡e)
... | eqN _   | gtN e<b  | _       = ⊥-elim (<-irrefl b (<-trans b<e e<b))
<M→ltMᵇ (<z {a}{b}{c}{f} c<f) with triℕ a a | triℕ b b | triℕ c f
... | ltN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | gtN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | eqN _   | ltN b<b  | _       = ⊥-elim (<-irrefl b b<b)
... | eqN _   | gtN b<b  | _       = ⊥-elim (<-irrefl b b<b)
... | eqN _   | eqN _    | ltN _   = refl
... | eqN _   | eqN _    | eqN c≡f = ⊥-elim (<→≢ c<f c≡f)
... | eqN _   | eqN _    | gtN f<c = ⊥-elim (<-irrefl c (<-trans c<f f<c))

ltMᵇ→<M : (m n : Mono) → ltMᵇ m n ≡ tt → m <M n
ltMᵇ→<M (mono a b c) (mono d e f) h with triℕ a d | triℕ b e | triℕ c f
... | ltN a<d  | _        | _       = <x a<d
... | gtN _    | _        | _       = ⊥-elim (ff≢tt h)
... | eqN refl | ltN b<e  | _       = <y b<e
... | eqN refl | gtN _    | _       = ⊥-elim (ff≢tt h)
... | eqN refl | eqN refl | ltN c<f = <z c<f
... | eqN refl | eqN refl | gtN _   = ⊥-elim (ff≢tt h)
... | eqN refl | eqN refl | eqN _   = ⊥-elim (ff≢tt h)

-- explicit monos: `ltMᵇ` is a defined function, so its implicits are NOT
-- inferrable by inversion (same reason eqM-sound pins its `and-l`/`and-r`).
ltMᵇ-trans : (m n o : Mono) → ltMᵇ m n ≡ tt → ltMᵇ n o ≡ tt → ltMᵇ m o ≡ tt
ltMᵇ-trans m n o h1 h2 = <M→ltMᵇ (<M-trans (ltMᵇ→<M m n h1) (ltMᵇ→<M n o h2))

ltMᵇ-irrefl : (m : Mono) → ltMᵇ m m ≡ tt → ⊥
ltMᵇ-irrefl m h = <M-irrefl (ltMᵇ→<M m m h)

-- strict key-order ⇒ keys distinct ⇒ eqM ff (bridges to coeff's eqM test; RUNG 3b).
ltMᵇ→eqMff : (m n : Mono) → ltMᵇ m n ≡ tt → eqM m n ≡ ff
ltMᵇ→eqMff m n h with eqM m n in e
... | ff = refl
... | tt = ⊥-elim (<M→≢ (ltMᵇ→<M m n h) (eqM-sound {m}{n} e))

------------------------------------------------------------------------
-- Nonzero-coefficient lemmas.
------------------------------------------------------------------------

nzB-tt : {k : ℤ} → ¬ (k ≡ 0ℤ) → nzB k ≡ tt
nzB-tt {k} k≢0 with k ≟ℤ 0ℤ
... | yes k≡0 = ⊥-elim (k≢0 k≡0)
... | no  _   = refl

nzB-ff : {k : ℤ} → k ≡ 0ℤ → nzB k ≡ ff
nzB-ff {k} k≡0 with k ≟ℤ 0ℤ
... | yes _   = refl
... | no  k≢0 = ⊥-elim (k≢0 k≡0)

------------------------------------------------------------------------
-- coeff is a homomorphism (invariant under normalize).
------------------------------------------------------------------------

coeff-cons : (j m : Mono) (k : ℤ) (p : MPoly) →
             coeff j (term m k ∷ p) ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
coeff-cons j m k p with eqM j m
... | tt = refl
... | ff = refl

coeff-cons-tt : (j m : Mono) (k : ℤ) (p : MPoly) →
                eqM j m ≡ tt → coeff j (term m k ∷ p) ≡ k +ℤ coeff j p
coeff-cons-tt j m k p e =
  trans (coeff-cons j m k p) (cong (λ b → Bcase b (k +ℤ coeff j p) (coeff j p)) e)

coeff-cons-ff : (j m : Mono) (k : ℤ) (p : MPoly) →
                eqM j m ≡ ff → coeff j (term m k ∷ p) ≡ coeff j p
coeff-cons-ff j m k p e =
  trans (coeff-cons j m k p) (cong (λ b → Bcase b (k +ℤ coeff j p) (coeff j p)) e)

coeff-++ : (m : Mono) (p q : MPoly) → coeff m (p ++ q) ≡ coeff m p +ℤ coeff m q
coeff-++ m [] q = sym (+ℤ-identityˡ (coeff m q))
coeff-++ m (term n k ∷ p) q with eqM m n
... | tt = trans (cong (k +ℤ_) (coeff-++ m p q)) (sym (+ℤ-assoc k (coeff m p) (coeff m q)))
... | ff = coeff-++ m p q

coeff-consNZ : (j m : Mono) (k : ℤ) (p : MPoly) →
               coeff j (consNZ m k p) ≡ coeff j (term m k ∷ p)
coeff-consNZ j m k p with k ≟ℤ 0ℤ
... | no  _ = refl
... | yes k≡0 = trans eq (sym (coeff-cons j m k p))
  where
    eq : coeff j p ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
    eq with eqM j m
    ... | tt = sym (trans (cong (_+ℤ coeff j p) k≡0) (+ℤ-identityˡ (coeff j p)))
    ... | ff = refl

coeff-insertT : (j m : Mono) (k : ℤ) (p : MPoly) →
                coeff j (insertT m k p) ≡ coeff j (term m k ∷ p)
coeff-insertT j m k [] = coeff-consNZ j m k []
coeff-insertT j m k (term n d ∷ p) with triM m n
... | ltM _ = coeff-consNZ j m k (term n d ∷ p)
... | eqM≡ refl =
      trans (coeff-consNZ j m (k +ℤ d) p)
      (trans (coeff-cons j m (k +ℤ d) p)
      (trans mid (sym (coeff-cons j m k (term m d ∷ p)))))
  where
    mid : Bcase (eqM j m) ((k +ℤ d) +ℤ coeff j p) (coeff j p)
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term m d ∷ p)) (coeff j (term m d ∷ p))
    mid rewrite coeff-cons j m d p with eqM j m
    ... | tt = +ℤ-assoc k d (coeff j p)
    ... | ff = refl
coeff-insertT j m k (term n d ∷ p) | gtM n<m =
      trans (coeff-cons j n d (insertT m k p))
      (trans mid
             (sym (coeff-cons j m k (term n d ∷ p))))
  where
    m≢n : ¬ (m ≡ n)
    m≢n e = <M→≢ n<m (sym e)
    mid : Bcase (eqM j n) (d +ℤ coeff j (insertT m k p)) (coeff j (insertT m k p))
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term n d ∷ p))  (coeff j (term n d ∷ p))
    mid rewrite coeff-insertT j m k p | coeff-cons j m k p | coeff-cons j n d p
              with eqM j m in ejm | eqM j n in ejn
    ... | tt | tt = ⊥-elim (m≢n (trans (sym (eqM-sound {j} {m} ejm)) (eqM-sound {j} {n} ejn)))
    ... | tt | ff = refl
    ... | ff | tt = refl
    ... | ff | ff = refl

coeff-normalize : (j : Mono) (p : MPoly) → coeff j (normalize p) ≡ coeff j p
coeff-normalize j []             = refl
coeff-normalize j (term m k ∷ p) =
  trans (coeff-insertT j m k (normalize p))
  (trans (coeff-cons j m k (normalize p))
  (trans step (sym (coeff-cons j m k p))))
  where
    step : Bcase (eqM j m) (k +ℤ coeff j (normalize p)) (coeff j (normalize p))
         ≡ Bcase (eqM j m) (k +ℤ coeff j p)            (coeff j p)
    step with eqM j m
    ... | tt = cong (k +ℤ_) (coeff-normalize j p)
    ... | ff = coeff-normalize j p

------------------------------------------------------------------------
-- invariant-extraction (pinned `and-l`/`and-r` implicits: `and` is a
-- defined function ⇒ not inferrable by inversion).
------------------------------------------------------------------------

sorted-nz : (n : Mono) (d : ℤ) (p : MPoly) → isSortedB (term n d ∷ p) ≡ tt → nzB d ≡ tt
sorted-nz n d []              sq = sq
sorted-nz n d (term u f ∷ p') sq = and-l {nzB d} sq

sorted-tail : (n : Mono) (d : ℤ) (p : MPoly) → isSortedB (term n d ∷ p) ≡ tt → isSortedB p ≡ tt
sorted-tail n d []              _  = refl
sorted-tail n d (term u f ∷ p') sq = and-r {ltMᵇ n u} (and-r {nzB d} sq)

sorted-min : (n : Mono) (d : ℤ) (p : MPoly) → isSortedB (term n d ∷ p) ≡ tt → minB n p ≡ tt
sorted-min n d []              _  = refl
sorted-min n d (term u f ∷ p') sq = and-l {ltMᵇ n u} (and-r {nzB d} sq)

minB-trans : (n o : Mono) (p : MPoly) → ltMᵇ n o ≡ tt → minB o p ≡ tt → minB n p ≡ tt
minB-trans n o []             _   _   = refl
minB-trans n o (term u f ∷ _) n<o o<u = ltMᵇ-trans n o u n<o o<u

------------------------------------------------------------------------
-- normalize produces a sorted list.
------------------------------------------------------------------------

consNZ-sorted : (m : Mono) (k : ℤ) (q : MPoly) →
                isSortedB q ≡ tt → minB m q ≡ tt → isSortedB (consNZ m k q) ≡ tt
consNZ-sorted m k []             sq mq with k ≟ℤ 0ℤ
... | yes _  = refl
... | no k≢0 = nzB-tt k≢0
consNZ-sorted m k (term n d ∷ q') sq mq with k ≟ℤ 0ℤ
... | yes _  = sq
... | no k≢0 = and-tt (nzB-tt k≢0) (and-tt mq sq)

consNZ-min : (n m : Mono) (k : ℤ) (xs : MPoly) →
             ltMᵇ n m ≡ tt → minB n xs ≡ tt → minB n (consNZ m k xs) ≡ tt
consNZ-min n m k xs n<m nxs with k ≟ℤ 0ℤ
... | yes _ = nxs
... | no  _ = n<m

insertT-min : (n m : Mono) (k : ℤ) (q : MPoly) →
              ltMᵇ n m ≡ tt → isSortedB q ≡ tt → minB n q ≡ tt →
              minB n (insertT m k q) ≡ tt
insertT-min n m k []             n<m sq n<q = consNZ-min n m k [] n<m refl
insertT-min n m k (term o e ∷ q') n<m sq n<q with triM m o
... | ltM _   = consNZ-min n m k (term o e ∷ q') n<m n<q
... | eqM≡ refl = consNZ-min n m (k +ℤ e) q' n<q (minB-trans n m q' n<q (sorted-min m e q' sq))
... | gtM _   = n<q

cons-sorted : (n : Mono) (d : ℤ) (xs : MPoly) →
              nzB d ≡ tt → minB n xs ≡ tt → isSortedB xs ≡ tt → isSortedB (term n d ∷ xs) ≡ tt
cons-sorted n d []              nzd _   _   = nzd
cons-sorted n d (term u f ∷ xs') nzd n<u sxs = and-tt nzd (and-tt n<u sxs)

insertT-sorted : (m : Mono) (k : ℤ) (q : MPoly) →
                 isSortedB q ≡ tt → isSortedB (insertT m k q) ≡ tt
insertT-sorted m k []             sq = consNZ-sorted m k [] sq refl
insertT-sorted m k (term n d ∷ p) sq with triM m n
... | ltM m<n = consNZ-sorted m k (term n d ∷ p) sq (<M→ltMᵇ m<n)
... | eqM≡ refl = consNZ-sorted n (k +ℤ d) p (sorted-tail n d p sq) (sorted-min n d p sq)
... | gtM n<m = cons-sorted n d (insertT m k p)
                  (sorted-nz n d p sq)
                  (insertT-min n m k p (<M→ltMᵇ n<m) (sorted-tail n d p sq) (sorted-min n d p sq))
                  (insertT-sorted m k p (sorted-tail n d p sq))

normalize-sorted : (p : MPoly) → isSortedB (normalize p) ≡ tt
normalize-sorted []             = refl
normalize-sorted (term m k ∷ p) = insertT-sorted m k (normalize p) (normalize-sorted p)

------------------------------------------------------------------------
-- normalize fixes an already-sorted list ⇒ idempotence.
------------------------------------------------------------------------

consNZ-nz : (m : Mono) (k : ℤ) (q : MPoly) → nzB k ≡ tt → consNZ m k q ≡ term m k ∷ q
consNZ-nz m k q nzk with k ≟ℤ 0ℤ
... | no  _ = refl
... | yes _ = ⊥-elim (ff≢tt nzk)

insertT-prepend : (m : Mono) (k : ℤ) (q : MPoly) →
                  nzB k ≡ tt → minB m q ≡ tt → insertT m k q ≡ term m k ∷ q
insertT-prepend m k []              nzk _   = consNZ-nz m k [] nzk
insertT-prepend m k (term u f ∷ q'') nzk m<u with triM m u
... | ltM _   = consNZ-nz m k (term u f ∷ q'') nzk
... | eqM≡ refl = ⊥-elim (ltMᵇ-irrefl m m<u)
... | gtM u<m = ⊥-elim (<M-irrefl (<M-trans (ltMᵇ→<M m u m<u) u<m))

normalize-fixed : (q : MPoly) → isSortedB q ≡ tt → normalize q ≡ q
normalize-fixed []             _  = refl
normalize-fixed (term m k ∷ q') sq =
  trans (cong (insertT m k) (normalize-fixed q' (sorted-tail m k q' sq)))
        (insertT-prepend m k q' (sorted-nz m k q' sq) (sorted-min m k q' sq))

normalize-idem : (p : MPoly) → normalize (normalize p) ≡ normalize p
normalize-idem p = normalize-fixed (normalize p) (normalize-sorted p)

-- THE REUSE WITNESS: normalize is a canonical form for its own kernel.
normalize-Canonical : Canonical⟦de760d07⟧ (ker-Quotient normalize)
normalize-Canonical = idem-Canonical normalize normalize-idem

------------------------------------------------------------------------
-- Non-vacuity poles (ship as terms).
------------------------------------------------------------------------

-- (a) x + x normalizes so coeff x = 2 (combine-on-equal actually fires).
xP : MPoly
xP = term (mono 1 0 0) 1ℤ ∷ term (mono 1 0 0) 1ℤ ∷ []
pole-x+x : coeff (mono 1 0 0) (normalize xP) ≡ + 2
pole-x+x = refl

-- (b) isSortedB rejects a descending list [2x, 1].
reject-pole : isSortedB (term (mono 1 0 0) (+ 2) ∷ term (mono 0 0 0) 1ℤ ∷ []) ≡ ff
reject-pole = refl

-- (c) isSortedB rejects a zero-coeff term.
zero-reject : isSortedB (term (mono 1 0 0) 0ℤ ∷ []) ≡ ff
zero-reject = refl

-- (d) isSortedB accepts a strictly-ascending, all-nonzero list.
accept-pole : isSortedB (term (mono 0 0 0) 1ℤ ∷ term (mono 1 0 0) (+ 2) ∷ []) ≡ tt
accept-pole = refl
