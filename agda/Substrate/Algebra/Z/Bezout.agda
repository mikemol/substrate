------------------------------------------------------------------------
-- Substrate.Algebra.Z.Bezout
--
-- The WEDGE FOLD: EEA's free trace folded into the Bézout bridge over ℤ.
-- Where gcd-fold (the annihilating fold) returns the residue g, this
-- returns the oriented mediating witness s·a ℕ+ t·b = g — the proof of HOW
-- a and b reach their common part, kept and composable. This is the
-- archetype the recognizer is modelled on: recognition returns the bridge,
-- not the quotient's value.
--
-- "Changing the type EEA operates on": same EEATrace, target = ℤ. The
-- signed coefficients make the Euclidean back-substitution clean ring
-- algebra (Z.Properties), no ℕ-balanced sign-tag. This completes the
-- previously-deferred bezout-from-trace, over ℤ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Bezout where
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt

open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-assoc; +ℤ-comm; +ℤ-identityˡ; +ℤ-inverseʳ)
open import Substrate.Algebra.Z.Properties.Mul
  using (distribˡ-pos; distribʳ-pos; neg-*-left; *ℤ-assoc-pos-pos)
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; wedge-eq) renaming (Wedge-GCD to Wedge-GCD)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.Fold using (eea-fold)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.Nat.GCD.Wedge

------------------------------------------------------------------------
-- 1. The Bézout witness over ℤ: the oriented bridge s·a ℕ+ t·b = g.
------------------------------------------------------------------------

BezoutℤWitness : ℕ → ℕ → ℕ → Set
BezoutℤWitness a b g =
  Σ ℤ (λ s → Σ ℤ (λ t → (s *ℤ (+ a)) +ℤ (t *ℤ (+ b)) ≡ (+ g)))

------------------------------------------------------------------------
-- 2. The two fold-interpretations.
------------------------------------------------------------------------

-- base: gcd(a,0) = a; bridge 1·a ℕ+ 0·0 = a.
base-bezout : (a : ℕ) → BezoutℤWitness a 0 a
base-bezout a =
  1ℤ , 0ℤ , cong +_ (trans (+ℕ-identityʳ (a ℕ+ 0)) (+ℕ-identityʳ a))

-- step: the Euclidean back-substitution. Given a = q·(suc b) ℕ+ r and a
-- bridge s'·(suc b) ℕ+ t'·r = g, the new bridge for (a, suc b) has
-- s = t', t = s' − t'·q  (clean over ℤ).
step-bezout :
  {a g : ℕ} (b : ℕ) (w : Wedge-GCD a (suc b)) →
  BezoutℤWitness (suc b) (remainder w) g → BezoutℤWitness a (suc b) g
step-bezout {a} {g} b w (s' , t' , eq') =
  t' , (s' -ℤ (t' *ℤ (+ q))) , proof
  where
    q  = quotient w
    r  = remainder w
    x  = + (suc b)
    A  = t' *ℤ (+ (q * suc b))
    B  = t' *ℤ (+ r)
    C  = s' *ℤ x

    aeq : (+ a) ≡ ((+ q) *ℤ x) +ℤ (+ r)
    aeq = cong +_ (wedge-eq w)

    α : (t' *ℤ (+ a)) ≡ (A +ℤ B)
    α = trans (cong (t' *ℤ_) aeq) (distribˡ-pos t' (q * suc b) r)

    β : ((s' -ℤ (t' *ℤ (+ q))) *ℤ x) ≡ (C +ℤ (-ℤ A))
    β = trans (distribʳ-pos s' (-ℤ (t' *ℤ (+ q))) (suc b))
              (trans (cong (C +ℤ_) (neg-*-left (t' *ℤ (+ q)) x))
                     (cong (λ z → C +ℤ (-ℤ z)) (*ℤ-assoc-pos-pos t' q (suc b))))

    rearr : ((A +ℤ B) +ℤ (C +ℤ (-ℤ A))) ≡ (+ g)
    rearr =
      trans (+ℤ-assoc A B (C +ℤ (-ℤ A)))
      (trans (cong (A +ℤ_) (sym (+ℤ-assoc B C (-ℤ A))))
      (trans (cong (A +ℤ_) (+ℤ-comm (B +ℤ C) (-ℤ A)))
      (trans (sym (+ℤ-assoc A (-ℤ A) (B +ℤ C)))
      (trans (cong (_+ℤ (B +ℤ C)) (+ℤ-inverseʳ A))
      (trans (+ℤ-identityˡ (B +ℤ C))
      (trans (+ℤ-comm B C) eq'))))))

    proof : (t' *ℤ (+ a)) +ℤ ((s' -ℤ (t' *ℤ (+ q))) *ℤ x) ≡ (+ g)
    proof = trans (cong₂ _+ℤ_ α β) rearr

------------------------------------------------------------------------
-- 3. The bridge fold.
------------------------------------------------------------------------

bezout-ℤ : {a b g : ℕ} → EEATrace a b g → BezoutℤWitness a b g
bezout-ℤ t = eea-fold {T = BezoutℤWitness} base-bezout step-bezout t
