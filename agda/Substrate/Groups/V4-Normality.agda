------------------------------------------------------------------------
-- Substrate.Groups.V4-Normality
--
-- V_4 ⊳ S_4 — the V_4 image inside S_4 is a normal subgroup. This
-- closes the documented S8 gap from Substrate.Groups.V4-Embedding
-- (which states the normality signature but defers the proof).
--
-- Proof strategy: structural-predicate route.
--
--   1. Define `is-V₄-shape τ` = "(τ ∙ τ) ≈ ε ∧ (all-fixed τ ∨ no-fixed τ)".
--      A permutation of order ≤ 2 with either all 4 axes fixed or
--      none fixed. The 3 non-identity V_4 elements are double
--      transpositions (no fixed axes); the identity fixes all 4.
--
--   2. Show embed v satisfies is-V₄-shape (for each v ∈ V₄).
--
--   3. Show is-V₄-shape is conjugation-invariant: σ ∈ S_4 acting by
--      conjugation preserves the predicate.
--
--   4. Classify: any τ satisfying is-V₄-shape is in V₄-image. This
--      is the case-heavy step: enumerate τ.D ∈ {D,C,S,W}, derive
--      τ.C, τ.S, τ.W from bijection + τ² = ε + the fixed-shape
--      disjunct, and identify the matching V_4 element.
--
-- Then V₄-normal : ∀ σ v, V₄-image (σ ∙ embed v ∙ σ⁻¹) follows by
-- composing (2), (3), (4).
--
-- See: catalog/cocycles.md § CY-5 V_4 ⋊ S_3 ≅ S_4;
--      Substrate.Groups.V4-Embedding (S8) — the gap this closes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Normality where

open import Level using (0ℓ)
open import Data.Empty using (⊥; ⊥-elim)
open import Data.Product using (_×_; _,_; proj₁; proj₂; ∃; -,_)
open import Data.Sum using (_⊎_; inj₁; inj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; _≢_)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; ≈-refl; inv-l; inv-r)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; embed-hom; act-axis-involutive;
         V₄-image; embed-in-image)

------------------------------------------------------------------------
-- Axis distinctness — the 12 ordered ≢ lemmas.
------------------------------------------------------------------------

D≢C : D ≡ C → ⊥
D≢C ()
D≢S : D ≡ S → ⊥
D≢S ()
D≢W : D ≡ W → ⊥
D≢W ()
C≢D : C ≡ D → ⊥
C≢D ()
C≢S : C ≡ S → ⊥
C≢S ()
C≢W : C ≡ W → ⊥
C≢W ()
S≢D : S ≡ D → ⊥
S≢D ()
S≢C : S ≡ C → ⊥
S≢C ()
S≢W : S ≡ W → ⊥
S≢W ()
W≢D : W ≡ D → ⊥
W≢D ()
W≢C : W ≡ C → ⊥
W≢C ()
W≢S : W ≡ S → ⊥
W≢S ()

------------------------------------------------------------------------
-- σ-injective: every Permutation's apply is injective via inv-l.
------------------------------------------------------------------------

σ-injective :
  (σ : Permutation) (x y : Axis) →
  applyₛ σ x ≡ applyₛ σ y → x ≡ y
σ-injective σ x y eq =
  trans (sym (inv-l σ x))
        (trans (cong (invₐₛ σ) eq) (inv-l σ y))

------------------------------------------------------------------------
-- The structural predicates.
------------------------------------------------------------------------

-- All four axes are fixed by τ.
all-fixed : Permutation → Set
all-fixed τ = (applyₛ τ D ≡ D) × (applyₛ τ C ≡ C)
            × (applyₛ τ S ≡ S) × (applyₛ τ W ≡ W)

-- None of the four axes are fixed by τ.
no-fixed : Permutation → Set
no-fixed τ = (applyₛ τ D ≢ D) × (applyₛ τ C ≢ C)
           × (applyₛ τ S ≢ S) × (applyₛ τ W ≢ W)

-- The V_4-shape predicate: order ≤ 2 and (all-fixed or no-fixed).
is-V₄-shape : Permutation → Set
is-V₄-shape τ = ((τ · τ) ≈ ε) × (all-fixed τ ⊎ no-fixed τ)

------------------------------------------------------------------------
-- Step 1: embed v satisfies is-V₄-shape for every v ∈ V₄.
------------------------------------------------------------------------

-- (embed v · embed v) ≈ ε. By V_4 self-inverse + act-axis-involutive.
embed-self-inverse : (v : V₄) → (embed v · embed v) ≈ ε
embed-self-inverse v x = act-axis-involutive v x

-- e is all-fixed; α, β, γ are no-fixed.
embed-fixed-shape : (v : V₄) → all-fixed (embed v) ⊎ no-fixed (embed v)
embed-fixed-shape e = inj₁ (refl , refl , refl , refl)
-- α: D→C, C→D, S→W, W→S — each axis moved.
embed-fixed-shape α = inj₂ (C≢D , D≢C , W≢S , S≢W)
-- β: D→S, C→W, S→D, W→C.
embed-fixed-shape β = inj₂ (S≢D , W≢C , D≢S , C≢W)
-- γ: D→W, C→S, S→C, W→D.
embed-fixed-shape γ = inj₂ (W≢D , S≢C , C≢S , D≢W)

embed-is-V₄-shape : (v : V₄) → is-V₄-shape (embed v)
embed-is-V₄-shape v = embed-self-inverse v , embed-fixed-shape v

------------------------------------------------------------------------
-- Step 2: is-V₄-shape is conjugation-invariant.
------------------------------------------------------------------------

-- (σ τ σ⁻¹)² ≈ ε whenever τ² ≈ ε.
--   σ τ σ⁻¹ σ τ σ⁻¹ x = σ τ (σ⁻¹ σ) τ (σ⁻¹ x)
--                     = σ τ τ (σ⁻¹ x)
--                     = σ (σ⁻¹ x)
--                     = x
conj-preserves-order-2 :
  (σ τ : Permutation) → (τ · τ) ≈ ε →
  (((σ · τ) · (σ ⁻¹)) · ((σ · τ) · (σ ⁻¹))) ≈ ε
conj-preserves-order-2 σ τ τ² x =
  trans (cong (λ y → applyₛ σ (applyₛ τ y))
              (inv-l σ (applyₛ τ (invₐₛ σ x))))
        (trans (cong (applyₛ σ) (τ² (invₐₛ σ x)))
               (inv-r σ x))

-- all-fixed conjugation: if τ fixes everything, so does σ τ σ⁻¹.
--   (σ τ σ⁻¹) z = σ (τ (σ⁻¹ z)) = σ (σ⁻¹ z) = z.
all-fixed-conj :
  (σ τ : Permutation) → all-fixed τ → all-fixed ((σ · τ) · (σ ⁻¹))
all-fixed-conj σ τ (τD , τC , τS , τW) =
  fix D , fix C , fix S , fix W
  where
    τ-fixes-all : (y : Axis) → applyₛ τ y ≡ y
    τ-fixes-all D = τD
    τ-fixes-all C = τC
    τ-fixes-all S = τS
    τ-fixes-all W = τW

    fix : (z : Axis) → applyₛ ((σ · τ) · (σ ⁻¹)) z ≡ z
    fix z = trans (cong (applyₛ σ) (τ-fixes-all (invₐₛ σ z)))
                  (inv-r σ z)

-- no-fixed conjugation: if τ moves every axis, so does σ τ σ⁻¹.
--   Contrapositive: if (σ τ σ⁻¹) z = z, then τ (σ⁻¹ z) = σ⁻¹ z —
--   a fixed point of τ. But no-fixed τ rules this out.
no-fixed-conj :
  (σ τ : Permutation) → no-fixed τ → no-fixed ((σ · τ) · (σ ⁻¹))
no-fixed-conj σ τ ¬f =
  helper D , helper C , helper S , helper W
  where
    ¬τ-fix : (y : Axis) → applyₛ τ y ≢ y
    ¬τ-fix D = proj₁ ¬f
    ¬τ-fix C = proj₁ (proj₂ ¬f)
    ¬τ-fix S = proj₁ (proj₂ (proj₂ ¬f))
    ¬τ-fix W = proj₂ (proj₂ (proj₂ ¬f))

    helper : (z : Axis) → applyₛ ((σ · τ) · (σ ⁻¹)) z ≢ z
    helper z eq =
      ¬τ-fix (invₐₛ σ z)
        (trans (sym (inv-l σ (applyₛ τ (invₐₛ σ z))))
               (cong (invₐₛ σ) eq))

is-V₄-shape-conj :
  (σ τ : Permutation) → is-V₄-shape τ → is-V₄-shape ((σ · τ) · (σ ⁻¹))
is-V₄-shape-conj σ τ (τ² , inj₁ all-fix) =
  conj-preserves-order-2 σ τ τ² , inj₁ (all-fixed-conj σ τ all-fix)
is-V₄-shape-conj σ τ (τ² , inj₂ no-fix) =
  conj-preserves-order-2 σ τ τ² , inj₂ (no-fixed-conj σ τ no-fix)

------------------------------------------------------------------------
-- Step 3: classification — is-V₄-shape implies V₄-image.
--
-- Case analysis on τ.D ∈ {D, C, S, W}.
--   D: must be all-fixed (no-fixed would say τ.D ≢ D). Then τ ≈ ε.
--   X (X ∈ {C, S, W}): must be no-fixed. Then:
--     - τ.X = D (from τ² at D)
--     - Two remaining axes Y, Z (the complement {C,S,W} \ {X}):
--         τ.Y is forced — not Y (no-fixed.Y), not τ.D=X (bijection),
--         not τ.X=D (bijection); only option is the third axis Z.
--       So τ.Y = Z, τ.Z = Y (bijection).
------------------------------------------------------------------------

-- Case all-fixed: τ ≈ ε, so V₄-image with v = e.
case-all-fixed : (τ : Permutation) → all-fixed τ → V₄-image τ
case-all-fixed τ all-fix = e , match
  where
    match : (x : Axis) → applyₛ τ x ≡ applyₛ (embed e) x
    match D = proj₁ all-fix
    match C = proj₁ (proj₂ all-fix)
    match S = proj₁ (proj₂ (proj₂ all-fix))
    match W = proj₂ (proj₂ (proj₂ all-fix))

-- Consolidated no-fix case: τ in the no-fixed branch with τ.D = target
-- (target ≢ D) ⇒ τ is the V₄ element that swaps (D, target) and swaps
-- the remaining two non-D axes.
--
-- This was three case-{C,S,W}-no-fix lemmas (orbit detected by
-- `scratch/findings.py`); consolidated into one function with
-- target-dispatch. The dispatcher passes the target ≢ D witness
-- explicitly (using the axis-distinctness lemmas).
--
-- Takes the three relevant inequalities (τ.C ≢ C, τ.S ≢ S, τ.W ≢ W)
-- directly rather than the bundled `no-fixed τ`. This avoids the
-- `with...in` substitution that would rewrite `applyₛ τ D` inside the
-- bundle's type when the dispatcher discriminates on it.
case-D-no-fix :
  (τ : Permutation) → (τ · τ) ≈ ε →
  (target : Axis) → target ≢ D →
  applyₛ τ D ≡ target →
  applyₛ τ C ≢ C →
  applyₛ τ S ≢ S →
  applyₛ τ W ≢ W →
  V₄-image τ
case-D-no-fix τ τ² D D≢D _ _ _ _ = ⊥-elim (D≢D refl)
case-D-no-fix τ τ² C _ τD≡C τC≢ τS≢ τW≢ = α , α-matches
  where
    τC≡D : applyₛ τ C ≡ D
    τC≡D = trans (sym (cong (applyₛ τ) τD≡C)) (τ² D)

    τS≡W : applyₛ τ S ≡ W
    τS≡W with applyₛ τ S in pS
    ... | D = ⊥-elim (S≢C (σ-injective τ S C (trans pS (sym τC≡D))))
    ... | C = ⊥-elim (S≢D (σ-injective τ S D (trans pS (sym τD≡C))))
    ... | S = ⊥-elim (τS≢ refl)
    ... | W = refl

    τW≡S : applyₛ τ W ≡ S
    τW≡S with applyₛ τ W in pW
    ... | D = ⊥-elim (W≢C (σ-injective τ W C (trans pW (sym τC≡D))))
    ... | C = ⊥-elim (W≢D (σ-injective τ W D (trans pW (sym τD≡C))))
    ... | S = refl
    ... | W = ⊥-elim (τW≢ refl)

    α-matches : (x : Axis) → applyₛ τ x ≡ applyₛ (embed α) x
    α-matches D = τD≡C
    α-matches C = τC≡D
    α-matches S = τS≡W
    α-matches W = τW≡S
case-D-no-fix τ τ² S _ τD≡S τC≢ τS≢ τW≢ = β , β-matches
  where
    τS≡D : applyₛ τ S ≡ D
    τS≡D = trans (sym (cong (applyₛ τ) τD≡S)) (τ² D)

    τC≡W : applyₛ τ C ≡ W
    τC≡W with applyₛ τ C in pC
    ... | D = ⊥-elim (C≢S (σ-injective τ C S (trans pC (sym τS≡D))))
    ... | C = ⊥-elim (τC≢ refl)
    ... | S = ⊥-elim (C≢D (σ-injective τ C D (trans pC (sym τD≡S))))
    ... | W = refl

    τW≡C : applyₛ τ W ≡ C
    τW≡C with applyₛ τ W in pW
    ... | D = ⊥-elim (W≢S (σ-injective τ W S (trans pW (sym τS≡D))))
    ... | C = refl
    ... | S = ⊥-elim (W≢D (σ-injective τ W D (trans pW (sym τD≡S))))
    ... | W = ⊥-elim (τW≢ refl)

    β-matches : (x : Axis) → applyₛ τ x ≡ applyₛ (embed β) x
    β-matches D = τD≡S
    β-matches C = τC≡W
    β-matches S = τS≡D
    β-matches W = τW≡C
case-D-no-fix τ τ² W _ τD≡W τC≢ τS≢ τW≢ = γ , γ-matches
  where
    τW≡D : applyₛ τ W ≡ D
    τW≡D = trans (sym (cong (applyₛ τ) τD≡W)) (τ² D)

    τC≡S : applyₛ τ C ≡ S
    τC≡S with applyₛ τ C in pC
    ... | D = ⊥-elim (C≢W (σ-injective τ C W (trans pC (sym τW≡D))))
    ... | C = ⊥-elim (τC≢ refl)
    ... | S = refl
    ... | W = ⊥-elim (C≢D (σ-injective τ C D (trans pC (sym τD≡W))))

    τS≡C : applyₛ τ S ≡ C
    τS≡C with applyₛ τ S in pS
    ... | D = ⊥-elim (S≢W (σ-injective τ S W (trans pS (sym τW≡D))))
    ... | C = refl
    ... | S = ⊥-elim (τS≢ refl)
    ... | W = ⊥-elim (S≢D (σ-injective τ S D (trans pS (sym τD≡W))))

    γ-matches : (x : Axis) → applyₛ τ x ≡ applyₛ (embed γ) x
    γ-matches D = τD≡W
    γ-matches C = τC≡S
    γ-matches S = τS≡C
    γ-matches W = τW≡D

-- Putting the classification together. The all-fixed branch dispatches
-- directly; the no-fixed branch case-analyses on τ.D and passes the
-- three "axes ≠ self" inequalities (whose types don't mention τ.D, so
-- they survive the `with...in` substitution).
is-V₄-shape-classifies :
  (τ : Permutation) → is-V₄-shape τ → V₄-image τ
is-V₄-shape-classifies τ (_ , inj₁ all-fix) = case-all-fixed τ all-fix
is-V₄-shape-classifies τ (τ² , inj₂ no-fix)
  with applyₛ τ D in τD-eq
... | D = ⊥-elim (proj₁ no-fix refl)
... | C = case-D-no-fix τ τ² C (λ ()) τD-eq
            (proj₁ (proj₂ no-fix))
            (proj₁ (proj₂ (proj₂ no-fix)))
            (proj₂ (proj₂ (proj₂ no-fix)))
... | S = case-D-no-fix τ τ² S (λ ()) τD-eq
            (proj₁ (proj₂ no-fix))
            (proj₁ (proj₂ (proj₂ no-fix)))
            (proj₂ (proj₂ (proj₂ no-fix)))
... | W = case-D-no-fix τ τ² W (λ ()) τD-eq
            (proj₁ (proj₂ no-fix))
            (proj₁ (proj₂ (proj₂ no-fix)))
            (proj₂ (proj₂ (proj₂ no-fix)))

------------------------------------------------------------------------
-- V_4 ⊳ S_4 — the load-bearing theorem.
------------------------------------------------------------------------

V₄-normal :
  (σ : Permutation) (v : V₄) → V₄-image ((σ · embed v) · (σ ⁻¹))
V₄-normal σ v =
  is-V₄-shape-classifies ((σ · embed v) · (σ ⁻¹))
                         (is-V₄-shape-conj σ (embed v)
                                           (embed-is-V₄-shape v))

------------------------------------------------------------------------
-- Notes
--
-- 1. The structural-predicate approach makes the proof modular:
--    embed-is-V₄-shape (step 1, mechanical) + is-V₄-shape-conj (step 2,
--    one-line proofs per axiom) + is-V₄-shape-classifies (step 3,
--    case-heavy enumeration on τ.D) compose to give V₄-normal.
--
-- 2. The case-analysis on τ.D (step 3) requires 16 sub-cases (4
--    main cases × 4 each for the bijection-forced positions of τ on
--    the other axes). Each is a `with ... in` pattern on `applyₛ τ
--    (some axis)`. The cases are exhausted by injectivity (σ-injective)
--    + no-fixed contradictions; no V_4 element is enumerated
--    incorrectly.
--
-- 3. Compared to the alternative "explicit pair-V₄ conjugation
--    formula" approach: the structural predicate route trades
--    formula-enumeration (4 × 4 = 16 pointwise verifications, each
--    requiring case analysis on σ⁻¹ z) for a structural classifier
--    (3 non-trivial cases, each with 8 sub-cases via bijection). The
--    case counts are similar; the structural route generalises better
--    (any τ satisfying the predicate is in V_4-image, not just
--    conjugates of V_4 elements).
--
-- 4. With normality established, the quotient S_4 / V_4 ≅ S_3 becomes
--    a downstream theorem; deferred to a follow-on slice.
------------------------------------------------------------------------
