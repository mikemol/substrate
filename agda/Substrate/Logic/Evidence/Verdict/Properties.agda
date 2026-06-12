------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Properties
--
-- The crossbar identities (el-atlas S4/S5): the rail-swap and the
-- verdict-level dual are involutions, and `verdict` INTERTWINES them —
-- the square
--
--        Evidence --verdict--> Verdict
--          |                     |
--        swapE                 swapV
--          v                     v
--        Evidence --verdict--> Verdict
--
-- commutes.  Every case holds by refl after δ-reduction through
-- `verdict`/`swapE`/`swapV`.
--
-- Also: the laws of the connectives (the joiners, defined with the carrier
-- in `Verdict`): De Morgan (Theorem 5.2), the twist-structure, the
-- semilattice laws, and the Remark 6.2 "two operations are forced"
-- non-collapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Properties where

open import Substrate.Foundation.Bool using (true; false)
open import Substrate.Foundation.Bool.Properties
  using (∧-comm; ∨-comm; ∧-assoc; ∨-assoc; ∧-idem; ∨-idem; ∧-identityʳ; ∨-identityʳ)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong; cong₂)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)

open import Substrate.Logic.Evidence.Verdict

------------------------------------------------------------------------
-- S5: both swaps are involutions.
------------------------------------------------------------------------

swapE-involutive : (e : Evidence) → swapE (swapE e) ≡ e
swapE-involutive ⟨ p , n ⟩ = refl

swapV-involutive : (v : Verdict) → swapV (swapV v) ≡ v
swapV-involutive P = refl
swapV-involutive F = refl
swapV-involutive U = refl
swapV-involutive V = refl

------------------------------------------------------------------------
-- S4, the crossbar: verdict ∘ swapE ≡ swapV ∘ verdict (pointwise).
------------------------------------------------------------------------

intertwine : (e : Evidence) → verdict (swapE e) ≡ swapV (verdict e)
intertwine ⟨ true  , false ⟩ = refl
intertwine ⟨ false , true  ⟩ = refl
intertwine ⟨ true  , true  ⟩ = refl
intertwine ⟨ false , false ⟩ = refl

------------------------------------------------------------------------
-- Theorem 5.2 / §6.1 — De Morgan: notE exchanges the truth connectives
-- ∧E ↔ ∨E. Pure rail-permutation, hence refl.
------------------------------------------------------------------------

deMorgan-∧∨ : (a b : Evidence) → notE (a ∧E b) ≡ notE a ∨E notE b
deMorgan-∧∨ ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

deMorgan-∨∧ : (a b : Evidence) → notE (a ∨E b) ≡ notE a ∧E notE b
deMorgan-∨∧ ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

------------------------------------------------------------------------
-- Twist-structure: notE PRESERVES the info connectives (it reverses the
-- truth order, but not the information order).
------------------------------------------------------------------------

notE-⊕ : (a b : Evidence) → notE (a ⊕E b) ≡ notE a ⊕E notE b
notE-⊕ ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

notE-⊗ : (a b : Evidence) → notE (a ⊗E b) ≡ notE a ⊗E notE b
notE-⊗ ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

------------------------------------------------------------------------
-- Semilattice laws (commutative idempotent monoids). cong₂ on the rails.
------------------------------------------------------------------------

∧E-comm : (a b : Evidence) → a ∧E b ≡ b ∧E a
∧E-comm ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = cong₂ ⟨_,_⟩ (∧-comm pa pb) (∨-comm na nb)

∨E-comm : (a b : Evidence) → a ∨E b ≡ b ∨E a
∨E-comm ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = cong₂ ⟨_,_⟩ (∨-comm pa pb) (∧-comm na nb)

⊕E-comm : (a b : Evidence) → a ⊕E b ≡ b ⊕E a
⊕E-comm ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = cong₂ ⟨_,_⟩ (∨-comm pa pb) (∨-comm na nb)

⊗E-comm : (a b : Evidence) → a ⊗E b ≡ b ⊗E a
⊗E-comm ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = cong₂ ⟨_,_⟩ (∧-comm pa pb) (∧-comm na nb)

∧E-assoc : (a b c : Evidence) → (a ∧E b) ∧E c ≡ a ∧E (b ∧E c)
∧E-assoc ⟨ pa , na ⟩ ⟨ pb , nb ⟩ ⟨ pc , nc ⟩ =
  cong₂ ⟨_,_⟩ (∧-assoc pa pb pc) (∨-assoc na nb nc)

∨E-assoc : (a b c : Evidence) → (a ∨E b) ∨E c ≡ a ∨E (b ∨E c)
∨E-assoc ⟨ pa , na ⟩ ⟨ pb , nb ⟩ ⟨ pc , nc ⟩ =
  cong₂ ⟨_,_⟩ (∨-assoc pa pb pc) (∧-assoc na nb nc)

∧E-idem : (a : Evidence) → a ∧E a ≡ a
∧E-idem ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∧-idem pa) (∨-idem na)

∨E-idem : (a : Evidence) → a ∨E a ≡ a
∨E-idem ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∨-idem pa) (∧-idem na)

-- units: ⊤t (= P) is the ∧E identity; ⊥t (= F) is the ∨E identity.
∧E-identityʳ : (a : Evidence) → a ∧E ⊤t ≡ a
∧E-identityʳ ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∧-identityʳ pa) (∨-identityʳ na)

∨E-identityʳ : (a : Evidence) → a ∨E ⊥t ≡ a
∨E-identityʳ ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∨-identityʳ pa) (∧-identityʳ na)

-- the info pair ⊕E (accumulate) / ⊗E (consensus): assoc + units (⊥k = V for
-- ⊕E, ⊤k = U for ⊗E), so they too are commutative monoids.
⊕E-assoc : (a b c : Evidence) → (a ⊕E b) ⊕E c ≡ a ⊕E (b ⊕E c)
⊕E-assoc ⟨ pa , na ⟩ ⟨ pb , nb ⟩ ⟨ pc , nc ⟩ =
  cong₂ ⟨_,_⟩ (∨-assoc pa pb pc) (∨-assoc na nb nc)

⊗E-assoc : (a b c : Evidence) → (a ⊗E b) ⊗E c ≡ a ⊗E (b ⊗E c)
⊗E-assoc ⟨ pa , na ⟩ ⟨ pb , nb ⟩ ⟨ pc , nc ⟩ =
  cong₂ ⟨_,_⟩ (∧-assoc pa pb pc) (∧-assoc na nb nc)

⊕E-identityʳ : (a : Evidence) → a ⊕E ⊥k ≡ a
⊕E-identityʳ ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∨-identityʳ pa) (∨-identityʳ na)

⊗E-identityʳ : (a : Evidence) → a ⊗E ⊤k ≡ a
⊗E-identityʳ ⟨ pa , na ⟩ = cong₂ ⟨_,_⟩ (∧-identityʳ pa) (∧-identityʳ na)

------------------------------------------------------------------------
-- GROUNDED: each joiner IS a substrate-named `Category.CommutativeMonoid` —
-- the bilattice is four commutative monoids on the Evidence carrier. The
-- bare laws above witness the named primitives; identityˡ = comm ∘ identityʳ.
------------------------------------------------------------------------

∧E-CommutativeMonoid : CommutativeMonoid _
∧E-CommutativeMonoid = record
  { R = Evidence ; _+R_ = _∧E_ ; 0R = ⊤t
  ; +R-assoc = ∧E-assoc
  ; +R-identityˡ = λ a → trans (∧E-comm ⊤t a) (∧E-identityʳ a)
  ; +R-identityʳ = ∧E-identityʳ ; +R-comm = ∧E-comm }

∨E-CommutativeMonoid : CommutativeMonoid _
∨E-CommutativeMonoid = record
  { R = Evidence ; _+R_ = _∨E_ ; 0R = ⊥t
  ; +R-assoc = ∨E-assoc
  ; +R-identityˡ = λ a → trans (∨E-comm ⊥t a) (∨E-identityʳ a)
  ; +R-identityʳ = ∨E-identityʳ ; +R-comm = ∨E-comm }

⊕E-CommutativeMonoid : CommutativeMonoid _
⊕E-CommutativeMonoid = record
  { R = Evidence ; _+R_ = _⊕E_ ; 0R = ⊥k
  ; +R-assoc = ⊕E-assoc
  ; +R-identityˡ = λ a → trans (⊕E-comm ⊥k a) (⊕E-identityʳ a)
  ; +R-identityʳ = ⊕E-identityʳ ; +R-comm = ⊕E-comm }

⊗E-CommutativeMonoid : CommutativeMonoid _
⊗E-CommutativeMonoid = record
  { R = Evidence ; _+R_ = _⊗E_ ; 0R = ⊤k
  ; +R-assoc = ⊗E-assoc
  ; +R-identityˡ = λ a → trans (⊗E-comm ⊤k a) (⊗E-identityʳ a)
  ; +R-identityʳ = ⊗E-identityʳ ; +R-comm = ⊗E-comm }

------------------------------------------------------------------------
-- Remark 6.2 — the two truth operations are GENUINELY DIFFERENT. A single
-- operation under inversion is self-dual and collapses the ∧/∨ distinction
-- (Theorem 5.3(2)), leaving De Morgan nothing to exchange; the semiring is
-- the minimum structure under which NOT has something to swap. Witnessed
-- on the (P, F) probe — the same distinct-verdict pair that drives
-- NoCollapse: ⊤t ∧E ⊥t = ⊥t (F) but ⊤t ∨E ⊥t = ⊤t (P).
------------------------------------------------------------------------

∧E≢∨E : (⊤t ∧E ⊥t) ≢ (⊤t ∨E ⊥t)
∧E≢∨E eq = P≢F (sym (cong verdict eq))

------------------------------------------------------------------------
-- The verdict-level reading of NOT is exactly the crossbar intertwining
-- (notE ≡ swapE on the nose) — the joiners and the crossbar are the same
-- negation.
------------------------------------------------------------------------

verdict-notE : (a : Evidence) → verdict (notE a) ≡ swapV (verdict a)
verdict-notE = intertwine
