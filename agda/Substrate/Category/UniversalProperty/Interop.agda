------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Interop
--
-- INTEROPERABILITY = the backed CONE over the PAIR (toward the universal
-- property of the pair — see the caveat below). The center
-- (Free ⊣ Forgetful, the universal property) recursed one level up: from
-- objects to pairs of objects. Two backed universal properties A, B
-- INTEROPERATE iff their combination has a backed cone — an apex object
-- whose single solution simultaneously witnesses BOTH factors (legs to A
-- and B). Existence of the bridge = maximal expressibility; that it is the
-- backed combination = the structure they share. (Uniqueness/universality
-- of the cone — that it is THE product, not merely A cone — is the next
-- tightening; this slice witnesses the cone, and does not yet claim it is
-- terminal among cones. DEFERRED WITH CAUSE: terminality needs a notion of
-- BackedUP cone-morphism + a terminal-object proof — a separate categorical
-- layer, not the trivial observational lemma that discharges Equalizer/
-- Pullback uniqueness. See Equalizer.equalizer-factor-unique for that idiom;
-- it does not apply here because Interop has no mediating `factor` map yet.)
--
-- This is the ⊗ (multiplicative) operation of the topos ring on backed
-- objects: A ⊗ B = their backed combination, defined exactly where an
-- Interop witness exists. (The ⊕ side is the registry's free-monoid ++ —
-- see Registry.) It is a PARTIAL operation, and its partiality IS the
-- content: pairs that do not interoperate (e.g. ℤ/2, ℤ/4 — gcd ≠ 1) admit
-- no Interop, because no total solution can satisfy both residue systems.
--
-- THE RING IDENTITY:  [ℤ/3] ⊗ [ℤ/5] = [ℤ/15].
-- crt-interop witnesses Interop ℤ/3 ℤ/5 with combination = crt-backed, and
-- combination crt-interop ≡ crt-backed definitionally. The combination's
-- residue system (mod 3 ∧ mod 5) IS the ℤ/15 CRT structure — the iso to
-- ℤ/15 itself is Algebra.Quotient.CRT.CRT-as-QuotientProduct. Non-vacuity
-- of the product is INHERITED (interop-non-vacuous): a ⊤-cone cannot be a
-- combination, since BackedUP carries content.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Interop where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Vacuous)
open import Substrate.Category.UniversalProperty.Backed
  using (BackedUP; arrow; solve; solves; content; backed-non-vacuous; crt-backed)

------------------------------------------------------------------------
-- 1. The factors: ℤ/3 and ℤ/5 as residue universal properties.
--    Witness a x = "x is congruent to a" (mod the modulus); the bridge is
--    the identity solution (a solves itself), and each is Contentful (1 is
--    not solved by 0). These are exactly the two legs of crt-UP.
------------------------------------------------------------------------

Z3-UP : UPArrow
Z3-UP = record { Source = ℕ ; Target = ℕ ; Witness = λ a x → x mod-suc 2 ≡ a mod-suc 2 }

Z5-UP : UPArrow
Z5-UP = record { Source = ℕ ; Target = ℕ ; Witness = λ a x → x mod-suc 4 ≡ a mod-suc 4 }

Z3-backed : BackedUP
Z3-backed = record
  { arrow = Z3-UP ; solve = λ a → a ; solves = λ a → refl ; content = 1 , 0 , λ () }

Z5-backed : BackedUP
Z5-backed = record
  { arrow = Z5-UP ; solve = λ a → a ; solves = λ a → refl ; content = 1 , 0 , λ () }

------------------------------------------------------------------------
-- 2. Interop A B — A and B interoperate: a backed combination whose single
--    solution witnesses both factors at once (the cone with legs to A, B).
------------------------------------------------------------------------

record Interop (A B : BackedUP) : Set₁ where
  field
    combination : BackedUP
    -- the combined problem carries a problem for each factor:
    legA : Source (arrow combination) → Source (arrow A)
    legB : Source (arrow combination) → Source (arrow B)
    -- the combined solution, read in each factor's target:
    solnA : Source (arrow combination) → Target (arrow A)
    solnB : Source (arrow combination) → Target (arrow B)
    -- and it genuinely solves both, simultaneously (the two legs):
    bridge-A : (s : Source (arrow combination)) → Witness (arrow A) (legA s) (solnA s)
    bridge-B : (s : Source (arrow combination)) → Witness (arrow B) (legB s) (solnB s)

open Interop public

-- non-vacuity of the product is inherited: the combination carries content,
-- so an interoperation can never collapse to ⊤.
interop-non-vacuous : {A B : BackedUP} (i : Interop A B) → ¬ Vacuous (arrow (combination i))
interop-non-vacuous i = backed-non-vacuous (combination i)

------------------------------------------------------------------------
-- 3. ⊗ : the multiplicative operation — A ⊗ B (given they interoperate).
------------------------------------------------------------------------

_⊗_∣_ : (A B : BackedUP) → Interop A B → BackedUP
(A ⊗ B ∣ i) = combination i

------------------------------------------------------------------------
-- 4. THE WITNESS: ℤ/3 and ℤ/5 interoperate, and their product is the CRT
--    (ℤ/15) structure. crt-interop is a pure projection of crt-backed: its
--    legs are the two coordinates of crt-UP's source (ℕ × ℕ), its solution
--    is crt-backed's combine-bridge, and the two leg-witnesses are the two
--    halves of crt-backed's own proven congruence (combine-mod-m / -n).
------------------------------------------------------------------------

crt-interop : Interop Z3-backed Z5-backed
crt-interop = record
  { combination = crt-backed
  ; legA  = proj₁
  ; legB  = proj₂
  ; solnA = solve crt-backed
  ; solnB = solve crt-backed
  ; bridge-A = λ s → proj₁ (solves crt-backed s)
  ; bridge-B = λ s → proj₂ (solves crt-backed s)
  }

-- THE RING IDENTITY, definitionally: [ℤ/3] ⊗ [ℤ/5] = [ℤ/15].
crt-ring-identity : (Z3-backed ⊗ Z5-backed ∣ crt-interop) ≡ crt-backed
crt-ring-identity = refl
