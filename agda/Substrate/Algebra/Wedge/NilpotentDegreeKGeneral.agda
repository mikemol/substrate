{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentDegreeKGeneral — ⟡nf-degree-k-general: the
-- ∀-k theorem behind NilpotentDegreeK's concrete k=3,4 refl-witnesses. For EVERY
-- k, the generator gen = 1 in the truncated counter Rₖ has nilpotency degree
-- EXACTLY (suc k): pow gen (suc k) ≡ 0, and pow gen m ≡ suc m ≢ 0 for all m ≤ k.
--
-- The concrete refls (NilpotentDegreeK) validated k=3,4; this proves the family
-- by induction on the exponent, via the two addCap branch lemmas (keep below the
-- cap, collapse at it). Uses Rₖ at (suc k) so the degree is always ≥ 1 (k=0 is the
-- degenerate edge where the below-cap range is empty). --safe, zero postulate.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentDegreeKGeneral where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; _<_; z≤n; s≤s; s≤s-injective; _<?_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; pow; Nilpotent)
open import Substrate.Algebra.Wedge.NilpotentDegreeK using (addCap; Rk; gen)

------------------------------------------------------------------------
-- Small order lemmas (not in Foundation.Nat) — derived inline.
------------------------------------------------------------------------
≤-refl : ∀ {n} → n ≤ n
≤-refl {zero}  = z≤n
≤-refl {suc n} = s≤s ≤-refl

<-irrefl : ∀ {n} → n < n → ⊥
<-irrefl {suc n} (s≤s p) = <-irrefl p

≤-from-suc : ∀ {m n} → suc m ≤ n → m ≤ n
≤-from-suc {zero}  _        = z≤n
≤-from-suc {suc m} (s≤s p)  = s≤s (≤-from-suc p)

≤-weaken : ∀ {m n} → m ≤ n → m ≤ suc n
≤-weaken z≤n      = z≤n
≤-weaken (s≤s p)  = s≤s (≤-weaken p)

------------------------------------------------------------------------
-- The two addCap branch lemmas: below the cap it KEEPS the sum; at/over it
-- COLLAPSES to 0. Proved by matching the same `with (x+y) <? suc k` as addCap.
------------------------------------------------------------------------
addCap-keep : ∀ k x y → (x + y) < suc k → addCap k x y ≡ x + y
addCap-keep k x y lt with (x + y) <? suc k
... | yes _  = refl
... | no ¬p  = ⊥-elim (¬p lt)

addCap-collapse : ∀ k x y → ¬ ((x + y) < suc k) → addCap k x y ≡ 0
addCap-collapse k x y ¬lt with (x + y) <? suc k
... | yes p  = ⊥-elim (¬lt p)
... | no  _  = refl

------------------------------------------------------------------------
-- CLAIM A (below the cap): pow (Rk (suc k)) gen n ≡ suc n, for n ≤ k.
-- Induction on n. Base: pow gen 0 = gen = 1 = suc 0. Step: pow gen (suc m) =
-- addCap (suc k) 1 (pow gen m) = addCap (suc k) 1 (suc m) [IH] = suc (suc m),
-- since 1 + suc m = suc (suc m) < suc (suc k) (from suc m ≤ k, i.e. the step's
-- hypothesis). The bound suc n ≤ suc k threads the cap-keep condition.
------------------------------------------------------------------------
pow-val : ∀ k n → n ≤ k → pow (Rk (suc k)) gen n ≡ suc n
pow-val k zero    _         = refl
pow-val k (suc m) sm≤k =
  -- pow gen (suc m) = addCap (suc k) gen (pow gen m) = addCap (suc k) 1 (pow gen m)
  trans (cong (addCap (suc k) gen) (pow-val k m (≤-from-suc sm≤k)))
        (addCap-keep (suc k) gen (suc m) lt)
  where
    -- gen + suc m = suc (suc m); need suc(suc m) < suc(suc k) = suc(suc(suc m)) ≤
    -- suc(suc k) = s≤s (suc(suc m) ≤ suc k) = s≤s (s≤s (suc m ≤ k)) = s≤s (s≤s sm≤k).
    lt : (gen + suc m) < suc (suc k)
    lt = s≤s (s≤s sm≤k)

------------------------------------------------------------------------
-- CLAIM B (at the cap): pow (Rk (suc k)) gen (suc k) ≡ 0. The (suc k)-th power
-- overflows: pow gen (suc k) = addCap (suc k) 1 (pow gen k) = addCap (suc k) 1
-- (suc k) [Claim A at k] = 0, since 1 + suc k = suc (suc k) is NOT < suc (suc k).
------------------------------------------------------------------------
pow-cap : ∀ k → pow (Rk (suc k)) gen (suc k) ≡ 0
pow-cap k =
  trans (cong (addCap (suc k) gen) (pow-val k k ≤-refl))
        (addCap-collapse (suc k) gen (suc k) ¬lt)
  where
    ¬lt : ¬ ((gen + suc k) < suc (suc k))
    ¬lt lt = <-irrefl lt      -- gen + suc k = suc (suc k); suc(suc k) < suc(suc k) is absurd

------------------------------------------------------------------------
-- THE THEOREM: gen is nilpotent of degree EXACTLY (suc k) in Rₖ(suc k).
--   • nilpotent : the (suc k)-th power is z (0).
--   • degree-minimal : every SMALLER power (m ≤ k) is suc m ≢ 0 — no earlier
--     witness, so the degree is exactly (suc k), not less. Together: exact.
------------------------------------------------------------------------
gen-nilpotent : ∀ k → Nilpotent (Rk (suc k)) gen
gen-nilpotent k = suc k , pow-cap k

gen-degree-minimal : ∀ k m → m ≤ k → pow (Rk (suc k)) gen m ≡ 0 → ⊥
gen-degree-minimal k m m≤k p with trans (sym (pow-val k m m≤k)) p
... | ()      -- suc m ≡ 0 is impossible

------------------------------------------------------------------------
-- So the Nf-obstruction ladder's degree parameter is fully general: for every k
-- there is a carrier (Rₖ(suc k)) whose generator is nilpotent of degree exactly
-- (suc k). The concrete k=3 (deg 4) / k=4 (deg 5) of NilpotentDegreeK are the
-- instances pow-cap 3 / pow-cap 4; this is the ∀-k proof they sampled.
------------------------------------------------------------------------
