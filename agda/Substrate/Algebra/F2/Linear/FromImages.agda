------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages
--
-- Repurposed M-5 of the Cocycles structural-migration plan: the
-- canonical Linear-from-basis-images combinator. Given a function
-- `images : Fin k → Vector n` specifying where the k basis vectors
-- should go, produces the unique linear map satisfying that
-- prescription (uniqueness by M-3.5 linear-extensionality).
--
-- Construction: apply v = sum (λ i → lookup v i *ₛ images i). All
-- linearity proofs follow from the F₂ algebra of *ₛ over +ⱽ + sum
-- distribution, packaged here as small helpers.
--
-- (Originally-planned M-5 = F₂-affine subspaces deferred; not
-- needed for the immediate CY-5 migration target.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages where

open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin)
  renaming (zero to fz; suc to fs)
open import Data.Vec using (Vec; []; _∷_; lookup)
open import Function using (_∘_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Universal using (sum-cong)

------------------------------------------------------------------------
-- Small F₂-Vector helpers (factored for clarity; promoted to
-- Substrate.Algebra.F2.Vector if used elsewhere).
------------------------------------------------------------------------

-- Scalar pulls through: c *ₛ 𝟎ⱽ ≡ 𝟎ⱽ.
*ₛ-zeroʳ : ∀ {n} (c : F₂) → (c *ₛ (𝟎ⱽ {n})) ≡ 𝟎ⱽ
*ₛ-zeroʳ c = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ c 𝟎ⱽ i)
  (trans (cong (c ·_) (lookup-𝟎 i))
  (trans (·-absorbʳ c)
         (sym (lookup-𝟎 i)))))

-- Scalar associativity at the vector level: (c · d) *ₛ v ≡ c *ₛ (d *ₛ v).
*ₛ-·-assoc : ∀ {n} (c d : F₂) (v : Vector n) →
             ((c · d) *ₛ v) ≡ (c *ₛ (d *ₛ v))
*ₛ-·-assoc c d v = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ (c · d) v i)
  (trans (·-assoc c d (lookup v i))
  (trans (sym (cong (c ·_) (lookup-*ₛ d v i)))
         (sym (lookup-*ₛ c (d *ₛ v) i)))))

-- Scalar distributes from the right: (a + b) *ₛ v ≡ a *ₛ v +ⱽ b *ₛ v.
*ₛ-distribʳ-+ : ∀ {n} (a b : F₂) (v : Vector n) →
                ((a + b) *ₛ v) ≡ ((a *ₛ v) +ⱽ (b *ₛ v))
*ₛ-distribʳ-+ a b v = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ (a + b) v i)
  (trans (·-distribʳ-+ (lookup v i) a b)
         (sym (trans (lookup-+ⱽ (a *ₛ v) (b *ₛ v) i)
                     (cong₂ _+_ (lookup-*ₛ a v i) (lookup-*ₛ b v i))))))

------------------------------------------------------------------------
-- Sum distributes over componentwise +ⱽ on the family.
--
-- sum (λ i → f i +ⱽ g i) ≡ sum f +ⱽ sum g.
------------------------------------------------------------------------

sum-+ⱽ-distrib :
  ∀ {n m} (f g : Fin n → Vector m) →
  sum (λ i → f i +ⱽ g i) ≡ sum f +ⱽ sum g
sum-+ⱽ-distrib {zero}  f g = sym (+ⱽ-identityˡ 𝟎ⱽ)
sum-+ⱽ-distrib {suc _} f g =
  trans (cong (f fz +ⱽ g fz +ⱽ_) (sum-+ⱽ-distrib (f ∘ fs) (g ∘ fs)))
        (swap-+ⱽ (f fz) (g fz) (sum (f ∘ fs)) (sum (g ∘ fs)))
  where
    -- (a +ⱽ b) +ⱽ (c +ⱽ d) ≡ (a +ⱽ c) +ⱽ (b +ⱽ d), via lookup-componentwise
    -- + F₂ associativity / commutativity.
    swap-+ⱽ : ∀ {m} (a b c d : Vector m) →
              ((a +ⱽ b) +ⱽ (c +ⱽ d)) ≡ ((a +ⱽ c) +ⱽ (b +ⱽ d))
    swap-+ⱽ a b c d = ≡-from-lookup _ _ (λ i →
      let la = lookup a i; lb = lookup b i
          lc = lookup c i; ld = lookup d i
      in trans (lookup-+ⱽ (a +ⱽ b) (c +ⱽ d) i)
         (trans (cong₂ _+_ (lookup-+ⱽ a b i) (lookup-+ⱽ c d i))
         (trans (+-assoc la lb (lc + ld))
         (trans (cong (la +_) (sym (+-assoc lb lc ld)))
         (trans (cong (λ z → la + (z + ld)) (+-comm lb lc))
         (trans (cong (la +_) (+-assoc lc lb ld))
         (trans (sym (+-assoc la lc (lb + ld)))
                (sym (trans (lookup-+ⱽ (a +ⱽ c) (b +ⱽ d) i)
                            (cong₂ _+_ (lookup-+ⱽ a c i) (lookup-+ⱽ b d i)))))))))))

------------------------------------------------------------------------
-- Scalar pulls through sum.
------------------------------------------------------------------------

*ₛ-sum-distrib :
  ∀ {n m} (c : F₂) (f : Fin n → Vector m) →
  (c *ₛ sum f) ≡ sum (λ i → c *ₛ f i)
*ₛ-sum-distrib {zero}  c f = *ₛ-zeroʳ c
*ₛ-sum-distrib {suc _} c f =
  trans (*ₛ-distribˡ-+ⱽ c (f fz) (sum (f ∘ fs)))
        (cong (c *ₛ f fz +ⱽ_) (*ₛ-sum-distrib c (f ∘ fs)))

------------------------------------------------------------------------
-- The main construction: linear-from-images.
------------------------------------------------------------------------

linear-from-images : ∀ {k n} → (Fin k → Vector n) → Linear k n
linear-from-images images = record
  { apply        = λ v → sum (λ i → lookup v i *ₛ images i)
  ; preserves-+  = λ u v →
      trans (sum-cong (λ i →
              trans (cong (_*ₛ images i) (lookup-+ⱽ u v i))
                    (*ₛ-distribʳ-+ (lookup u i) (lookup v i) (images i))))
            (sum-+ⱽ-distrib (λ i → lookup u i *ₛ images i)
                              (λ i → lookup v i *ₛ images i))
  ; preserves-*ₛ = λ c v →
      trans (sum-cong (λ i →
              trans (cong (_*ₛ images i) (lookup-*ₛ c v i))
                    (*ₛ-·-assoc c (lookup v i) (images i))))
            (sym (*ₛ-sum-distrib c (λ i → lookup v i *ₛ images i)))
  }

------------------------------------------------------------------------
-- Foundational apply-reduction (universal-property discipline).
--
-- The canonical componentwise unfolding of `apply (linear-from-images f) v`
-- at any output coordinate `j`. Used to discharge `apply-Selector-lookup`-
-- style proofs for any specific Selector without manual F₂-axiom chains.
--
-- Per memory `feedback_universal_property_discipline`: this is the
-- structural primitive that scales to large RM/Hamming codes. Per-
-- instance unfolding of the sum is replaced by one application of
-- this lemma plus a `O(k)` collapse over the basis-images. The
-- per-instance work is bounded by k (number of basis-images), not
-- 2^n (number of input vectors).
------------------------------------------------------------------------

apply-linear-from-images-lookup :
  ∀ {k n} (f : Fin k → Vector n) (v : Vector k) (j : Fin n) →
  lookup (apply (linear-from-images f) v) j ≡
  sum-F₂ (λ i → lookup v i · lookup (f i) j)
apply-linear-from-images-lookup f v j =
  trans (lookup-sum (λ i → lookup v i *ₛ f i) j)
        (sum-F₂-cong (λ i → lookup-*ₛ (lookup v i) (f i) j))

------------------------------------------------------------------------
-- Apply on basis: the canonical identification of `linear-from-images f`.
--
-- Per memory `feedback_universal_property_discipline`: this is the
-- second foundational primitive for the universal-property tower —
-- it says `linear-from-images f` does exactly what it claims to do at
-- basis vectors. Used directly for the Hamming syndrome identification
-- in M-11.fano and for any future "apply Selector basis" lemmas.
--
-- Proof structure:
--   1. Reduce to componentwise via `apply-linear-from-images-lookup` +
--      `≡-from-lookup`.
--   2. Apply `sum-F₂-basis-collapse`: sum-F₂ of (basis_i · g) ≡ g i.
--
-- The basis-collapse helper uses that `lookup (basis i) j = 𝟙 iff i ≡ j`
-- (basis orthogonality from M-2.5).
------------------------------------------------------------------------

-- Sum collapses when one factor is a basis vector.
sum-F₂-basis-collapse :
  ∀ {k} (i : Fin k) (g : Fin k → F₂) →
  sum-F₂ (λ j → lookup (basis i) j · g j) ≡ g i
sum-F₂-basis-collapse {suc k} fz g =
  trans (cong (_+ tail-sum) (·-identityˡ (g fz)))
  (trans (cong (g fz +_) (zero-tail g))
         (+-identityʳ (g fz)))
  where
    tail-sum : F₂
    tail-sum = sum-F₂ {k} (λ j' → lookup (𝟎ⱽ {k}) j' · g (fs j'))

    -- After basis fz unfolds to 𝟙 ∷ 𝟎ⱽ, the suc-indexed summands
    -- become lookup 𝟎ⱽ j' · g (suc j') = 𝟘.
    zero-tail : ∀ {k} (g : Fin (suc k) → F₂) →
      sum-F₂ {k} (λ j' → lookup (𝟎ⱽ {k}) j' · g (fs j')) ≡ 𝟘
    zero-tail {zero}    _ = refl
    zero-tail {suc k'} g =
      trans (cong (_+ sum-F₂ {k'} (λ j' → lookup (𝟎ⱽ {k'}) j' · g (fs (fs j'))))
                  (·-absorbˡ (g (fs fz))))
      (trans (+-identityˡ _)
             (zero-tail (g ∘ fs)))
sum-F₂-basis-collapse {suc k} (fs i) g =
  trans (cong (_+ sum-F₂ {k} (λ j → lookup (basis i) j · g (fs j)))
              (·-absorbˡ (g fz)))
  (trans (+-identityˡ _)
         (sum-F₂-basis-collapse i (g ∘ fs)))

apply-linear-from-images-basis :
  ∀ {k n} (f : Fin k → Vector n) (i : Fin k) →
  apply (linear-from-images f) (basis i) ≡ f i
apply-linear-from-images-basis f i = ≡-from-lookup _ _ goal
  where
    goal : (m : Fin _) →
           lookup (apply (linear-from-images f) (basis i)) m ≡ lookup (f i) m
    goal m = trans (apply-linear-from-images-lookup f (basis i) m)
                   (sum-F₂-basis-collapse i (λ j → lookup (f j) m))
