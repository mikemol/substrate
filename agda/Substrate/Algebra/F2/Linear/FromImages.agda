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

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans; sym-trans; trans-sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Universal using (sum-cong)
open import Substrate.Algebra.F2.AsModule using (*ₛ-distribʳ-+)

------------------------------------------------------------------------
-- Small F₂-Vector helpers (factored for clarity; promoted to
-- Substrate.Algebra.F2.Vector if used elsewhere).
------------------------------------------------------------------------

-- Scalar pulls through: c *ₛ 𝟎ⱽ ≡ 𝟎ⱽ.
*ₛ-zeroʳ : ∀ {n} (c : F₂) → (c *ₛ (𝟎ⱽ {n})) ≡ 𝟎ⱽ
*ₛ-zeroʳ c = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ c 𝟎ⱽ i)
  (cong-trans (c ·_) (lookup-𝟎 i)
  (trans-sym (·-absorbʳ c)
             (lookup-𝟎 i))))

-- Scalar associativity at the vector level: (c · d) *ₛ v ≡ c *ₛ (d *ₛ v).
*ₛ-·-assoc : ∀ {n} (c d : F₂) (v : Vector n) →
             ((c · d) *ₛ v) ≡ (c *ₛ (d *ₛ v))
*ₛ-·-assoc c d v = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ (c · d) v i)
  (trans (·-assoc c d (lookup v i))
  (sym-trans (cong (c ·_) (lookup-*ₛ d v i))
             (sym (lookup-*ₛ c (d *ₛ v) i)))))

-- Ⓓ: (a + b) *ₛ v ≡ a *ₛ v +ⱽ b *ₛ v is AsModule's *ₛ-distribʳ-+ (the F₂
-- module structure's home), imported above; it was re-proved here identically.

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
  cong-trans (f fzero +ⱽ g fzero +ⱽ_) (sum-+ⱽ-distrib (λ ix → f (fsuc ix)) (λ ix → g (fsuc ix)))
             (swap-+ⱽ (f fzero) (g fzero) (sum (λ ix → f (fsuc ix))) (sum (λ ix → g (fsuc ix))))
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
         (cong-trans (la +_) (sym (+-assoc lb lc ld))
         (cong-trans (λ z → la + (z + ld)) (+-comm lb lc)
         (cong-trans (la +_) (+-assoc lc lb ld)
         (sym-trans (+-assoc la lc (lb + ld))
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
  trans (*ₛ-distribˡ-+ⱽ c (f fzero) (sum (λ ix → f (fsuc ix))))
        (cong (c *ₛ f fzero +ⱽ_) (*ₛ-sum-distrib c (λ ix → f (fsuc ix))))

------------------------------------------------------------------------
-- Basis-collapse helper (does NOT mention linear-from-images; kept
-- OUTSIDE the opacity boundary so the sealed block can use it).
--
-- Sum collapses when one factor is a basis vector:
--   sum-F₂ (λ j → lookup (basis i) j · g j) ≡ g i
-- Uses `lookup (basis i) j = 𝟙 iff i ≡ j` (basis orthogonality).
------------------------------------------------------------------------

sum-F₂-basis-collapse :
  ∀ {k} (i : Fin k) (g : Fin k → F₂) →
  sum-F₂ (λ j → lookup (basis i) j · g j) ≡ g i
sum-F₂-basis-collapse {suc k} fzero g =
  cong-trans (_+ tail-sum) (·-identityˡ (g fzero))
  (cong-trans (g fzero +_) (zero-tail g)
         (+-identityʳ (g fzero)))
  where
    tail-sum : F₂
    tail-sum = sum-F₂ {k} (λ j' → lookup (𝟎ⱽ {k}) j' · g (fsuc j'))

    -- After basis fzero unfolds to 𝟙 ∷ 𝟎ⱽ, the suc-indexed summands
    -- become lookup 𝟎ⱽ j' · g (suc j') = 𝟘.
    zero-tail : ∀ {k} (g : Fin (suc k) → F₂) →
      sum-F₂ {k} (λ j' → lookup (𝟎ⱽ {k}) j' · g (fsuc j')) ≡ 𝟘
    zero-tail {zero}    _ = refl
    zero-tail {suc k'} g =
      cong-trans (_+ sum-F₂ {k'} (λ j' → lookup (𝟎ⱽ {k'}) j' · g (fsuc (fsuc j'))))
                 (·-absorbˡ (g (fsuc fzero)))
      (trans (+-identityˡ _)
             (zero-tail (λ ix → g (fsuc ix))))
sum-F₂-basis-collapse {suc k} (fsuc i) g =
  cong-trans (_+ sum-F₂ {k} (λ j → lookup (basis i) j · g (fsuc j)))
             (·-absorbˡ (g fzero))
  (trans (+-identityˡ _)
         (sum-F₂-basis-collapse i (λ ix → g (fsuc ix))))

------------------------------------------------------------------------
-- The main construction: linear-from-images, sealed behind `opaque`.
--
-- OPACITY BOUNDARY (memory architecture, the source-level generalization
-- of the Cycle7 fix): linear-from-images represents a dense F₂ linear
-- map as `apply v = sum (λ i → lookup v i *ₛ images i)`. If transparent,
-- any consumer that normalizes through `apply (linear-from-images f)` —
-- iterating it, composing it, raising it to a power — forces the dense
-- sum into normal form, which is super-exponential in the dimension
-- (this is exactly what made Cycle7 = cyclic-* {6} OOM the machine).
--
-- Sealing `apply` here fixes the WHOLE dense-linear-map family at the
-- source (fan-in 213): cyclic, Hodge ★, Fano, FreeLinearization, every
-- permutation-as-matrix. Consumers interact through the two proven
-- characterizing equations below (apply-...-lookup / -basis), NOT through
-- reduction — the prime is sealed; compounds reduce down to it and halt.
--
-- The two characterizing lemmas live INSIDE the block so their proofs
-- may unfold `linear-from-images` (opaque-block members unfold each
-- other); externally they are the equational interface.
------------------------------------------------------------------------

opaque
  linear-from-images : ∀ {k n} → (Fin k → Vector n) → Linear k n
  linear-from-images images = record
    { apply        = λ v → sum (λ i → lookup v i *ₛ images i)
    ; preserves-+  = λ u v →
        trans (sum-cong (λ i →
                cong-trans (_*ₛ images i) (lookup-+ⱽ u v i)
                           (*ₛ-distribʳ-+ (lookup u i) (lookup v i) (images i))))
              (sum-+ⱽ-distrib (λ i → lookup u i *ₛ images i)
                                (λ i → lookup v i *ₛ images i))
    ; preserves-*ₛ = λ c v →
        trans (sum-cong (λ i →
                cong-trans (_*ₛ images i) (lookup-*ₛ c v i)
                           (*ₛ-·-assoc c (lookup v i) (images i))))
              (sym (*ₛ-sum-distrib c (λ i → lookup v i *ₛ images i)))
    }

  -- Foundational apply-reduction (universal-property discipline): the
  -- canonical componentwise unfolding at output coordinate j. The
  -- per-instance work is bounded by k (number of basis-images), not 2^n.
  apply-linear-from-images-lookup :
    ∀ {k n} (f : Fin k → Vector n) (v : Vector k) (j : Fin n) →
    lookup (apply (linear-from-images f) v) j ≡
    sum-F₂ (λ i → lookup v i · lookup (f i) j)
  apply-linear-from-images-lookup f v j =
    trans (lookup-sum (λ i → lookup v i *ₛ f i) j)
          (sum-F₂-cong (λ i → lookup-*ₛ (lookup v i) (f i) j))

  -- Apply on basis: linear-from-images f does exactly what it claims at
  -- basis vectors. THE characterizing equation consumers use in place of
  -- reducing the dense sum.
  apply-linear-from-images-basis :
    ∀ {k n} (f : Fin k → Vector n) (i : Fin k) →
    apply (linear-from-images f) (basis i) ≡ f i
  apply-linear-from-images-basis f i = ≡-from-lookup _ _ goal
    where
      goal : (m : Fin _) →
             lookup (apply (linear-from-images f) (basis i)) m ≡ lookup (f i) m
      goal m = trans (apply-linear-from-images-lookup f (basis i) m)
                     (sum-F₂-basis-collapse i (λ j → lookup (f j) m))
