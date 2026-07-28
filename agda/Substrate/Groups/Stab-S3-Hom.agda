------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3-Hom
--
-- Slice 14e: group-homomorphism properties for BOTH sides of the
-- Stab(anchor) ≅ S_3 iso. Shows restrict AND extend each preserve
-- identity, composition, and inverse.
--
-- The six homomorphism lemmas (all stated pointwise, anchor-parametric):
--
--   restrict-hom-ε   : restrict anchor (ε , Stab-ε anchor) ≈ SFinI.ε
--   restrict-hom-∙   : restrict anchor (σ₁·σ₂ , Stab-∙ p₁ p₂) ≈
--                       restrict anchor (σ₁,p₁) SFinC.·
--                       restrict anchor (σ₂,p₂)
--   restrict-hom-⁻¹  : restrict anchor (σ⁻¹ , Stab-inv p) ≈
--                       (restrict anchor (σ,p)) SFinV.⁻¹
--   extend-hom-ε     : extend anchor SFinI.ε ≈ ε  (S4-side)
--   extend-hom-∙     : extend anchor (s₁ SFinC.· s₂) ≈
--                       extend anchor s₁ · extend anchor s₂
--   extend-hom-⁻¹    : extend anchor (s SFinV.⁻¹) ≈ (extend anchor s) ⁻¹
--
-- For restrict-hom-⁻¹ the equation is refl by definition: both sides
-- are restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i, since
-- restrict-invₐ unfolds to restrict-apply (σ⁻¹) (Stab-inv ...).
--
-- For extend-hom-{ε, ⁻¹} the equation is refl per Axis-input (16 cases
-- each): both sides reduce through fin3-to-non-anchor to the same
-- expression. For extend-hom-∙: 4 refl cases (anchor-fixed) + 12 axes
-- × 3 Fin-3 dispatch = 36 sub-cases via `with ... in p`, each closing
-- by refl after the with-substitution propagates through SFinC._·_'s
-- definition.
--
-- For restrict-hom-ε and -∙ the chain uses non-anchor-to-fin3-cong +
-- the bridge round-trips from slice 14a, in the same shape as slices
-- 14b/14d.
--
-- Side parametric closure laws (added here):
--   Stab-ε : (anchor : Axis) → Stab anchor ε  (refl, ε.apply = id)
--   Stab-∙ : (anchor : Axis) {σ τ} → Stab σ → Stab τ → Stab (σ · τ)
--
-- Symmetry note (patched 2026-05-16): originally slice 14e proved
-- only the restrict-side hom and deferred the extend-side to a
-- hypothetical slice 14f. The module-graph Jaccard analysis flagged
-- the (Stab-S3-Hom ⇄ Stab-S3-Iso) gap as an unrealized symmetry —
-- Iso used both halves of the iso, Hom only one. The extend-side
-- lemmas below close that gap.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3-Hom where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.PairCover using (axis×axis-cover)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis using (_⁻¹)
open import Substrate.Groups.Symmetric.Identity Axis using (ε)
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.Symmetric.Permutation.SFinCompose as SFinC
import Substrate.Groups.SFin.Identity as SFinI
import Substrate.Groups.Symmetric.Permutation.SFinInverse as SFinV
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Groups.Stab-S3
  using (Stab; Stab-inv;
         fin3-to-non-anchor; fin3-to-non-anchor-≢;
         non-anchor-to-fin3; non-anchor-fin3-non-anchor;
         fin3-non-anchor-fin3; stab-preserves-≢)
open import Substrate.Groups.Stab-S3-Restrict
  using (non-anchor-to-fin3-cong; restrict)
open import Substrate.Groups.Stab-S3-Extend using (extend)

------------------------------------------------------------------------
-- Parametric closure laws for Stab anchor (identity and composition).
------------------------------------------------------------------------

Stab-ε : (anchor : Axis) → Stab anchor ε
Stab-ε anchor = refl

Stab-∙ :
  (anchor : Axis) {σ τ : Permutation} →
  Stab anchor σ → Stab anchor τ →
  Stab anchor (σ · τ)
Stab-∙ anchor {σ} {τ} σ-stab τ-stab =
  trans (cong (apply σ) τ-stab) σ-stab

------------------------------------------------------------------------
-- restrict-hom-ε: restrict preserves the identity.
--
-- LHS reduces to non-anchor-to-fin3 anchor (fin3-to-non-anchor anchor
-- i) (some stab-preserves-≢ proof) — since apply ε x = x. The
-- chain: bridge proof-difference via non-anchor-to-fin3-cong (with
-- refl on the axis component), then close via fin3-non-anchor-fin3.
------------------------------------------------------------------------

restrict-hom-ε :
  (anchor : Axis) (i : Fin 3) →
  SFinA.apply (restrict anchor (ε , Stab-ε anchor)) i ≡ SFinA.apply SFinI.ε i
restrict-hom-ε anchor i =
  trans (non-anchor-to-fin3-cong anchor refl _
          (fin3-to-non-anchor-≢ anchor i))
        (fin3-non-anchor-fin3 anchor i)

------------------------------------------------------------------------
-- restrict-hom-∙: restrict preserves composition.
--
-- LHS:
--   non-anchor-to-fin3 anchor (apply σ₁ (apply σ₂ X)) (proof_L)
-- RHS:
--   non-anchor-to-fin3 anchor (apply σ₁ (fin3-to-non-anchor anchor
--                              (restrict-apply anchor σ₂ p₂ i)))
--                              (proof_R)
-- where X = fin3-to-non-anchor anchor i.
--
-- The two axis-expressions agree after rewriting via
-- non-anchor-fin3-non-anchor anchor (apply σ₂ X) (the stab-preserves-≢
-- proof restrict-apply uses internally). cong (apply σ₁) lifts to
-- the σ₁-applied form; sym reverses the direction; then
-- non-anchor-to-fin3-cong handles the proof-component difference.
------------------------------------------------------------------------

restrict-hom-∙ :
  (anchor : Axis) {σ₁ σ₂ : Permutation}
  (p₁ : Stab anchor σ₁) (p₂ : Stab anchor σ₂) (i : Fin 3) →
  SFinA.apply (restrict anchor
               (σ₁ · σ₂ , Stab-∙ anchor {σ₁} {σ₂} p₁ p₂)) i
  ≡ SFinA.apply (restrict anchor (σ₁ , p₁) SFinC.·
                restrict anchor (σ₂ , p₂)) i
restrict-hom-∙ anchor {σ₁} {σ₂} p₁ p₂ i =
  non-anchor-to-fin3-cong anchor axis-eq _ _
  where
    X : Axis
    X = fin3-to-non-anchor anchor i

    σ₂X-≢ : apply σ₂ X ≢ anchor
    σ₂X-≢ = stab-preserves-≢ anchor σ₂ p₂ X (fin3-to-non-anchor-≢ anchor i)

    axis-eq :
      apply σ₁ (apply σ₂ X)
      ≡ apply σ₁ (fin3-to-non-anchor anchor
                    (non-anchor-to-fin3 anchor (apply σ₂ X) σ₂X-≢))
    axis-eq =
      cong (apply σ₁) (sym (non-anchor-fin3-non-anchor anchor (apply σ₂ X) σ₂X-≢))

------------------------------------------------------------------------
-- restrict-hom-⁻¹: restrict preserves inverse — by definition.
--
-- Both sides are restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i:
--   LHS  = restrict anchor (σ ⁻¹ , Stab-inv anchor σ p)'s apply at i
--        = restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i.
--   RHS  = SFinA.apply ((restrict anchor (σ,p)) SFinV.⁻¹) i
--        = SFinA.invₐ (restrict anchor (σ,p)) i
--        = restrict-invₐ anchor σ p i
--        = restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i.
-- refl.
------------------------------------------------------------------------

restrict-hom-⁻¹ :
  (anchor : Axis) {σ : Permutation} (p : Stab anchor σ) (i : Fin 3) →
  SFinA.apply (restrict anchor (σ ⁻¹ , Stab-inv anchor σ p)) i
  ≡ SFinA.apply ((restrict anchor (σ , p)) SFinV.⁻¹) i
restrict-hom-⁻¹ anchor p i = refl

------------------------------------------------------------------------
-- Extend-side homomorphism (the dual of restrict-hom-*).
--
-- Slice 14e originally deferred these to "slice 14f if needed". The
-- module-Jaccard analysis (slice 18+) flagged the Hom ⇄ Iso asymmetry
-- (Iso uses both Extend AND Restrict; Hom used only Restrict) as an
-- unrealized symmetry. Per [[feedback-two-path-commutativity]] and
-- the user's "no such thing as legitimate distinction" rule, the gap
-- is patched by adding the parallel extend-side lemmas.
--
-- After this patch: Stab-S3-Hom imports both halves of the iso (slice
-- 14b's restrict + slice 14c's extend), so the (Hom ⇄ Iso) Jaccard
-- gap closes. Stab-S3-Hom is now the full both-direction
-- homomorphism module.
--
-- The proofs:
--   extend-hom-ε   : extend anchor SFinI.ε ≈ ε        (16 refls — anchor × axis)
--   extend-hom-∙   : extend anchor (s₁ · s₂) ≈ extend anchor s₁ · extend anchor s₂
--                    (4 refl-anchor cases + 12 axis cases × 3 Fin-dispatch each)
--   extend-hom-⁻¹  : extend anchor (s ⁻¹) ≈ (extend anchor s) ⁻¹  (16 refls)
--
-- All anchor-parametric.
------------------------------------------------------------------------

extend-hom-ε :
  (anchor : Axis) (x : Axis) →
  apply (proj₁ (extend anchor SFinI.ε)) x ≡ apply ε x
extend-hom-ε =
  axis×axis-cover _
    ((refl , refl , refl , refl) ,
     (refl , refl , refl , refl) ,
     (refl , refl , refl , refl) ,
     (refl , refl , refl , refl))

------------------------------------------------------------------------
-- extend-hom-∙: extend preserves composition.
--
-- Dispatch on (anchor, x). For x = anchor: refl (extend fixes anchor).
-- For x ≠ anchor: dispatch on SFinA.apply s₂ <Fin-index-of-x> via
-- `with ... in p` (3 sub-cases per axis), each closing by refl.
--
-- The Fin index for axis x under anchor's convention follows
-- declaration-order of {D, C, S, W} minus anchor (per slice 14a/14c
-- — [[feedback-ordering-is-chirality-choice]]).
------------------------------------------------------------------------

extend-hom-∙ :
  (anchor : Axis) (s₁ s₂ : SFinP.Permutation 3) (x : Axis) →
  apply (proj₁ (extend anchor (s₁ SFinC.· s₂))) x
  ≡ apply ((proj₁ (extend anchor s₁)) · (proj₁ (extend anchor s₂))) x
-- Anchor-fixed cases (each = anchor):
extend-hom-∙ D s₁ s₂ D = refl
extend-hom-∙ C s₁ s₂ C = refl
extend-hom-∙ S s₁ s₂ S = refl
extend-hom-∙ W s₁ s₂ W = refl
-- Anchor D, non-anchor axes (C=0, S=1, W=2):
extend-hom-∙ D s₁ s₂ C with SFinA.apply s₂ zero in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ D s₁ s₂ S with SFinA.apply s₂ ₁ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ D s₁ s₂ W with SFinA.apply s₂ ₂ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
-- Anchor C, non-anchor axes (D=0, S=1, W=2):
extend-hom-∙ C s₁ s₂ D with SFinA.apply s₂ zero in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ C s₁ s₂ S with SFinA.apply s₂ ₁ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ C s₁ s₂ W with SFinA.apply s₂ ₂ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
-- Anchor S, non-anchor axes (D=0, C=1, W=2):
extend-hom-∙ S s₁ s₂ D with SFinA.apply s₂ zero in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ S s₁ s₂ C with SFinA.apply s₂ ₁ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ S s₁ s₂ W with SFinA.apply s₂ ₂ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
-- Anchor W, non-anchor axes (D=0, C=1, S=2):
extend-hom-∙ W s₁ s₂ D with SFinA.apply s₂ zero in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ W s₁ s₂ C with SFinA.apply s₂ ₁ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl
extend-hom-∙ W s₁ s₂ S with SFinA.apply s₂ ₂ in p
... | zero             = refl
... | ₁         = refl
... | ₂   = refl

------------------------------------------------------------------------
-- extend-hom-⁻¹: extend preserves inverse — by definition.
--
-- Both sides reduce to fin3-to-non-anchor anchor (SFinA.invₐ s <i>)
-- for non-anchor axes (using SFinV._⁻¹.apply = SFinA.invₐ and
-- S4._⁻¹.apply = invₐ, plus extend's record structure with invₐ =
-- extend-invₐ). For anchor x, both = anchor. 16 refls.
------------------------------------------------------------------------

extend-hom-⁻¹ :
  (anchor : Axis) (s : SFinP.Permutation 3) (x : Axis) →
  apply (proj₁ (extend anchor (s SFinV.⁻¹))) x
  ≡ apply ((proj₁ (extend anchor s)) ⁻¹) x
extend-hom-⁻¹ anchor s x = refl
-- Both sides reduce to `extend-fn anchor (SFinA.invₐ s) x`:
--   LHS = extend-apply anchor (s SFinV.⁻¹) x
--       = extend-fn anchor (SFinA.apply (s SFinV.⁻¹)) x
--       = extend-fn anchor (SFinA.invₐ s) x   [SFinV._⁻¹ swaps apply ↔ invₐ]
--   RHS = (extend anchor s) ⁻¹.apply x
--       = (extend anchor s).invₐ x           [S4._⁻¹ swaps apply ↔ invₐ]
--       = extend-invₐ anchor s x             [record projection]
--       = extend-fn anchor (SFinA.invₐ s) x

------------------------------------------------------------------------
-- Notes
--
-- 1. With ε, ∙, ⁻¹ all preserved, restrict is a group homomorphism
--    from the (informal) Stab(anchor)-group into SFin.S-Group 3.
--    Combined with slice 14d's bijection, this means Stab(anchor) ≅
--    S_3 AS GROUPS, not just as sets.
--
-- 2. To package as a stdlib `IsGroupIsomorphism`, we'd need to
--    construct Stab(anchor) as a stdlib Group bundle (Carrier = Σ
--    Permutation (Stab anchor); operations from slice 12's Subgroup
--    closure laws, generalised to anchor). That's the slice 14f
--    move if downstream theorems require the bundle. The pointwise
--    homomorphism lemmas here are the structural content.
--
-- 3. The extend-side homomorphism (extend-hom-ε / ∙ / ⁻¹) follows
--    the same shape and is symmetric; deferred to slice 14g if
--    needed.
--
-- 4. Cross-references:
--    * Slice 14a: parametric Stab, Stab-inv, bridges.
--    * Slice 14b: restrict bundle + non-anchor-to-fin3-cong.
--    * Slice 14d: set-bijection iso.
------------------------------------------------------------------------
