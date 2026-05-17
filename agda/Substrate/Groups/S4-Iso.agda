------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso
--
-- The iso S4-Composed.Carrier ↔ Permutation Axis, bridging the
-- compositional construction (V₄ ⋊ S₃ via the Coxeter framework) and
-- the permutation-based representation (Sym(Axis)).
--
-- DBE plan:
--   Shadows (this file):
--     embed-S₃          : S₃.Carrier → Permutation Axis
--                         (S₃ acting on Axis via Axis ↔ V₄ ∘ φ.act)
--     compositional-to-perm : S4-Composed.Carrier → Permutation Axis
--                             ((v, s) ↦ embed v · embed-S₃ s)
--     perm-to-compositional : Permutation Axis → S4-Composed.Carrier
--                             (via existing factorization in SemidirectProduct.agda)
--     round-trips        : forward ∘ backward ≈ id and back
--     hom proofs         : forward is a Group homomorphism
--
--   Composition: G1 (forward) + G2 (backward) + G3 (round-trips)
--                ⊢ iso. Add G4 (hom) ⊢ group iso.
--
--   Entail: iso transports structural facts (e.g., V₄ ⊳ S₄ by
--           construction in S4-Composed) to the Permutation side.
--           V₄-normal in V4-Normality is already proven; this gives
--           an alternative structural proof for documentation.
--
-- Start: G1 (embed-S₃ and compositional-to-perm).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso where

open import Substrate.Axes using (Axis; D; C; S; W; act-axis;
                                   v-of-axis; axis-of-v;
                                   axis-of-v-v-of-axis; v-of-axis-axis-of-v)
import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Groups.V4-Embedding using (embed; act-axis-∙; act-axis-involutive)
open import Substrate.Groups.S4 as S4 using (Permutation; _·_; ε; _⁻¹;
                                              _≈_; ≈-refl; ≈-sym; ≈-trans;
                                              ·-assoc; ·-cong; ε-left; ε-right;
                                              inv-left; inv-right)
open Permutation
open import Data.Product using (_,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong)

------------------------------------------------------------------------
-- 1. embed-S₃: S₃ acting on Axis via the Axis ↔ V₄ bijection.
--
-- Composition: x → v-of-axis → φ.act s → axis-of-v.
-- inverse: x → v-of-axis → φ.act (s⁻¹) → axis-of-v.
------------------------------------------------------------------------

private
  s3-apply : S₃.Carrier → Axis → Axis
  s3-apply s x = axis-of-v (φ.act s (v-of-axis x))

  s3-inv-apply : S₃.Carrier → Axis → Axis
  s3-inv-apply s x = axis-of-v (φ.act (s S₃.⁻¹) (v-of-axis x))

  -- Helper: φ.act-cong specialised to v-eq = refl. Makes the v₁, v₂
  -- implicits explicit, avoiding the normalize-unification block.
  φ-cong-v : (s₁ s₂ : S₃.Carrier) (v : V₄) → s₁ S₃.≈ s₂ →
             φ.act s₁ v ≡ φ.act s₂ v
  φ-cong-v s₁ s₂ v eq = φ.act-cong {s₁ = s₁} {s₂ = s₂} {v₁ = v} {v₂ = v} eq refl

  -- s3-apply s ∘ s3-inv-apply s = id (inv-r for embed-S₃).
  s3-apply-inv-r : (s : S₃.Carrier) (x : Axis) →
                   s3-apply s (s3-inv-apply s x) ≡ x
  s3-apply-inv-r s x =
    -- s3-apply s (s3-inv-apply s x)
    --   = axis-of-v (φ.act s (v-of-axis (axis-of-v (φ.act (s ⁻¹) (v-of-axis x)))))
    --   = axis-of-v (φ.act s (φ.act (s ⁻¹) (v-of-axis x)))      [v-of-axis-axis-of-v]
    --   ≡ axis-of-v (φ.act (s S₃.∙ s ⁻¹) (v-of-axis x))         [sym φ.act-∙]
    --   ≡ axis-of-v (φ.act S₃.ε (v-of-axis x))                  [cong, S₃.inv-inverseʳ]
    --   ≡ axis-of-v (v-of-axis x)                               [φ.act-ε]
    --   ≡ x                                                      [axis-of-v-v-of-axis]
    trans (cong (λ y → axis-of-v (φ.act s y))
                (v-of-axis-axis-of-v (φ.act (s S₃.⁻¹) (v-of-axis x))))
    (trans (sym (cong axis-of-v (φ.act-∙ s (s S₃.⁻¹) (v-of-axis x))))
    (trans (cong axis-of-v (φ-cong-v (s S₃.∙ s S₃.⁻¹) S₃.ε (v-of-axis x) (proj₂ S₃.inv-inverse s)))
    (trans (cong axis-of-v (φ.act-ε (v-of-axis x)))
           (axis-of-v-v-of-axis x))))

  -- s3-inv-apply s ∘ s3-apply s = id (inv-l for embed-S₃). Symmetric.
  s3-inv-apply-l : (s : S₃.Carrier) (x : Axis) →
                   s3-inv-apply s (s3-apply s x) ≡ x
  s3-inv-apply-l s x =
    trans (cong (λ y → axis-of-v (φ.act (s S₃.⁻¹) y))
                (v-of-axis-axis-of-v (φ.act s (v-of-axis x))))
    (trans (sym (cong axis-of-v (φ.act-∙ (s S₃.⁻¹) s (v-of-axis x))))
    (trans (cong axis-of-v (φ-cong-v (s S₃.⁻¹ S₃.∙ s) S₃.ε (v-of-axis x) (proj₁ S₃.inv-inverse s)))
    (trans (cong axis-of-v (φ.act-ε (v-of-axis x)))
           (axis-of-v-v-of-axis x))))

embed-S₃ : S₃.Carrier → Permutation
embed-S₃ s = record
  { apply = s3-apply s
  ; invₐ  = s3-inv-apply s
  ; inv-l = s3-inv-apply-l s
  ; inv-r = s3-apply-inv-r s
  }

------------------------------------------------------------------------
-- 2. compositional-to-perm: forward direction of the iso.
--
-- (v, s) ↦ embed v · embed-S₃ s.
-- The V₄ component acts on the Axis output of the S₃ action.
------------------------------------------------------------------------

compositional-to-perm : S4C.Carrier → Permutation
compositional-to-perm (v , s) = embed v · embed-S₃ s

------------------------------------------------------------------------
-- 3. G2: perm-to-compositional (backward direction).
--
-- Uses existing factorization (SemidirectProduct.semidirect-factorisation):
-- σ ≈ embed (v-for σ) · s-for σ where s-for σ ∈ Stab(D).
-- Plus extract-s : Stab(D)-permutation → S₃.Carrier (6-case dispatch).
------------------------------------------------------------------------

import Substrate.Groups.SemidirectProduct as SP-old
open SP-old using (v-for; s-for; s-for-fixes-D)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

-- Extract an S₃.Carrier from a Stab(D)-permutation by reading off its
-- action on (C, S). Factored through extract-s-from so the with-cases
-- unfold under proof-level `with apply s C in eqC | apply s S in eqS`.
-- 6 valid cases; default for the 10 cases that can't arise from a
-- bijective Stab(D) permutation.
extract-s-from : Axis → Axis → S₃.Carrier
extract-s-from C S = ([] , [])                                -- identity
extract-s-from S W = (Z₃.a ∷ [] , [])                         -- rotate (CSW)
extract-s-from W C = (Z₃.a ∷ Z₃.a ∷ [] , [])                  -- rotate² (CWS)
extract-s-from S C = ([] , Z₂.a ∷ [])                         -- swap CS
extract-s-from W S = (Z₃.a ∷ [] , Z₂.a ∷ [])                  -- swap CW
extract-s-from C W = (Z₃.a ∷ Z₃.a ∷ [] , Z₂.a ∷ [])           -- swap SW
extract-s-from _ _ = ([] , [])                                -- impossible

extract-s : Permutation → S₃.Carrier
extract-s s = extract-s-from (apply s C) (apply s S)

perm-to-compositional : Permutation → S4C.Carrier
perm-to-compositional σ = (v-for σ , extract-s (s-for σ))

------------------------------------------------------------------------
-- 4. Foundation lemmas for forward-hom + V₄-normal transport.
--
-- embed-S₃-ε   : embed-S₃ ε_S₃ ≈ ε_perm (identity action)
-- embed-S₃-hom : embed-S₃ (s₁ ∙ s₂) ≈ embed-S₃ s₁ · embed-S₃ s₂
-- swap-relation : embed-S₃ s · embed v ≈ embed (φ.act s v) · embed-S₃ s
--                 (S₃ ⊂ S₄ conjugates V₄ ⊂ S₄ via the AGL action)
------------------------------------------------------------------------

-- embed-S₃ of S₃'s identity is the identity permutation (pointwise).
embed-S₃-ε : (x : Axis) → apply (embed-S₃ S₃.ε) x ≡ x
embed-S₃-ε x =
  -- apply (embed-S₃ S₃.ε) x = axis-of-v (φ.act S₃.ε (v-of-axis x))
  --   = axis-of-v (v-of-axis x)   [φ.act-ε]
  --   = x                          [axis-of-v-v-of-axis]
  trans (cong axis-of-v (φ.act-ε (v-of-axis x)))
        (axis-of-v-v-of-axis x)

-- embed-S₃ is a Group homomorphism (pointwise on the Permutation side).
embed-S₃-hom : (s₁ s₂ : S₃.Carrier) →
               (x : Axis) →
               apply (embed-S₃ (s₁ S₃.∙ s₂)) x ≡
               apply (embed-S₃ s₁ · embed-S₃ s₂) x
embed-S₃-hom s₁ s₂ x =
  trans (cong axis-of-v (φ.act-∙ s₁ s₂ (v-of-axis x)))
        (cong (λ y → axis-of-v (φ.act s₁ y))
              (sym (v-of-axis-axis-of-v (φ.act s₂ (v-of-axis x)))))

-- The defining "S₃ conjugates V₄" relation at the Permutation level:
-- embed-S₃ s · embed v ≈ embed (φ.act s v) · embed-S₃ s.
-- Both sides reduce to axis-of-v (φ.act s v V4.· φ.act s (v-of-axis x)).
swap-relation : (s : S₃.Carrier) (v : V₄) →
                (x : Axis) →
                apply (embed-S₃ s · embed v) x ≡
                apply (embed (φ.act s v) · embed-S₃ s) x
swap-relation s v x = trans LHS-to-canonical (sym RHS-to-canonical)
  where
    open import Substrate.Groups.V4-Embedding using (act-axis-as-V₄-mult)
    -- The common reduced form.
    LHS-to-canonical :
      apply (embed-S₃ s · embed v) x ≡
      axis-of-v (φ.act s v V4.· φ.act s (v-of-axis x))
    LHS-to-canonical =
      trans (cong (λ y → axis-of-v (φ.act s (v-of-axis y)))
                  (act-axis-as-V₄-mult v x))
      (trans (cong (λ y → axis-of-v (φ.act s y))
                   (v-of-axis-axis-of-v (v V4.· v-of-axis x)))
             (cong axis-of-v (φ.act-hom s v (v-of-axis x))))
    RHS-to-canonical :
      apply (embed (φ.act s v) · embed-S₃ s) x ≡
      axis-of-v (φ.act s v V4.· φ.act s (v-of-axis x))
    RHS-to-canonical =
      trans (act-axis-as-V₄-mult (φ.act s v)
                                  (axis-of-v (φ.act s (v-of-axis x))))
            (cong (λ y → axis-of-v (φ.act s v V4.· y))
                  (v-of-axis-axis-of-v (φ.act s (v-of-axis x))))

------------------------------------------------------------------------
-- 5. G4: forward-hom — compositional-to-perm is a Group homomorphism.
--
-- For s₁ = (v₁, sa) and s₂ = (v₂, sb):
--   compositional-to-perm (s₁ S4C.∙ s₂)
--   = embed (v₁ V4.· φ.act sa v₂) · embed-S₃ (sa S3.∙ sb)
--   ≈ (embed v₁ · embed-S₃ sa) · (embed v₂ · embed-S₃ sb)
--   = compositional-to-perm s₁ · compositional-to-perm s₂
--
-- Composes embed-hom + embed-S₃-hom + swap-relation + S4.·-assoc.
------------------------------------------------------------------------

private
  open import Substrate.Groups.V4-Embedding using (embed-hom)

  -- Wrap embed-S₃-hom and swap-relation as Permutation _≈_ statements
  -- (their bodies already are pointwise; this packages them).
  embed-S₃-hom-≈ : (s₁ s₂ : S₃.Carrier) →
                   embed-S₃ (s₁ S₃.∙ s₂) ≈ (embed-S₃ s₁ · embed-S₃ s₂)
  embed-S₃-hom-≈ s₁ s₂ x = embed-S₃-hom s₁ s₂ x

  swap-relation-≈ : (s : S₃.Carrier) (v : V₄) →
                    (embed-S₃ s · embed v) ≈ (embed (φ.act s v) · embed-S₃ s)
  swap-relation-≈ s v x = swap-relation s v x

-- Per-x pointwise proof: both sides reduce to the canonical form
--   axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· φ.act (sa S3.∙ sb) (v-of-axis x))
-- via act-axis-as-V₄-mult + v-of-axis-axis-of-v + φ.act-hom + φ.act-∙.
forward-hom : (s₁ s₂ : S4C.Carrier) →
              compositional-to-perm (s₁ S4C.∙ s₂) ≈
              (compositional-to-perm s₁ · compositional-to-perm s₂)
forward-hom (v₁ , sa) (v₂ , sb) x = trans LHS-form (sym RHS-form)
  where
    open import Substrate.Groups.V4-Embedding using (act-axis-as-V₄-mult)
    -- The canonical form both sides reduce to.
    Canon : Axis
    Canon = axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· φ.act (sa S₃.∙ sb) (v-of-axis x))

    -- LHS = act-axis (v₁ V4.· φ.act sa v₂) (apply (embed-S₃ (sa S3.∙ sb)) x)
    --     = act-axis (v₁ V4.· φ.act sa v₂) (axis-of-v (φ.act (sa S3.∙ sb) (v-of-axis x)))
    --     ≡ axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· v-of-axis (axis-of-v (φ.act (sa S3.∙ sb) (v-of-axis x))))
    --     ≡ axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· φ.act (sa S3.∙ sb) (v-of-axis x))
    LHS-form :
      apply (compositional-to-perm ((v₁ , sa) S4C.∙ (v₂ , sb))) x ≡ Canon
    LHS-form =
      trans (act-axis-as-V₄-mult (v₁ V4.· φ.act sa v₂)
                                  (axis-of-v (φ.act (sa S₃.∙ sb) (v-of-axis x))))
            (cong (λ y → axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· y))
                  (v-of-axis-axis-of-v (φ.act (sa S₃.∙ sb) (v-of-axis x))))

    -- RHS chain: 8 steps, written with ≡-Reasoning for clarity.
    RHS-form :
      apply (compositional-to-perm (v₁ , sa) · compositional-to-perm (v₂ , sb)) x ≡ Canon
    RHS-form = begin
      act-axis v₁ (apply (embed-S₃ sa) (act-axis v₂ (apply (embed-S₃ sb) x)))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) y))
                 (act-axis-as-V₄-mult v₂ (apply (embed-S₃ sb) x)) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· v-of-axis (apply (embed-S₃ sb) x))))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· y))))
                 (v-of-axis-axis-of-v (φ.act sb (v-of-axis x))) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· φ.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → act-axis v₁ (axis-of-v (φ.act sa y)))
                 (v-of-axis-axis-of-v (v₂ V4.· φ.act sb (v-of-axis x))) ⟩
      act-axis v₁ (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x))))
        ≡⟨ act-axis-as-V₄-mult v₁
             (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· v-of-axis (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (v-of-axis-axis-of-v
                   (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (φ.act-hom sa v₂ (φ.act sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· φ.act sa (φ.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· y)))
                 (sym (φ.act-∙ sa sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· φ.act (sa S₃.∙ sb) (v-of-axis x)))
        ≡⟨ cong axis-of-v
                 (sym (V4.·-assoc v₁ (φ.act sa v₂)
                                    (φ.act (sa S₃.∙ sb) (v-of-axis x)))) ⟩
      Canon
        ∎
      where
        open import Relation.Binary.PropositionalEquality
          using (module ≡-Reasoning)
        open ≡-Reasoning

------------------------------------------------------------------------
-- 6. H-1: extract-s-correct.
--
-- For s ∈ Stab(D), embed-S₃ (extract-s s) recovers s. Per-axis proof:
-- x = D: both sides are D (sD on RHS, φ.act-ε-N on LHS).
-- x ∈ {C, S, W}: case-split on (apply s C, apply s S). 10 impossible
-- combinations (eliminated via apply-injective + sD); 6 valid
-- combinations exhaust Sym({C,S,W}) and the proof is refl per (case, x).
------------------------------------------------------------------------

open import Data.Empty using (⊥; ⊥-elim)

private
  -- Permutation apply is injective (derived from inv-l).
  apply-inj : (s : Permutation) → ∀ {x y} → apply s x ≡ apply s y → x ≡ y
  apply-inj s {x} {y} eq =
    trans (sym (inv-l s x)) (trans (cong (invₐ s) eq) (inv-l s y))

  -- φ.act-ε-N transports through axis-of-v to recover D at the D-axis.
  embed-S₃-D : (s' : S₃.Carrier) → apply (embed-S₃ s') D ≡ D
  embed-S₃-D s' = cong axis-of-v (φ.act-ε-N s')

  -- Distinct-constructor disequalities (used to close 10 impossible
  -- (apply s C, apply s S, apply s W) combinations via apply-inj).
  C≢D : C ≡ D → ⊥
  C≢D ()
  S≢D : S ≡ D → ⊥
  S≢D ()
  W≢D : W ≡ D → ⊥
  W≢D ()
  C≢S : C ≡ S → ⊥
  C≢S ()
  C≢W : C ≡ W → ⊥
  C≢W ()
  S≢W : S ≡ W → ⊥
  S≢W ()

------------------------------------------------------------------------
-- DBE H-1 (second-failure intervention):
--   Target: extract-s-correct on Stab(D) — embed-S₃ (extract-s s) ≈ s.
--   Shadows:
--     extract-image  : (X Y x : Axis) → Axis — the image at x of the
--                      S₃ element extract-s-from X Y produces.
--     embed-S₃-of-extract-eval : (X Y x : Axis) → apply
--                                  (embed-S₃ (extract-s-from X Y)) x
--                                  ≡ extract-image X Y x — definitional
--                                  for the 6 valid (X,Y) pairs.
--   Compose: pointwise on x; case-split on (apply s C, apply s S, apply s W)
--            with eqC, eqS, eqW; 10/16 (X,Y) pairs are impossible via
--            apply-inj + sD/eqW; the remaining 6 close via refl after
--            with-rewriting cascades extract-s-from to its concrete output.
--   Entail: enumerate ALL 16 cases explicitly (no `_` wildcard) — Agda's
--           with-elaboration didn't specialise eq-variables under `_`.
------------------------------------------------------------------------

-- Pointwise round-trip: embed-S₃ ∘ extract-s recovers s on Stab(D).
-- Each axis is handled in its own equation. The 16 (apply s C × apply s S)
-- cases are fully enumerated to avoid the with/wildcard interaction.
extract-s-correct : (s : Permutation) → apply s D ≡ D →
                    embed-S₃ (extract-s s) ≈ s
extract-s-correct s sD D = trans (embed-S₃-D (extract-s s)) (sym sD)

extract-s-correct s sD C with apply s C in eqC | apply s S in eqS
... | D | D = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | C = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | S = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | W = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | C | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | S | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | W | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | C | C = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | S | S = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | W | W = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
-- 6 valid Sym({C,S,W}) cases — extract-s-from reduces, both sides become
-- the matched value via with-substitution.
... | C | S = refl
... | S | W = refl
... | W | C = refl
... | S | C = refl
... | W | S = refl
... | C | W = refl

extract-s-correct s sD S with apply s C in eqC | apply s S in eqS
... | D | D = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | C = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | S = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | W = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | C | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | S | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | W | D = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | C | C = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | S | S = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | W | W = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | C | S = refl
... | S | W = refl
... | W | C = refl
... | S | C = refl
... | W | S = refl
... | C | W = refl

-- x = W: also case-split on apply s W to enable refl in the valid cases.
extract-s-correct s sD W with apply s C in eqC | apply s S in eqS | apply s W in eqW
... | D | D | _ = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | C | _ = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | S | _ = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | D | W | _ = ⊥-elim (C≢D (apply-inj s (trans eqC (sym sD))))
... | C | D | _ = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | S | D | _ = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | W | D | _ = ⊥-elim (S≢D (apply-inj s (trans eqS (sym sD))))
... | C | C | _ = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | S | S | _ = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
... | W | W | _ = ⊥-elim (C≢S (apply-inj s (trans eqC (sym eqS))))
-- Impossible W-image cases. Uniform pattern:
--   Z = D → W≢D  via trans eqW (sym sD)
--   Z = X → C≢W  via trans eqC (sym eqW)   (apply-inj gives C ≡ W)
--   Z = Y → S≢W  via trans eqS (sym eqW)   (apply-inj gives S ≡ W)
... | C | S | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | C | S | C = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | C | S | S = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | C | W | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | C | W | C = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | C | W | W = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | S | C | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | S | C | S = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | S | C | C = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | S | W | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | S | W | S = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | S | W | W = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | W | C | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | W | C | W = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | W | C | C = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | W | S | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | W | S | W = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | W | S | S = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
-- 6 valid cases:
... | C | S | W = refl
... | S | W | C = refl
... | W | C | S = refl
... | S | C | W = refl
... | W | S | C = refl
... | C | W | S = refl

------------------------------------------------------------------------
-- 7. H-2: perm-roundtrip-≈ — compositional-to-perm inverts
-- perm-to-compositional on every σ : Permutation.
--
-- Pointwise chain:
--   apply (embed (v-for σ) · embed-S₃ (extract-s (s-for σ))) x
--     = apply (embed (v-for σ)) (apply (embed-S₃ (extract-s (s-for σ))) x)
--     ≡ apply (embed (v-for σ)) (apply (s-for σ) x)           [H-1]
--     = apply (embed (v-for σ)) (apply (embed (v-for σ)) (apply σ x))
--                                                             [s-for unfolds]
--     ≡ apply σ x                                            [V₄ self-inverse]
------------------------------------------------------------------------

open import Substrate.Groups.V4-Embedding using (embed-self-inverse)

perm-roundtrip-≈ : (σ : Permutation) →
                   compositional-to-perm (perm-to-compositional σ) ≈ σ
perm-roundtrip-≈ σ x =
  trans (cong (apply (embed (v-for σ)))
              (extract-s-correct (s-for σ) (s-for-fixes-D σ) x))
        (embed-self-inverse (v-for σ) (apply σ x))

------------------------------------------------------------------------
-- 8. H-4: embed-as-N-injection.
--
-- The permutation-side V₄ embed agrees with the compositional-side
-- (v, ε_S₃) injection. Direct consequence of embed-S₃-ε.
------------------------------------------------------------------------

embed-as-N-injection : (v : V₄) →
                       embed v ≈ compositional-to-perm (v , S₃.ε)
embed-as-N-injection v x = sym (cong (apply (embed v)) (embed-S₃-ε x))

------------------------------------------------------------------------
-- 9. H-4-aux: a few small permutation algebra lemmas needed to
-- compose the V₄-normal-compositional proof.
--
-- inv-distrib    : (σ · τ) ⁻¹ ≈ τ ⁻¹ · σ ⁻¹    — refl, by Permutation
--                                                  record swap.
-- embed-inv-≈    : (embed v) ⁻¹ ≈ embed v       — refl, since embed v
--                                                  has apply ≡ invₐ.
-- σ-factorises  : σ ≈ embed (v-for σ) · s-for σ — via embed-self-inverse.
------------------------------------------------------------------------

private
  inv-distrib : (σ τ : Permutation) → ((σ · τ) ⁻¹) ≈ ((τ ⁻¹) · (σ ⁻¹))
  inv-distrib σ τ x = refl

  embed-inv-≈ : (v : V₄) → (embed v) ⁻¹ ≈ embed v
  embed-inv-≈ v x = refl

------------------------------------------------------------------------
-- 10. Iso-transport infrastructure (K-shadows).
--
-- BHK / inference-rule construction: each lemma is a proof-transformer.
-- Composed, they give compositional-to-perm full Group-hom status (hom,
-- ε, inv), at which point V₄ ⊳ S₄ becomes a structural transport of
-- S4C.N-normal-in-SP (from SemidirectProductGroup) through the iso.
--
-- K-1: forward-ε         — compositional-to-perm sends S4C.ε ↦ ε
-- K-1a: embed-cong       — V₄ ≡ → embed ≈  (cong)
-- K-1b: embed-S₃-cong    — S₃.≈ → embed-S₃ ≈  (via φ.act-cong)
-- K-1c: compositional-to-perm-cong — S4C.≈ → ≈  (·-cong of K-1a + K-1b)
-- K-2: forward-inv       — compositional-to-perm respects ⁻¹
--                          via inverseˡ-unique applied to forward-ε + forward-hom.
------------------------------------------------------------------------

open import Substrate.Groups.V4-Embedding using (act-axis-id; V₄-image; embed-hom)

-- K-1: compositional-to-perm preserves identity.
forward-ε : compositional-to-perm S4C.ε ≈ ε
forward-ε x = trans (cong (act-axis e) (embed-S₃-ε x)) (act-axis-id x)

private
  -- K-1a: embed is ≡-respecting (trivial via cong + V₄.≈ = V₄._≡_).
  embed-cong : ∀ {v₁ v₂} → v₁ ≡ v₂ → embed v₁ ≈ embed v₂
  embed-cong refl x = refl

  -- K-1b: embed-S₃ respects S₃.≈ (lifted Coxeter Word equivalence).
  -- BHK: input = proof of s₁ S₃.≈ s₂; output = pointwise ≡ at each x via
  -- cong-axis-of-v of φ.act-cong.
  embed-S₃-cong : ∀ {s₁ s₂} → s₁ S₃.≈ s₂ → embed-S₃ s₁ ≈ embed-S₃ s₂
  embed-S₃-cong {s₁} {s₂} s-eq x =
    cong axis-of-v
         (φ.act-cong {s₁ = s₁} {s₂ = s₂}
                      {v₁ = v-of-axis x} {v₂ = v-of-axis x}
                      s-eq refl)

-- K-1c: compositional-to-perm respects S4C._≈_ = V₄.≡ × S₃.≈.
compositional-to-perm-cong :
  ∀ {s₁ s₂ : S4C.Carrier} → s₁ S4C.≈ s₂ →
  compositional-to-perm s₁ ≈ compositional-to-perm s₂
compositional-to-perm-cong {v₁ , sa} {v₂ , sb} (v-eq , s-eq) =
  ·-cong {σ₁ = embed v₁} {σ₂ = embed v₂}
          {τ₁ = embed-S₃ sa} {τ₂ = embed-S₃ sb}
          (embed-cong v-eq)
          (embed-S₃-cong {s₁ = sa} {s₂ = sb} s-eq)

------------------------------------------------------------------------
-- K-2: forward-inv.
--
-- BHK: given the Group axioms + forward-hom + forward-ε, the unique
-- left-inverse property (Algebra.Properties.Group.inverseˡ-unique)
-- discharges:
--
--   compositional-to-perm (s S4C.⁻¹) · compositional-to-perm s ≈ ε
--   ⇒ compositional-to-perm (s S4C.⁻¹) ≈ (compositional-to-perm s) ⁻¹
--
-- The LHS-≈-ε is built by:
--   (sym forward-hom) ∘ (compositional-to-perm-cong + S4C.inverseˡ s)
--     ∘ forward-ε
------------------------------------------------------------------------

open import Algebra.Properties.Group S4.Symmetric-Group using (inverseˡ-unique)

forward-inv : ∀ (s : S4C.Carrier) →
              compositional-to-perm (s S4C.⁻¹) ≈ (compositional-to-perm s) ⁻¹
forward-inv s =
  inverseˡ-unique (compositional-to-perm (s S4C.⁻¹)) (compositional-to-perm s)
                  inverse-eq
  where
    -- inverse-eq : compositional-to-perm (s S4C.⁻¹) · compositional-to-perm s ≈ ε
    -- Built as: ≈-trans (sym forward-hom) (≈-trans cong-of-S4C-inv forward-ε)
    -- with each intermediate Permutation named.
    M1 : Permutation
    M1 = compositional-to-perm (s S4C.⁻¹) · compositional-to-perm s
    M2 : Permutation
    M2 = compositional-to-perm ((s S4C.⁻¹) S4C.∙ s)
    M3 : Permutation
    M3 = compositional-to-perm S4C.ε

    -- step A: M1 ≈ M2  (sym forward-hom)
    eqA : M1 ≈ M2
    eqA = ≈-sym {σ = M2} {τ = M1} (forward-hom (s S4C.⁻¹) s)

    -- step B: M2 ≈ M3  (compositional-to-perm-cong on S4C.inverseˡ)
    eqB : M2 ≈ M3
    eqB = compositional-to-perm-cong {s₁ = (s S4C.⁻¹) S4C.∙ s} {s₂ = S4C.ε}
                                       (proj₁ S4C.inv-inverse s)

    -- step C: M3 ≈ ε   (forward-ε)
    eqC : M3 ≈ ε
    eqC = forward-ε

    inverse-eq : M1 ≈ ε
    inverse-eq = ≈-trans {σ = M1} {τ = M2} {ρ = ε} eqA
                  (≈-trans {σ = M2} {τ = M3} {ρ = ε} eqB eqC)

------------------------------------------------------------------------
-- 11. V₄-normal-compositional: V₄ ⊳ S₄ as iso-transport of H-3.
--
-- BHK construction:
--   sp-norm : S4C.N-normal-in-SP at the compositional side gives (v', S4C-eq).
--   chain at the Permutation level transports S4C-eq through:
--     σ ≈ compositional-to-perm σ̂              [H-2]
--     embed v ≈ compositional-to-perm (v, S₃.ε)   [H-4]
--     σ⁻¹ ≈ compositional-to-perm (σ̂ S4C.⁻¹)   [K-2 sym]
--     ·-cong twice                              [combine three iso lifts]
--     (sym forward-hom) × 2                    [push compositional-to-perm out]
--     compositional-to-perm-cong + S4C-eq      [apply SP normality]
--     sym H-4                                   [recover embed v']
--
-- All named intermediates so ≈-trans implicits are determinate.
------------------------------------------------------------------------

V₄-normal-compositional :
  (σ : Permutation) (v : V₄) → V₄-image ((σ · embed v) · (σ ⁻¹))
V₄-normal-compositional σ v =
  v' , conj-eq
  where
    σ̂ : S4C.Carrier
    σ̂ = perm-to-compositional σ

    v' : V₄
    v' = proj₁ (S4C.N-normal-in-SP σ̂ v)

    s4c-eq : (σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹)) S4C.≈ (v' , S₃.ε)
    s4c-eq = proj₂ (S4C.N-normal-in-SP σ̂ v)

    -- Named permutations along the chain.
    L  P-σ  P-v  P-σ⁻¹  P-σv  P-σvσ⁻¹  P-prod-inner  P-prod  P-result  R : Permutation
    L          = (σ · embed v) · (σ ⁻¹)
    P-σ        = compositional-to-perm σ̂
    P-v        = compositional-to-perm (v , S₃.ε)
    P-σ⁻¹      = compositional-to-perm (σ̂ S4C.⁻¹)
    P-σv       = P-σ · P-v
    P-σvσ⁻¹    = P-σv · P-σ⁻¹
    P-prod-inner = compositional-to-perm (σ̂ S4C.∙ (v , S₃.ε))
    P-prod       = compositional-to-perm (σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹))
    P-result     = compositional-to-perm (v' , S₃.ε)
    R            = embed v'

    -- Step 1: σ ≈ P-σ, embed v ≈ P-v, σ⁻¹ ≈ P-σ⁻¹.
    σ≈P : σ ≈ P-σ
    σ≈P = ≈-sym {σ = P-σ} {τ = σ} (perm-roundtrip-≈ σ)

    v≈P : embed v ≈ P-v
    v≈P = embed-as-N-injection v

    σ⁻¹≈P : (σ ⁻¹) ≈ P-σ⁻¹
    σ⁻¹≈P = ≈-trans {σ = σ ⁻¹} {τ = (compositional-to-perm σ̂) ⁻¹} {ρ = P-σ⁻¹}
              (S4.⁻¹-cong {σ = σ} {τ = compositional-to-perm σ̂} σ≈P)
              (≈-sym {σ = P-σ⁻¹} {τ = (compositional-to-perm σ̂) ⁻¹}
                      (forward-inv σ̂))

    -- step E1: L ≈ P-σvσ⁻¹  via ·-cong twice.
    eqE1 : L ≈ P-σvσ⁻¹
    eqE1 = ·-cong {σ₁ = σ · embed v} {σ₂ = P-σv}
                   {τ₁ = σ ⁻¹}        {τ₂ = P-σ⁻¹}
                   (·-cong {σ₁ = σ}       {σ₂ = P-σ}
                            {τ₁ = embed v} {τ₂ = P-v}
                            σ≈P v≈P)
                   σ⁻¹≈P

    -- step E2: P-σvσ⁻¹ ≈ compositional-to-perm (σ̂ S4C.∙ (v, S₃.ε)) · P-σ⁻¹
    --        ≈ P-prod   (via sym forward-hom twice)
    eqE2-inner : P-σv ≈ P-prod-inner
    eqE2-inner = ≈-sym {σ = P-prod-inner} {τ = P-σv}
                        (forward-hom σ̂ (v , S₃.ε))

    eqE2 : P-σvσ⁻¹ ≈ P-prod
    eqE2 = ≈-trans {σ = P-σvσ⁻¹} {τ = P-prod-inner · P-σ⁻¹} {ρ = P-prod}
            (·-cong {σ₁ = P-σv} {σ₂ = P-prod-inner}
                     {τ₁ = P-σ⁻¹} {τ₂ = P-σ⁻¹}
                     eqE2-inner (≈-refl P-σ⁻¹))
            (≈-sym {σ = P-prod} {τ = P-prod-inner · P-σ⁻¹}
                    (forward-hom (σ̂ S4C.∙ (v , S₃.ε)) (σ̂ S4C.⁻¹)))

    -- step E3: P-prod ≈ P-result via compositional-to-perm-cong + s4c-eq.
    eqE3 : P-prod ≈ P-result
    eqE3 = compositional-to-perm-cong
             {s₁ = σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹)} {s₂ = v' , S₃.ε}
             s4c-eq

    -- step E4: P-result ≈ R = embed v' via sym H-4.
    eqE4 : P-result ≈ R
    eqE4 = ≈-sym {σ = R} {τ = P-result} (embed-as-N-injection v')

    -- Compose: L ≈ R.
    conj-eq : L ≈ R
    conj-eq =
      ≈-trans {σ = L} {τ = P-σvσ⁻¹} {ρ = R} eqE1
        (≈-trans {σ = P-σvσ⁻¹} {τ = P-prod} {ρ = R} eqE2
          (≈-trans {σ = P-prod} {τ = P-result} {ρ = R} eqE3 eqE4))
