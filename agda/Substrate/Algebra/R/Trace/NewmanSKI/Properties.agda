{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanSKI.Properties — SN, WCR, and (via the substrate's
-- own Newman's lemma) CR for I-reduction. Split from NewmanSKI (the definition
-- module) per the def/proof separation policy: the proof-module imports
-- (Nat.Properties*) live here, so a def-consumer of NewmanSKI never pays for them.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.NewmanSKI.Properties where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; s≤s; z≤n; _≤_)
open import Substrate.Foundation.Nat.Properties using (+-comm)
open import Substrate.Foundation.Nat.Properties.Order using (≤-refl; ≤-<-trans; m≤m+n; n≤m+n; +-monoʳ-≤)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.R.Trace.NewmanSKI
open import Substrate.Foundation.RewriteConfluence _⇒_
  using (_⇒*_; done; _◅_; _++*_; Converge; WCR; CR; SN; newman)

------------------------------------------------------------------------
-- 3. Every step strictly shrinks size (⟹ SN).
------------------------------------------------------------------------
step-size< : {a b : Tm} → a ⇒ b → size b < size a
step-size< (β-I x)      = s≤s (n≤m+n 1 (size x))
step-size< (cong-l g r) = s≤s (+-monoˡ-< (size g) (step-size< r))
  where +-monoˡ-< : {m n : ℕ} (k : ℕ) → m < n → (m + k) < (n + k)
        +-monoˡ-< {m}{n} k m<n rewrite +-comm m k | +-comm n k = +-monoʳ-< k m<n
          where +-monoʳ-< : (k : ℕ) {m n : ℕ} → m < n → (k + m) < (k + n)
                +-monoʳ-< zero    m<n = m<n
                +-monoʳ-< (suc k) m<n = s≤s (+-monoʳ-< k m<n)
step-size< (cong-r f r) = s≤s (+-monoʳ-< (size f) (step-size< r))
  where +-monoʳ-< : (k : ℕ) {m n : ℕ} → m < n → (k + m) < (k + n)
        +-monoʳ-< zero    m<n = m<n
        +-monoʳ-< (suc k) m<n = s≤s (+-monoʳ-< k m<n)

------------------------------------------------------------------------
-- 4. SN by measure transport (Acc _<_ (size a) ⟹ Acc (flip _⇒_) a).
------------------------------------------------------------------------
acc-from-size : (a : Tm) → Acc _<_ (size a) → Acc (λ x y → y ⇒ x) a
acc-from-size a (acc rs) = acc (λ b a⇒b → acc-from-size b (rs (size b) (step-size< a⇒b)))

sn : (a : Tm) → Acc (λ x y → y ⇒ x) a
sn a = acc-from-size a (<-wellFounded (size a))

------------------------------------------------------------------------
-- 5. WCR: one-step peaks converge.
------------------------------------------------------------------------
cong-l* : {f f' : Tm} (g : Tm) → f ⇒* f' → (f ∙ g) ⇒* (f' ∙ g)
cong-l* g done         = done
cong-l* g (s ◅ r)      = cong-l g s ◅ cong-l* g r

cong-r* : (f : Tm) {g g' : Tm} → g ⇒* g' → (f ∙ g) ⇒* (f ∙ g')
cong-r* f done         = done
cong-r* f (s ◅ r)      = cong-r f s ◅ cong-r* f r

wcr : WCR
wcr (β-I x)      (β-I .x)     = x , (done , done)
wcr (β-I x)      (cong-r .I r) = _ , ((r ◅ done) , (β-I _ ◅ done))
wcr (cong-r .I r)(β-I x)       = _ , ((β-I _ ◅ done) , (r ◅ done))
wcr (cong-l g r1)(cong-l .g r2) with wcr r1 r2
... | d , (p , q) = (d ∙ g) , (cong-l* g p , cong-l* g q)
wcr (cong-r f r1)(cong-r .f r2) with wcr r1 r2
... | d , (p , q) = (f ∙ d) , (cong-r* f p , cong-r* f q)
wcr (cong-l g r1)(cong-r f r2) = _ , ((cong-r _ r2 ◅ done) , (cong-l _ r1 ◅ done))
wcr (cong-r f r1)(cong-l g r2) = _ , ((cong-l _ r2 ◅ done) , (cong-r _ r1 ◅ done))

------------------------------------------------------------------------
-- 6. THE INSTANCE: Newman gives CR for I-reduction on combinator terms.
------------------------------------------------------------------------
I-reduction-CR : ∀ {a b c : Tm} → a ⇒* b → a ⇒* c → Converge b c
I-reduction-CR {a} = newman wcr (sn a)
