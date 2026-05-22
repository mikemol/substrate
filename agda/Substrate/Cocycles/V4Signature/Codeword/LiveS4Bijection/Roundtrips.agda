------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Roundtrips
--
-- The mechanical case-enumeration round-trip lemmas for the
-- Live ↔ Permutation bijection:
--   * axis-selector-roundtrip    — 24 refls
--   * axis-selector-roundtrip-cw — 24+1 refls + ⊥-elim
--   * live-perm-axis-sel         — 24 refls
--   * stab-from-selector-eq-orbit — 16 refls
--   * stab-from-selector-fixes-D — 6 refls
--   * stab-roundtrip             — pointwise lift
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Roundtrips where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4
  using (Permutation; _≈_; _·_)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (Stab; v-of-axis)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (orbit-key-to-stab-d; stab-round-trip)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Live)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt; live-to-axis-selector; axis-selector-to-live)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (stab-from-selector; live-to-permutation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
  using (classify-CS-to-selector; selector-from-stab)

------------------------------------------------------------------------
-- Axis × Selector → Live → Axis × Selector ≡ id (24 refls).
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- Reverse at codeword level. 8 reserved patterns ruled out via ¬res.
------------------------------------------------------------------------

axis-selector-roundtrip-cw :
  (lv : Live) →
  proj₁ (axis-selector-to-live (live-to-axis-selector lv)) ≡ proj₁ lv
axis-selector-roundtrip-cw ((_ , _ , _ , false , false) , ¬res) =
  ⊥-elim (¬res (refl , refl))
axis-selector-roundtrip-cw ((false , false , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , false , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , false , true) , _) = refl
axis-selector-roundtrip-cw ((false , false , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , true , false) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , true , false) , _) = refl
axis-selector-roundtrip-cw ((false , false , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , false , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , false , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((false , true  , true  , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , false , true , true) , _) = refl
axis-selector-roundtrip-cw ((true  , true  , true  , true , true) , _) = refl

------------------------------------------------------------------------
-- live-to-permutation specialised at axis-selector-to-live (24 refls).
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
-- classify-CS, pointwise (16 refls).
------------------------------------------------------------------------

open import Substrate.Cocycles.V4Signature.S4Iso using (classify-CS)

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
  (σ : Permutation) (σ-stab : Stab D σ) →
  stab-from-selector (selector-from-stab σ) ≈ σ
stab-roundtrip σ σ-stab z =
  trans (cong (λ p → applyₛ p z)
              (stab-from-selector-eq-orbit (applyₛ σ C) (applyₛ σ S)))
        (stab-round-trip σ σ-stab z)

------------------------------------------------------------------------
-- stab-from-selector sel fixes D, for every selector (6 refls).
------------------------------------------------------------------------

stab-from-selector-fixes-D :
  (sel : Selector) → applyₛ (stab-from-selector sel) D ≡ D
stab-from-selector-fixes-D sel-fft = refl
stab-from-selector-fixes-D sel-tft = refl
stab-from-selector-fixes-D sel-ftf = refl
stab-from-selector-fixes-D sel-ttf = refl
stab-from-selector-fixes-D sel-ftt = refl
stab-from-selector-fixes-D sel-ttt = refl
