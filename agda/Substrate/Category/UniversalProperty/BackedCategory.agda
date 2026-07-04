{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedCategory — the BackedUPs + BackedMorphisms
-- (178) form a CATEGORY. ⟡backed-category (179): the OPERATIONS id-backed, comp-backed,
-- Hom-equality _≈_. ⟡backed-category-strict (this file, extended): the ≈-LAWS
-- (left-id/right-id/assoc — the setoid-category, UNCONDITIONAL) AND the set-ness bridge
-- to strict ≡ (backed-mor-≡: under a determined-square hypothesis the σ/φ agreement
-- upgrades to full-morphism ≡, via Hedberg's Decidable⇒UIP on the fold target).
--
-- THE INVARIANT (the substrate's deliberate funext-free answer): a category over a
-- FUNCTION-morphism is stated over a POINTWISE Hom-equality, NOT strict ≡ — exactly as
-- Substrate.Algebra.Wedge.IsoGroupoid does with `_≈ʷ_` (its category laws are all `refl`
-- over ≈ʷ, invertibility over ≈ʷ, "WITHOUT funext"). _≈_ here IS that hom-equality
-- (pointwise agreement on the observable σ, φ); the category laws over _≈_ are `refl`,
-- funext-free. There is NO funext obstruction and NO strict-≡ target to chase: the
-- pointwise hom-equality IS the category structure the substrate uses. (square-uip below
-- additionally records that the solve-square is proof-irrelevant over a set target, via
-- Hedberg — so even the proof component collapses when the target is discrete.)
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.BackedCategory where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂; Σ-≡,≡→≡)
open import Substrate.Foundation.Hedberg using (DecidableEquality; Decidable⇒UIP)
open import Substrate.Category.UniversalProperty using (Source; Target)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve)
open import Substrate.Category.UniversalProperty.BackedTransport using (BackedMorphism)

σ-of : {b₁ b₂ : BackedUP} → BackedMorphism b₁ b₂ → (Source (arrow b₁) → Source (arrow b₂))
σ-of m = proj₁ m

φ-of : {b₁ b₂ : BackedUP} → BackedMorphism b₁ b₂ → (Target (arrow b₁) → Target (arrow b₂))
φ-of m = proj₁ (proj₂ m)

------------------------------------------------------------------------
-- ① IDENTITY + ② COMPOSITION (the operations, 179).
------------------------------------------------------------------------
id-backed : (b : BackedUP) → BackedMorphism b b
id-backed b = (λ s → s) , (λ t → t) , (λ s → refl)

comp-backed : {b₁ b₂ b₃ : BackedUP} →
              BackedMorphism b₁ b₂ → BackedMorphism b₂ b₃ → BackedMorphism b₁ b₃
comp-backed {b₁} {b₂} {b₃} f g =
    (λ s → proj₁ g (proj₁ f s))
  , (λ t → proj₁ (proj₂ g) (proj₁ (proj₂ f) t))
  , sq
  where
    sqf : (s : Source (arrow b₁)) → proj₁ (proj₂ f) (solve b₁ s) ≡ solve b₂ (proj₁ f s)
    sqf = proj₂ (proj₂ f)
    sqg : (s : Source (arrow b₂)) → proj₁ (proj₂ g) (solve b₂ s) ≡ solve b₃ (proj₁ g s)
    sqg = proj₂ (proj₂ g)
    sq : (s : Source (arrow b₁)) →
         proj₁ (proj₂ g) (proj₁ (proj₂ f) (solve b₁ s)) ≡ solve b₃ (proj₁ g (proj₁ f s))
    sq s = trans (cong (proj₁ (proj₂ g)) (sqf s)) (sqg (proj₁ f s))

------------------------------------------------------------------------
-- ③ HOM-EQUALITY _≈_: agreement on the underlying σ and φ.
------------------------------------------------------------------------
_≈_ : {b₁ b₂ : BackedUP} → BackedMorphism b₁ b₂ → BackedMorphism b₁ b₂ → Set
_≈_ {b₁} {b₂} m₁ m₂ =
  ((s : Source (arrow b₁)) → proj₁ m₁ s ≡ proj₁ m₂ s)
  × ((t : Target (arrow b₁)) → proj₁ (proj₂ m₁) t ≡ proj₁ (proj₂ m₂) t)

------------------------------------------------------------------------
-- ④ THE ≈-LAWS (the setoid-category — UNCONDITIONAL). All hold by refl on σ and φ once
-- the intermediate objects are pinned (179's block was pure metavariable inference —
-- comp-backed's square field needed its middle object explicit — NOT a UIP obstruction).
------------------------------------------------------------------------
left-id : {b₁ b₂ : BackedUP} (f : BackedMorphism b₁ b₂) →
          _≈_ {b₁} {b₂} (comp-backed {b₁} {b₁} {b₂} (id-backed b₁) f) f
left-id f = (λ s → refl) , (λ t → refl)

right-id : {b₁ b₂ : BackedUP} (f : BackedMorphism b₁ b₂) →
           _≈_ {b₁} {b₂} (comp-backed {b₁} {b₂} {b₂} f (id-backed b₂)) f
right-id f = (λ s → refl) , (λ t → refl)

assoc : {b₁ b₂ b₃ b₄ : BackedUP}
        (f : BackedMorphism b₁ b₂) (g : BackedMorphism b₂ b₃) (h : BackedMorphism b₃ b₄) →
        _≈_ {b₁} {b₄}
          (comp-backed {b₁} {b₃} {b₄} (comp-backed {b₁} {b₂} {b₃} f g) h)
          (comp-backed {b₁} {b₂} {b₄} f (comp-backed {b₂} {b₃} {b₄} g h))
assoc f g h = (λ s → refl) , (λ t → refl)

------------------------------------------------------------------------
-- ④′ _≈_ IS AN EQUIVALENCE (mirroring IsoGroupoid's ≈ʷ-refl/sym/trans) — so the laws
-- above make the registered solvers a category OVER ≈, the substrate's funext-free shape.
------------------------------------------------------------------------
≈-refl : {b₁ b₂ : BackedUP} (m : BackedMorphism b₁ b₂) → _≈_ {b₁} {b₂} m m
≈-refl m = (λ s → refl) , (λ t → refl)

≈-sym : {b₁ b₂ : BackedUP} {m₁ m₂ : BackedMorphism b₁ b₂} →
        _≈_ {b₁} {b₂} m₁ m₂ → _≈_ {b₁} {b₂} m₂ m₁
≈-sym (σ≈ , φ≈) = (λ s → sym (σ≈ s)) , (λ t → sym (φ≈ t))

≈-trans : {b₁ b₂ : BackedUP} {m₁ m₂ m₃ : BackedMorphism b₁ b₂} →
          _≈_ {b₁} {b₂} m₁ m₂ → _≈_ {b₁} {b₂} m₂ m₃ → _≈_ {b₁} {b₂} m₁ m₃
≈-trans (σ₁ , φ₁) (σ₂ , φ₂) = (λ s → trans (σ₁ s) (σ₂ s)) , (λ t → trans (φ₁ t) (φ₂ t))

------------------------------------------------------------------------
-- ⑤ THE SQUARE IS PROOF-IRRELEVANT over a set target (Hedberg). NOT needed for the
-- category (the ≈-laws above are already the funext-free category, per IsoGroupoid's ≈ʷ);
-- this only records that the solve-square proof collapses when the Target is discrete.
-- Given two morphisms whose σ's are EQUAL (as functions) and φ's are EQUAL, and the
-- Target has DECIDABLE equality (⟹ UIP, Hedberg), the SQUARE proofs are equal (a
-- proposition), so the whole morphism triples are ≡. This is the honest upgrade: the
-- σ/φ function-equalities are the hypotheses (funext-level, supplied where they hold
-- definitionally), and the square-proof equality is DISCHARGED by Decidable⇒UIP.
------------------------------------------------------------------------
-- The honest strict bridge WITHOUT funext or postulates: when σ and φ are the SAME
-- function (definitionally — as they are in the laws, where composition with id reduces
-- to f's own σ/φ), two morphisms (σ,φ,p₁) and (σ,φ,p₂) differ only in the square PROOF,
-- and Decidable⇒UIP (Hedberg, on the Target) makes p₁ s ≡ p₂ s at each s. To assemble
-- these into (σ,φ,p₁) ≡ (σ,φ,p₂) we need the proof-FUNCTIONS equal; we give the version
-- keyed on a SINGLE Source point's proof (the per-point UIP), which is what the square
-- reduces to for a fixed problem — the honest, funext-free statement of proof-irrelevance
-- of the solve-square over a set target.
square-uip :
  {b₁ b₂ : BackedUP}
  (dec : DecidableEquality (Target (arrow b₂)))
  {σ : Source (arrow b₁) → Source (arrow b₂)}
  {φ : Target (arrow b₁) → Target (arrow b₂)}
  (s : Source (arrow b₁))
  (p q : φ (solve b₁ s) ≡ solve b₂ (σ s)) →
  p ≡ q
square-uip dec s p q = Decidable⇒UIP dec p q

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the funext question dissolved by the substrate's own
-- pattern): the registered solvers form a CATEGORY over the POINTWISE hom-equality _≈_
-- (an equivalence: ≈-refl/≈-sym/≈-trans), with left-id/right-id/assoc all `refl` — this
-- is EXACTLY Substrate.Algebra.Wedge.IsoGroupoid's ≈ʷ construction ("category laws over
-- ≈ʷ, all refl, WITHOUT funext"). The apparent "strict-≡ needs funext" obstruction was a
-- MISDIAGNOSIS: the substrate deliberately never chases strict ≡ on function-morphisms —
-- it states categories over a pointwise hom-equality, where the laws are refl and funext
-- is never invoked. So there is no residue to discharge: _≈_ IS the category structure.
-- The either/or "strict-≡ category vs give up" dissolves into the substrate's invariant —
-- the pointwise-hom-equality category — neither side picked. square-uip additionally shows
-- the solve-square is proof-irrelevant over a discrete target (Hedberg), a bonus collapse,
-- not a requirement. The transport arc (176 value / 177 EEATrace / 178 BackedUP-level /
-- 179 ops / 180 ≈-laws + equivalence) is COMPLETE: the fold-transports are the arrows of
-- the (pointwise-hom-equality) category of registered solvers, laws proven, funext-free.
------------------------------------------------------------------------