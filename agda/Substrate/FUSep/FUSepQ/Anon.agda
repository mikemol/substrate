------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQ.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQ; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQ.Anon where

open import Substrate.Foundation.List
open import Substrate.FUSep.FUSepConv.Adjunction
open import Substrate.FUSep.FUSepConv.Anon
open import Substrate.FUSep.FUSepConv.EqSetoid
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQ.Eqsym
open import Substrate.FUSep.FUSepQ.Eqtrans
open import Substrate.FUSep.FUSepQ.Cong2



module _ (H : Set) where

  -- FINITE Böhm tree: the ℚ side (finite CF / normal form). `node head children`.
  data BT : Set where
    node : H → List BT → BT

  -- BT-bisimilarity: same head (the "leading quotient") + children bisimilar
  -- (the "cross-equation for the tails"). Mutual with its list lifting.
  data _≈BT_ : BT → BT → Set
  data _≈L_  : List BT → List BT → Set
  data _≈BT_ where
    node≈ : ∀ {h₁ h₂ cs ds} → h₁ ≡ h₂ → cs ≈L ds → (node h₁ cs) ≈BT (node h₂ ds)
  data _≈L_ where
    []≈  : [] ≈L []
    _∷≈_ : ∀ {x y xs ys} → x ≈BT y → xs ≈L ys → (x ∷ xs) ≈L (y ∷ ys)

  ------------------------------------------------------------------
  -- THE CFInvariance-SHAPED THEOREM: bisimilar FINITE Böhm trees are EQUAL, by
  -- STRUCTURAL INDUCTION. The coinductive ≋ collapses to ≡ because the tree is
  -- finite (the CF terminates). This is the retraction on the finite image.
  ------------------------------------------------------------------
  bt-reflect : ∀ {u v} → u ≈BT v → u ≡ v
  l-reflect  : ∀ {xs ys} → xs ≈L ys → xs ≡ ys
  bt-reflect (node≈ h≡ cs) = cong₂ node h≡ (l-reflect cs)
  l-reflect []≈         = refl
  l-reflect (p ∷≈ ps)   = cong₂ _∷_ (bt-reflect p) (l-reflect ps)

  ------------------------------------------------------------------
  -- ≈BT is an equivalence (so it is a Setoid — the Coin side of the adjunction).
  ------------------------------------------------------------------
  ≈BT-refl : ∀ {u} → u ≈BT u
  ≈L-refl  : ∀ {xs} → xs ≈L xs
  ≈BT-refl {node h cs} = node≈ refl ≈L-refl
  ≈L-refl {[]}     = []≈
  ≈L-refl {x ∷ xs} = ≈BT-refl ∷≈ ≈L-refl

  ≈BT-sym : ∀ {u v} → u ≈BT v → v ≈BT u
  ≈L-sym  : ∀ {xs ys} → xs ≈L ys → ys ≈L xs
  ≈BT-sym (node≈ h≡ cs) = node≈ (≡sym h≡) (≈L-sym cs)
  ≈L-sym []≈        = []≈
  ≈L-sym (p ∷≈ ps)  = ≈BT-sym p ∷≈ ≈L-sym ps

  ≈BT-trans : ∀ {u v w} → u ≈BT v → v ≈BT w → u ≈BT w
  ≈L-trans  : ∀ {xs ys zs} → xs ≈L ys → ys ≈L zs → xs ≈L zs
  ≈BT-trans (node≈ h₁ cs₁) (node≈ h₂ cs₂) = node≈ (≡trans h₁ h₂) (≈L-trans cs₁ cs₂)
  ≈L-trans []≈ []≈               = []≈
  ≈L-trans (p ∷≈ ps) (q ∷≈ qs)  = ≈BT-trans p q ∷≈ ≈L-trans ps qs

  ------------------------------------------------------------------
  -- DISCHARGE FUSepConv.Coincidence for the finite BT model. obs = id (the
  -- finite value's observation IS its Böhm tree — the finite CF); Fin = (BT, ≡);
  -- Coin = (BT, ≈BT); fwd = ≡⟹≈BT; coin-obs = bt-reflect (THE retraction);
  -- fin-obs = id; value-reflect = id (trivial once obs = id — the real content
  -- is bt-reflect in coin-obs). Then unit-id-on-finite: ≡ = ≈BT on finite BTs.
  ------------------------------------------------------------------
  -- ⟡set1-paydown: EqSetoid now parameterizes its relation (`EqSetoid C _≈_`), and
  -- Adjunction carries the two relations as _≈ᶠ_/_≈ᶜ_ fields.
  finSetoid : EqSetoid BT _≡_
  finSetoid = record { refl≈ = refl ; sym≈ = ≡sym ; trans≈ = ≡trans }

  coinSetoid : EqSetoid BT _≈BT_
  coinSetoid = record { refl≈ = ≈BT-refl ; sym≈ = ≈BT-sym ; trans≈ = ≈BT-trans }

  ≡⟹≈BT : ∀ {u v} → u ≡ v → u ≈BT v
  ≡⟹≈BT refl = ≈BT-refl

  adjBT : Adjunction BT BT _≡_ _≈BT_
  adjBT = record
    { Fin      = finSetoid
    ; Coin     = coinSetoid
    ; obs      = λ x → x
    ; fwd      = ≡⟹≈BT
    ; coin-obs = bt-reflect      -- THE ℚ-side retraction, the CFInvariance shape
    ; fin-obs  = λ e → e
    }

  open Coincidence {BT} {BT} adjBT (λ ra rb e → e) public
