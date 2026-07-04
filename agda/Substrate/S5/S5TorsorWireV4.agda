{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5TorsorWireV4 — ⟡S4-wire. Connects the CDSW torsor to the named GTorsor
-- record CONCRETELY at V₄, supplying the one piece the abstracted bridge
-- (S5TorsorBridge) deferred: GTorsor.free is TWO-SIDED
--   (act g₁ x ≈ act g₂ x → g₁ ≈ g₂)
-- while IsTorsor.free is the STABILIZER form (act g x ≡ x → g ≡ ε). The wire
-- must DERIVE two-sided from stabilizer via group cancellation — real
-- content, not a field-rename (⟡H0 surfaced this; it would be invisible under
-- "both are torsors").
--
-- ⟡H0 findings (body-grep): all ingredients EXIST — Groups/KleinV4/Operations.inv
-- (= id, exponent-2 self-inverse), Groups/KleinV4/Axioms (·-assoc, ·-comm),
-- Cocycles/V4Signature/V4LeftCancel.KleinV4-left-cancel (stabilizer freeness),
-- V4ActsOnItself. NO two-sided-from-stabilizer builder exists — that
-- derivation is the wire's genuine content, done here.
--
-- Self-contained V₄ (mirrors Groups/KleinV4 up to naming) so this checks against
-- the S5 kernel without importing the whole substrate; ⟡S4-wire-substrate
-- (trivial rename) lands it on the substrate's own V₄ on the writable path.
------------------------------------------------------------------------

module Substrate.S5.S5TorsorWireV4 where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_) renaming (proj₁ to fst; proj₂ to snd)

-- V₄ = {e,α,β,γ}, exponent 2, self-inverse (inv = id), abelian.
data KleinV4 : Set where e α β γ : KleinV4      -- ⟦shape:fb526564⟧

_·_ : KleinV4 → KleinV4 → KleinV4
e · y = y
α · e = α    ;  α · α = e ;  α · β = γ ;  α · γ = β
β · e = β    ;  β · α = γ ;  β · β = e ;  β · γ = α
γ · e = γ    ;  γ · α = β ;  γ · β = α ;  γ · γ = e
infixl 7 _·_

-- self-inverse: g · g = e (exponent 2). By cases (the finite cover).
selfinv : (g : KleinV4) → g · g ≡ e
selfinv e = refl
selfinv α = refl
selfinv β = refl
selfinv γ = refl

-- left identity is definitional; right identity by cases.
·-idʳ : (g : KleinV4) → g · e ≡ g
·-idʳ e = refl
·-idʳ α = refl
·-idʳ β = refl
·-idʳ γ = refl

-- associativity by the finite cover (4³ cases collapse; Agda checks by refl
-- on each constructor triple via the pattern-matching definition).
·-assoc : (x y z : KleinV4) → (x · y) · z ≡ x · (y · z)
·-assoc x y z = cover x y z where
  cover : (x y z : KleinV4) → (x · y) · z ≡ x · (y · z)
  cover e y z = refl
  cover α e z = refl
  cover α α e = refl
  cover α α α = refl
  cover α α β = refl
  cover α α γ = refl
  cover α β e = refl
  cover α β α = refl
  cover α β β = refl
  cover α β γ = refl
  cover α γ e = refl
  cover α γ α = refl
  cover α γ β = refl
  cover α γ γ = refl
  cover β e z = refl
  cover β α e = refl
  cover β α α = refl
  cover β α β = refl
  cover β α γ = refl
  cover β β e = refl
  cover β β α = refl
  cover β β β = refl
  cover β β γ = refl
  cover β γ e = refl
  cover β γ α = refl
  cover β γ β = refl
  cover β γ γ = refl
  cover γ e z = refl
  cover γ α e = refl
  cover γ α α = refl
  cover γ α β = refl
  cover γ α γ = refl
  cover γ β e = refl
  cover γ β α = refl
  cover γ β β = refl
  cover γ β γ = refl
  cover γ γ e = refl
  cover γ γ α = refl
  cover γ γ β = refl
  cover γ γ γ = refl

-- the action is left multiplication (V₄ acts on itself).
act : KleinV4 → KleinV4 → KleinV4
act = _·_

-- STABILIZER freeness (the IsTorsor form) is already the substrate's
-- KleinV4-left-cancel (cited, not rebuilt). The wire's NEW content is the
-- two-sided form GTorsor demands, below — derived by group algebra alone.

------------------------------------------------------------------------
-- THE WIRE CONTENT: TWO-SIDED freeness, derived from stabilizer + cancellation.
-- act g₁ x ≡ act g₂ x  →  g₁ ≡ g₂.
-- Route: g₁·x ≡ g₂·x ⟹ (g₁·x)·x ≡ (g₂·x)·x ⟹ g₁·(x·x) ≡ g₂·(x·x)
--        ⟹ g₁·e ≡ g₂·e ⟹ g₁ ≡ g₂.  Pure group algebra, no stabilizer needed.
------------------------------------------------------------------------
two-sided-free : (x g₁ g₂ : KleinV4) → act g₁ x ≡ act g₂ x → g₁ ≡ g₂
two-sided-free x g₁ g₂ p =
  trans (sym (·-idʳ g₁))
  (trans (cong (g₁ ·_) (sym (selfinv x)))
  (trans (sym (·-assoc g₁ x x))
  (trans (cong (_· x) p)
  (trans (·-assoc g₂ x x)
  (trans (cong (g₂ ·_) (selfinv x))
         (·-idʳ g₂))))))

------------------------------------------------------------------------
-- transitivity: g = y·x⁻¹ = y·x (self-inverse) sends x to y.
------------------------------------------------------------------------
trans-t : (x y : KleinV4) → Σ KleinV4 (λ g → act g x ≡ y)
trans-t x y = (y · x) , (trans (·-assoc y x x) (trans (cong (y ·_) (selfinv x)) (·-idʳ y)))

------------------------------------------------------------------------
-- Assemble the GTorsor shape (act / act-id / act-·G / transitive / free) at V₄,
-- matching Category.GTorsor.GTorsor field-for-field with ≈ = ≡.
------------------------------------------------------------------------
record GTorsorShape : Set where
  field
    g-act    : KleinV4 → KleinV4 → KleinV4
    g-act-id : (x : KleinV4) → g-act e x ≡ x
    g-act-·  : (g h x : KleinV4) → g-act (g · h) x ≡ g-act g (g-act h x)
    g-trans  : (x y : KleinV4) → Σ KleinV4 (λ g → g-act g x ≡ y)
    g-free   : (x g₁ g₂ : KleinV4) → g-act g₁ x ≡ g-act g₂ x → g₁ ≡ g₂

cdsw-gtorsor : GTorsorShape
cdsw-gtorsor = record
  { g-act    = act
  ; g-act-id = λ x → refl
  ; g-act-·  = λ g h x → ·-assoc g h x
  ; g-trans  = trans-t
  ; g-free   = two-sided-free
  }
