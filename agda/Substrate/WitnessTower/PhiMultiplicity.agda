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
-- NAMED GAPS (borrowed-name discipline — NOT overclaimed):
--  (1) the full fibered≡closed identity  mult2 p n ≡ 2·p·faces n 1 ∸ (p+1)·n
--      ∀n needs ℕ monus-mul distributivity (a·(b∸c)=a·b∸a·c), absent from
--      Foundation; proven here only at the corners. (→ a Foundation lemma.)
--  (2) the SPECTRAL grounding — that mult2/2 IS the multiplicity of Φ_p in the
--      cycle-space operator's char poly — is the cotype's PROBE-verified input
--      (linear algebra over a field absent); this module formalizes the COUNTING
--      structure + the FaceCount base, not the spectral derivation.
-- The fiber weight (p−1) is the degree of Φ_p (Algebra.Polynomial.Cyclotomic,
-- Ⓕ.cyclotomic); the /2 is the reality involution ζ ↔ ζ⁻¹ on its roots.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.PhiMultiplicity where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans; sym)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-identityˡ; *-comm; *-assoc; *-distribˡ-+)
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
