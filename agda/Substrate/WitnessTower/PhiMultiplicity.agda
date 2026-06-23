------------------------------------------------------------------------
-- Substrate.WitnessTower.PhiMultiplicity
--
-- Ⓕ.mult — the JEA-Pi cotype's Φ_p multiplicity (warrant family f090_2),
-- formalized AS A FIBERED COUNT OVER THE WITNESSTOWER SIMPLEX, exactly as the
-- cotype's f090_2_tower directs: "f090_2_grounded is a fibered count over the
-- WitnessTower's rung-(c−1) simplex; the c p-cycles form a witness-tower Δ^(c−1);
-- the crossing strata C(c,k) ARE the Agda FaceCount f-vector faces(c−1,k−1)."
--
-- Indexed by RUNG n = c−1 (n p-cycles+1; faces n 0 = suc n vertices = c, the
-- monus-free index). The DOUBLED multiplicity (×2 clears the reality-involution
-- /2, keeping it over ℕ) is the cotype's f090_2_generalized closed form:
--
--   mult2 p n  =  n · (n · p ∸ 1)        ( = 2 · mult(p, c) for c = n+1 )
--
-- PROBE-VERIFIED CORNERS (the cotype's pinned data, now Agda lemmas):
--   * mult2 p 0 ≡ 0           — c=1, a single p-cycle gives NO Φ_p (f089_2).
--   * mult2 p 1 ≡ p ∸ 1       — c=2, mult = (p−1)/2 = φ(p)/2 (f090_2_pinned;
--                                p=3→1, p=5→2, p=7→3, doubled = 2,4,6 = p−1).
--
-- BASE/FIBER split (the f090_2_tower thesis): the GROSS pairwise count is
-- p · C(c,2) = p · faces(c−1,1) — the cyclotomic fiber weight p times the
-- machine-checked simplex edge count. `gross2-faces` proves the doubled gross
-- term over the real FaceCount base:  2·p·faces n 1 ≡ p·(n·(n+1)).
--
-- The full fibered≡closed identity ∀n (`mult2-fibered`, Ⓕ.mult-gen) is now PROVEN
-- — both sides reduce to p·(n·n) ∸ n — having closed the monus-mul distributivity
-- gap as the reusable Foundation lemma `Nat.Properties.SubMul.*-distribˡ-∸`.
--
-- ONE NAMED GAP remains (borrowed-name discipline — NOT overclaimed): the SPECTRAL
-- grounding — that mult2/2 IS the multiplicity of Φ_p in the cycle-space operator's
-- char poly — is the cotype's PROBE-verified input (linear algebra over a field
-- absent); this module formalizes the COUNTING structure + the FaceCount base + the
-- closed-form/fibered/nullity renderings, not the spectral derivation.
-- The fiber weight (p−1) is the degree of Φ_p (Algebra.Polynomial.Cyclotomic,
-- Ⓕ.cyclotomic); the /2 is the reality involution ζ ↔ ζ⁻¹ on its roots.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.PhiMultiplicity where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans; sym)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-identityˡ; *-identityʳ; *-comm; *-assoc; *-distribˡ-+)
open import Substrate.Foundation.Nat.Properties.SubMul
  using (*-distribˡ-∸; +-∸-cancelˡ; *-sucʳ)
open import Substrate.WitnessTower.FaceCount using (faces; cone-step)

------------------------------------------------------------------------
-- 1. The FaceCount base: the rung-n simplex has n·(n+1)/2 edges, i.e.
--    2 · faces n 1 ≡ n · (n+1). (faces n 1 = C(n+1, 2); REUSING FaceCount.)
------------------------------------------------------------------------

faces-edges : (n : ℕ) → 2 * faces n 1 ≡ n * suc n
faces-edges zero    = refl
faces-edges (suc n) =
  trans (cong (2 *_) (cone-step n 0))                              -- 2·faces(suc n)1 = 2·(faces n 1 + suc n)
  (trans (*-distribˡ-+ 2 (faces n 1) (suc n))                      -- = 2·faces n 1 + 2·suc n
  (trans (cong (_+ (2 * suc n)) (faces-edges n))                   -- = n·suc n + 2·suc n
  (trans (cong (_+ (2 * suc n)) (*-comm n (suc n)))                -- = suc n·n + 2·suc n
  (trans (cong ((suc n * n) +_) (*-comm 2 (suc n)))                -- = suc n·n + suc n·2
  (trans (sym (*-distribˡ-+ (suc n) n 2))                          -- = suc n·(n+2)
         (cong (suc n *_) (+-comm n 2)))))))                       -- = suc n·suc(suc n)

------------------------------------------------------------------------
-- 2. The doubled Φ_p multiplicity (f090_2_generalized closed form) and the
--    probe-verified corners.
------------------------------------------------------------------------

-- mult2 p n = 2 · mult(p, c=n+1); the reality-involution /2 cleared to stay over ℕ.
mult2 : ℕ → ℕ → ℕ
mult2 p n = n * (n * p ∸ 1)

-- c = 1 (rung 0): a single p-cycle carries no Φ_p (f089_2).
mult2-c1 : (p : ℕ) → mult2 p 0 ≡ 0
mult2-c1 p = refl

-- c = 2 (rung 1): mult = (p−1)/2 = φ(p)/2, so the doubled multiplicity is p−1
-- (f090_2_pinned: p=3→1, p=5→2, p=7→3; doubled 2,4,6 = p−1).
mult2-c2 : (p : ℕ) → mult2 p 1 ≡ p ∸ 1
mult2-c2 p = trans (cong (λ z → 1 * (z ∸ 1)) (*-identityˡ p)) (*-identityˡ (p ∸ 1))

------------------------------------------------------------------------
-- 3. The base/fiber split: the gross pairwise count is the cyclotomic fiber
--    weight p TIMES the machine-checked FaceCount simplex edge count.
--    (The fibered reading of mult2 = gross ∸ join-correction; the gross term
--    over the real base. The full ∸-identity is the named Foundation gap.)
------------------------------------------------------------------------

gross2-faces : (p n : ℕ) → 2 * p * faces n 1 ≡ p * (n * suc n)
gross2-faces p n =
  trans (cong (_* faces n 1) (*-comm 2 p))     -- (2·p)·faces = (p·2)·faces
  (trans (*-assoc p 2 (faces n 1))             -- = p·(2·faces n 1)
         (cong (p *_) (faces-edges n)))         -- = p·(n·suc n)

------------------------------------------------------------------------
-- 4. The FULL fibered ≡ closed identity (∀ n, no longer corners-only). Both
--    sides reduce to p·(n·n) ∸ n. Uses the Foundation monus-mul lemma
--    *-distribˡ-∸ (Ⓕ.mult's named gap, now closed in Nat.Properties.SubMul).
------------------------------------------------------------------------

-- the closed form, expanded past the inner monus:  mult2 p n ≡ p·(n·n) ∸ n.
mult2-expand : (p n : ℕ) → mult2 p n ≡ p * (n * n) ∸ n
mult2-expand p n =
  trans (*-distribˡ-∸ n (n * p) 1)                       -- n·(n·p ∸ 1) = n·(n·p) ∸ n·1
  (trans (cong (n * (n * p) ∸_) (*-identityʳ n))         -- = n·(n·p) ∸ n
         (cong (_∸ n) (trans (sym (*-assoc n n p)) (*-comm (n * n) p))))  -- = p·(n·n) ∸ n

-- the join-correction term:  (p+1)·n ≡ p·n + n.
pp1*n : (p n : ℕ) → (p + 1) * n ≡ p * n + n
pp1*n p n =
  trans (*-comm (p + 1) n)
  (trans (*-distribˡ-+ n p 1)
  (trans (cong (n * p +_) (*-identityʳ n))
         (cong (_+ n) (*-comm n p))))

-- the fibered count over FaceCount, expanded:  2p·faces n 1 ∸ (p+1)·n ≡ p·(n·n) ∸ n.
gross-expand : (p n : ℕ) → 2 * p * faces n 1 ∸ (p + 1) * n ≡ p * (n * n) ∸ n
gross-expand p n =
  trans (cong (_∸ (p + 1) * n) (gross2-faces p n))                       -- p·(n·suc n) ∸ (p+1)·n
  (trans (cong (λ z → p * z ∸ (p + 1) * n) (*-sucʳ n n))                  -- p·(n + n·n) ∸ (p+1)·n
  (trans (cong (_∸ (p + 1) * n) (*-distribˡ-+ p n (n * n)))               -- (p·n + p·(n·n)) ∸ (p+1)·n
  (trans (cong ((p * n + p * (n * n)) ∸_) (pp1*n p n))                    -- ∸ (p·n + n)
         (+-∸-cancelˡ (p * n) (p * (n * n)) n))))                         -- cancel p·n → p·(n·n) ∸ n

-- THE f090_2_tower claim, ∀n: the closed-form multiplicity IS the FaceCount-fibered count.
mult2-fibered : (p n : ℕ) → mult2 p n ≡ 2 * p * faces n 1 ∸ (p + 1) * n
mult2-fibered p n = trans (mult2-expand p n) (sym (gross-expand p n))

------------------------------------------------------------------------
-- 5. The nullity (f090_2_generalized): nullity = mult · deg(Φ_p), deg Φ_p = p−1.
--    Doubled (×2 again): nullity2 = mult2 · (p−1). The eigenspace is `mult`
--    copies of the degree-(p−1) cyclotomic factor (Ⓕ.cyclotomic).
------------------------------------------------------------------------

nullity2 : ℕ → ℕ → ℕ
nullity2 p n = mult2 p n * (p ∸ 1)

-- c = 2: nullity = (p−1)²/2, so 2·nullity (doubled again) = (p−1)·(p−1) (f090_2_pinned: 2,8,18 = (p−1)²).
nullity2-c2 : (p : ℕ) → nullity2 p 1 ≡ (p ∸ 1) * (p ∸ 1)
nullity2-c2 p = cong (_* (p ∸ 1)) (mult2-c2 p)
