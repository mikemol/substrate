------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationBimonoidal
--
-- ⟡rig-11 — THE UNIFYING FRAME (the generic record). The recursive-common-structure
-- endpoint of the whole arc: ⊕ and ⊗ are ONE structure — a graded product over a grading
-- MONOID — differing only in the grading (ℕ,+,0) vs (ℕ,·,1).
--
--   GradedProductOver (op)(ε)(C) = { u : C ε ; _∧_ : C i → C j → C (op i j) }
--
-- The existing Algebra.Wedge.Product.GradedProduct is exactly GradedProductOver _+_ 0.
-- This module is PROOF-FREE (def/proof separation): the concrete instances (⊕-over,
-- ⊗-over) and the fact that both associators instantiate the ONE generic law live in
-- .Properties. The full four-law table (assoc/unit/comm-iso/comm-nat on both fibres, all
-- proven this arc) is documented there.
--
-- (Reuse-search catalog.db: no bimonoidal/rig-category record exists; Category.Symmetric-
-- Monoidal needs a full CategoryOf of orderings — heavier.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationBimonoidal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; subst)

------------------------------------------------------------------------
-- The parameterized structure: a graded product over a grading operation (op, ε).
------------------------------------------------------------------------

record GradedProductOver (op : ℕ → ℕ → ℕ) (ε : ℕ) (C : ℕ → Set) : Set where
  field
    u   : C ε
    _∧_ : {i j : ℕ} → C i → C j → C (op i j)

open GradedProductOver public

-- the generic associativity law-type over the grading operation's own associativity.
GradedAssocOver : {op : ℕ → ℕ → ℕ} {ε : ℕ} {C : ℕ → Set}
                  (assoc : (x y z : ℕ) → op (op x y) z ≡ op x (op y z))
                  (P : GradedProductOver op ε C) → Set
GradedAssocOver {C = C} assoc P =
  ∀ {i j k} (a : C i) (b : C j) (c : C k) →
  subst C (assoc i j k) (_∧_ P (_∧_ P a b) c) ≡ _∧_ P a (_∧_ P b c)

------------------------------------------------------------------------
-- ⟡lift-generic — THE GRADED HOMOMORPHISM, over an arbitrary grading (op, ε) AND an
-- arbitrary TARGET EQUALITY. This is the recursive bottom of the ⊕/⊗ tower: fold-⊕
-- (the additive catamorphism-hom) and ⊗-combine (the multiplicative lookup-hom) are
-- ONE structure — a map preserving u and _∧_ — differing ONLY in the target equality:
--   * additive: the target carrier is DATA, so _≈_ = _≡_ (strict);
--   * multiplicative: the target carrier is a Fin-endofunction Fin n → Fin n, so _≈_ is
--     POINTWISE equality (lookup-extensional) — the funext-free reading of the same law.
-- The target equality is a PARAMETER, not a picked side: a homomorphism is always valued
-- in the codomain's equality. (Algebra.Wedge.Product.Hom.GradedHom is the (+,0,≡) case;
-- this generalizes the grading op AND relaxes ≡ to any _≈_, so BOTH fibres are instances.)
--
-- Law-free by design (the 3 hom fields only): instances CONSTRUCT it; id/∘ composition
-- (which would need _≈_ an equivalence) is out of scope here.
------------------------------------------------------------------------

record GradedHomOver
  {op : ℕ → ℕ → ℕ} {ε : ℕ} {Cᴾ Cᴽ : ℕ → Set}
  (P : GradedProductOver op ε Cᴾ) (Q : GradedProductOver op ε Cᴽ)
  (_≈_ : {n : ℕ} → Cᴽ n → Cᴽ n → Set) : Set where
  field
    map₀  : {n : ℕ} → Cᴾ n → Cᴽ n
    map-u : map₀ (u P) ≈ u Q
    map-∧ : {i j : ℕ} (a : Cᴾ i) (b : Cᴾ j) →
            map₀ (_∧_ P a b) ≈ _∧_ Q (map₀ a) (map₀ b)

open GradedHomOver public

------------------------------------------------------------------------
-- ⟡lift-generic (comm-iso level) — THE GRADED INDEX-BRAIDING: the involutive index-swap
-- that witnesses commutativity of a grading op up to iso. blockSwap (⟡rig-6, over +, the
-- ⊎-swap via splitAt) and factorSwap (⟡rig-8, over *, the ×-swap via remQuot) are ONE
-- structure — an order-2 self-inverse family Fin(op m n) → Fin(op n m). The naive lift
-- (abstracting the decomposition target ⊎-vs-× as a field D : ℕ → ℕ → Set) would be Set₁,
-- the enemy; but the INVARIANT is Set₀ — a family of Fin-maps with an involution law, the
-- decomposition never held. The instance-specific L/R characterizations (which mention
-- inject+ / combine) stay in the fibres; the braiding-and-involution invariant lifts here.
------------------------------------------------------------------------

record GradedBraid (op : ℕ → ℕ → ℕ) : Set where
  field
    braid       : ∀ m n → Fin (op m n) → Fin (op n m)
    braid-invol : ∀ m n (k : Fin (op m n)) → braid n m (braid m n k) ≡ k

open GradedBraid public

------------------------------------------------------------------------
-- Endo: finite endofunctions Fin n → Fin n — the READOUT carrier, shared by the graded
-- hom's multiplicative target and the naturality layer below. (A permutation, a fold's
-- decoded action: everything reads out to an endofunction; pointwise equality on Endo is
-- the funext-free target equality — Perm = Vec, lookup-extensional.)
------------------------------------------------------------------------

Endo : ℕ → Set
Endo n = Fin n → Fin n

------------------------------------------------------------------------
-- ⟡rig-UP-nat — THE BRAIDING IS NATURAL w.r.t. a readout ρ : C n → Endo n. The two
-- naturality squares of the arc — ⊕-comm-nat (blockSwap over +) and ⊗-comm-nat (factorSwap
-- over *) — are ONE coherence: reading out the op-SWAPPED product at a BRAIDED index equals
-- braiding the readout of the original product. This couples GradedBraid (the index-swap)
-- with the hom's readout — the symmetric-monoidal σ made natural, uniform over the grading
-- op. Set₀, pointwise (no funext). A predicate; the fibres CONSTRUCT it from the already-
-- proven comm-nat lemmas (the hard content stays in the fibres, the shape lifts here).
------------------------------------------------------------------------

GradedBraidNatural : {op : ℕ → ℕ → ℕ} {ε : ℕ} {C : ℕ → Set}
                     (B : GradedBraid op) (P : GradedProductOver op ε C)
                     (ρ : {n : ℕ} → C n → Endo n) → Set
GradedBraidNatural {op = op} {C = C} B P ρ =
  ∀ {m n} (x : C m) (y : C n) (k : Fin (op m n)) →
  ρ (_∧_ P y x) (braid B m n k) ≡ braid B m n (ρ (_∧_ P x y) k)

------------------------------------------------------------------------
-- ⟡rig-UP-map — THE GRADED BIFUNCTOR: the product's action ON MORPHISMS. ⊕map (over +,
-- the ⊎-split) and ⊗map (over *, the ×-split) are ONE structure — a map lifting a pair of
-- index-functions (Fin m→Fin m', Fin n→Fin n') to Fin(op m n)→Fin(op m' n'), FUNCTORIALLY
-- (identity + composition). Crucially the functoriality LAWS are DECOMPOSITION-FREE (they
-- mention only gmap, id, ∘ — never inject+/combine), so this lifts to a Set₀ invariant just
-- like the braid; only the fibres' PROOFS touch the ⊎/× split. (This is the level that a
-- too-hasty earlier reading called "decomposition-bound, does not lift" — the char lemmas
-- are decomposition-bound, but the functoriality laws that make a bifunctor are not.)
------------------------------------------------------------------------

record GradedBifunctor (op : ℕ → ℕ → ℕ) : Set where
  field
    gmap    : ∀ {m n m' n'} → (Fin m → Fin m') → (Fin n → Fin n') →
              Fin (op m n) → Fin (op m' n')
    gmap-id : ∀ {m n} (k : Fin (op m n)) →
              gmap {m} {n} {m} {n} (λ i → i) (λ j → j) k ≡ k
    gmap-∘  : ∀ {m n m' n' m'' n''}
              (f : Fin m' → Fin m'') (f' : Fin m → Fin m')
              (g : Fin n' → Fin n'') (g' : Fin n → Fin n') (k : Fin (op m n)) →
              gmap (λ i → f (f' i)) (λ j → g (g' j)) k ≡ gmap f g (gmap f' g' k)

open GradedBifunctor public

------------------------------------------------------------------------
-- ⟡rig-UP-cat (Set₀ capstone) — A GRADED SYMMETRIC MONOIDAL STRUCTURE: the bundle of the
-- whole arc's decomposition-free invariants for ONE grading (op, ε). ⊕ and ⊗ are each an
-- INSTANCE — the "recursively, ONE structure" endpoint: the two monoidal halves of the rig
-- differ only in the grading (ℕ,+,0) vs (ℕ,·,1). Carrier C and readout ρ are PARAMETERS,
-- never fields, so this stays Set₀ — the whole point of the mission.
--
-- This is a bundled WITNESS that the orientation rig satisfies the symmetric-monoidal
-- axioms. It is NOT the categorical universal property (initiality among symmetric rig
-- CATEGORIES): that quantifies over category-targets and is irreducibly Set₁ (a
-- grade-collapse), deliberately not built here. The full RIG adds the distributor + Laplaza
-- coherences (OrientationDistributor*), a further pure-assembly step over two of these.
------------------------------------------------------------------------

record GradedSymMonoidal
  (op : ℕ → ℕ → ℕ) (ε : ℕ) (C : ℕ → Set)
  (assoc : (x y z : ℕ) → op (op x y) z ≡ op x (op y z))
  (ρ : {n : ℕ} → C n → Endo n) : Set where
  field
    product   : GradedProductOver op ε C
    prodAssoc : GradedAssocOver assoc product
    braiding  : GradedBraid op
    braidNat  : GradedBraidNatural braiding product ρ
    bifunctor : GradedBifunctor op

open GradedSymMonoidal public
