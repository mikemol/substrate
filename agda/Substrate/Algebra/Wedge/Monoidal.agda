------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Monoidal
--
-- THE PENTAGON — closing the foundational quotient algebra into a coherent
-- surface. The shred of the realizable peak showed the foundation is an OPEN
-- DAG: the roots reference each other only one-way, so there is no fluidity
-- to find structurally. Fluidity must come from the wedge's bridges — and the
-- bridges only cohere if their COMPOSITION is associative up to a coherent
-- isomorphism. That coherence is the PENTAGON.
--
-- The monoidal product is the cross-carrier tensor `_⊗ᴰ_` (Cross.agda):
-- product carrier, componentwise recon. The associator
--     α : (A ⊗ᴰ B) ⊗ᴰ C  ≃  A ⊗ᴰ (B ⊗ᴰ C)
-- is product reassociation `((a,b),c) ↔ (a,(b,c))`, a `WedgeIso` whose
-- `respects`/`z-pres`/round-trips are all `refl` (the carrier `Σ` has η). The
-- pentagon says the two ways of reassociating a FOUR-fold tensor agree — and
-- both composite bridges reduce to the SAME projection tree on
-- `(((a,b),c),d)`, so the pentagon closes by `refl`.
--
-- This is the "geodesic sphere": with the roots wedge-founded (ℕ-div, F₂-div,
-- ℤ-div) as vertices, the EEA folds (gcd-fold, bezout-ℤ) as operations, and
-- the associator coherent, the open tree becomes a coherent monoidal
-- groupoid — you transport along it without ever re-deriving a bridge, no
-- retrofits. `roots-pentagon` grounds the coherence at the actual roots.
--
-- BOTH FACES of Mac Lane coherence are closed here: the PENTAGON
-- (associativity, §4) and the TRIANGLE (unit, §6) — the unit object `⊤-div`,
-- the unitors λ/ρ, and the triangle identity, all `refl` (⊤ is a no-field
-- record, so it too has η). Pentagon + triangle is exactly Mac Lane's
-- coherence hypothesis: the sphere is fully closed.
--
-- HONEST SCOPE: the coherence diagrams are stated at the level of the forward
-- bridges' `translate` (morphism equality = action equality), the honest
-- --without-K statement — full WedgeIso equality would need proof-irrelevance
-- of the round-trip fields, which we do not assume. Naturality of α/λ/ρ (the
-- squares, as opposed to the coherence pentagons/triangle) is a further lift.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Monoidal where

open import Substrate.Foundation.Eq using (_≡_; refl; cong₂)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div) renaming (C to Carrier)
open import Substrate.Algebra.Wedge.Cross using (_⊗ᴰ_)
open import Substrate.Algebra.Wedge.Bridge
  using (Bridge; translate; respects; z-pres; id-bridge)
open import Substrate.Algebra.Wedge.Correspondence using (_⊚_)
open import Substrate.Algebra.Wedge.Iso
  using (WedgeIso; fwd; bwd; bwd∘fwd; fwd∘bwd)
open import Substrate.Algebra.F2.Wedge using (F₂-div)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)

------------------------------------------------------------------------
-- 1. The tensor on morphisms — the bifunctor on bridges (and on the groupoid).
------------------------------------------------------------------------

_⊗ᵇ_ : {A A′ B B′ : DivStr} → Bridge A A′ → Bridge B B′ →
       Bridge (A ⊗ᴰ B) (A′ ⊗ᴰ B′)
f ⊗ᵇ g = record
  { translate = λ p → translate f (proj₁ p) , translate g (proj₂ p)
  ; respects  = λ q p p′ →
      cong₂ _,_ (respects f q (proj₁ p) (proj₁ p′))
                (respects g q (proj₂ p) (proj₂ p′))
  ; z-pres    = cong₂ _,_ (z-pres f) (z-pres g)
  }

------------------------------------------------------------------------
-- 2. The associator — product reassociation, both directions (all refl).
------------------------------------------------------------------------

assoc→ : (A B C : DivStr) → Bridge ((A ⊗ᴰ B) ⊗ᴰ C) (A ⊗ᴰ (B ⊗ᴰ C))
assoc→ A B C = record
  { translate = λ p → proj₁ (proj₁ p) , (proj₂ (proj₁ p) , proj₂ p)
  ; respects  = λ _ _ _ → refl
  ; z-pres    = refl
  }

assoc← : (A B C : DivStr) → Bridge (A ⊗ᴰ (B ⊗ᴰ C)) ((A ⊗ᴰ B) ⊗ᴰ C)
assoc← A B C = record
  { translate = λ p → (proj₁ p , proj₁ (proj₂ p)) , proj₂ (proj₂ p)
  ; respects  = λ _ _ _ → refl
  ; z-pres    = refl
  }

-- the associator is a wedge-iso: the round-trips are refl (Σ has η).
assocᴰ : (A B C : DivStr) → WedgeIso ((A ⊗ᴰ B) ⊗ᴰ C) (A ⊗ᴰ (B ⊗ᴰ C))
assocᴰ A B C = record
  { fwd = assoc→ A B C ; bwd = assoc← A B C
  ; bwd∘fwd = λ _ → refl ; fwd∘bwd = λ _ → refl }

------------------------------------------------------------------------
-- 3. The tensor on isos (the monoidal bifunctor on the groupoid of roots).
------------------------------------------------------------------------

_⊗ᵢ_ : {A A′ B B′ : DivStr} → WedgeIso A A′ → WedgeIso B B′ →
       WedgeIso (A ⊗ᴰ B) (A′ ⊗ᴰ B′)
f ⊗ᵢ g = record
  { fwd = fwd f ⊗ᵇ fwd g
  ; bwd = bwd f ⊗ᵇ bwd g
  ; bwd∘fwd = λ x → cong₂ _,_ (bwd∘fwd f (proj₁ x)) (bwd∘fwd g (proj₂ x))
  ; fwd∘bwd = λ y → cong₂ _,_ (fwd∘bwd f (proj₁ y)) (fwd∘bwd g (proj₂ y))
  }

------------------------------------------------------------------------
-- 4. THE PENTAGON — the two reassociations of a four-fold tensor agree.
--
--   ((A⊗B)⊗C)⊗D ──α──→ (A⊗B)⊗(C⊗D) ──α──→ A⊗(B⊗(C⊗D))
--        │                                      ▲
--      α⊗id                                  id⊗α
--        ▼                                      │
--   (A⊗(B⊗C))⊗D ───────α──────→ A⊗((B⊗C)⊗D) ───┘
--
-- Both composite forward bridges reduce to the same projection tree, so the
-- diagram commutes by refl.
------------------------------------------------------------------------

pentagon : (A B C D : DivStr) (x : Carrier (((A ⊗ᴰ B) ⊗ᴰ C) ⊗ᴰ D)) →
  translate (assoc→ A B (C ⊗ᴰ D) ⊚ assoc→ (A ⊗ᴰ B) C D) x
    ≡ translate ((id-bridge A ⊗ᵇ assoc→ B C D)
                 ⊚ (assoc→ A (B ⊗ᴰ C) D
                    ⊚ (assoc→ A B C ⊗ᵇ id-bridge D))) x
pentagon A B C D x = refl

------------------------------------------------------------------------
-- 5. GROUNDED at the founded roots — coherence at the actual carriers.
--    The pentagon holds for ANY DivStr, hence at every choice of roots;
--    this is the instance at (F₂, ℕ, ℤ, F₂), the geodesic sphere closed.
------------------------------------------------------------------------

roots-pentagon :
  (x : Carrier (((F₂-div ⊗ᴰ ℕ-div) ⊗ᴰ ℤ-div) ⊗ᴰ F₂-div)) →
  translate (assoc→ F₂-div ℕ-div (ℤ-div ⊗ᴰ F₂-div)
             ⊚ assoc→ (F₂-div ⊗ᴰ ℕ-div) ℤ-div F₂-div) x
    ≡ translate ((id-bridge F₂-div ⊗ᵇ assoc→ ℕ-div ℤ-div F₂-div)
                 ⊚ (assoc→ F₂-div (ℕ-div ⊗ᴰ ℤ-div) F₂-div
                    ⊚ (assoc→ F₂-div ℕ-div ℤ-div ⊗ᵇ id-bridge F₂-div))) x
roots-pentagon = pentagon F₂-div ℕ-div ℤ-div F₂-div

------------------------------------------------------------------------
-- 6. THE UNIT FACE — unit object, unitors, and the triangle identity.
--    ⊤-div is the monoidal unit; the unitors strip it; the triangle says
--    the associator and the unitors agree. All refl (⊤ has η).
------------------------------------------------------------------------

⊤-div : DivStr
⊤-div = record { C = ⊤ ; z = tt ; recon = λ _ _ _ → tt }

-- left unitor: ⊤-div ⊗ᴰ A ≃ A  (drop the unit on the left).
unitˡ→ : (A : DivStr) → Bridge (⊤-div ⊗ᴰ A) A
unitˡ→ A = record { translate = λ p → proj₂ p ; respects = λ _ _ _ → refl ; z-pres = refl }

unitˡ← : (A : DivStr) → Bridge A (⊤-div ⊗ᴰ A)
unitˡ← A = record { translate = λ a → tt , a ; respects = λ _ _ _ → refl ; z-pres = refl }

unitᴸ : (A : DivStr) → WedgeIso (⊤-div ⊗ᴰ A) A
unitᴸ A = record
  { fwd = unitˡ→ A ; bwd = unitˡ← A ; bwd∘fwd = λ _ → refl ; fwd∘bwd = λ _ → refl }

-- right unitor: A ⊗ᴰ ⊤-div ≃ A  (drop the unit on the right).
unitʳ→ : (A : DivStr) → Bridge (A ⊗ᴰ ⊤-div) A
unitʳ→ A = record { translate = λ p → proj₁ p ; respects = λ _ _ _ → refl ; z-pres = refl }

unitʳ← : (A : DivStr) → Bridge A (A ⊗ᴰ ⊤-div)
unitʳ← A = record { translate = λ a → a , tt ; respects = λ _ _ _ → refl ; z-pres = refl }

unitᴿ : (A : DivStr) → WedgeIso (A ⊗ᴰ ⊤-div) A
unitᴿ A = record
  { fwd = unitʳ→ A ; bwd = unitʳ← A ; bwd∘fwd = λ _ → refl ; fwd∘bwd = λ _ → refl }

-- THE TRIANGLE: (id_A ⊗ λ_B) ∘ α_{A,⊤,B}  =  ρ_A ⊗ id_B   on (A ⊗ ⊤) ⊗ B.
--
--   (A ⊗ ⊤) ⊗ B ──────α──────→ A ⊗ (⊤ ⊗ B)
--        │                           │
--      ρ ⊗ id                      id ⊗ λ
--        ▼                           ▼
--        A ⊗ B ════════════════════ A ⊗ B
triangle : (A B : DivStr) (x : Carrier ((A ⊗ᴰ ⊤-div) ⊗ᴰ B)) →
  translate ((id-bridge A ⊗ᵇ unitˡ→ B) ⊚ assoc→ A ⊤-div B) x
    ≡ translate (unitʳ→ A ⊗ᵇ id-bridge B) x
triangle A B x = refl

------------------------------------------------------------------------
-- 7. NATURALITY — α, λ, ρ are natural in their arguments. The coherence
--    diagrams (§4, §6) say the structure maps cohere with each other; these
--    say they cohere with every bridge between objects. Both sides reshuffle
--    to the same projection tree with the component bridges applied → refl.
--    Together with §4/§6 this makes (DivStr, _⊗ᴰ_, ⊤-div, α, λ, ρ) a genuine
--    monoidal structure (natural isos + coherence), not just a pile of isos.
------------------------------------------------------------------------

assoc-nat : {A A′ B B′ C C′ : DivStr}
            (f : Bridge A A′) (g : Bridge B B′) (h : Bridge C C′)
            (x : Carrier ((A ⊗ᴰ B) ⊗ᴰ C)) →
  translate (assoc→ A′ B′ C′ ⊚ ((f ⊗ᵇ g) ⊗ᵇ h)) x
    ≡ translate ((f ⊗ᵇ (g ⊗ᵇ h)) ⊚ assoc→ A B C) x
assoc-nat f g h x = refl

unitˡ-nat : {A A′ : DivStr} (f : Bridge A A′) (x : Carrier (⊤-div ⊗ᴰ A)) →
  translate (unitˡ→ A′ ⊚ (id-bridge ⊤-div ⊗ᵇ f)) x
    ≡ translate (f ⊚ unitˡ→ A) x
unitˡ-nat f x = refl

unitʳ-nat : {A A′ : DivStr} (f : Bridge A A′) (x : Carrier (A ⊗ᴰ ⊤-div)) →
  translate (unitʳ→ A′ ⊚ (f ⊗ᵇ id-bridge ⊤-div)) x
    ≡ translate (f ⊚ unitʳ→ A) x
unitʳ-nat f x = refl
