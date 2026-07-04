{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.V4-as-PFG
--
-- ⟡S4-wire-substrate. Lands the CDSW-torsor-as-GTorsor result (proved
-- concretely in S5TorsorWireV4) on the substrate's OWN records, mirroring
-- Algebra/Abelian/Z6-as-PFG. V₄ is the exponent-2 Klein group — one prime
-- (2), one Sylow (all of V₄), abelian — so it is the SIMPLEST AbelianPFG:
-- the whole group is its own 2-Sylow, and joint-generation is `base`.
--
-- The GTorsor field's two-sided `free` (act g₁ x ≈ act g₂ x → g₁ ≈ g₂) is
-- the genuine content ⟡H0 surfaced (Category.GTorsor.free is two-sided;
-- IsTorsor/V4-left-cancel is stabilizer-form). It is supplied here from the
-- group data by cancellation — the derivation machine-checked in
-- S5TorsorWireV4.two-sided-free, transcribed onto the substrate carrier.
--
-- Parameterized over the V₄ group data (mirroring Z6-as-PFG's style) so this
-- module checks against the substrate records without pinning a specific V₄
-- encoding; the concrete instance is `Groups.V4` fed in (⟡S4-wire-apply,
-- trivial: Groups.V4.Operations supplies _·_, ε, and inv=id/self-inverse).
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (ℕ; suc; zero)
open import Substrate.Foundation.Fin using (Fin; zero)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Category.GTorsor using (GTorsor; mkGTorsor)
open import Substrate.Category.SylowDecomposition
  using (SylowDecomposition; mkSylowDecomposition; InGenerated)
open import Substrate.Category.PrimeFactoredGauge
  using (PrimeFactoredGauge; mkPFG)
open import Substrate.Category.AbelianPFG
  using (AbelianPFG; mkAbelianPFG)

module Substrate.Algebra.Abelian.V4-as-PFG
  -- the V₄ carrier and group data (Groups.V4.Operations supplies these)
  (V4 : Set)
  (_·_ : V4 → V4 → V4)
  (εV : V4)
  -- the three algebraic facts the wire needs, all V₄-true (Groups/V4/Axioms):
  (·-assoc : (x y z : V4) → ((x · y) · z) ≡ (x · (y · z)))
  (·-idˡ   : (x : V4) → (εV · x) ≡ x)
  (·-idʳ   : (x : V4) → (x · εV) ≡ x)
  (selfinv : (x : V4) → (x · x) ≡ εV)      -- exponent-2 (Groups/V4/Operations.inv = id)
  (·-comm  : (x y : V4) → (x · y) ≡ (y · x))
  where

  -- the action: left multiplication (V₄ acts on itself).
  actV : V4 → V4 → V4
  actV = _·_

  ----------------------------------------------------------------------
  -- The GTorsor content. `free` is the two-sided form; the derivation is
  -- S5TorsorWireV4.two-sided-free transcribed: from act g₁ x ≡ act g₂ x,
  -- right-multiply by x and collapse x·x = εV both sides.
  ----------------------------------------------------------------------
  two-sided-free : (x g₁ g₂ : V4) → actV g₁ x ≡ actV g₂ x → g₁ ≡ g₂
  two-sided-free x g₁ g₂ p =
    trans (sym (·-idʳ g₁))
    (trans (cong (g₁ ·_) (sym (selfinv x)))
    (trans (sym (·-assoc g₁ x x))
    (trans (cong (_· x) p)
    (trans (·-assoc g₂ x x)
    (trans (cong (g₂ ·_) (selfinv x))
           (·-idʳ g₂))))))

  transV : (x y : V4) → Σ V4 (λ g → actV g x ≡ y)
  transV x y = (y · x) ,
    trans (·-assoc y x x) (trans (cong (y ·_) (selfinv x)) (·-idʳ y))

  v4-GTorsor : GTorsor V4 V4 _·_ εV _≡_ _≡_
  v4-GTorsor = mkGTorsor
    actV
    (λ x → ·-idˡ x)                       -- act εV x ≡ x
    (λ g h x → ·-assoc g h x)             -- act (g·h) x ≡ act g (act h x)
    transV
    two-sided-free

  ----------------------------------------------------------------------
  -- The Sylow decomposition: V₄ = the single 2-Sylow (all of V₄), one prime.
  -- Sylow 0 x = ⊤-ish (every x is in it) via the trivial predicate; joint-
  -- generation of any g is `base g` (g is in the sole Sylow).
  ----------------------------------------------------------------------
  data ⊤ : Set where tt : ⊤

  Sylow2 : V4 → Set
  Sylow2 _ = ⊤

  joint-gen : (g : V4) →
              InGenerated (λ x → Σ (Fin 1) (λ i → Sylow2 x)) _·_ εV g
  joint-gen g = InGenerated.base g (zero , tt)

  v4-Sylow : SylowDecomposition V4 _·_ εV 1
  v4-Sylow = mkSylowDecomposition
    (λ _ → 2)                             -- the single prime: 2
    (λ _ → 2)                             -- |V₄| = 2² ⇒ multiplicity 2
    (λ _ → Sylow2)
    joint-gen

  ----------------------------------------------------------------------
  -- Assemble: V₄ as a PrimeFactoredGauge, then as an AbelianPFG.
  ----------------------------------------------------------------------
  v4-PFG : PrimeFactoredGauge V4 V4 _·_ εV _≡_ _≡_ 1
  v4-PFG = mkPFG v4-Sylow v4-GTorsor

  v4-AbelianPFG : AbelianPFG V4 V4 _·_ εV _≡_ _≡_ 1
  v4-AbelianPFG = mkAbelianPFG v4-PFG ·-comm
