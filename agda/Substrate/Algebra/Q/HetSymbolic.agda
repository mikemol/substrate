------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetSymbolic
--
-- HetQ is NOT about numbers or radix — it is SYMBOLIC QUOTIENTING under a
-- term algebra. `CrossEq` (HetBasis) already takes the cross-multiply ⊗ and
-- the equality ≈R as PARAMETERS, so:
--
--   • ⊗ is a term CONSTRUCTOR of the algebra (always closed — building a term,
--     never "computing a value"); there is no arithmetic-closure question.
--   • ≈R is the algebra's CONGRUENCE (its equational theory) — the relations we
--     quotient by. That is the only "law" content.
--
-- Then HetQ A B with `p ≈H q = (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p)` is
-- precisely the FIELD OF FRACTIONS / localization of the term algebra: a/b is
-- identified with c/d exactly when the cross-terms are congruent. ℚ is the
-- instance over (ℤ, ·, ≡); this module is the instance over a FREE COMMUTATIVE
-- SEMIGROUP of symbols — no ℕ values, just atoms-as-labels and one product,
-- quotiented by commutativity + associativity. The classic cancellation law
-- a/b = (a·k)/(b·k) holds by a symbolic derivation in the congruence.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetSymbolic where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Function using (id)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Q.HetBasis

------------------------------------------------------------------------
-- A free term algebra: atoms (labels, NOT numbers) and one binary product.
------------------------------------------------------------------------

data Tm : Set where      -- ⟦shape:27e68fcc atom,_∙_⟧
  atom : ℕ → Tm
  _∙_  : Tm → Tm → Tm

infixl 7 _∙_

------------------------------------------------------------------------
-- Its equational theory (the congruence we quotient by): ∙ is a commutative
-- semigroup operation. This is the ONLY "law" content — purely symbolic.
------------------------------------------------------------------------

data _≈t_ : Tm → Tm → Set where
  rfl   : ∀ {t}      → t ≈t t
  comm  : ∀ {a b}    → (a ∙ b) ≈t (b ∙ a)
  assoc : ∀ {a b c}  → ((a ∙ b) ∙ c) ≈t (a ∙ (b ∙ c))
  congˡ : ∀ {a a′ b} → a ≈t a′ → (a ∙ b) ≈t (a′ ∙ b)
  congʳ : ∀ {a b b′} → b ≈t b′ → (a ∙ b) ≈t (a ∙ b′)
  symm  : ∀ {a b}    → a ≈t b → b ≈t a
  tran  : ∀ {a b c}  → a ≈t b → b ≈t c → a ≈t c

------------------------------------------------------------------------
-- Codecs and bridges. A cross-multiply ⊗ : A → B → R is ALWAYS two codecs
-- into a common semantics R, combined by R's product:  ⊗ a b = codecA a ·R
-- codecB b. That factorization IS the CrossMul cospan  A →codecA R ←codecB B
-- (Wedge.CrossMul: cross a b = mul R (embA a) (embB b)) — and it is exactly why
-- different symbolic LANGUAGES transport and interact: each side is translated
-- into the shared semantics R by its own bridge, and they meet there. The whole
-- zoo of instances is one constructor at three codec choices:
--     ℚ        =  viaBridges id (λ d → ⋯ ℕ↪ℤ ⋯) _*ℤ_   -- num ℤ, den ℕ, meet in ℤ
--     radix    =  viaBridges (decode 2) (decode 3) _*ℕ_  -- base-2 & base-3, meet in ℕ
--     symbolic =  viaBridges id id _∙_                   -- one language into itself
-- (`viaBridges` lives in HetBasis, next to CrossEq; imported above.)
------------------------------------------------------------------------

-- The symbolic product ∙ is itself the bridged cross with IDENTITY codecs
-- (same language on both sides, no translation needed): definitional.
∙-via-bridges : (s t : Tm) → (s ∙ t) ≡ viaBridges id id _∙_ s t
∙-via-bridges s t = refl

------------------------------------------------------------------------
-- HetQ over the term algebra: a SYMBOLIC quotient num/den of terms. The
-- cross-multiply is the term product ∙; equality is cross-multiplication
-- modulo the congruence ≈t. (= the localization / field of fractions of the
-- free commutative semigroup. No arithmetic — ∙ is a constructor.)
------------------------------------------------------------------------

open CrossEq _∙_ _≈t_ rfl symm renaming (_≈H_ to _≈s_)

-- Atoms as names (the ℕ is a LABEL, not a quantity).
a b k : Tm
a = atom 0
b = atom 1
k = atom 2

------------------------------------------------------------------------
-- Demonstrations — symbolic identifications, no numbers evaluated.
------------------------------------------------------------------------

-- (a∙b)/k  ≈  (b∙a)/k   — numerator commuted, by the congruence at one rung.
comm-num : ((a ∙ b) // k) ≈s ((b ∙ a) // k)
comm-num = congˡ comm                    -- (a∙b)∙k ≈t (b∙a)∙k

-- THE cancellation law, symbolically:  a/b  ≈  (a∙k)/(b∙k).
-- Unfolds to the cross-equation  a ∙ (b ∙ k)  ≈t  (a ∙ k) ∙ b.
cancel : (a // b) ≈s ((a ∙ k) // (b ∙ k))
cancel = tran (congʳ comm) (symm assoc)  -- a∙(b∙k) ≈t a∙(k∙b) ≈t (a∙k)∙b

-- Reflexivity on a symbolic value (CrossEq's generic ≈H-refl).
self : (a // b) ≈s (a // b)
self = ≈H-refl (a // b)
