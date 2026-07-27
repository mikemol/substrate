------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.ModZero
--
-- The Bézout inverse read (B-INV): `reduce-split` → `reduce-drop` → `reduce-read`
-- → `reduce-unit` → `inverse-from-bezout`. TIP: re-exports ModZero.Base (its own).
--
-- ⟡mod-content-squeeze (propagation): ModZero measured 150MB. MEASURED: its floor with
-- the F+Mod opens alone is 90MB and adding the Quotient and Div opens costs ZERO (90/90/90),
-- so the 60MB is ModZero's OWN CONTENT — the parents did not need splitting, this file did.
-- Split at the Bézout-inverse boundary; each part carries ~30MB over the shared floor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.ModZero where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D

import Substrate.Algebra.Polynomial.Graded.ModZero.Base as Base

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  -- ⟡public-policy: NO RE-EXPORT. Bind at the sources.
  open F.Over CR
  open M.Over CR d f-lo
  open Q.Over CR d f-lo
  open D.Over CR d f-lo
  open Base.Over CR d f-lo public   -- our own, split across files

  private variable n m : ℕ

  -- THE BRIDGE: from the convCoeff Bézout (convCoeff s a + convCoeff t m ≡ nth g,
  -- ∀k) to reduce-level additivity — pad both products into one +P, push reduce
  -- through, match g by reduce-cong-nth.  (B-INV-DROP then drops the t·m term.)
  reduce-split : {ns na nt nm ng : ℕ}
                 (sv : Poly ns) (av : Poly na) (tv : Poly nt) (mv : Poly nm) (gv : Poly ng)
               → ((k : ℕ) → convCoeff sv av k + convCoeff tv mv k ≡ nth gv k)
               → reduce-mod-f (sv *P av) +P reduce-mod-f (tv *P mv) ≡ reduce-mod-f gv
  reduce-split {ns} {na} {nt} {nm} sv av tv mv gv bez = trans (sym redW) (reduce-cong-nth W gv nthW)
    where
      U  = pad-end (nt ℕ+ nm) (sv *P av)
      V′ = subst Poly (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv))
      W  = U +P V′
      redW : reduce-mod-f W ≡ reduce-mod-f (sv *P av) +P reduce-mod-f (tv *P mv)
      redW = trans (reduce-+P U V′)
             (cong₂ _+P_ (reduce-pad-end (nt ℕ+ nm) (sv *P av))
                         (trans (reduce-subst (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv)))
                                (reduce-pad-end (ns ℕ+ na) (tv *P mv))))
      nthW : (k : ℕ) → nth W k ≡ nth gv k
      nthW k = trans (nth-+P U V′ k)
               (trans (cong₂ _+_
                         (trans (nth-pad-end (nt ℕ+ nm) (sv *P av) k) (nth-*P sv av k))
                         (trans (nth-subst (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv)) k)
                                (trans (nth-pad-end (ns ℕ+ na) (tv *P mv) k) (nth-*P tv mv k))))
                      (bez k))

  -- B-INV-DROP: the t·m term DROPS (it is a multiple of the modulus).  From a
  -- Bézout against the divisor b-poly, reduce(s·a) ≡ reduce g.  Mirrors ℕ `drop`.
  reduce-drop : {ns na nt ng : ℕ}
                (sv : Poly ns) (av : Poly na) (tv : Poly nt) (gv : Poly ng)
              → ((k : ℕ) → convCoeff sv av k + convCoeff tv b-poly k ≡ nth gv k)
              → reduce-mod-f (sv *P av) ≡ reduce-mod-f gv
  reduce-drop sv av tv gv bez =
    trans (sym (+P-identityʳ (reduce-mod-f (sv *P av))))
    (trans (cong (reduce-mod-f (sv *P av) +P_) (sym (modulus-multiple tv)))
           (reduce-split sv av tv b-poly gv bez))

  -- B-INV-READ: the inverse property in the quotient ring.  From a Bézout
  -- against b-poly with gcd = unit, a *Q (reduce s) ≡ 𝟙.  Mirrors ℕ `proof`.
  reduce-read : {ns nt ng : ℕ}
                (s : Poly ns) (a : Poly (suc d)) (t : Poly nt) (g : Poly ng)
              → ((k : ℕ) → convCoeff s a k + convCoeff t b-poly k ≡ nth g k)
              → reduce-mod-f g ≡ oneC
              → a *Q (reduce-mod-f s) ≡ oneC
  reduce-read {ns} s a t g bez gunit =
    trans (sym (reduce-*-hom a s))
    (trans (trans (cong reduce-mod-f (*P-comm a s)) (reduce-subst (+ℕ-comm ns (suc d)) (s *P a)))
    (trans (reduce-drop s a t g bez) gunit))

  -- B-INV-UNIT: the gcd unit reduces to 𝟙.  Over F₂ a coprime pair's gcd is the
  -- constant 𝟙; a g with those coefficients (𝟙 at 0, 𝟘 above) reduces to oneC.
  reduce-unit : {ng : ℕ} (g : Poly ng)
              → nth g zero ≡ 𝟙 → ((k : ℕ) → nth g (suc k) ≡ 𝟘)
              → reduce-mod-f g ≡ oneC
  reduce-unit g h0 hs = trans (reduce-cong-nth g oneC nth-eq) (reduce-idempotent oneC)
    where
      nth-eq : (k : ℕ) → nth g k ≡ nth oneC k
      nth-eq zero    = h0
      nth-eq (suc k) = trans (hs k) (sym (nth-replicate d k))

  -- B-INV (composed): the full inverse read.  From a Bézout `s·a + t·b-poly = g`
  -- (coefficient-wise) with g the unit, `a⁻¹ = reduce-mod-f s` and a *Q a⁻¹ ≡ 𝟙.
  inverse-from-bezout : {ns nt ng : ℕ}
                        (s : Poly ns) (a : Poly (suc d)) (t : Poly nt) (g : Poly ng)
                      → ((k : ℕ) → convCoeff s a k + convCoeff t b-poly k ≡ nth g k)
                      → nth g zero ≡ 𝟙 → ((k : ℕ) → nth g (suc k) ≡ 𝟘)
                      → a *Q (reduce-mod-f s) ≡ oneC
  inverse-from-bezout s a t g bez h0 hs = reduce-read s a t g bez (reduce-unit g h0 hs)
