------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP
--
-- ⟡rig-UP-cat-UP — THE FUNCTOR UNIVERSAL PROPERTY IS Set₀ (the arc's 7th
-- "same move": a ∀-over-carriers STATEMENT has a large TYPE by polymorphism,
-- but the NOTION it quantifies — RigFunctor — is a Set₀ record, exactly like
-- foldF-free-unique (COMMITTED, --safe) quantifies `∀ {C : ℕ → Set}` yet holds
-- no Set₁ object).
--
-- A prior (cat-graded) agent called the functor-UP "irreducibly Set₁" because
-- it quantifies over targets with Obj : ℕ → Set. That CONFLATES a polymorphic
-- statement's large type with a held Set₁ carrier. This module refutes it by
-- CONSTRUCTION:
--
--   S1 (THE DISSOLUTION): `record RigFunctor S T : Set` — Obj/Hom of both the
--      source and the target are MODULE/RECORD PARAMETERS, so no Set-valued
--      field forces the bundle up a universe. It type-checks AT `: Set`. That
--      green compile IS the dissolution. + id-RigFunctor + comp-RigFunctor
--      (the category of GradedRigCats).
--   S2' (THE UP — NO Σ): the universal property is EXPOSED, not ∃-collapsed —
--      exactly like foldF-free-unique. `freeFunctor` (a CONSTRUCTION) and
--      `freeFunctor-obj-unique` (a separate uniqueness lemma) live in
--      .Properties; here we provide `RigFunctor≈`, the pointwise, transport-
--      aware extensional equality on RigFunctor against which uniqueness is
--      stated (mirroring GradedHomOver's target-equality). NO Σ / ∃ anywhere.
--
-- HONEST SCOPE: this is the DECATEGORIFIED (identity-on-morphisms up to the
-- thin structure) functor-UP — it settles that RigFunctor and the functor-UP
-- are Set₀. The FULL symmetric UP (free object = the Perm rig category with
-- permutation morphisms) is ⟡rig-UP-cat-perm-UP and is NOT claimed here.
--
-- Proof-free notion home (def/proof separation): the record + id + comp + the
-- UP statement live here; the initiality PROOF for the skeletal free object —
-- which imports the proof-carrying orientationRigCatₛ — lives in .Properties.
--
-- Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; _∧_; u)
open import Substrate.WitnessTower.Wedge.OrientationRigCat
  using (GradedRigCat; idHom; _∘_; ⊕obj; ⊗obj; braid⊕; braid⊗)

------------------------------------------------------------------------
-- trⱽ — transport a morphism along equalities of BOTH its endpoint objects
-- (the categorification coherence transport). It is the nested double-subst
-- packaged once, so the braid-preservation law and its pasting/naturality
-- lemmas read cleanly.
------------------------------------------------------------------------

trⱽ : {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
      {i j : ℕ} {a a' : Obj i} {b b' : Obj j} →
      a ≡ a' → b ≡ b' → Hom a b → Hom a' b'
trⱽ {Hom = Hom} {a = a} {a' = a'} {b = b} {b' = b'} p q h =
  subst (λ x → Hom x b') p (subst (λ y → Hom a y) q h)

-- pasting: a transport along composed endpoint-equalities is the two
-- transports in sequence.
trⱽ-paste : {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
            {i j : ℕ} {a₀ a₁ a₂ : Obj i} {b₀ b₁ b₂ : Obj j}
            (p₁ : a₀ ≡ a₁) (p₂ : a₁ ≡ a₂) (q₁ : b₀ ≡ b₁) (q₂ : b₁ ≡ b₂)
            (h : Hom a₀ b₀) →
            trⱽ {Obj = Obj} {Hom = Hom} (trans p₁ p₂) (trans q₁ q₂) h
            ≡ trⱽ {Obj = Obj} {Hom = Hom} p₂ q₂
                  (trⱽ {Obj = Obj} {Hom = Hom} p₁ q₁ h)
trⱽ-paste refl p₂ refl q₂ h = refl

-- naturality: a functor's hom-map commutes with the transport (its object-map
-- carries the endpoint equalities across).
trⱽ-nat : {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
          {Obj' : ℕ → Set} {Hom' : {i j : ℕ} → Obj' i → Obj' j → Set}
          (Fobj : {n : ℕ} → Obj n → Obj' n)
          (Fhom : {i j : ℕ} {a : Obj i} {b : Obj j} →
                  Hom a b → Hom' (Fobj a) (Fobj b))
          {i j : ℕ} {a a' : Obj i} {b b' : Obj j}
          (p : a ≡ a') (q : b ≡ b') (h : Hom a b) →
          Fhom (trⱽ {Obj = Obj} {Hom = Hom} p q h)
          ≡ trⱽ {Obj = Obj'} {Hom = Hom'} (cong Fobj p) (cong Fobj q) (Fhom h)
trⱽ-nat Fobj Fhom refl refl h = refl

------------------------------------------------------------------------
-- S1 — THE DISSOLUTION. RigFunctor between two GradedRigCats. Both objects
-- (Obj₁,Obj₂ : ℕ → Set) and both hom-families are PARAMETERS, not fields, so
-- the record bundle lands in `Set` — NOT Set (lsuc …). The green compile at
-- `: Set` (below, checked by Agda) IS the settling of the Set₁ over-call.
--
-- The preservation fields:
--   F-idHom, F-∘        — a functor of the underlying categories
--   F-⊕obj-u/∧,
--   F-⊗obj-u/∧          — preserves both object-monoid products (⊕ over
--                          (ℕ,+,0), ⊗ over (ℕ,*,1))
--   F-braid⊕, F-braid⊗  — preserves the two braidings; because the braiding's
--                          source/target objects change under F-obj, the law
--                          is stated with the ∧-preservation transports (the
--                          coherence square), all still in `Set`.
------------------------------------------------------------------------

record RigFunctor
  {Obj₁ : ℕ → Set} {Hom₁ : {i j : ℕ} → Obj₁ i → Obj₁ j → Set}
  {Obj₂ : ℕ → Set} {Hom₂ : {i j : ℕ} → Obj₂ i → Obj₂ j → Set}
  (S : GradedRigCat Obj₁ Hom₁)
  (T : GradedRigCat Obj₂ Hom₂) : Set where
  field
    F-obj : {n : ℕ} → Obj₁ n → Obj₂ n
    F-hom : {i j : ℕ} {a : Obj₁ i} {b : Obj₁ j} →
            Hom₁ a b → Hom₂ (F-obj a) (F-obj b)

    ----------------------------------------------------------------
    -- functoriality of the underlying category
    ----------------------------------------------------------------
    F-idHom : {i : ℕ} (a : Obj₁ i) →
              F-hom (idHom S a) ≡ idHom T (F-obj a)
    F-∘     : {i j k : ℕ} {a : Obj₁ i} {b : Obj₁ j} {c : Obj₁ k}
              (g : Hom₁ b c) (f : Hom₁ a b) →
              F-hom (_∘_ S g f) ≡ _∘_ T (F-hom g) (F-hom f)

    ----------------------------------------------------------------
    -- preservation of the two object-monoid products
    ----------------------------------------------------------------
    F-⊕obj-u : F-obj (u (⊕obj S)) ≡ u (⊕obj T)
    F-⊕obj-∧ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
               F-obj (_∧_ (⊕obj S) a b) ≡ _∧_ (⊕obj T) (F-obj a) (F-obj b)
    F-⊗obj-u : F-obj (u (⊗obj S)) ≡ u (⊗obj T)
    F-⊗obj-∧ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
               F-obj (_∧_ (⊗obj S) a b) ≡ _∧_ (⊗obj T) (F-obj a) (F-obj b)

    ----------------------------------------------------------------
    -- preservation of the braidings (the coherence square, transported
    -- along the ∧-preservation of the respective product).
    ----------------------------------------------------------------
    F-braid⊕ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
               trⱽ {Obj = Obj₂} {Hom = Hom₂} (F-⊕obj-∧ a b) (F-⊕obj-∧ b a)
                   (F-hom (braid⊕ S a b))
               ≡ braid⊕ T (F-obj a) (F-obj b)
    F-braid⊗ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
               trⱽ {Obj = Obj₂} {Hom = Hom₂} (F-⊗obj-∧ a b) (F-⊗obj-∧ b a)
                   (F-hom (braid⊗ S a b))
               ≡ braid⊗ T (F-obj a) (F-obj b)

open RigFunctor public

------------------------------------------------------------------------
-- The category of GradedRigCats: identity and composition of RigFunctors.
-- Their existence (at `: Set`) confirms RigFunctor is a genuine hom-notion,
-- not a Set₁ artefact.
------------------------------------------------------------------------

-- Identity functor: everything is preserved definitionally (all refl); each
-- braid transport is a subst-by-refl, so it too reduces to refl.
id-RigFunctor :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (S : GradedRigCat Obj Hom) → RigFunctor S S
id-RigFunctor S = record
  { F-obj     = λ x → x
  ; F-hom     = λ h → h
  ; F-idHom   = λ _ → refl
  ; F-∘       = λ _ _ → refl
  ; F-⊕obj-u  = refl
  ; F-⊕obj-∧  = λ _ _ → refl
  ; F-⊗obj-u  = refl
  ; F-⊗obj-∧  = λ _ _ → refl
  ; F-braid⊕  = λ _ _ → refl
  ; F-braid⊗  = λ _ _ → refl
  }

-- Composition of RigFunctors. Object/hom preservation compose by trans∘cong;
-- the braid-coherence squares PASTE: the inner square (F) is carried across
-- G by trⱽ-nat, then closed against the outer square (G) by trⱽ-paste.
comp-RigFunctor :
  {Obj₁ : ℕ → Set} {Hom₁ : {i j : ℕ} → Obj₁ i → Obj₁ j → Set}
  {Obj₂ : ℕ → Set} {Hom₂ : {i j : ℕ} → Obj₂ i → Obj₂ j → Set}
  {Obj₃ : ℕ → Set} {Hom₃ : {i j : ℕ} → Obj₃ i → Obj₃ j → Set}
  {S : GradedRigCat Obj₁ Hom₁} {U : GradedRigCat Obj₂ Hom₂}
  {T : GradedRigCat Obj₃ Hom₃} →
  RigFunctor U T → RigFunctor S U → RigFunctor S T
comp-RigFunctor {Obj₁ = Obj₁} {Hom₁ = Hom₁} {Obj₂ = Obj₂} {Hom₂ = Hom₂}
                {Obj₃ = Obj₃} {Hom₃ = Hom₃}
                {S = S} {U = U} {T = T} G F = record
  { F-obj    = H-obj
  ; F-hom    = H-hom
  ; F-idHom  = λ a → trans (cong (F-hom G) (F-idHom F a)) (F-idHom G (F-obj F a))
  ; F-∘      = λ g f → trans (cong (F-hom G) (F-∘ F g f))
                             (F-∘ G (F-hom F g) (F-hom F f))
  ; F-⊕obj-u = trans (cong (F-obj G) (F-⊕obj-u F)) (F-⊕obj-u G)
  ; F-⊕obj-∧ = H-⊕∧
  ; F-⊗obj-u = trans (cong (F-obj G) (F-⊗obj-u F)) (F-⊗obj-u G)
  ; F-⊗obj-∧ = H-⊗∧
  ; F-braid⊕ = br⊕
  ; F-braid⊗ = br⊗
  }
  where
    H-obj : {n : ℕ} → Obj₁ n → Obj₃ n
    H-obj x = F-obj G (F-obj F x)

    H-hom : {i j : ℕ} {a : Obj₁ i} {b : Obj₁ j} →
            Hom₁ a b → Hom₃ (H-obj a) (H-obj b)
    H-hom h = F-hom G (F-hom F h)

    H-⊕∧ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
           H-obj (_∧_ (⊕obj S) a b) ≡ _∧_ (⊕obj T) (H-obj a) (H-obj b)
    H-⊕∧ a b = trans (cong (F-obj G) (F-⊕obj-∧ F a b))
                     (F-⊕obj-∧ G (F-obj F a) (F-obj F b))

    H-⊗∧ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
           H-obj (_∧_ (⊗obj S) a b) ≡ _∧_ (⊗obj T) (H-obj a) (H-obj b)
    H-⊗∧ a b = trans (cong (F-obj G) (F-⊗obj-∧ F a b))
                     (F-⊗obj-∧ G (F-obj F a) (F-obj F b))

    br⊕ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
          trⱽ {Obj = Obj₃} {Hom = Hom₃} (H-⊕∧ a b) (H-⊕∧ b a) (H-hom (braid⊕ S a b))
          ≡ braid⊕ T (H-obj a) (H-obj b)
    br⊕ a b =
      trans (trⱽ-paste {Obj = Obj₃} {Hom = Hom₃}
               (cong (F-obj G) (F-⊕obj-∧ F a b)) (F-⊕obj-∧ G (F-obj F a) (F-obj F b))
               (cong (F-obj G) (F-⊕obj-∧ F b a)) (F-⊕obj-∧ G (F-obj F b) (F-obj F a))
               (F-hom G (F-hom F (braid⊕ S a b))))
      (trans (cong (trⱽ {Obj = Obj₃} {Hom = Hom₃}
                        (F-⊕obj-∧ G (F-obj F a) (F-obj F b))
                        (F-⊕obj-∧ G (F-obj F b) (F-obj F a)))
                (trans (sym (trⱽ-nat {Obj = Obj₂} {Hom = Hom₂}
                              {Obj' = Obj₃} {Hom' = Hom₃} (F-obj G) (F-hom G)
                              (F-⊕obj-∧ F a b) (F-⊕obj-∧ F b a)
                              (F-hom F (braid⊕ S a b))))
                       (cong (F-hom G) (F-braid⊕ F a b))))
             (F-braid⊕ G (F-obj F a) (F-obj F b)))

    br⊗ : {i j : ℕ} (a : Obj₁ i) (b : Obj₁ j) →
          trⱽ {Obj = Obj₃} {Hom = Hom₃} (H-⊗∧ a b) (H-⊗∧ b a) (H-hom (braid⊗ S a b))
          ≡ braid⊗ T (H-obj a) (H-obj b)
    br⊗ a b =
      trans (trⱽ-paste {Obj = Obj₃} {Hom = Hom₃}
               (cong (F-obj G) (F-⊗obj-∧ F a b)) (F-⊗obj-∧ G (F-obj F a) (F-obj F b))
               (cong (F-obj G) (F-⊗obj-∧ F b a)) (F-⊗obj-∧ G (F-obj F b) (F-obj F a))
               (F-hom G (F-hom F (braid⊗ S a b))))
      (trans (cong (trⱽ {Obj = Obj₃} {Hom = Hom₃}
                        (F-⊗obj-∧ G (F-obj F a) (F-obj F b))
                        (F-⊗obj-∧ G (F-obj F b) (F-obj F a)))
                (trans (sym (trⱽ-nat {Obj = Obj₂} {Hom = Hom₂}
                              {Obj' = Obj₃} {Hom' = Hom₃} (F-obj G) (F-hom G)
                              (F-⊗obj-∧ F a b) (F-⊗obj-∧ F b a)
                              (F-hom F (braid⊗ S a b))))
                       (cong (F-hom G) (F-braid⊗ F a b))))
             (F-braid⊗ G (F-obj F a) (F-obj F b)))

------------------------------------------------------------------------
-- RigFunctor≈ — extensional (pointwise) equality of RigFunctors, the
-- transport-aware target-equality against which the universal property's
-- uniqueness is stated WITHOUT a Σ. Two functors agree when their object-
-- maps agree pointwise (obj≈) and, TRANSPORTED along that agreement, their
-- hom-maps agree (hom≈) — the same shape as GradedHomOver's parameterised
-- _≈_. A record of ≡-valued fields over the parameters: it lands in `Set`.
------------------------------------------------------------------------

record RigFunctor≈
  {Obj₁ : ℕ → Set} {Hom₁ : {i j : ℕ} → Obj₁ i → Obj₁ j → Set}
  {Obj₂ : ℕ → Set} {Hom₂ : {i j : ℕ} → Obj₂ i → Obj₂ j → Set}
  {S : GradedRigCat Obj₁ Hom₁} {T : GradedRigCat Obj₂ Hom₂}
  (F G : RigFunctor S T) : Set where
  field
    obj≈ : {n : ℕ} (a : Obj₁ n) → F-obj F a ≡ F-obj G a
    hom≈ : {i j : ℕ} {a : Obj₁ i} {b : Obj₁ j} (h : Hom₁ a b) →
           trⱽ {Obj = Obj₂} {Hom = Hom₂} (obj≈ a) (obj≈ b) (F-hom F h)
           ≡ F-hom G h

open RigFunctor≈ public
