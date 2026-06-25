------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim
--
-- Ⓕ.spectral (a) connector — closing dim ker Φ_p(σ_p) = p−1 via Φ_p(σ_p) = A.
-- Reuse-search verdict: the orbit-sum assembles from existing blocks
-- (basis-decomp, preserves-sum, iterate-on-basis, σ-iterate-toℕ, mod-suc) —
-- no off-the-shelf orbit-sum operator. This file builds the two REUSABLE
-- pieces the closure plugs into:
--
--   KernelDim-cong : pointwise-equal operators have the same KernelDim
--                    (so dim ker Φ_p(σ_p) = dim ker A once Φ_p(σ_p) = A).
--   A-on-basis     : apply A (basis k) ≡ ones  (the A-side of the agreement).
--
-- The remaining seam is the orbit-sum  Φ_p(σ_p)(basis k) ≡ ones  (then
-- Φ_p(σ_p) = A by linear-extensionality, and `dim` = `KernelDim-cong` of
-- `Augmentation.aug-dim`). Its one new lemma: the cyclic orbit hits each
-- coordinate exactly once (countHits p ≡ 𝟙 via mod-suc injectivity).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; _≤?_; s≤s-injective)
open import Substrate.Foundation.Nat.Properties.Order
  using (<→≤; ≤-<-trans; <-irrefl; ≤-tight; ≤-suc-r; ≤-refl)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Fin.Properties using (toℕ-injective; toℕ-bound)
open import Substrate.Foundation.Vec using (_∷_; []; lookup)
open import Substrate.Foundation.Eq using (_≡_; _≢_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Foundation.Negation using (yes; no)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (basis-lookup-other)
open import Substrate.Algebra.Nat.Mod using (mod-suc-id)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.Augmentation using (A; total; ones; aug-dim)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (powL; geomSumL)
open import Substrate.Algebra.F2.Linear.SpectralCycle using (σ; Φσ)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate using (σ-iterate)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-Linear-basis; σ-iterate-toℕ; cyclic-suc-HasOrderPerm)

------------------------------------------------------------------------
-- Transport: pointwise-equal operators share their KernelDim. (Generic;
-- the dimension of a kernel depends on the operator only through inKer.)
------------------------------------------------------------------------

KernelDim-cong :
  ∀ {n m} {L L′ : Linear n m} {d} →
  ((v : Vector n) → apply L v ≡ apply L′ v) →
  KernelDim L′ d → KernelDim L d
KernelDim-cong {L = L} {L′} eq KD = record
  { into     = KernelDim.into KD
  ; retract  = KernelDim.retract KD
  ; into-ker = λ x → trans (eq (apply (KernelDim.into KD) x)) (KernelDim.into-ker KD x)
  ; indep    = KernelDim.indep KD
  ; spans    = λ v h → KernelDim.spans KD v (trans (sym (eq v)) h)
  }

------------------------------------------------------------------------
-- The A-side of Φ_p(σ_p) = A: total of a basis vector is 𝟙, so A(eₖ) = ones.
------------------------------------------------------------------------

total-𝟎 : ∀ {n} → total (𝟎ⱽ {n}) ≡ 𝟘
total-𝟎 {zero}  = refl
total-𝟎 {suc n} = total-𝟎 {n}

total-basis : ∀ {n} (k : Fin n) → total (basis k) ≡ 𝟙
total-basis {suc n} zero    = trans (cong (𝟙 +_) (total-𝟎 {n})) (+-identityʳ 𝟙)
total-basis {suc n} (suc k) = total-basis k

A-on-basis : ∀ {n} (k : Fin (suc n)) → apply (A {suc n}) (basis k) ≡ ones
A-on-basis k = trans (cong (_*ₛ ones) (total-basis k)) (*ₛ-identityˡ ones)

------------------------------------------------------------------------
-- conn2: σ_p^i sends basis k to the orbit position basis(σ-iterate i cyc k).
-- Induction on i, reusing the exposed cyclic-Linear-basis (conn1).
------------------------------------------------------------------------

apply-powL-basis :
  ∀ {n} (i : ℕ) (k : Fin (suc n)) →
  apply (powL i (σ {n})) (basis k) ≡ basis (σ-iterate i (cyclic-suc {n}) k)
apply-powL-basis zero    k = refl
apply-powL-basis (suc i) k =
  trans (cong (apply (σ)) (apply-powL-basis i k))
        (cyclic-Linear-basis (σ-iterate i (cyclic-suc) k))

------------------------------------------------------------------------
-- conn3: the per-coordinate orbit count. lookup j of Σ_{i<m} σ_p^i(eₖ) is the
-- F₂-tally of orbit visits to j. Induction on m, reusing conn2 + lookup-+ⱽ.
------------------------------------------------------------------------

occ : ∀ {n} → ℕ → Fin (suc n) → Fin (suc n) → F₂
occ zero    k j = 𝟘
occ (suc m) k j = occ m k j + lookup (basis (σ-iterate m (cyclic-suc) k)) j

orbit-count :
  ∀ {n} (m : ℕ) (k j : Fin (suc n)) →
  lookup (apply (geomSumL (σ {n}) m) (basis k)) j ≡ occ m k j
orbit-count zero    k j = lookup-𝟎 j
orbit-count (suc m) k j =
  trans (lookup-+ⱽ (apply (geomSumL (σ) m) (basis k)) (apply (powL m (σ)) (basis k)) j)
        (cong₂ _+_ (orbit-count m k j)
                   (cong (λ w → lookup w j) (apply-powL-basis m k)))

------------------------------------------------------------------------
-- conn4: orbit-hits-once — occ (suc n) k j ≡ 𝟙. Strategy: occ is INVARIANT
-- under k ↦ cyclic-suc k (the boundary term cancels via σ_p^p=id), so every k
-- reduces to k=0, where the orbit is the identity enumeration (Kronecker base).
------------------------------------------------------------------------

-- two F₂ helpers
+-cancelʳ : (a b c : F₂) → (a + c) ≡ (b + c) → a ≡ b
+-cancelʳ a b c eq =
  trans (sym (+-identityʳ a))
  (trans (cong (a +_) (sym (+-self-inverse c)))
  (trans (sym (+-assoc a c c))
  (trans (cong (_+ c) eq)
  (trans (+-assoc b c c)
  (trans (cong (b +_) (+-self-inverse c)) (+-identityʳ b))))))

+-swap-mid : (a b c : F₂) → ((a + b) + c) ≡ ((a + c) + b)
+-swap-mid a b c =
  trans (+-assoc a b c) (trans (cong (a +_) (+-comm b c)) (sym (+-assoc a c b)))

-- the rotation-of-the-orbit identity (direct induction, no σ-iterate-add).
σ-iter-cyc : ∀ {n} (m : ℕ) (k : Fin (suc n)) →
             σ-iterate m (cyclic-suc {n}) (cyclic-suc k) ≡ σ-iterate (suc m) (cyclic-suc {n}) k
σ-iter-cyc zero    k = refl
σ-iter-cyc (suc m) k = cong (cyclic-suc) (σ-iter-cyc m k)

-- telescoping: Σ_{i<m} T(suc i) + T 0 ≡ Σ_{i<m} T i + T m  (T i = lookup(basis(σⁱk)) j).
occ-tele : ∀ {n} (m : ℕ) (k j : Fin (suc n)) →
           (occ m (cyclic-suc k) j + lookup (basis k) j)
             ≡ (occ m k j + lookup (basis (σ-iterate m (cyclic-suc) k)) j)
occ-tele zero    k j = refl
occ-tele (suc m) k j =
  trans (cong (λ z → (occ m (cyclic-suc k) j + lookup (basis z) j) + lookup (basis k) j)
              (σ-iter-cyc m k))
  (trans (+-swap-mid (occ m (cyclic-suc k) j)
                     (lookup (basis (σ-iterate (suc m) (cyclic-suc) k)) j)
                     (lookup (basis k) j))
         (cong (_+ lookup (basis (σ-iterate (suc m) (cyclic-suc) k)) j) (occ-tele m k j)))

-- shift-invariance: occ(p)(cyclic-suc k) ≡ occ(p) k  (boundary cancels via σ_p^p=id).
occ-shift : ∀ {n} (k j : Fin (suc n)) →
            occ (suc n) (cyclic-suc k) j ≡ occ (suc n) k j
occ-shift {n} k j =
  +-cancelʳ _ _ (lookup (basis k) j)
    (trans (occ-tele (suc n) k j)
           (cong (λ z → occ (suc n) k j + lookup (basis z) j) (cyclic-suc-HasOrderPerm k)))

-- iterate the shift from 0: occ(p)(σ-iterate m cyc 0) ≡ occ(p) 0.
occ-shift-iter : ∀ {n} (m : ℕ) (j : Fin (suc n)) →
                 occ (suc n) (σ-iterate m (cyclic-suc) (zero {n})) j ≡ occ (suc n) (zero {n}) j
occ-shift-iter zero    j = refl
occ-shift-iter (suc m) j =
  trans (occ-shift (σ-iterate m (cyclic-suc) zero) j) (occ-shift-iter m j)

-- every k is reachable from 0 by the orbit: σ-iterate(toℕ k) cyc 0 ≡ k.
σ-iter-k0 : ∀ {n} (k : Fin (suc n)) → σ-iterate (toℕ k) (cyclic-suc {n}) (zero {n}) ≡ k
σ-iter-k0 {n} k =
  toℕ-injective (trans (σ-iterate-toℕ (toℕ k) zero) (mod-suc-id (toℕ k) n (toℕ-bound k)))

-- so occ(p) k ≡ occ(p) 0 for every k.
occ-k-to-0 : ∀ {n} (k j : Fin (suc n)) → occ (suc n) k j ≡ occ (suc n) (zero {n}) j
occ-k-to-0 {n} k j =
  trans (cong (λ z → occ (suc n) z j) (sym (σ-iter-k0 k))) (occ-shift-iter (toℕ k) j)

------------------------------------------------------------------------
-- The Kronecker base: at k=0 the orbit is the identity enumeration (step i
-- lands on toℕ⁻¹ i), so j is visited exactly at step toℕ j ⟹ occ(p) 0 j ≡ 𝟙.
------------------------------------------------------------------------

-- step i (i < p) of the orbit from 0 has toℕ = i.
σ-iter0-toℕ : ∀ {n} (i : ℕ) → i < suc n →
              toℕ (σ-iterate i (cyclic-suc {n}) (zero {n})) ≡ i
σ-iter0-toℕ {n} i i<sn = trans (σ-iterate-toℕ i (zero {n})) (mod-suc-id i n i<sn)

private
  term0-hit : ∀ {n} (i : ℕ) (j : Fin (suc n)) → i < suc n → toℕ j ≡ i →
              lookup (basis (σ-iterate i (cyclic-suc) (zero {n}))) j ≡ 𝟙
  term0-hit i j i<sn eq =
    trans (cong (λ a → lookup (basis a) j)
                (toℕ-injective (trans (σ-iter0-toℕ i i<sn) (sym eq))))
          (basis-lookup-same j)

  term0-miss : ∀ {n} (i : ℕ) (j : Fin (suc n)) → i < suc n → toℕ j ≢ i →
               lookup (basis (σ-iterate i (cyclic-suc) (zero {n}))) j ≡ 𝟘
  term0-miss i j i<sn neq =
    basis-lookup-other (σ-iterate i (cyclic-suc) zero) j
      (λ e → neq (sym (trans (sym (σ-iter0-toℕ i i<sn)) (cong toℕ e))))

-- j not yet visited in the first m steps (m ≤ toℕ j).
occ-0-miss : ∀ {n} (m : ℕ) (j : Fin (suc n)) → suc m ≤ suc (toℕ j) → occ m (zero {n}) j ≡ 𝟘
occ-0-miss zero       j _      = refl
occ-0-miss {n} (suc m) j sm≤tj =
  cong₂ _+_ (occ-0-miss m j (≤-suc-r (s≤s-injective sm≤tj)))
            (term0-miss m j (≤-<-trans (<→≤ (s≤s-injective sm≤tj)) (toℕ-bound j))
              (λ tj≡m → <-irrefl m (subst (suc m ≤_) tj≡m (s≤s-injective sm≤tj))))

-- j visited (exactly once) by step m (toℕ j < m ≤ p).
occ-0-hit : ∀ {n} (m : ℕ) (j : Fin (suc n)) → toℕ j < m → m ≤ suc n → occ m (zero {n}) j ≡ 𝟙
occ-0-hit (suc m) j tj<sm sm≤sn with suc (toℕ j) ≤? m
... | yes tj<m =
  trans (cong₂ _+_ (occ-0-hit m j tj<m (≤-suc-r (s≤s-injective sm≤sn)))
                   (term0-miss m j sm≤sn
                     (λ tj≡m → <-irrefl m (subst (λ x → suc x ≤ m) tj≡m tj<m))))
        (+-identityʳ 𝟙)
... | no ¬tj<m =
  cong₂ _+_ (occ-0-miss m j (subst (λ x → suc m ≤ suc x) (sym (≤-tight (toℕ j) m tj<sm ¬tj<m)) (≤-refl (suc m))))
            (term0-hit m j sm≤sn (≤-tight (toℕ j) m tj<sm ¬tj<m))

occ-0 : ∀ {n} (j : Fin (suc n)) → occ (suc n) (zero {n}) j ≡ 𝟙
occ-0 {n} j = occ-0-hit (suc n) j (toℕ-bound j) (≤-refl (suc n))

------------------------------------------------------------------------
-- conn4 (orbit-hits-once) and conn5 (close): Φ_p(σ_p) = A ⟹ dim ker = p−1.
------------------------------------------------------------------------

conn4 : ∀ {n} (k j : Fin (suc n)) → occ (suc n) k j ≡ 𝟙
conn4 k j = trans (occ-k-to-0 k j) (occ-0 j)

-- ones is all-𝟙.
ones-lookup : ∀ {n} (j : Fin n) → lookup (ones {n}) j ≡ 𝟙
ones-lookup {suc n} zero    = refl
ones-lookup {suc n} (suc j) = ones-lookup j

-- Φ_p(σ_p)(basis k) ≡ ones (each coordinate is the orbit tally = 𝟙).
Φσ-on-basis : ∀ {n} (k : Fin (suc n)) → apply (Φσ {n}) (basis k) ≡ ones
Φσ-on-basis {n} k =
  ≡-from-lookup _ _ (λ j → trans (trans (orbit-count (suc n) k j) (conn4 k j))
                                 (sym (ones-lookup j)))

-- Φ_p(σ_p) = A as operators (agree on basis ⟹ everywhere).
Φσ≡A : ∀ {n} (v : Vector (suc n)) → apply (Φσ {n}) v ≡ apply (A {suc n}) v
Φσ≡A {n} = linear-extensionality (Φσ {n}) (A {suc n}) (λ k → trans (Φσ-on-basis k) (sym (A-on-basis k)))

-- THE GOAL: dim ker Φ_p(σ_p) = p − 1 (= n), the literal-shift presentation.
dim-ker-Φσ : ∀ {n} → KernelDim (Φσ {n}) n
dim-ker-Φσ {n} = KernelDim-cong Φσ≡A (aug-dim n)
