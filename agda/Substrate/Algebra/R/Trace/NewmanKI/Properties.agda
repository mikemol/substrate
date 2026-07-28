{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanKI.Properties — SN, WCR, and (via Newman's
-- lemma) CR for KI-reduction. Split from NewmanKI (the definition module) per the
-- def/proof separation policy: the proof-module imports (Nat.Properties*) live here,
-- so a def-consumer of NewmanKI never pays for these proofs.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.NewmanKI.Properties where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; s≤s; z≤n; _≤_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Order using (≤-refl; ≤-<-trans; m≤m+n; n≤m+n; +-monoʳ-≤; ≤-trans)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.R.Trace.NewmanKI

------------------------------------------------------------------------
-- 3. Every step strictly shrinks size (⟹ SN). β-K DELETES y: size x < size ((K∙x)∙y).
------------------------------------------------------------------------
open import Substrate.Foundation.RewriteConfluence _⇒_
  using (_⇒*_; done; _◅_; _++*_; Converge; WCR; CR; SN; newman)
+-monoʳ-< : (k : ℕ) {m n : ℕ} → m < n → (k + m) < (k + n)
+-monoʳ-< zero    m<n = m<n
+-monoʳ-< (suc k) m<n = s≤s (+-monoʳ-< k m<n)

+-monoˡ-< : {m n : ℕ} (k : ℕ) → m < n → (m + k) < (n + k)
+-monoˡ-< {m}{n} k m<n rewrite +-comm m k | +-comm n k = +-monoʳ-< k m<n

step-size< : {a b : Tm} → a ⇒ b → size b < size a
step-size< (β-I x)      = s≤s (n≤m+n 1 (size x))
step-size< (β-K x y)    = s≤s (≤-trans (n≤m+n 2 (size x)) (m≤m+n (suc (suc (size x))) (size y)))
step-size< (cong-l g r) = s≤s (+-monoˡ-< (size g) (step-size< r))
step-size< (cong-r f r) = s≤s (+-monoʳ-< (size f) (step-size< r))

------------------------------------------------------------------------
-- 4. SN by measure transport.
------------------------------------------------------------------------
acc-from-size : (a : Tm) → Acc _<_ (size a) → Acc (λ x y → y ⇒ x) a
acc-from-size a (acc rs) = acc (λ b a⇒b → acc-from-size b (rs (size b) (step-size< a⇒b)))

sn : (a : Tm) → Acc (λ x y → y ⇒ x) a
sn a = acc-from-size a (<-wellFounded (size a))

------------------------------------------------------------------------
-- 5. WCR (Newman API + congruence closure), then the critical pairs.
------------------------------------------------------------------------

cong-l* : {f f' : Tm} (g : Tm) → f ⇒* f' → (f ∙ g) ⇒* (f' ∙ g)
cong-l* g done    = done
cong-l* g (s ◅ r) = cong-l g s ◅ cong-l* g r

cong-r* : (f : Tm) {g g' : Tm} → g ⇒* g' → (f ∙ g) ⇒* (f ∙ g')
cong-r* f done    = done
cong-r* f (s ◅ r) = cong-r f s ◅ cong-r* f r

wcr : WCR
wcr (β-I x)       (β-I .x)      = x , (done , done)
wcr (β-K x y)     (β-K .x .y)   = x , (done , done)
wcr (β-I x)       (cong-r .I r) = _ , ((r ◅ done) , (β-I _ ◅ done))
wcr (cong-r .I r) (β-I x)       = _ , ((β-I _ ◅ done) , (r ◅ done))
wcr (β-K x y)     (cong-r .(K ∙ x) r) = _ , (done , (β-K _ _ ◅ done))
wcr (cong-r .(K ∙ x) r) (β-K x y)     = _ , ((β-K _ _ ◅ done) , done)
wcr (β-K x y)     (cong-l .y (cong-r .K r')) = _ , ((r' ◅ done) , (β-K _ _ ◅ done))
wcr (cong-l .y (cong-r .K r')) (β-K x y)     = _ , ((β-K _ _ ◅ done) , (r' ◅ done))
wcr (cong-l g r1) (cong-l .g r2) with wcr r1 r2
... | d , (p , q) = (d ∙ g) , (cong-l* g p , cong-l* g q)
wcr (cong-r f r1) (cong-r .f r2) with wcr r1 r2
... | d , (p , q) = (f ∙ d) , (cong-r* f p , cong-r* f q)
wcr (cong-l g r1) (cong-r f r2) = _ , ((cong-r _ r2 ◅ done) , (cong-l _ r1 ◅ done))
wcr (cong-r f r1) (cong-l g r2) = _ , ((cong-l _ r2 ◅ done) , (cong-r _ r1 ◅ done))

------------------------------------------------------------------------
-- 6. THE INSTANCE: Newman gives CR for KI-reduction on combinator terms.
------------------------------------------------------------------------
KI-reduction-CR : ∀ {a b c : Tm} → a ⇒* b → a ⇒* c → Converge b c
KI-reduction-CR {a} = newman wcr (sn a)
