------------------------------------------------------------------------
-- Substrate.Algebra.F2.AsModule
--
-- Mod6 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- Packages Substrate.Algebra.F2.Vector as a Module instance over
-- F₂-Ring (M9). Componentwise + / scalar * / 0 / negation discharge
-- the 4 module axioms via F₂.Vector's existing pointwise lemmas.
--
-- This closes the visible-surface F₂-vector arithmetic gap: the
-- existing Vector laws become Module-accessor projections.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AsModule where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
  using (F₂; 𝟘; 𝟙; _+_; _·_; -_;
         +-self-inverse; ·-distribʳ-+; ·-assoc)
open import Substrate.Algebra.F2.Vector
  using (Vector; 𝟎ⱽ; _+ⱽ_; _*ₛ_; -ⱽ_; basis;
         lookup-𝟎; lookup-+ⱽ; lookup-*ₛ; lookup--ⱽ;
         ≡-from-lookup;
         +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-comm; +ⱽ-assoc;
         +ⱽ-self-inverse;
         *ₛ-identityˡ; *ₛ-distribˡ-+ⱽ)
open import Substrate.Algebra.F2.AsField
  using (F₂-+-Magma; F₂-+-Semigroup; F₂-+-Monoid;
         F₂-+-Group; F₂-+-AbelianGroup; F₂-Ring)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Free using (FreeCarrier)

------------------------------------------------------------------------
-- 1. The two missing pointwise lemmas for the Module axioms.
--
-- F2.Vector already proves distrib-vector (`*ₛ-distribˡ-+ⱽ`) and
-- identity-scalar (`*ₛ-identityˡ`); we need distrib-scalar and
-- scalar-mult-assoc.
------------------------------------------------------------------------

-- (r + s) *ₛ v ≡ (r *ₛ v) +ⱽ (s *ₛ v)
*ₛ-distribʳ-+ : ∀ {n} (r s : F₂) (v : Vector n) →
                ((r + s) *ₛ v) ≡ ((r *ₛ v) +ⱽ (s *ₛ v))
*ₛ-distribʳ-+ r s v = ≡-from-lookup ((r + s) *ₛ v) ((r *ₛ v) +ⱽ (s *ₛ v))
  (λ i →
    trans (lookup-*ₛ (r + s) v i)
    (trans (·-distribʳ-+ (lookup v i) r s)
    (trans (cong₂ _+_ (sym (lookup-*ₛ r v i)) (sym (lookup-*ₛ s v i)))
           (sym (lookup-+ⱽ (r *ₛ v) (s *ₛ v) i)))))

-- (r · s) *ₛ v ≡ r *ₛ (s *ₛ v)
*ₛ-assoc : ∀ {n} (r s : F₂) (v : Vector n) →
           ((r · s) *ₛ v) ≡ (r *ₛ (s *ₛ v))
*ₛ-assoc r s v = ≡-from-lookup ((r · s) *ₛ v) (r *ₛ (s *ₛ v))
  (λ i →
    trans (lookup-*ₛ (r · s) v i)
    (trans (·-assoc r s (lookup v i))
           (trans (cong (r ·_) (sym (lookup-*ₛ s v i)))
                  (sym (lookup-*ₛ r (s *ₛ v) i)))))

------------------------------------------------------------------------
-- 2. The additive AbelianGroup on Vector n.
------------------------------------------------------------------------

F₂Vec-+-Magma : ∀ {n} → Magma (Vector n)
F₂Vec-+-Magma = record { _·_ = _+ⱽ_ }

F₂Vec-+-Semigroup : ∀ {n} → Semigroup (Vector n)
F₂Vec-+-Semigroup = record
  { magma   = F₂Vec-+-Magma
  ; ·-assoc = +ⱽ-assoc
  }

F₂Vec-+-Monoid : ∀ {n} → Monoid (Vector n)
F₂Vec-+-Monoid = record
  { semigroup = F₂Vec-+-Semigroup
  ; ε         = 𝟎ⱽ
  ; ε-left    = +ⱽ-identityˡ
  ; ε-right   = +ⱽ-identityʳ
  }

-- In char-2 -ⱽ v ≡ v definitionally up to map, so we prove
-- both inverse laws by reducing to lookup and applying F₂'s
-- +-inverseˡ / +-inverseʳ.
+ⱽ-invˡ : ∀ {n} (v : Vector n) → ((-ⱽ v) +ⱽ v) ≡ 𝟎ⱽ
+ⱽ-invˡ v = ≡-from-lookup ((-ⱽ v) +ⱽ v) 𝟎ⱽ
  (λ i →
    trans (lookup-+ⱽ (-ⱽ v) v i)
    (trans (cong (_+ lookup v i) (lookup--ⱽ v i))
    (trans (Substrate.Algebra.F2.+-inverseˡ (lookup v i))
           (sym (lookup-𝟎 i)))))

+ⱽ-invʳ : ∀ {n} (v : Vector n) → (v +ⱽ (-ⱽ v)) ≡ 𝟎ⱽ
+ⱽ-invʳ v = ≡-from-lookup (v +ⱽ (-ⱽ v)) 𝟎ⱽ
  (λ i →
    trans (lookup-+ⱽ v (-ⱽ v) i)
    (trans (cong (lookup v i +_) (lookup--ⱽ v i))
    (trans (Substrate.Algebra.F2.+-inverseʳ (lookup v i))
           (sym (lookup-𝟎 i)))))

F₂Vec-+-Group : ∀ {n} → Group (Vector n)
F₂Vec-+-Group = record
  { monoid    = F₂Vec-+-Monoid
  ; inv       = -ⱽ_
  ; inv-left  = +ⱽ-invˡ
  ; inv-right = +ⱽ-invʳ
  }

F₂Vec-+-AbelianGroup : ∀ {n} → AbelianGroup (Vector n)
F₂Vec-+-AbelianGroup = record
  { group  = F₂Vec-+-Group
  ; ·-comm = +ⱽ-comm
  }

------------------------------------------------------------------------
-- 3. F₂ⁿ as a Module over F₂-Ring.
------------------------------------------------------------------------

F₂-FreeModule : (n : ℕ) → Module F₂-Ring (Vector n)
F₂-FreeModule n = record
  { M-abelian         = F₂Vec-+-AbelianGroup
  ; _·ₛ_              = _*ₛ_
  ; distrib-scalar    = *ₛ-distribʳ-+
  ; distrib-vector    = *ₛ-distribˡ-+ⱽ
  ; scalar-mult-assoc = *ₛ-assoc
  ; identity-scalar   = *ₛ-identityˡ
  }

-- Sanity: Vector n IS FreeCarrier F₂ n at the type level (definitionally).
F₂-FreeModule-on-FreeCarrier :
  (n : ℕ) → Module F₂-Ring (FreeCarrier F₂ n)
F₂-FreeModule-on-FreeCarrier = F₂-FreeModule

------------------------------------------------------------------------
-- 4. Capstone for Mod6.
--
-- F₂ⁿ packaged as Module F₂-Ring. The visible-surface F₂-Vector
-- arithmetic laws collapse to Module-accessor projections via
-- F₂-FreeModule. Mod7 supplies the analogous ℚ instance.
------------------------------------------------------------------------
