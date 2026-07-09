{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQ — ⟡FU-sep-Q: discharge FUSepConv's value-reflect (the ℚ-side
-- retraction) for the FINITE IMAGE, mirroring CFInvariance.
--
-- THE DISSOLUTION: value-reflect looks coinductive (the ≋-retraction: bisimilar
-- values ⟹ convertible). But on the FINITE IMAGE the object is a FINITE Böhm
-- tree — the CF TERMINATES — so the coinductive ≋ COLLAPSES to inductive ≡ by
-- STRUCTURAL INDUCTION, exactly as CFInvariance's shape-value-invariance inducts
-- on the finite EEATrace (head determined by divmod-unique, tails by IH). The
-- invariant: bisimilarity of FINITE values is decided by structural induction.
--
-- bt-reflect (below) IS that: bisimilar finite Böhm trees are EQUAL. It is the
-- RETRACTION leg R → ℚ of the ℚ ⊣ R adjunction (convergent recovers the rational
-- from its finite CF prefix), and it discharges the Coincidence's value-reflect
-- CONCRETELY — the finite BT model builds a full FUSepConv.Adjunction with
-- bt-reflect as coin-obs (the "same value ⟹ same shape" head-to-tail projection).
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQ where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.List    using (List; []; _∷_)
import Substrate.FUSep.FUSepConv as FUSepConv

private
  ≡sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
  ≡sym refl = refl
  ≡trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
  ≡trans refl q = q
  cong₂ : {A B C : Set} (f : A → B → C) {x x' : A} {y y' : B}
        → x ≡ x' → y ≡ y' → f x y ≡ f x' y'
  cong₂ f refl refl = refl

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
  finSetoid : FUSepConv.EqSetoid BT _≡_
  finSetoid = record { refl≈ = refl ; sym≈ = ≡sym ; trans≈ = ≡trans }

  coinSetoid : FUSepConv.EqSetoid BT _≈BT_
  coinSetoid = record { refl≈ = ≈BT-refl ; sym≈ = ≈BT-sym ; trans≈ = ≈BT-trans }

  ≡⟹≈BT : ∀ {u v} → u ≡ v → u ≈BT v
  ≡⟹≈BT refl = ≈BT-refl

  adjBT : FUSepConv.Adjunction BT BT
  adjBT = record
    { _≈ᶠ_     = _≡_
    ; _≈ᶜ_     = _≈BT_
    ; Fin      = finSetoid
    ; Coin     = coinSetoid
    ; obs      = λ x → x
    ; fwd      = ≡⟹≈BT
    ; coin-obs = bt-reflect      -- THE ℚ-side retraction, the CFInvariance shape
    ; fin-obs  = λ e → e
    }

  open FUSepConv.Coincidence {BT} {BT} adjBT (λ ra rb e → e) public
