------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection
--
-- Slice 11d: bundles Live ↔ Permutation as a constructive bijection.
--
-- The round-trips compose from the algebraic identities in slice 11c
-- plus three case-analytic lemmas in this module:
--
--   axis-selector-roundtrip   — Axis × Selector ↔ Live decoding
--                                roundtrip (24 refls).
--   axis-selector-roundtrip-2 — the codeword half of the same
--                                roundtrip (24 refls, with the 8
--                                reserved cases ruled out by ¬res).
--   stab-from-selector-eq-orbit
--                              — bridge to S4Iso.stab-round-trip
--                                (16 refls; selector and orbit-key
--                                are isomorphic relabellings of the
--                                same 6 stab elements).
--
-- The forward round trip uses the V_4 ⋊ Stab(D) factorisation
-- (slice 3) and S4Iso's stab-round-trip (slice 4) as load-bearing
-- premises; the reverse round trip uses the same plus the algebraic
-- identities from slice 11c.
--
-- Custom record bundling: stdlib's _↔_ wants _≡_ on both sides;
-- Permutation has _≈_ pointwise and Live's Σ-type wraps a ¬-component
-- whose propositional equality needs funext. So we use codeword-level
-- _≡_ on the Live side and _≈_ on the Permutation side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection where

open import Level using (0ℓ)
open import Data.Bool using (Bool; true; false)
open import Data.Empty using (⊥; ⊥-elim)
open import Data.Product using (_×_; _,_; proj₁; proj₂; Σ; Σ-syntax)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; ε; ≈-refl; ≈-trans)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive)
open import Substrate.Groups.SemidirectProduct
  using (Stab-D; v-of-axis; v-of-axis-sends-D;
         v-for; s-for; s-for-fixes-D; factorisation)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (stab-id; stab-sw; stab-cs; stab-cw; stab-csw; stab-cws;
         classify-CS; orbit-key-to-stab-d;
         stab-d-to-orbit-key; stab-round-trip;
         orbit-key-to-stab-anchor; orbit-key-to-stab-anchor-fixes)
open import Substrate.Cocycles.V4Signature
  using (OrbitKey; α-pair; β-pair; γ-pair; even; odd)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Codeword; IsReserved; Live; axis-from-bits; axis-to-bits)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt;
         selector-to-bits;
         live-to-axis-selector; axis-selector-to-live)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (stab-from-selector; live-to-permutation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
  using (axis-of-v; axis-of-v-v-of-axis-id; v-of-axis-axis-of-v-id;
         classify-CS-to-selector; selector-from-stab;
         selector-stab-id; permutation-to-live)

------------------------------------------------------------------------
-- Axis × Selector ↔ Live roundtrips at codeword level.
------------------------------------------------------------------------

-- Forward: live-to-axis-selector ∘ axis-selector-to-live ≡ id.
-- 24 cases, all refl (Axis × Selector → Codeword bits → Axis × Selector).
axis-selector-roundtrip :
  (xy : Axis × Selector) →
  live-to-axis-selector (axis-selector-to-live xy) ≡ xy
axis-selector-roundtrip (D , sel-fft) = refl
axis-selector-roundtrip (D , sel-tft) = refl
axis-selector-roundtrip (D , sel-ftf) = refl
axis-selector-roundtrip (D , sel-ttf) = refl
axis-selector-roundtrip (D , sel-ftt) = refl
axis-selector-roundtrip (D , sel-ttt) = refl
axis-selector-roundtrip (C , sel-fft) = refl
axis-selector-roundtrip (C , sel-tft) = refl
axis-selector-roundtrip (C , sel-ftf) = refl
axis-selector-roundtrip (C , sel-ttf) = refl
axis-selector-roundtrip (C , sel-ftt) = refl
axis-selector-roundtrip (C , sel-ttt) = refl
axis-selector-roundtrip (S , sel-fft) = refl
axis-selector-roundtrip (S , sel-tft) = refl
axis-selector-roundtrip (S , sel-ftf) = refl
axis-selector-roundtrip (S , sel-ttf) = refl
axis-selector-roundtrip (S , sel-ftt) = refl
axis-selector-roundtrip (S , sel-ttt) = refl
axis-selector-roundtrip (W , sel-fft) = refl
axis-selector-roundtrip (W , sel-tft) = refl
axis-selector-roundtrip (W , sel-ftf) = refl
axis-selector-roundtrip (W , sel-ttf) = refl
axis-selector-roundtrip (W , sel-ftt) = refl
axis-selector-roundtrip (W , sel-ttt) = refl

-- Reverse: at codeword level (sidestep ¬-component funext concern).
-- For each of the 24 live bit patterns, the round trip recovers the
-- codeword exactly. The 8 reserved patterns are ruled out by the
-- ¬-IsReserved proof.
axis-selector-roundtrip-cw :
  (lv : Live) →
  proj₁ (axis-selector-to-live (live-to-axis-selector lv)) ≡ proj₁ lv
axis-selector-roundtrip-cw ((_ , _ , _ , false , false) , ¬res) =
  ⊥-elim (¬res (refl , refl))
-- (b₃ , b₄) = (false , true) — 8 patterns (4 b₀b₁ × 2 b₂)
axis-selector-roundtrip-cw ((false , false , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , false , true) , _) = refl
-- (b₃ , b₄) = (true , false)
axis-selector-roundtrip-cw ((false , false , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , true , false) , _) = refl
-- (b₃ , b₄) = (true , true)
axis-selector-roundtrip-cw ((false , false , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , true , true) , _) = refl

------------------------------------------------------------------------
-- live-to-permutation specialised at axis-selector-to-live.
--
-- 24 cases × 1 line each (refl by computation through the with).
------------------------------------------------------------------------

live-perm-axis-sel :
  (a : Axis) (sel : Selector) →
  live-to-permutation (axis-selector-to-live (a , sel))
  ≡ embed (v-of-axis a) · stab-from-selector sel
live-perm-axis-sel D sel-fft = refl
live-perm-axis-sel D sel-tft = refl
live-perm-axis-sel D sel-ftf = refl
live-perm-axis-sel D sel-ttf = refl
live-perm-axis-sel D sel-ftt = refl
live-perm-axis-sel D sel-ttt = refl
live-perm-axis-sel C sel-fft = refl
live-perm-axis-sel C sel-tft = refl
live-perm-axis-sel C sel-ftf = refl
live-perm-axis-sel C sel-ttf = refl
live-perm-axis-sel C sel-ftt = refl
live-perm-axis-sel C sel-ttt = refl
live-perm-axis-sel S sel-fft = refl
live-perm-axis-sel S sel-tft = refl
live-perm-axis-sel S sel-ftf = refl
live-perm-axis-sel S sel-ttf = refl
live-perm-axis-sel S sel-ftt = refl
live-perm-axis-sel S sel-ttt = refl
live-perm-axis-sel W sel-fft = refl
live-perm-axis-sel W sel-tft = refl
live-perm-axis-sel W sel-ftf = refl
live-perm-axis-sel W sel-ttf = refl
live-perm-axis-sel W sel-ftt = refl
live-perm-axis-sel W sel-ttt = refl

------------------------------------------------------------------------
-- stab-from-selector ∘ classify-CS-to-selector ≡ orbit-key-to-stab-d ∘
-- classify-CS, pointwise on (a, b).
--
-- 16 cases (4 × 4 axis pairs). Both compositions return the same stab
-- element for each pair; the wildcards in classify-CS and
-- classify-CS-to-selector both default to stab-id.
------------------------------------------------------------------------

stab-from-selector-eq-orbit :
  (a b : Axis) →
  stab-from-selector (classify-CS-to-selector a b)
  ≡ orbit-key-to-stab-d (classify-CS a b)
stab-from-selector-eq-orbit D D = refl
stab-from-selector-eq-orbit D C = refl
stab-from-selector-eq-orbit D S = refl
stab-from-selector-eq-orbit D W = refl
stab-from-selector-eq-orbit C D = refl
stab-from-selector-eq-orbit C C = refl
stab-from-selector-eq-orbit C S = refl
stab-from-selector-eq-orbit C W = refl
stab-from-selector-eq-orbit S D = refl
stab-from-selector-eq-orbit S C = refl
stab-from-selector-eq-orbit S S = refl
stab-from-selector-eq-orbit S W = refl
stab-from-selector-eq-orbit W D = refl
stab-from-selector-eq-orbit W C = refl
stab-from-selector-eq-orbit W S = refl
stab-from-selector-eq-orbit W W = refl

-- Lift to permutations: stab-from-selector ∘ selector-from-stab σ ≈ σ
-- for σ ∈ Stab(D), via the orbit-key bridge.
stab-roundtrip :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  stab-from-selector (selector-from-stab σ) ≈ σ
stab-roundtrip σ σ-stab z =
  trans (cong (λ p → applyₛ p z)
              (stab-from-selector-eq-orbit (applyₛ σ C) (applyₛ σ S)))
        (stab-round-trip σ σ-stab z)

------------------------------------------------------------------------
-- stab-from-selector sel fixes D, for every selector.
-- 6 refls — each canonical Stab(D) element fixes D by construction.
------------------------------------------------------------------------

stab-from-selector-fixes-D :
  (sel : Selector) → applyₛ (stab-from-selector sel) D ≡ D
stab-from-selector-fixes-D sel-fft = refl
stab-from-selector-fixes-D sel-tft = refl
stab-from-selector-fixes-D sel-ftf = refl
stab-from-selector-fixes-D sel-ttf = refl
stab-from-selector-fixes-D sel-ftt = refl
stab-from-selector-fixes-D sel-ttt = refl

------------------------------------------------------------------------
-- Anchor-parametric stab-from-selector. For each anchor X and each
-- Selector, picks the corresponding Stab(X) element via the parametric
-- orbit-key-to-stab-anchor. The X=D specialisation coincides with
-- stab-from-selector up to definitional reduction.
--
-- The selector ↔ OrbitKey bijection is fixed by the convention in
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4.stab-from-selector
-- (which maps Selector → specific stab-X values; we invert through
-- the orbit-key-to-stab-d table).
--
-- The C/S/W siblings of stab-from-selector-fixes-D close the partial
-- coset the detector surfaces on stem 'stab-from-selector-fixes'.
------------------------------------------------------------------------

selector-to-orbit-key : Selector → OrbitKey
selector-to-orbit-key sel-fft = α-pair , even   -- stab-id
selector-to-orbit-key sel-tft = α-pair , odd    -- stab-sw
selector-to-orbit-key sel-ftf = β-pair , odd    -- stab-cs
selector-to-orbit-key sel-ttf = γ-pair , odd    -- stab-cw
selector-to-orbit-key sel-ftt = β-pair , even   -- stab-csw
selector-to-orbit-key sel-ttt = γ-pair , even   -- stab-cws

stab-from-selector-anchor : Axis → Selector → Permutation
stab-from-selector-anchor X sel =
  orbit-key-to-stab-anchor X (selector-to-orbit-key sel)

stab-from-selector-fixes-anchor :
  (X : Axis) (sel : Selector) →
  applyₛ (stab-from-selector-anchor X sel) X ≡ X
stab-from-selector-fixes-anchor X sel =
  orbit-key-to-stab-anchor-fixes X (selector-to-orbit-key sel)

stab-from-selector-fixes-C :
  (sel : Selector) → applyₛ (stab-from-selector-anchor C sel) C ≡ C
stab-from-selector-fixes-C = stab-from-selector-fixes-anchor C

stab-from-selector-fixes-S :
  (sel : Selector) → applyₛ (stab-from-selector-anchor S sel) S ≡ S
stab-from-selector-fixes-S = stab-from-selector-fixes-anchor S

stab-from-selector-fixes-W :
  (sel : Selector) → applyₛ (stab-from-selector-anchor W sel) W ≡ W
stab-from-selector-fixes-W = stab-from-selector-fixes-anchor W

------------------------------------------------------------------------
-- Forward round trip on the Permutation side:
--
--   live-to-permutation (permutation-to-live σ) ≈ σ
--
-- Proof chain:
--   live-to-permutation (axis-selector-to-live (axis-of-v (v-for σ),
--                                               selector-from-stab (s-for σ)))
--   ≡ embed (v-of-axis (axis-of-v (v-for σ))) ·
--     stab-from-selector (selector-from-stab (s-for σ))
--                                        [live-perm-axis-sel]
--   ≡ embed (v-for σ) ·
--     stab-from-selector (selector-from-stab (s-for σ))
--                                        [v-of-axis-axis-of-v-id]
--   ≈ embed (v-for σ) · s-for σ          [stab-roundtrip on s-for σ]
--   ≈ σ                                  [factorisation]
------------------------------------------------------------------------

σ-live-σ-roundtrip :
  (σ : Permutation) →
  live-to-permutation (permutation-to-live σ) ≈ σ
σ-live-σ-roundtrip σ z =
  trans step1 (trans step2 (trans step3 (sym (factorisation σ z))))
  where
    a-σ = axis-of-v (v-for σ)
    sel-σ = selector-from-stab (s-for σ)

    step1 :
      applyₛ (live-to-permutation (permutation-to-live σ)) z
      ≡ applyₛ (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
    step1 = cong (λ p → applyₛ p z) (live-perm-axis-sel a-σ sel-σ)

    step2 :
      applyₛ (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
      ≡ applyₛ (embed (v-for σ) · stab-from-selector sel-σ) z
    step2 =
      cong (λ v → act-axis v (applyₛ (stab-from-selector sel-σ) z))
           (v-of-axis-axis-of-v-id (v-for σ))

    step3 :
      applyₛ (embed (v-for σ) · stab-from-selector sel-σ) z
      ≡ applyₛ (embed (v-for σ) · s-for σ) z
    step3 = cong (act-axis (v-for σ))
                 (stab-roundtrip (s-for σ) (s-for-fixes-D σ) z)

------------------------------------------------------------------------
-- Reverse round trip on the Live side (codeword level).
--
--   proj₁ (permutation-to-live (live-to-permutation lv)) ≡ proj₁ lv
--
-- Proof structure:
--   live-to-permutation lv decodes lv to (a, sel) via slice 11a,
--   then σ = embed (v-of-axis a) · stab-from-selector sel.
--   permutation-to-live σ produces (axis-of-v (v-for σ),
--                                    selector-from-stab (s-for σ)).
--   We need (axis-of-v (v-for σ), selector-from-stab (s-for σ))
--   = (a, sel), so axis-selector-to-live recovers proj₁ lv.
--
-- The two derivations are:
--   * σ.D = a:   applyₛ σ D = act-axis (v-of-axis a) (applyₛ
--                              (stab-from-selector sel) D)
--                            = act-axis (v-of-axis a) D
--                              [stab fixes D]
--                            = a [v-of-axis-sends-D]
--     So v-for σ = v-of-axis (σ.D) = v-of-axis a,
--     and axis-of-v (v-for σ) = axis-of-v (v-of-axis a) = a.
--
--   * selector-from-stab (s-for σ) = sel: shown via
--     selector-from-stab respecting _≈_ and s-for σ ≈
--     stab-from-selector sel.
------------------------------------------------------------------------

-- Helper: for σ ∈ Stab(D), if σ ≈ τ then selector-from-stab σ ≡
-- selector-from-stab τ. (Selector classification depends only on
-- applyₛ at C and S, which are pointwise equivalent.)
selector-from-stab-resp-≈ :
  (σ τ : Permutation) → σ ≈ τ →
  selector-from-stab σ ≡ selector-from-stab τ
selector-from-stab-resp-≈ σ τ σ≈τ =
  cong₂ classify-CS-to-selector (σ≈τ C) (σ≈τ S)

-- Helper: for any (a, sel), s-for (embed (v-of-axis a) ·
-- stab-from-selector sel) ≈ stab-from-selector sel.
--
-- Proof: s-for σ = embed (v-for σ) · σ. With σ = embed v · s
-- (here v = v-of-axis a, s = stab-from-selector sel), v-for σ = v
-- (by v-of-axis-sends-D + stab fixes D), so s-for σ = embed v ·
-- embed v · s ≈ ε · s ≈ s.
s-for-of-live-perm-≈ :
  (a : Axis) (sel : Selector) →
  s-for (embed (v-of-axis a) · stab-from-selector sel)
  ≈ stab-from-selector sel
s-for-of-live-perm-≈ a sel z =
  trans
    (cong (λ v → act-axis v
                  (act-axis (v-of-axis a)
                    (applyₛ (stab-from-selector sel) z)))
          v-for-σ'-eq)
    (act-axis-involutive (v-of-axis a)
                          (applyₛ (stab-from-selector sel) z))
  where
    σ'D≡a : applyₛ (embed (v-of-axis a) · stab-from-selector sel) D ≡ a
    σ'D≡a = trans
              (cong (act-axis (v-of-axis a))
                    (stab-from-selector-fixes-D sel))
              (v-of-axis-sends-D a)

    v-for-σ'-eq :
      v-for (embed (v-of-axis a) · stab-from-selector sel)
      ≡ v-of-axis a
    v-for-σ'-eq = cong v-of-axis σ'D≡a

-- The reverse roundtrip at codeword level.
--
-- The `with live-to-axis-selector lv in p` commits to the decoded
-- (a, sel) so that `live-to-permutation lv` reduces to
-- `embed (v-of-axis a) · stab-from-selector sel = σ'`. The proof then
-- uses the explicit σ' form to derive the round-trip.
live-σ-live-roundtrip :
  (lv : Live) →
  proj₁ (permutation-to-live (live-to-permutation lv))
  ≡ proj₁ lv
live-σ-live-roundtrip lv with live-to-axis-selector lv in p-decoded
... | a , sel =
  trans (cong (λ as → proj₁ (axis-selector-to-live as)) recovers)
        cw-via-roundtrip
  where
    σ' : Permutation
    σ' = embed (v-of-axis a) · stab-from-selector sel

    -- σ'.D = a: by stab fixing D + v-of-axis-sends-D.
    σ'D≡a : applyₛ σ' D ≡ a
    σ'D≡a = trans (cong (act-axis (v-of-axis a))
                        (stab-from-selector-fixes-D sel))
                  (v-of-axis-sends-D a)

    v-for-σ'-eq : v-for σ' ≡ v-of-axis a
    v-for-σ'-eq = cong v-of-axis σ'D≡a

    axis-recovers : axis-of-v (v-for σ') ≡ a
    axis-recovers = trans (cong axis-of-v v-for-σ'-eq)
                          (axis-of-v-v-of-axis-id a)

    selector-recovers : selector-from-stab (s-for σ') ≡ sel
    selector-recovers =
      trans (selector-from-stab-resp-≈ (s-for σ')
                                        (stab-from-selector sel)
                                        (s-for-of-live-perm-≈ a sel))
            (selector-stab-id sel)

    recovers :
      (axis-of-v (v-for σ') , selector-from-stab (s-for σ'))
      ≡ (a , sel)
    recovers = cong₂ _,_ axis-recovers selector-recovers

    -- Use p-decoded : live-to-axis-selector lv ≡ (a, sel) to relate
    -- axis-selector-to-live (a, sel) back to axis-selector-to-live
    -- (live-to-axis-selector lv), then close via slice 11a's
    -- codeword roundtrip.
    cw-via-roundtrip : proj₁ (axis-selector-to-live (a , sel)) ≡ proj₁ lv
    cw-via-roundtrip =
      trans (cong (λ as → proj₁ (axis-selector-to-live as))
                  (sym p-decoded))
            (axis-selector-roundtrip-cw lv)

------------------------------------------------------------------------
-- The bundled bijection.
--
-- Live ≃ Permutation as a constructive bijection: forward map,
-- reverse map, and the two round-trip lemmas. Custom record because
-- stdlib's _↔_ needs _≡_ on both sides, but Permutation uses _≈_
-- and Live's Σ-type's ¬-component would require funext.
------------------------------------------------------------------------

record Live≃Permutation : Set where
  field
    to       : Live → Permutation
    from     : Permutation → Live
    to-from  : (σ : Permutation) → to (from σ) ≈ σ
    from-to  : (lv : Live) → proj₁ (from (to lv)) ≡ proj₁ lv

Live≃Permutation-bijection : Live≃Permutation
Live≃Permutation-bijection = record
  { to      = live-to-permutation
  ; from    = permutation-to-live
  ; to-from = σ-live-σ-roundtrip
  ; from-to = live-σ-live-roundtrip
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. The combinatorial discipline pays off again: this slice has
--    ~270 lines, of which ~120 are mechanical refls (the 24+24+24+16
--    case enumerations) and ~50 are structural proof chains. The
--    deep mathematics (V_4 ⋊ S_3 ≅ S_4, V_4 normality, stab-round-
--    trip) lives in earlier slices; this module just composes them.
--
-- 2. The codeword-level reverse round-trip lets us bundle the
--    bijection without funext. The full Σ-type equality (codeword AND
--    ¬-IsReserved proof) would need funext to nail down the ¬-
--    component, which we don't have.
--
-- 3. Cross-references:
--    - Substrate.Cocycles.V4Signature.Codeword (slice 10) — ambient.
--    - .Codeword.Live (slice 11a) — Selector + decoding.
--    - .Codeword.LiveS4 (slice 11b) — forward map.
--    - .Codeword.LiveS4Iso (slice 11c) — reverse map + algebraic
--      identities.
--    - Substrate.Groups.SemidirectProduct (slice 3) — factorisation.
--    - Substrate.Cocycles.V4Signature.S4Iso (slice 4) — stab-round-
--      trip + the 6 canonical Stab(D) elements.
------------------------------------------------------------------------
