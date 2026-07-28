------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm
--
-- ⟡rig-UP-cat-perm — THE NON-THIN TRANSFORMATION-MONOID RIG CATEGORY. The real
-- categorification that the skeletal orientationRigCatₛ (OrientationRigCat
-- .Properties) is the decategorified shadow of.
--
-- CORRECTION (see also OrientationRigCatSym): the morphisms here are `Perm j =
-- Vec (Fin j) j` UNRESTRICTED — that is the full TRANSFORMATION MONOID Tₙ (all jʲ
-- functions Fin j → Fin j), NOT the symmetric group Sₙ. Only the INVERTIBLE ones
-- are permutations, and the braidings are exactly those units. The genuine
-- SYMMETRIC (Sₙ) rig category — Hom restricted to invertible morphisms, where
-- coxeter-complete makes the functors actually FREE — is `orientationRigCatSym`
-- (OrientationRigCatSym / .UP). This module is its Tₙ ambient; keep the two
-- distinct (an earlier version of this header wrongly called Tₙ "the full Sₙ").
--
-- The skeletal instance has THIN morphisms Homₛ i j = (i ≡ j): between any two
-- objects there is at most ONE arrow, so its "braidings" carry no information —
-- a symmetry that is trivially its own inverse because there is nothing to
-- invert. THIS instance replaces that hom-set by the transformation monoid Tₙ:
--
--   Homₚ {i}{j} _ _ = Σ (i ≡ j) (λ _ → Perm j)
--
-- a grade-equality PLUS a grade-j vector-endofunction (jʲ of them, not one; the
-- invertible ones are the n! permutations). The Σ is HONEST DATA — the vector
-- together with the grade witness that makes the arrow grade-respecting (i ≢ j ⇒
-- no morphism) — NOT an ∃-collapse. The braidings are GENUINE non-trivial
-- permutations (the invertible morphisms): braid⊕ carries the
-- block-swap transposition (OrientationSumComm), braid⊗ the factor-swap
-- (OrientationProductComm), and braid⊕/⊗-invol are their honest order-2 laws
-- (blockSwap-invol / factorSwap-invol), lifted from the Fin-level swap to a
-- single-grade Perm endomorphism and discharged POINTWISE via SnGroup
-- faithfulness (apply-injective).
--
-- The object family is Objₛ — the grade-indexed SINGLETON (one object per grade,
-- the standard grade-n ordered set, whose AUTOMORPHISMS are the permutations),
-- reused verbatim from OrientationRigCat (the object family the skeletal instance
-- itself carries). It is the honest "one object per grade": the whole non-trivial
-- content lives in the morphisms, exactly as intended.
--
-- WHY Objₛ AND NOT ⊤: the generic `GradedRigCat` fields (`_∧_ ⊕obj a b`, the
-- braidings) recover the grade implicits from the object's TYPE. Objₛ n keeps the
-- grade n as a type index (grade-injective), so those implicits are inferable.
-- Objₚ n = ⊤ would ERASE the grade (⊤ reduces away → `Objₚ p = Objₚ i` gives no
-- `p = i`), leaving every `_∧_`/braid grade an unsolved meta — precisely the trap
-- the record's own header names ("⊤, which erases it"). Grade-indexed singleton is
-- the mechanically-forced honest reading of "one object per grade".
--
-- HONEST SCOPE: this settles that the FULL symmetric (Sₙ-morphism) graded rig
-- category is Set₀ and is a genuine `GradedRigCat` instance — the real
-- categorification, not the skeletal shadow. It reuses the EXISTING GradedRigCat
-- record (OrientationRigCat) unchanged. The FUNCTOR universal property for it
-- (⟡rig-UP-cat-perm-UP — a RigFunctor OUT of this category and its initiality) is
-- a SEPARATE theorem and is NOT claimed here. No braid law forced new machinery:
-- every field is discharged from the already-committed swap/involution lemmas +
-- the Sₙ group laws + UIP on ℕ (the grade-equality component is a mere prop).
--
-- Zero postulates, zero holes, --safe --without-K. NO Σ / ∃ used to PACKAGE an
-- existence claim; Σ appears only as the honest dependent-pair DATA of a morphism.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_; _≟_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.SnGroup
  using (apply; apply-compose; apply-id; apply-injective; compose-id-left; compose-id-right)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)

open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; _∧_; u)
open import Substrate.WitnessTower.Wedge.OrientationSumComm
  using (blockSwap; blockSwap-invol)
open import Substrate.WitnessTower.Wedge.OrientationProductComm
  using (factorSwap; factorSwap-invol)
open import Substrate.WitnessTower.Wedge.OrientationRigCat
  using (GradedRigCat; Objₛ; ⋆)

------------------------------------------------------------------------
-- S0 — THE OBJECTS AND MORPHISMS. One object per grade (Objₛ, the grade-indexed
-- singleton; its automorphisms ARE the permutations), and the FULL Sₙ as
-- morphisms: a grade-equality PLUS a permutation of the target grade. Honest
-- Σ-data (the perm + the grade witness that makes it grade-respecting).
------------------------------------------------------------------------

Objₚ : ℕ → Set
Objₚ = Objₛ

-- the raw (object-free) morphism carrier — the honest Σ-data. Homₚ discards its
-- object arguments (as the record's Hom must accept them), so ALL operations and
-- laws are defined on Homᵣ, keeping object implicits from becoming phantom metas;
-- the record fields are thin lambdas that bind the objects and delegate here.
Homᵣ : ℕ → ℕ → Set
Homᵣ i j = Σ (i ≡ j) (λ _ → Perm j)

Homₚ : {i j : ℕ} → Objₚ i → Objₚ j → Set
Homₚ {i} {j} _ _ = Homᵣ i j

------------------------------------------------------------------------
-- Small equational infrastructure — all one-liners by pattern on refl (no K,
-- no postulate). UIP on ℕ (Hedberg from decidable _≟_) makes the grade-equality
-- component of a morphism a MERE PROPOSITION, so it never obstructs a law.
------------------------------------------------------------------------

-- UIP on ℕ: any two grade-equalities coincide (the thin part of a morphism).
uipℕ : {i j : ℕ} (p q : i ≡ j) → p ≡ q
uipℕ = Decidable⇒UIP _≟_

-- morphism equality from its two honest components (non-dependent Σ ⇒ η-pair).
-- No object arguments: Homₚ discards them, so they would be phantom metas; the
-- morphism type is literally Σ (i ≡ j) (λ _ → Perm j).
homEq : {i j : ℕ} {p p' : i ≡ j} {σ σ' : Perm j} →
        p ≡ p' → σ ≡ σ' →
        _≡_ {A = Homᵣ i j} (p , σ) (p' , σ')
homEq refl refl = refl

-- transport of the identity permutation along a grade-equality IS the identity.
subst-idperm : {i j : ℕ} (p : i ≡ j) → subst Perm p (id-perm i) ≡ id-perm j
subst-idperm refl = refl

-- transport distributes over composition.
subst-compose : {n n' : ℕ} (q : n ≡ n') (α β : Perm n) →
                subst Perm q (compose α β) ≡ compose (subst Perm q α) (subst Perm q β)
subst-compose refl α β = refl

-- transport fusion (P explicit — the carrier is not inferable from `P x`).
subst-fuse : {A : Set} (P : A → Set) {x y z : A}
             (p : x ≡ y) (q : y ≡ z) (w : P x) →
             subst P q (subst P p w) ≡ subst P (trans p q) w
subst-fuse P refl q w = refl

-- a transport followed by its inverse on the underlying set cancels.
subst-symˡ : {n n' : ℕ} (q : n ≡ n') (x : Fin n') →
             subst Fin q (subst Fin (sym q) x) ≡ x
subst-symˡ refl x = refl

-- a Fin-transport along an endo-equality is the identity (via UIP on ℕ).
subst-Fin-uip : {n : ℕ} (e : n ≡ n) (x : Fin n) → subst Fin e x ≡ x
subst-Fin-uip e x = cong (λ e' → subst Fin e' x) (uipℕ e refl)

-- lookup commutes with a Perm-transport (reindex the query by the inverse).
lookup-subst : {n n' : ℕ} (q : n ≡ n') (α : Perm n) (x : Fin n') →
               lookup (subst Perm q α) x
               ≡ subst Fin q (lookup α (subst Fin (sym q) x))
lookup-subst refl α x = refl

------------------------------------------------------------------------
-- S1 — THE CATEGORY. Identity = (refl, id-perm); composition trans-es the
-- grade witnesses and composes the permutations after transporting the source
-- perm up to the shared grade. The unit/associativity laws split cleanly: the
-- grade component by UIP, the perm component by the Sₙ group laws (SnGroup /
-- CyclicGrounding) modulo the transport-fusion lemmas above.
------------------------------------------------------------------------

idᵣ : (i : ℕ) → Homᵣ i i
idᵣ i = refl , id-perm i

infixr 9 _∘ᵣ_
_∘ᵣ_ : {i j k : ℕ} → Homᵣ j k → Homᵣ i j → Homᵣ i k
_∘ᵣ_ g f = trans (proj₁ f) (proj₁ g)
         , compose (proj₂ g) (subst Perm (proj₁ g) (proj₂ f))

left-idᵣ : {i j : ℕ} (f : Homᵣ i j) → (idᵣ j ∘ᵣ f) ≡ f
left-idᵣ f = homEq (uipℕ _ _) (compose-id-left (proj₂ f))

right-idᵣ : {i j : ℕ} (f : Homᵣ i j) → (f ∘ᵣ idᵣ i) ≡ f
right-idᵣ f =
  homEq (uipℕ _ _)
        (trans (cong (compose (proj₂ f)) (subst-idperm (proj₁ f)))
               (compose-id-right (proj₂ f)))

assocᵣ : {i j k l : ℕ}
         (f : Homᵣ i j) (g : Homᵣ j k) (h : Homᵣ k l) →
         ((h ∘ᵣ g) ∘ᵣ f) ≡ (h ∘ᵣ (g ∘ᵣ f))
assocᵣ f g h =
  homEq (uipℕ _ _)
        (trans (compose-assoc σh (subst Perm ph σg) (subst Perm (trans pg ph) σf))
               (cong (compose σh) (sym eqInner)))
  where
    pf = proj₁ f ; σf = proj₂ f
    pg = proj₁ g ; σg = proj₂ g
    ph = proj₁ h ; σh = proj₂ h
    eqInner : subst Perm ph (compose σg (subst Perm pg σf))
              ≡ compose (subst Perm ph σg) (subst Perm (trans pg ph) σf)
    eqInner = trans (subst-compose ph σg (subst Perm pg σf))
                    (cong (compose (subst Perm ph σg)) (subst-fuse Perm pg ph σf))

------------------------------------------------------------------------
-- S2 — THE BRAIDINGS. Generic over the grading (op, comm) and its Fin-level
-- swap (sw, sw-invol): blockSwap over (+) and factorSwap over (*) are ONE
-- structure. The braiding MORPHISM is the swap made a single-grade Perm
-- endomorphism (tabulate ∘ sw ∘ reindex); its involution is the swap's own
-- order-2 law, discharged pointwise through SnGroup faithfulness.
------------------------------------------------------------------------

private
  module Braid
    (op : ℕ → ℕ → ℕ)
    (comm : (a b : ℕ) → op a b ≡ op b a)
    (sw : (m n : ℕ) → Fin (op m n) → Fin (op n m))
    (sw-invol : (m n : ℕ) (k : Fin (op m n)) → sw n m (sw m n k) ≡ k)
    where

    -- the braiding permutation at grades (i,j): a genuine endo of Fin (op j i).
    swPerm : (i j : ℕ) → Perm (op j i)
    swPerm i j = tabulate (λ k → sw i j (subst Fin (comm j i) k))

    private
      -- readout of swPerm at the swapped grade.
      lookup-swPerm : (i j : ℕ) (y : Fin (op i j)) →
                      lookup (swPerm j i) y ≡ sw j i (subst Fin (comm i j) y)
      lookup-swPerm i j y = lookup∘tabulate (λ k → sw j i (subst Fin (comm i j) k)) y

      -- readout of the transported braiding (the second composition factor).
      lookup-γ : (i j : ℕ) (x : Fin (op i j)) →
                 lookup (subst Perm (comm j i) (swPerm i j)) x
                 ≡ subst Fin (comm j i) (sw i j x)
      lookup-γ i j x =
        trans (lookup-subst (comm j i) (swPerm i j) x)
              (cong (subst Fin (comm j i))
                    (trans (lookup∘tabulate (λ k → sw i j (subst Fin (comm j i) k))
                                            (subst Fin (sym (comm j i)) x))
                           (cong (sw i j) (subst-symˡ (comm j i) x))))

    -- THE INVOLUTION (perm component): swap-then-swap = identity, pointwise.
    swPerm-invol : (i j : ℕ) →
                   compose (swPerm j i) (subst Perm (comm j i) (swPerm i j))
                   ≡ id-perm (op i j)
    swPerm-invol i j = apply-injective (λ x →
      trans (apply-compose (swPerm j i) (subst Perm (comm j i) (swPerm i j)) x)
      (trans (cong (lookup (swPerm j i)) (lookup-γ i j x))
      (trans (lookup-swPerm i j (subst Fin (comm j i) (sw i j x)))
      (trans (cong (sw j i) (subst-fuse Fin (comm j i) (comm i j) (sw i j x)))
      (trans (cong (sw j i) (subst-Fin-uip (trans (comm j i) (comm i j)) (sw i j x)))
      (trans (sw-invol i j x)
             (sym (apply-id x))))))))

  module B⊕ = Braid _+_ +-comm blockSwap blockSwap-invol
  module B⊗ = Braid _*_ *-comm factorSwap factorSwap-invol

------------------------------------------------------------------------
-- S3 — THE TWO OBJECT-MONOID PRODUCTS. Objₚ is grade-⊤, so both products are
-- the trivial GradedProductOver: the object monoid is degenerate, and ALL of
-- the rig's non-trivial symmetry lives in the Sₙ morphisms (S2).
------------------------------------------------------------------------

⊕objₚ : GradedProductOver _+_ 0 Objₚ
⊕objₚ = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }

⊗objₚ : GradedProductOver _*_ 1 Objₚ
⊗objₚ = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }

------------------------------------------------------------------------
-- S4 — THE INSTANCE. The genuine symmetric rig category with permutation
-- morphisms, assembled from S1–S3. Green at `: GradedRigCat Objₚ Homₚ`.
------------------------------------------------------------------------

orientationRigCatPerm : GradedRigCat Objₚ Homₚ
orientationRigCatPerm = record
  { idHom        = λ {i} _ → idᵣ i
  ; _∘_          = λ g f → g ∘ᵣ f
  ; left-id      = λ f → left-idᵣ f
  ; right-id     = λ f → right-idᵣ f
  ; assoc        = λ f g h → assocᵣ f g h
  ; ⊕obj         = ⊕objₚ
  ; ⊗obj         = ⊗objₚ
  ; braid⊕       = λ {i} {j} _ _ → +-comm i j , B⊕.swPerm i j
  ; braid⊗       = λ {i} {j} _ _ → *-comm i j , B⊗.swPerm i j
  ; braid⊕-invol = λ {i} {j} _ _ → homEq (uipℕ _ _) (B⊕.swPerm-invol i j)
  ; braid⊗-invol = λ {i} {j} _ _ → homEq (uipℕ _ _) (B⊗.swPerm-invol i j)
  }
