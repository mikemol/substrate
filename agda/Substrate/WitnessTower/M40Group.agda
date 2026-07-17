------------------------------------------------------------------------
-- Σ-SEAM-GLUE / ΞB2ii — the closure is SPECIFICALLY A₄×ℤ₂.
--
-- Two deliverables:
--  (1) GROUNDING: bundle A4Z2 (the realized closure) as a Substrate.Algebra.Group
--      instance — compose-assoc, identity ι, inverses. This discharges the
--      categorical-grounding FLOATING advisory on M40Closure (it now IS a
--      structure-instance, not hand-rolled laws) and makes "A4Z2 is a group"
--      rigorous rather than asserted.
--  (2) "SPECIFICALLY A₄": the Z₃ action in the compose law (σ z1 = rotate) is the
--      A₄ action — an order-3 V₄-AUTOMORPHISM that 3-CYCLES the three involutions
--      α→β→γ→α (identity fixed). This is what makes the order-12 part A₄ = V₄⋊Z₃
--      and NOT the abelian V₄×Z₃ (whose action would be trivial). v3's guard:
--      direct-factor-centrality alone gives only G×ℤ₂; the nontrivial 3-cycle
--      action is the (ii) that lands A₄ specifically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Group where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ; _·_)
open import Substrate.Groups.V4.Axioms using (·-assoc; ε-left; ε-identity)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom using (rotate-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (_×_; _,_; proj₂)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.WitnessTower.M40Closure
  using (Chir; even; odd; _*c_; Z3; z0; z1; z2; _+₃_; +₃-idʳ; σ; σ-fixes-e;
         A4Z2; mk; compose; a4z2-≡; ι; *c-sq; ·-sq)
open A4Z2
open import Substrate.WitnessTower.M40Action using (cinv)
open import Substrate.WitnessTower.M40Iso using (sigma-cinv)

ε-right : (x : V₄) → (x · e) ≡ x
ε-right = proj₂ ε-identity

------------------------------------------------------------------------
-- ℤ₂ / ℤ₃ arithmetic facts needed for the group laws.
------------------------------------------------------------------------

*c-assoc : (s t u : Chir) → (s *c t) *c u ≡ s *c (t *c u)
*c-assoc even t u = refl
*c-assoc odd even u = refl
*c-assoc odd odd even = refl
*c-assoc odd odd odd  = refl

*c-right-id : (s : Chir) → s *c even ≡ s
*c-right-id even = refl
*c-right-id odd  = refl

+₃-assoc : (i j k : Z3) → (i +₃ j) +₃ k ≡ i +₃ (j +₃ k)
+₃-assoc z0 j k = refl
+₃-assoc z1 z0 z0 = refl
+₃-assoc z1 z0 z1 = refl
+₃-assoc z1 z0 z2 = refl
+₃-assoc z1 z1 z0 = refl
+₃-assoc z1 z1 z1 = refl
+₃-assoc z1 z1 z2 = refl
+₃-assoc z1 z2 z0 = refl
+₃-assoc z1 z2 z1 = refl
+₃-assoc z1 z2 z2 = refl
+₃-assoc z2 z0 z0 = refl
+₃-assoc z2 z0 z1 = refl
+₃-assoc z2 z0 z2 = refl
+₃-assoc z2 z1 z0 = refl
+₃-assoc z2 z1 z1 = refl
+₃-assoc z2 z1 z2 = refl
+₃-assoc z2 z2 z0 = refl
+₃-assoc z2 z2 z1 = refl
+₃-assoc z2 z2 z2 = refl

+₃-comm : (i j : Z3) → i +₃ j ≡ j +₃ i
+₃-comm z0 z0 = refl
+₃-comm z0 z1 = refl
+₃-comm z0 z2 = refl
+₃-comm z1 z0 = refl
+₃-comm z1 z1 = refl
+₃-comm z1 z2 = refl
+₃-comm z2 z0 = refl
+₃-comm z2 z1 = refl
+₃-comm z2 z2 = refl

-- σ (the forward cycle power) is a V₄-homomorphism, and σ-iterates add.
σ-hom : (j : Z3) (a b : V₄) → σ j (a · b) ≡ σ j a · σ j b
σ-hom z0 a b = refl
σ-hom z1 a b = rotate-IsHom a b
σ-hom z2 a b = trans (cong rotate (rotate-IsHom a b)) (rotate-IsHom (rotate a) (rotate b))

σ-add : (i j : Z3) (a : V₄) → σ j (σ i a) ≡ σ (i +₃ j) a
σ-add z0 z0 a = refl
σ-add z0 z1 a = refl
σ-add z0 z2 a = refl
σ-add z1 z0 a = refl
σ-add z1 z1 a = refl
σ-add z1 z2 a = rotate³-id a
σ-add z2 z0 a = refl
σ-add z2 z1 a = rotate³-id a
σ-add z2 z2 a = rotate³-id (rotate a)

------------------------------------------------------------------------
-- (1) GROUP LAWS for compose.
------------------------------------------------------------------------

ι-left : (g : A4Z2) → compose ι g ≡ g
ι-left g = a4z2-≡ refl (ε-left (mask g)) refl

ι-right : (g : A4Z2) → compose g ι ≡ g
ι-right g = a4z2-≡ (*c-right-id (chir g))
                   (trans (cong (mask g ·_) (σ-fixes-e (zee g))) (ε-right (mask g)))
                   (+₃-idʳ (zee g))

compose-assoc : (g h k : A4Z2) → compose (compose g h) k ≡ compose g (compose h k)
compose-assoc g h k =
  a4z2-≡ (*c-assoc (chir g) (chir h) (chir k)) mask-eq (+₃-assoc (zee g) (zee h) (zee k))
  where
    mg mh mk2 : V₄
    mg = mask g ; mh = mask h ; mk2 = mask k
    jg jh : Z3
    jg = zee g ; jh = zee h
    rhs-chain : mg · σ jg (mh · σ jh mk2) ≡ mg · (σ jg mh · σ (jg +₃ jh) mk2)
    rhs-chain =
      trans (cong (mg ·_) (σ-hom jg mh (σ jh mk2)))
      (trans (cong (λ x → mg · (σ jg mh · x)) (σ-add jh jg mk2))
             (cong (λ z → mg · (σ jg mh · σ z mk2)) (+₃-comm jh jg)))
    mask-eq : (mg · σ jg mh) · σ (jg +₃ jh) mk2 ≡ mg · σ jg (mh · σ jh mk2)
    mask-eq = trans (·-assoc mg (σ jg mh) (σ (jg +₃ jh) mk2)) (sym rhs-chain)

------------------------------------------------------------------------
-- Inverse: (s,m,j)⁻¹ = (s, c⁻ʲ m, −j).
------------------------------------------------------------------------

negZ3 : Z3 → Z3
negZ3 z0 = z0
negZ3 z1 = z2
negZ3 z2 = z1

negZ3-left : (j : Z3) → (negZ3 j) +₃ j ≡ z0
negZ3-left z0 = refl
negZ3-left z1 = refl
negZ3-left z2 = refl

negZ3-right : (j : Z3) → j +₃ (negZ3 j) ≡ z0
negZ3-right z0 = refl
negZ3-right z1 = refl
negZ3-right z2 = refl

-- σ at the negated index IS c⁻ (the inverse cycle): σ (−j) ≡ cinv j.
σ-negZ3 : (j : Z3) (a : V₄) → σ (negZ3 j) a ≡ cinv j a
σ-negZ3 z0 a = refl
σ-negZ3 z1 a = refl
σ-negZ3 z2 a = refl

invA : A4Z2 → A4Z2
invA g = mk (chir g) (cinv (zee g) (mask g)) (negZ3 (zee g))

inv-leftA : (g : A4Z2) → compose (invA g) g ≡ ι
inv-leftA g =
  a4z2-≡ (*c-sq (chir g))
         (trans (cong (cinv (zee g) (mask g) ·_) (σ-negZ3 (zee g) (mask g)))
                (·-sq (cinv (zee g) (mask g))))
         (negZ3-left (zee g))

inv-rightA : (g : A4Z2) → compose g (invA g) ≡ ι
inv-rightA g =
  a4z2-≡ (*c-sq (chir g))
         (trans (cong (mask g ·_) (sigma-cinv (zee g) (mask g)))
                (·-sq (mask g)))
         (negZ3-right (zee g))

------------------------------------------------------------------------
-- A4Z2 bundled as a Substrate.Algebra.Group  (the grounding).
------------------------------------------------------------------------

A4Z2-Magma : Magma A4Z2
A4Z2-Magma = record { _·_ = compose }

A4Z2-Semigroup : Semigroup A4Z2
A4Z2-Semigroup = record { magma = A4Z2-Magma ; ·-assoc = compose-assoc }

A4Z2-Monoid : Monoid A4Z2
A4Z2-Monoid = record { semigroup = A4Z2-Semigroup ; ε = ι ; ε-left = ι-left ; ε-right = ι-right }

A4Z2-Group : Group A4Z2
A4Z2-Group = record { monoid = A4Z2-Monoid ; inv = invA ; inv-left = inv-leftA ; inv-right = inv-rightA }

------------------------------------------------------------------------
-- (1½) ONTO THE CATEGORICAL SPINE — the Algebra→Category bridge (deloop).
-- A4Z2-Monoid is a Monoid, so its ONE-OBJECT delooping `𝐁(A₄×ℤ₂)` is a
-- CategoryOf: the closure reaches the categorical spine (not merely the
-- PARALLEL Algebra hierarchy), discharging the categorical-grounding advisory's
-- GROUNDS-IN-ALGEBRA flag the "right" way — a typechecked bridge, not a note.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)

A4Z2-Category : CategoryOf ⊤ (λ _ _ → A4Z2)
A4Z2-Category = deloop A4Z2-Monoid

------------------------------------------------------------------------
-- (2) "SPECIFICALLY A₄": the Z₃ action (σ z1 = rotate) is the A₄ action.
------------------------------------------------------------------------

-- an automorphism of V₄ ...
A4-action-automorphism : (a b : V₄) → σ z1 (a · b) ≡ σ z1 a · σ z1 b
A4-action-automorphism = rotate-IsHom

-- ... of order 3 ...
A4-action-order3 : (a : V₄) → σ z1 (σ z1 (σ z1 a)) ≡ a
A4-action-order3 = rotate³-id

-- ... that 3-cycles the three involutions α→β→γ→α (and fixes the identity).
-- The nontrivial 3-cycle (α ↦ β, not α ↦ α) is exactly what makes the order-12
-- part A₄ = V₄⋊Z₃ rather than the abelian V₄×Z₃.
A4-action-3cycle : (σ z1 α ≡ β) × ((σ z1 β ≡ γ) × (σ z1 γ ≡ α))
A4-action-3cycle = refl , refl , refl

A4-action-fixes-id : σ z1 e ≡ e
A4-action-fixes-id = refl
