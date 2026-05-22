------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.Bilinearity
--
-- Bilinearity of the generic `bilinear-form-of M`. Proves additivity
-- and scalar-respect in EACH argument:
--
--   bilinear-form-of M (u +ⱽ v) w ≡ bf u w + bf v w   (left-additive)
--   bilinear-form-of M u (v +ⱽ w) ≡ bf u v + bf u w   (right-additive)
--   bilinear-form-of M (c *ₛ v) w ≡ c · bf v w         (left-scalar)
--   bilinear-form-of M v (c *ₛ w) ≡ c · bf v w         (right-scalar)
--
-- These are the foundational structural facts unblocking the
-- congruence chain at any n:
--
--   * `is-symmetric-congruence-act` — congruence-act preserves
--     symmetry (left/right additivity + scalar-respect lets us
--     swap argument order under symmetric M).
--
--   * `congruence-compose` — `congruence-act (T₁ ∘L T₂) M ≡
--     congruence-act T₂ (congruence-act T₁ M)`. Combined with
--     FixedPoint-of-compose from `Substrate.Category.Coalgebra`
--     primitive #1, automates the StabiliserClosure cascade at
--     ANY n.
--
--   * `metric-id-non-degenerate` at any n — the kernel-free witness
--     follows from bilinearity + basis decomposition.
--
-- Per `feedback_categorical_name_first`: bilinearity is the universal
-- property of bilinear forms — proven once, used everywhere downstream
-- as the inference rule, not re-derived per-instance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.Bilinearity where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm; bilinear-form-of)

------------------------------------------------------------------------
-- N-1: Helper sum-F₂ properties.
--
-- sum-F₂ distributes over pointwise + and respects scalar
-- multiplication. Both proved by induction on n.
------------------------------------------------------------------------

-- (a + b) + (c + d) ≡ (a + c) + (b + d). Used in sum-F₂-+-distribute.
+-rearrange : (a b c d : F₂) → (a + b) + (c + d) ≡ (a + c) + (b + d)
+-rearrange a b c d =
  trans (+-assoc a b (c + d))
  (trans (cong (a +_) (sym (+-assoc b c d)))
  (trans (cong (a +_) (cong (_+ d) (+-comm b c)))
  (trans (cong (a +_) (+-assoc c b d))
         (sym (+-assoc a c (b + d))))))

-- sum-F₂ distributes pointwise + into a sum of sums.
sum-F₂-+-distribute :
  ∀ {n} (f g : Fin n → F₂) →
  sum-F₂ (λ i → f i + g i) ≡ sum-F₂ f + sum-F₂ g
sum-F₂-+-distribute {zero}  f g = refl
sum-F₂-+-distribute {suc _} f g =
  trans (cong ((f zero + g zero) +_)
              (sum-F₂-+-distribute (f ∘ suc) (g ∘ suc)))
        (+-rearrange (f zero) (g zero) (sum-F₂ (f ∘ suc)) (sum-F₂ (g ∘ suc)))

-- sum-F₂ pulls a left-scalar out of each summand.
sum-F₂-scalar :
  ∀ {n} (c : F₂) (f : Fin n → F₂) →
  sum-F₂ (λ i → c · f i) ≡ c · sum-F₂ f
sum-F₂-scalar {zero}  c f = sym (·-absorbʳ c)
sum-F₂-scalar {suc _} c f =
  trans (cong (c · f zero +_) (sum-F₂-scalar c (f ∘ suc)))
        (sym (·-distribˡ-+ c (f zero) (sum-F₂ (f ∘ suc))))

------------------------------------------------------------------------
-- N-2: Right-additivity — bilinear-form-of M v (a +ⱽ b) is additive
-- in the right argument.
--
-- Chain of equalities:
--   bf M v (a +ⱽ b)
-- = sum-F₂ (λ i → v_i · sum-F₂ (λ j → M(i,j) · (a +ⱽ b)_j))    [definition]
-- = sum-F₂ (λ i → v_i · sum-F₂ (λ j → M(i,j) · (a_j + b_j)))   [lookup-+ⱽ]
-- = sum-F₂ (λ i → v_i · sum-F₂ (λ j → M(i,j)·a_j + M(i,j)·b_j)) [·-distribˡ-+]
-- = sum-F₂ (λ i → v_i · (sum-F₂ (j → M(i,j)·a_j) + sum-F₂ (j → M(i,j)·b_j)))
--                                                              [sum-F₂-+-distribute]
-- = sum-F₂ (λ i → v_i·sum-F₂(j→M(i,j)·a_j) + v_i·sum-F₂(j→M(i,j)·b_j))
--                                                              [·-distribˡ-+]
-- = sum-F₂ (...) + sum-F₂ (...)                                [sum-F₂-+-distribute]
-- = bf M v a + bf M v b
------------------------------------------------------------------------

bilinear-form-of-+ⱽ-right :
  ∀ {n} (M : BilinForm n) (v a b : Vector n) →
  bilinear-form-of M v (a +ⱽ b)
    ≡ bilinear-form-of M v a + bilinear-form-of M v b
bilinear-form-of-+ⱽ-right {n} M v a b =
  trans
    -- Push lookup-+ⱽ inside inner sum.
    (sum-F₂-cong {n} (λ i →
      cong (lookup v i ·_)
           (sum-F₂-cong {n} (λ j →
             trans (cong (M i j ·_) (lookup-+ⱽ a b j))
                   (·-distribˡ-+ (M i j) (lookup a j) (lookup b j))))))
  (trans
    -- Distribute inner sum across +.
    (sum-F₂-cong {n} (λ i →
      cong (lookup v i ·_)
           (sum-F₂-+-distribute (λ j → M i j · lookup a j)
                                (λ j → M i j · lookup b j))))
  (trans
    -- Pull v_i across the inner +.
    (sum-F₂-cong {n} (λ i →
      ·-distribˡ-+ (lookup v i)
                   (sum-F₂ (λ j → M i j · lookup a j))
                   (sum-F₂ (λ j → M i j · lookup b j))))
    -- Distribute outer sum across +.
    (sum-F₂-+-distribute
      (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup a j))
      (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup b j)))))

------------------------------------------------------------------------
-- N-3: Left-additivity — bilinear-form-of M (u +ⱽ v) w is additive
-- in the left argument.
--
--   bf M (u +ⱽ v) w
-- = sum-F₂ (λ i → (u +ⱽ v)_i · sum-F₂ (λ j → M(i,j)·w_j))     [definition]
-- = sum-F₂ (λ i → (u_i + v_i) · sum-F₂ (λ j → M(i,j)·w_j))    [lookup-+ⱽ]
-- = sum-F₂ (λ i → u_i·sum-F₂(...) + v_i·sum-F₂(...))           [·-distribʳ-+]
-- = sum-F₂(λ i → u_i·sum-F₂(...)) + sum-F₂(λ i → v_i·sum-F₂(...))
--                                                              [sum-F₂-+-distribute]
-- = bf M u w + bf M v w
------------------------------------------------------------------------

bilinear-form-of-+ⱽ-left :
  ∀ {n} (M : BilinForm n) (u v w : Vector n) →
  bilinear-form-of M (u +ⱽ v) w
    ≡ bilinear-form-of M u w + bilinear-form-of M v w
bilinear-form-of-+ⱽ-left {n} M u v w =
  trans
    -- Push lookup-+ⱽ inside outer factor, distribute over +.
    (sum-F₂-cong {n} (λ i →
      trans (cong (_· sum-F₂ (λ j → M i j · lookup w j))
                  (lookup-+ⱽ u v i))
            (·-distribʳ-+ (sum-F₂ (λ j → M i j · lookup w j))
                          (lookup u i) (lookup v i))))
    -- Distribute outer sum across +.
    (sum-F₂-+-distribute
      (λ i → lookup u i · sum-F₂ (λ j → M i j · lookup w j))
      (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup w j)))

------------------------------------------------------------------------
-- N-4: Left-scalar-respect — bilinear-form-of M (c *ₛ v) w respects
-- scalar multiplication on the left.
--
--   bf M (c *ₛ v) w
-- = sum-F₂ (λ i → (c *ₛ v)_i · sum-F₂ (λ j → M(i,j)·w_j))     [definition]
-- = sum-F₂ (λ i → (c · v_i) · sum-F₂ (...))                    [lookup-*ₛ]
-- = sum-F₂ (λ i → c · (v_i · sum-F₂ (...)))                    [·-assoc]
-- = c · sum-F₂ (λ i → v_i · sum-F₂ (...))                      [sum-F₂-scalar]
-- = c · bf M v w
------------------------------------------------------------------------

bilinear-form-of-*ₛ-left :
  ∀ {n} (M : BilinForm n) (c : F₂) (v w : Vector n) →
  bilinear-form-of M (c *ₛ v) w ≡ c · bilinear-form-of M v w
bilinear-form-of-*ₛ-left {n} M c v w =
  trans
    (sum-F₂-cong {n} (λ i →
      trans (cong (_· sum-F₂ (λ j → M i j · lookup w j))
                  (lookup-*ₛ c v i))
            (·-assoc c (lookup v i)
                       (sum-F₂ (λ j → M i j · lookup w j)))))
    (sum-F₂-scalar c
      (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup w j)))

------------------------------------------------------------------------
-- N-5: Right-scalar-respect — bilinear-form-of M v (c *ₛ w) respects
-- scalar multiplication on the right.
--
--   bf M v (c *ₛ w)
-- = sum-F₂ (λ i → v_i · sum-F₂ (λ j → M(i,j) · (c · w_j)))      [lookup-*ₛ]
-- = sum-F₂ (λ i → v_i · sum-F₂ (λ j → c · (M(i,j) · w_j)))      [·-assoc + ·-comm]
-- = sum-F₂ (λ i → v_i · (c · sum-F₂ (λ j → M(i,j) · w_j)))      [sum-F₂-scalar]
-- = sum-F₂ (λ i → c · (v_i · sum-F₂ (...)))                      [·-assoc + ·-comm]
-- = c · bf M v w                                                  [sum-F₂-scalar]
------------------------------------------------------------------------

-- M(i,j) · (c · w_j) ≡ c · (M(i,j) · w_j). Helper: shuffle c through.
shuffle-scalar : (a c b : F₂) → a · (c · b) ≡ c · (a · b)
shuffle-scalar a c b =
  trans (sym (·-assoc a c b))
  (trans (cong (_· b) (·-comm a c))
         (·-assoc c a b))

bilinear-form-of-*ₛ-right :
  ∀ {n} (M : BilinForm n) (c : F₂) (v w : Vector n) →
  bilinear-form-of M v (c *ₛ w) ≡ c · bilinear-form-of M v w
bilinear-form-of-*ₛ-right {n} M c v w =
  trans
    -- Push lookup-*ₛ inside innermost, shuffle scalar out of M(i,j)·(c·w_j).
    (sum-F₂-cong {n} (λ i →
      cong (lookup v i ·_)
           (sum-F₂-cong {n} (λ j →
             trans (cong (M i j ·_) (lookup-*ₛ c w j))
                   (shuffle-scalar (M i j) c (lookup w j))))))
  (trans
    -- Pull c out of inner sum.
    (sum-F₂-cong {n} (λ i →
      cong (lookup v i ·_)
           (sum-F₂-scalar c (λ j → M i j · lookup w j))))
  (trans
    -- Shuffle: v_i · (c · ⋯) ≡ c · (v_i · ⋯).
    (sum-F₂-cong {n} (λ i →
      shuffle-scalar (lookup v i) c
                     (sum-F₂ (λ j → M i j · lookup w j))))
    -- Pull c out of outer sum.
    (sum-F₂-scalar c
      (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup w j)))))

------------------------------------------------------------------------
-- N-6: Capstone — bilinearity at any n.
--
-- The four lemmas above establish that `bilinear-form-of M` is a
-- genuine bilinear form for any M : BilinForm n at any n. These are
-- the foundational structural facts unblocking:
--
--   * `is-symmetric-congruence-act` (follow-on): symmetry preservation
--     under T^T M T derives from left/right additivity + scalar-
--     respect + the symmetry of M.
--
--   * `congruence-compose` (follow-on): the GL(n, F₂) action's
--     composition law. With FixedPoint-of-compose (primitive #1's
--     derived rule), automates the StabiliserClosure cascade at any
--     n — the 6-element S₃ stabiliser of metric-id at dim 3 derives
--     from the 2 Coxeter generators' fixed-point witnesses alone.
--
--   * `metric-id-non-degenerate-generic` (follow-on): the kernel-free
--     witness via pair-with-each-basis-vector follows from bilinearity
--     + basis decomposition. Both NonDegenerate (dim-3) and
--     NonDegenerate-4 (existing) become specializations.
--
-- Per `feedback_universal_property_discipline`: bilinearity is THE
-- universal property of bilinear forms — proven once, used as the
-- inference rule wherever a bilinear-form-of expression is being
-- manipulated. The substrate's per-dim recomputations (NonDegenerate-4's
-- pair-metric-id-4-with-eᵢ, the StabiliserClosure proofs) reduce to
-- one-step bilinearity invocations once retrofitted.
------------------------------------------------------------------------
