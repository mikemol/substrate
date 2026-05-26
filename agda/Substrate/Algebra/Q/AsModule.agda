------------------------------------------------------------------------
-- Substrate.Algebra.Q.AsModule
--
-- Mod7 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- Packages Substrate.Algebra.Q.Vector as a Module instance over a
-- ℚ-Ring derived from `ℚ-Field-Obligation` (M10 scaffolding).
--
-- The Vector-level axioms (associativity, commutativity, identity,
-- inverse, scalar distributivity, scalar associativity, identity-
-- scalar) are derived COMPONENTWISE from the obligation record via
-- `≡-from-lookup` (mirrors Mod6's F₂ retrofit). This closes the
-- ℚ-linear-extensionality gap STRUCTURALLY: when the Q-arc supplies
-- a ℚ-Field-Obligation instance (Q-arc deferral), this slice
-- produces the full ℚ-FreeModule mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.AsModule where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate; lookup; zipWith; map)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans)

open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_; _*ℚ_; -ℚ_)
open import Substrate.Algebra.Q.Vector
  using (Vector; 𝟎ℚⱽ; _+ℚⱽ_; _*ℚₛ_; -ℚⱽ_; basis-ℚ)
open import Substrate.Algebra.Q.AsField
  using (ℚ-+-Magma; ℚ-·-Magma; ℚ-Field-Obligation)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Free using (FreeCarrier)

------------------------------------------------------------------------
-- 1. Lookup characterisations on ℚ-vectors (substrate-native).
--
-- Mirrors Substrate.Algebra.F2.Vector's lookup-𝟎 / lookup-+ⱽ /
-- lookup-*ₛ / lookup--ⱽ. These are structural and independent of
-- ℚ's ring-laws (only structural on Vec / map / zipWith).
------------------------------------------------------------------------

lookup-𝟎ℚⱽ : ∀ {n} (i : Fin n) → lookup (𝟎ℚⱽ {n}) i ≡ 0ℚ
lookup-𝟎ℚⱽ zero    = refl
lookup-𝟎ℚⱽ (suc i) = lookup-𝟎ℚⱽ i

lookup-+ℚⱽ :
  ∀ {n} (u v : Vector n) (i : Fin n) →
  lookup (u +ℚⱽ v) i ≡ (lookup u i +ℚ lookup v i)
lookup-+ℚⱽ (_ ∷ _) (_ ∷ _) zero    = refl
lookup-+ℚⱽ (_ ∷ u) (_ ∷ v) (suc i) = lookup-+ℚⱽ u v i

lookup-*ℚₛ :
  ∀ {n} (c : ℚ) (v : Vector n) (i : Fin n) →
  lookup (c *ℚₛ v) i ≡ (c *ℚ lookup v i)
lookup-*ℚₛ _ (_ ∷ _) zero    = refl
lookup-*ℚₛ c (_ ∷ v) (suc i) = lookup-*ℚₛ c v i

lookup--ℚⱽ :
  ∀ {n} (v : Vector n) (i : Fin n) →
  lookup (-ℚⱽ v) i ≡ (-ℚ lookup v i)
lookup--ℚⱽ (_ ∷ _) zero    = refl
lookup--ℚⱽ (_ ∷ v) (suc i) = lookup--ℚⱽ v i

≡-from-lookup-ℚ :
  ∀ {n} (u v : Vector n) →
  ((i : Fin n) → lookup u i ≡ lookup v i) →
  u ≡ v
≡-from-lookup-ℚ []      []      _ = refl
≡-from-lookup-ℚ (x ∷ u) (y ∷ v) eq =
  cong₂ _∷_ (eq zero) (≡-from-lookup-ℚ u v (λ i → eq (suc i)))

------------------------------------------------------------------------
-- 2. Parametric Vector-level axioms.
--
-- Given an ℚ-Field-Obligation instance, all per-Vector axioms lift
-- componentwise. The lifters are the SUBSTRATE-NATIVE structural
-- content of Mod7.
------------------------------------------------------------------------

module Lifters (o : ℚ-Field-Obligation) where
  open ℚ-Field-Obligation o

  +ℚⱽ-identityˡ : ∀ {n} (v : Vector n) → (𝟎ℚⱽ +ℚⱽ v) ≡ v
  +ℚⱽ-identityˡ v = ≡-from-lookup-ℚ (𝟎ℚⱽ +ℚⱽ v) v
    (λ i → trans (lookup-+ℚⱽ 𝟎ℚⱽ v i)
          (cong-trans (_+ℚ lookup v i) (lookup-𝟎ℚⱽ i)
                 (+ℚ-identityˡ (lookup v i))))

  +ℚⱽ-identityʳ : ∀ {n} (v : Vector n) → (v +ℚⱽ 𝟎ℚⱽ) ≡ v
  +ℚⱽ-identityʳ v = ≡-from-lookup-ℚ (v +ℚⱽ 𝟎ℚⱽ) v
    (λ i → trans (lookup-+ℚⱽ v 𝟎ℚⱽ i)
          (cong-trans (lookup v i +ℚ_) (lookup-𝟎ℚⱽ i)
                 (+ℚ-identityʳ (lookup v i))))

  +ℚⱽ-comm : ∀ {n} (u v : Vector n) → (u +ℚⱽ v) ≡ (v +ℚⱽ u)
  +ℚⱽ-comm u v = ≡-from-lookup-ℚ (u +ℚⱽ v) (v +ℚⱽ u)
    (λ i → trans (lookup-+ℚⱽ u v i)
          (trans (+ℚ-comm (lookup u i) (lookup v i))
                 (sym (lookup-+ℚⱽ v u i))))

  +ℚⱽ-assoc :
    ∀ {n} (u v w : Vector n) →
    ((u +ℚⱽ v) +ℚⱽ w) ≡ (u +ℚⱽ (v +ℚⱽ w))
  +ℚⱽ-assoc u v w = ≡-from-lookup-ℚ ((u +ℚⱽ v) +ℚⱽ w) (u +ℚⱽ (v +ℚⱽ w))
    (λ i →
      trans (lookup-+ℚⱽ (u +ℚⱽ v) w i)
      (cong-trans (_+ℚ lookup w i) (lookup-+ℚⱽ u v i)
      (trans (+ℚ-assoc (lookup u i) (lookup v i) (lookup w i))
      (cong-trans (lookup u i +ℚ_) (sym (lookup-+ℚⱽ v w i))
             (sym (lookup-+ℚⱽ u (v +ℚⱽ w) i))))))

  +ℚⱽ-inverseˡ : ∀ {n} (v : Vector n) → ((-ℚⱽ v) +ℚⱽ v) ≡ 𝟎ℚⱽ
  +ℚⱽ-inverseˡ v = ≡-from-lookup-ℚ ((-ℚⱽ v) +ℚⱽ v) 𝟎ℚⱽ
    (λ i → trans (lookup-+ℚⱽ (-ℚⱽ v) v i)
          (cong-trans (_+ℚ lookup v i) (lookup--ℚⱽ v i)
          (trans (+ℚ-inverseˡ (lookup v i))
                 (sym (lookup-𝟎ℚⱽ i)))))

  +ℚⱽ-inverseʳ : ∀ {n} (v : Vector n) → (v +ℚⱽ (-ℚⱽ v)) ≡ 𝟎ℚⱽ
  +ℚⱽ-inverseʳ v = ≡-from-lookup-ℚ (v +ℚⱽ (-ℚⱽ v)) 𝟎ℚⱽ
    (λ i → trans (lookup-+ℚⱽ v (-ℚⱽ v) i)
          (cong-trans (lookup v i +ℚ_) (lookup--ℚⱽ v i)
          (trans (+ℚ-inverseʳ (lookup v i))
                 (sym (lookup-𝟎ℚⱽ i)))))

  *ℚₛ-identityˡ : ∀ {n} (v : Vector n) → (1ℚ *ℚₛ v) ≡ v
  *ℚₛ-identityˡ v = ≡-from-lookup-ℚ (1ℚ *ℚₛ v) v
    (λ i → trans (lookup-*ℚₛ 1ℚ v i) (*ℚ-identityˡ (lookup v i)))

  *ℚₛ-distribˡ-+ℚⱽ :
    ∀ {n} (c : ℚ) (u v : Vector n) →
    (c *ℚₛ (u +ℚⱽ v)) ≡ ((c *ℚₛ u) +ℚⱽ (c *ℚₛ v))
  *ℚₛ-distribˡ-+ℚⱽ c u v =
    ≡-from-lookup-ℚ (c *ℚₛ (u +ℚⱽ v)) ((c *ℚₛ u) +ℚⱽ (c *ℚₛ v))
    (λ i →
      trans (lookup-*ℚₛ c (u +ℚⱽ v) i)
      (cong-trans (c *ℚ_) (lookup-+ℚⱽ u v i)
      (trans (distribˡ c (lookup u i) (lookup v i))
      (trans (cong₂ _+ℚ_ (sym (lookup-*ℚₛ c u i)) (sym (lookup-*ℚₛ c v i)))
             (sym (lookup-+ℚⱽ (c *ℚₛ u) (c *ℚₛ v) i))))))

  *ℚₛ-distribʳ-+ :
    ∀ {n} (r s : ℚ) (v : Vector n) →
    ((r +ℚ s) *ℚₛ v) ≡ ((r *ℚₛ v) +ℚⱽ (s *ℚₛ v))
  *ℚₛ-distribʳ-+ r s v =
    ≡-from-lookup-ℚ ((r +ℚ s) *ℚₛ v) ((r *ℚₛ v) +ℚⱽ (s *ℚₛ v))
    (λ i →
      trans (lookup-*ℚₛ (r +ℚ s) v i)
      (trans (distribʳ (lookup v i) r s)
      (trans (cong₂ _+ℚ_ (sym (lookup-*ℚₛ r v i)) (sym (lookup-*ℚₛ s v i)))
             (sym (lookup-+ℚⱽ (r *ℚₛ v) (s *ℚₛ v) i)))))

  *ℚₛ-assoc :
    ∀ {n} (r s : ℚ) (v : Vector n) →
    ((r *ℚ s) *ℚₛ v) ≡ (r *ℚₛ (s *ℚₛ v))
  *ℚₛ-assoc r s v = ≡-from-lookup-ℚ ((r *ℚ s) *ℚₛ v) (r *ℚₛ (s *ℚₛ v))
    (λ i →
      trans (lookup-*ℚₛ (r *ℚ s) v i)
      (trans (*ℚ-assoc r s (lookup v i))
      (cong-trans (r *ℚ_) (sym (lookup-*ℚₛ s v i))
             (sym (lookup-*ℚₛ r (s *ℚₛ v) i)))))

  ----------------------------------------------------------------------
  -- 3. ℚ-Ring assembly from obligation.
  --
  -- Mechanical packaging of obligation fields into the M1-M7 record
  -- stack. `+-coherent` holds by `refl` because both monoids are
  -- constructed from the same primitives.
  ----------------------------------------------------------------------

  ℚ-+-Semigroup : Semigroup ℚ
  ℚ-+-Semigroup = record { magma = ℚ-+-Magma ; ·-assoc = +ℚ-assoc }

  ℚ-+-Monoid : Monoid ℚ
  ℚ-+-Monoid = record
    { semigroup = ℚ-+-Semigroup
    ; ε         = 0ℚ
    ; ε-left    = +ℚ-identityˡ
    ; ε-right   = +ℚ-identityʳ
    }

  ℚ-+-Group : Group ℚ
  ℚ-+-Group = record
    { monoid    = ℚ-+-Monoid
    ; inv       = -ℚ_
    ; inv-left  = +ℚ-inverseˡ
    ; inv-right = +ℚ-inverseʳ
    }

  ℚ-+-AbelianGroup : AbelianGroup ℚ
  ℚ-+-AbelianGroup = record { group = ℚ-+-Group ; ·-comm = +ℚ-comm }

  ℚ-·-Semigroup : Semigroup ℚ
  ℚ-·-Semigroup = record { magma = ℚ-·-Magma ; ·-assoc = *ℚ-assoc }

  ℚ-·-Monoid : Monoid ℚ
  ℚ-·-Monoid = record
    { semigroup = ℚ-·-Semigroup
    ; ε         = 1ℚ
    ; ε-left    = *ℚ-identityˡ
    ; ε-right   = *ℚ-identityʳ
    }

  ℚ-Semiring : Semiring ℚ
  ℚ-Semiring = record
    { +-monoid          = ℚ-+-Monoid
    ; *-monoid          = ℚ-·-Monoid
    ; distrib-left      = distribˡ
    ; distrib-right     = λ a b c → distribʳ c a b
    ; zero-absorb-left  = zero-absorbˡ
    ; zero-absorb-right = zero-absorbʳ
    }

  ℚ-Ring : Ring ℚ
  ℚ-Ring = record
    { semiring   = ℚ-Semiring
    ; +-abelian  = ℚ-+-AbelianGroup
    ; +-coherent = refl
    }

  ----------------------------------------------------------------------
  -- 4. ℚⁿ as a Module over ℚ-Ring.
  ----------------------------------------------------------------------

  ℚVec-+-Magma : ∀ {n} → Magma (Vector n)
  ℚVec-+-Magma = record { _·_ = _+ℚⱽ_ }

  ℚVec-+-Semigroup : ∀ {n} → Semigroup (Vector n)
  ℚVec-+-Semigroup = record { magma = ℚVec-+-Magma ; ·-assoc = +ℚⱽ-assoc }

  ℚVec-+-Monoid : ∀ {n} → Monoid (Vector n)
  ℚVec-+-Monoid = record
    { semigroup = ℚVec-+-Semigroup
    ; ε         = 𝟎ℚⱽ
    ; ε-left    = +ℚⱽ-identityˡ
    ; ε-right   = +ℚⱽ-identityʳ
    }

  ℚVec-+-Group : ∀ {n} → Group (Vector n)
  ℚVec-+-Group = record
    { monoid    = ℚVec-+-Monoid
    ; inv       = -ℚⱽ_
    ; inv-left  = +ℚⱽ-inverseˡ
    ; inv-right = +ℚⱽ-inverseʳ
    }

  ℚVec-+-AbelianGroup : ∀ {n} → AbelianGroup (Vector n)
  ℚVec-+-AbelianGroup = record { group = ℚVec-+-Group ; ·-comm = +ℚⱽ-comm }

  ℚ-FreeModule : (n : ℕ) → Module ℚ-Ring (Vector n)
  ℚ-FreeModule n = record
    { M-abelian         = ℚVec-+-AbelianGroup
    ; _·ₛ_              = _*ℚₛ_
    ; distrib-scalar    = *ℚₛ-distribʳ-+
    ; distrib-vector    = *ℚₛ-distribˡ-+ℚⱽ
    ; scalar-mult-assoc = *ℚₛ-assoc
    ; identity-scalar   = *ℚₛ-identityˡ
    }

  -- Sanity: Vector n ≡ FreeCarrier ℚ n definitionally.
  ℚ-FreeModule-on-FreeCarrier :
    (n : ℕ) → Module ℚ-Ring (FreeCarrier ℚ n)
  ℚ-FreeModule-on-FreeCarrier = ℚ-FreeModule

------------------------------------------------------------------------
-- 5. Capstone for Mod7.
--
-- ℚⁿ assembled as Module ℚ-Ring(o) parametrically in any
-- `ℚ-Field-Obligation` o. The Q-arc's per-arithmetic obligation
-- (deferred at M10) feeds this lifter once discharged; the
-- ℚ-FreeModule then exists mechanically.
--
-- Closes the ℚ-linear-extensionality gap STRUCTURALLY: Mod5's
-- FreeBasisUniversal at ℚ-Ring(o) and ℚ-FreeModule o n is the lemma
-- TPQ7 / FLQ7 deferred — discharged at Mod8 via the generic
-- FreeBasisUniversal proof.
------------------------------------------------------------------------
