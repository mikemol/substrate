------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarLocal  (Ⓛ★ — the (p,e) prime-power apex)
--
-- Generalizes CenterIsStarNumeral (ℤ/8 = the (2,3) instance) to a PARAMETRIC
-- apex over prime powers (p, e): the local ring ℤ/pᵉ, in which the canonical
-- nilpotent p has nilpotency degree EXACTLY e — the p-adic valuation. Handoff
-- cotype `CenterIsStarLocal.cotype.md`, whose load-bearing gap (M-β / T2,
-- "needs the typechecker") is discharged here CONSTRUCTIVELY (not cited):
--
--   T2  degree-of p ≡ e :  pᵉ ≡ 0  (mod pᵉ)   [degree reached]
--                      ∧  pᵉ⁻¹ ≢ 0 (mod pᵉ)   [not reached earlier]
--
-- proven generically for p ≥ 2, e ≥ 1, by the substrate's own `_mod-suc_`
-- (suc-mod-suc-self + mod-suc-id) over the power positivity / strict
-- monotonicity proven here (^-pos, k<p*k). ℤ/8: 2↦deg3, 4↦deg2; ℤ/9: 3↦deg2.
--
-- T3 (clean/graded split): e = 1 ⟹ field (reduced, clean, degree-0 cross
-- terms); e > 1 ⟹ nilpotent ideal (graded, worst grade e−1). This recovers
-- 59174e8's own ℤ/15-(squarefree, clean) vs ℤ/8-(graded) distinction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarLocal where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _^_; _<_; _≤_; z≤n; s≤s; _∸_)
open import Substrate.Foundation.Nat.Properties.Order using (≤-trans; m≤m+n; n≤m+n)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-id; suc-mod-suc-self)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; subst)
open import Substrate.Foundation.Empty using (⊥)

------------------------------------------------------------------------
-- The apex, parametric in (p′, e′): p = suc (suc p′) ≥ 2 (prime base), and
-- the degree is e = suc e′ ≥ 1. The modulus is pᵉ.
------------------------------------------------------------------------

module Local (p′ e′ : ℕ) where

  p : ℕ
  p = suc (suc p′)                      -- the prime base, ≥ 2

  pe pe-1 : ℕ
  pe   = p ^ suc e′                     -- pᵉ  (the modulus)
  pe-1 = p ^ e′                         -- pᵉ⁻¹

  ------------------------------------------------------------------------
  -- Power positivity and the strict monotonicity p·k > k (k>0) — the ℕ
  -- content the thin substrate ℕ lacks; built from the order lemmas.
  ------------------------------------------------------------------------

  ^-pos : (n : ℕ) → 0 < p ^ n
  ^-pos zero    = s≤s z≤n
  ^-pos (suc n) = ≤-trans (^-pos n) (m≤m+n (p ^ n) ((suc p′) * (p ^ n)))

  k<p*k : (k : ℕ) → 0 < k → k < p * k
  k<p*k zero    ()
  k<p*k (suc j) _ =
    s≤s (≤-trans (m≤m+n (suc j) (p′ * suc j)) (n≤m+n j ((suc p′) * suc j)))

  pe-1<pe : pe-1 < pe
  pe-1<pe = k<p*k (p ^ e′) (^-pos e′)

  suc-pred : (n : ℕ) → 0 < n → suc (n ∸ 1) ≡ n
  suc-pred (suc n) _ = refl
  suc-pred zero ()

  ------------------------------------------------------------------------
  -- T2 — degree-of p ≡ e, constructively.
  ------------------------------------------------------------------------

  -- degree REACHED: pᵉ ≡ 0 (mod pᵉ). pᵉ is the modulus, so it vanishes.
  degree-reached : pe mod-suc (pe ∸ 1) ≡ 0
  degree-reached =
    subst (λ z → z mod-suc (pe ∸ 1) ≡ 0)
          (suc-pred pe (^-pos (suc e′)))
          (suc-mod-suc-self (pe ∸ 1))

  -- degree NOT reached earlier: pᵉ⁻¹ ≢ 0 (mod pᵉ). pᵉ⁻¹ < pᵉ and > 0, so it
  -- is its own (nonzero) residue.
  pe-1<suc : pe-1 < suc (pe ∸ 1)
  pe-1<suc = subst (pe-1 <_) (sym (suc-pred pe (^-pos (suc e′)))) pe-1<pe

  pe-1-fixed : pe-1 mod-suc (pe ∸ 1) ≡ pe-1
  pe-1-fixed = mod-suc-id pe-1 (pe ∸ 1) pe-1<suc

  degree-not-yet : pe-1 mod-suc (pe ∸ 1) ≡ 0 → ⊥
  degree-not-yet h with subst (0 <_) (trans (sym pe-1-fixed) h) (^-pos e′)
  ... | ()

------------------------------------------------------------------------
-- Instances: the degree facts are the parametric T2 INSTANTIATED (no per-
-- instance recomputation — the proof is symbolic over `_mod-suc_`).
--   ℤ/8 = (2,3) [= CenterIsStarNumeral's carrier]; ℤ/9 = (3,2).
-- T3 (clean/graded split): e′ = 0 ⟹ degree 1 ⟹ ℤ/p a FIELD (p ≡ 0, no
-- nontrivial nilpotent — clean); e′ ≥ 1 ⟹ p a degree-(suc e′) nilpotent
-- (graded, worst grade e′). The first graded case is the dual (p,2) [= e′=1]:
-- ℤ/9, ℤ/25, …. Recovers 59174e8's squarefree-clean vs prime-power-graded.
------------------------------------------------------------------------

module ℤ/8 = Local 0 2            -- p=2, e=3
module ℤ/9 = Local 1 1            -- p=3, e=2

-- ℤ/8: 2 has degree 3 (2³≡0 ∧ 2²≢0 mod 8) — the (2,3) instance generalised.
ℤ/8-reached : ℤ/8.pe mod-suc (ℤ/8.pe ∸ 1) ≡ 0
ℤ/8-reached = ℤ/8.degree-reached
ℤ/8-not-yet : ℤ/8.pe-1 mod-suc (ℤ/8.pe ∸ 1) ≡ 0 → ⊥
ℤ/8-not-yet = ℤ/8.degree-not-yet

-- ℤ/9: 3 has degree 2 (3²≡0 ∧ 3¹≢0 mod 9).
ℤ/9-reached : ℤ/9.pe mod-suc (ℤ/9.pe ∸ 1) ≡ 0
ℤ/9-reached = ℤ/9.degree-reached
ℤ/9-not-yet : ℤ/9.pe-1 mod-suc (ℤ/9.pe ∸ 1) ≡ 0 → ⊥
ℤ/9-not-yet = ℤ/9.degree-not-yet
