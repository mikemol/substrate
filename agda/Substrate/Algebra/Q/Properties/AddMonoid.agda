------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.AddMonoid
--
-- The additive monoid (ℚ, +ℚ, 0ℚ) realized as a ≡-based `Algebra.Monoid` on
-- the QUOTIENT ℚ/≈ℚ — i.e. on the canonical representatives, where the setoid
-- equality ≈ℚ collapses to propositional ≡. This is the ≡-structure the
-- categorical spine needs: `Category.Delooping.deloop` of it is 𝐁(ℚ,+ℚ), the
-- Algebra→Category bridge for the additive (G_OR / parallel-conductance) ℚ
-- structure that GValueAsQ's `gor` renames.
--
-- The canonicaliser is taken ABSTRACTLY (a module parameter `red` + its three
-- Canonical laws). This is not just hygiene: `Q.Reduce.reduce` runs gcd
-- (compute-trace), which does NOT normalise on SYMBOLIC ℚ — instantiating it
-- inside the nested-reduce monoid laws blows up typechecking. Kept abstract,
-- the laws never force it; the concrete instance substitutes `reduce` +
-- `canonical-respects-≈` + `≈-canonical` into the already-checked proofs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.AddMonoid where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Algebra.Q using (ℚ; 0ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.DecidableEq using (_≟ℚ_)
open import Substrate.Algebra.Q.Properties.Field
  using (+ℚ-assoc; +ℚ-identityˡ; +ℚ-identityʳ)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-canonical)
open import Substrate.Algebra.Q.Properties.Canonical using (canonical-respects-≈)
open import Substrate.Algebra.Monoid using (Monoid)

------------------------------------------------------------------------
-- The construction, ABSTRACT over the canonicaliser (never normalised).
------------------------------------------------------------------------

module ReducedMonoid
  (red       : ℚ → ℚ)
  (red-resp  : {a b : ℚ} → a ≈ℚ b → red a ≡ red b)
  (red-sound : (q : ℚ) → q ≈ℚ red q)
  where

  -- the quotient carrier: canonical reps (≈ℚ is ≡ here).
  RQ : Set
  RQ = Σ ℚ (λ q → red q ≡ q)

  red-idem : (q : ℚ) → red (red q) ≡ red q
  red-idem q = sym (red-resp (red-sound q))

  -- ℚ is a set (decidable ≡), so the reducedness proof is irrelevant.
  RQ-≡ : {x y : RQ} → proj₁ x ≡ proj₁ y → x ≡ y
  RQ-≡ {a , pa} {.a , pb} refl = cong (a ,_) (Decidable⇒UIP _≟ℚ_ pa pb)

  _·R_ : RQ → RQ → RQ
  (a , _) ·R (b , _) = red (a +ℚ b) , red-idem (a +ℚ b)

  εR : RQ
  εR = red 0ℚ , red-idem 0ℚ

  ·R-assoc : (x y z : RQ) → ((x ·R y) ·R z) ≡ (x ·R (y ·R z))
  ·R-assoc (a , _) (b , _) (c , _) = RQ-≡ fst-eq
    where
      fst-eq : red (red (a +ℚ b) +ℚ c) ≡ red (a +ℚ red (b +ℚ c))
      fst-eq =
        trans (red-resp {red (a +ℚ b) +ℚ c} {(a +ℚ b) +ℚ c}
                 (+ℚ-cong {red (a +ℚ b)} {a +ℚ b} {c} {c}
                          (≈ℚ-sym {a +ℚ b} {red (a +ℚ b)} (red-sound (a +ℚ b)))
                          (≈ℚ-refl c)))
        (trans (red-resp {(a +ℚ b) +ℚ c} {a +ℚ (b +ℚ c)} (+ℚ-assoc a b c))
               (sym (red-resp {a +ℚ red (b +ℚ c)} {a +ℚ (b +ℚ c)}
                 (+ℚ-cong {a} {a} {red (b +ℚ c)} {b +ℚ c}
                          (≈ℚ-refl a)
                          (≈ℚ-sym {b +ℚ c} {red (b +ℚ c)} (red-sound (b +ℚ c)))))))

  εR-left : (x : RQ) → (εR ·R x) ≡ x
  εR-left (a , pa) = RQ-≡ (trans (red-resp {red 0ℚ +ℚ a} {a} stepL) pa)
    where
      stepL : (red 0ℚ +ℚ a) ≈ℚ a
      stepL = ≈ℚ-trans {red 0ℚ +ℚ a} {0ℚ +ℚ a} {a}
                (+ℚ-cong {red 0ℚ} {0ℚ} {a} {a}
                         (≈ℚ-sym {0ℚ} {red 0ℚ} (red-sound 0ℚ)) (≈ℚ-refl a))
                (+ℚ-identityˡ a)

  εR-right : (x : RQ) → (x ·R εR) ≡ x
  εR-right (a , pa) = RQ-≡ (trans (red-resp {a +ℚ red 0ℚ} {a} stepR) pa)
    where
      stepR : (a +ℚ red 0ℚ) ≈ℚ a
      stepR = ≈ℚ-trans {a +ℚ red 0ℚ} {a +ℚ 0ℚ} {a}
                (+ℚ-cong {a} {a} {red 0ℚ} {0ℚ}
                         (≈ℚ-refl a) (≈ℚ-sym {0ℚ} {red 0ℚ} (red-sound 0ℚ)))
                (+ℚ-identityʳ a)

  Reduced-Monoid : Monoid RQ
  Reduced-Monoid = record
    { semigroup = record { magma = record { _·_ = _·R_ } ; ·-assoc = ·R-assoc }
    ; ε = εR ; ε-left = εR-left ; ε-right = εR-right }

------------------------------------------------------------------------
-- The concrete instance: red := the ℚ `reduce`-Canonical.
------------------------------------------------------------------------

module Reduced = ReducedMonoid reduce canonical-respects-≈ ≈-canonical

open Reduced public using () renaming (RQ to ℚ/≈; Reduced-Monoid to +ℚ-reduced-Monoid)
