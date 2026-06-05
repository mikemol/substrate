------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality
--
-- THE WEDGE AS CONNECTING MAP, made concrete on the published detector —
-- sheaf-theoretic / cohomological contextuality (Abramsky–Brandenburger;
-- Abramsky, Barbosa, Kishida, Lal, Mansfield, "Contextuality, Cohomology and
-- Paradox"), restricted to the All-vs-Nothing fragment over ℤ₂ = F₂. It lives
-- here, with the wedge machinery, because the obstruction's connecting
-- homomorphism IS a wedge read (scratch/dent_system_primer.md §5): XOR-of-
-- contexts is the connecting map, the obstruction is the kept residue.
--
-- THE SETUP (their framework, in F₂). A measurement scenario is a family of
-- contexts; a possibilistic empirical model is, in the AvN case, one F₂
-- PARITY EQUATION per context: `⟨ lhs , s ⟩ = rhs`, where `lhs` is the
-- context's support (which measurements it constrains) and `rhs ∈ F₂` its
-- parity outcome. A GLOBAL SECTION is one assignment `s : Vector n` satisfying
-- every context's equation at once. The model is CONTEXTUAL iff there is no
-- global section although each context is individually satisfiable.
--
-- THE OBSTRUCTION (their Čech H¹ class). XOR-ing constraints is the CONNECTING
-- MAP (`_⊕ᶜ_`, the wedge read): if `s` satisfies `c₁` and `c₂` it satisfies
-- `c₁ ⊕ᶜ c₂` (`⊕ᶜ-satisfies`). When a cycle of contexts XORs to the constraint
-- `(𝟎ⱽ, 𝟙)` — empty support, odd parity, literally "0 = 1" — that derived
-- constraint is the nonzero cohomology class: entailed by the model yet
-- satisfied by nothing (`zero-one-unsat`). Its irreducible core is `𝟘 ≢ 𝟙`,
-- the substrate's FLIP ATOM (Substrate.WitnessTower.Diagonal; primer §7:
-- Lawvere/Cantor). The contextuality obstruction bottoms out at the same single
-- distinction that founds the diagonal arguments.
--
-- WHAT THEY DO vs WHAT WE ADD. The literature uses `H¹ ≠ 0` as a *detector*
-- (it witnesses contextuality, then stops). Here the obstruction is KEPT AS
-- DATA (`tri-obstruction`, proved `≡ con 𝟎ⱽ 𝟙` by refl) and the connecting map
-- `⊕ᶜ-satisfies` is a *retained operation* that CONSTRUCTS the refutation from
-- any purported section. The non-existence of a global section is therefore a
-- genuine `P ⊢ ⊥` function (`tri-contextual`), not absence-of-proof — faithful
-- to the substrate's constructive-negation discipline (no LEM): we carry the
-- class, we do not merely flag it.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.F2
  using (F₂; 𝟘; 𝟙; _+_; _·_; 𝟘≢𝟙; +-assoc; +-comm; ·-distribʳ-+)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; _+ⱽ_)

------------------------------------------------------------------------
-- 0. A 4-term commutative-monoid rearrangement, reused below.
------------------------------------------------------------------------

+-middle4 : (a b c d : F₂) → ((a + b) + (c + d)) ≡ ((a + c) + (b + d))
+-middle4 a b c d =
  trans (+-assoc a b (c + d))
        (trans (cong (a +_)
                  (trans (sym (+-assoc b c d))
                         (trans (cong (_+ d) (+-comm b c))
                                (+-assoc c b d))))
               (sym (+-assoc a c (b + d))))

------------------------------------------------------------------------
-- 1. The F₂ inner product ⟨lhs, s⟩ — the "evaluate this parity at the
--    assignment s" pairing — and its two structural lemmas.
------------------------------------------------------------------------

⟨_,_⟩ : ∀ {n} → Vector n → Vector n → F₂
⟨ []     , []     ⟩ = 𝟘
⟨ x ∷ xs , y ∷ ys ⟩ = (x · y) + ⟨ xs , ys ⟩

-- ADDITIVITY in the first argument: this is what makes XOR-of-contexts a
-- well-defined operation on parities — the connecting map's linearity.
inner-add : ∀ {n} (u v s : Vector n) → ⟨ u +ⱽ v , s ⟩ ≡ ⟨ u , s ⟩ + ⟨ v , s ⟩
inner-add []         []         []         = refl
inner-add (ux ∷ us) (vx ∷ vs) (sx ∷ ss) =
  trans (cong₂ _+_ (·-distribʳ-+ sx ux vx) (inner-add us vs ss))
        (+-middle4 (ux · sx) (vx · sx) ⟨ us , ss ⟩ ⟨ vs , ss ⟩)

-- The empty support pairs to 𝟘 against any assignment.
inner-zero : ∀ {n} (s : Vector n) → ⟨ 𝟎ⱽ {n} , s ⟩ ≡ 𝟘
inner-zero []       = refl
inner-zero (x ∷ xs) = inner-zero xs

------------------------------------------------------------------------
-- 2. Contexts as parity constraints; satisfaction; the connecting map.
------------------------------------------------------------------------

record Constraint (n : ℕ) : Set where
  constructor con
  field
    lhs : Vector n        -- the context's support (which measurements)
    rhs : F₂              -- the parity outcome
open Constraint public

-- s satisfies a context iff its assignment hits the parity.
satisfies : ∀ {n} → Vector n → Constraint n → Set
satisfies s c = ⟨ lhs c , s ⟩ ≡ rhs c

-- THE CONNECTING MAP: XOR two contexts (supports and parities both). This is
-- the wedge read as the connecting homomorphism (primer §5).
_⊕ᶜ_ : ∀ {n} → Constraint n → Constraint n → Constraint n
c₁ ⊕ᶜ c₂ = con (lhs c₁ +ⱽ lhs c₂) (rhs c₁ + rhs c₂)

-- and it is sound on satisfaction: a section of both is a section of the XOR.
-- (The cocycle composes; this is the retained operation we carry.)
⊕ᶜ-satisfies : ∀ {n} {s : Vector n} (c₁ c₂ : Constraint n) →
               satisfies s c₁ → satisfies s c₂ → satisfies s (c₁ ⊕ᶜ c₂)
⊕ᶜ-satisfies {s = s} c₁ c₂ e₁ e₂ =
  trans (inner-add (lhs c₁) (lhs c₂) s) (cong₂ _+_ e₁ e₂)

------------------------------------------------------------------------
-- 3. THE OBSTRUCTION. The constraint (empty support, odd parity) — "0 = 1" —
--    is satisfied by nothing. Its core is the flip atom 𝟘 ≢ 𝟙.
------------------------------------------------------------------------

zero-one-unsat : ∀ {n} (s : Vector n) → ¬ satisfies s (con (𝟎ⱽ {n}) 𝟙)
zero-one-unsat s eq = 𝟘≢𝟙 (trans (sym (inner-zero s)) eq)

------------------------------------------------------------------------
-- 4. THE MINIMAL CONTEXTUAL MODEL — the parity triangle (the simplest AvN /
--    GHZ-family cohomologically-contextual model):
--      x_a + x_b = 0      x_b + x_c = 0      x_a + x_c = 1
--    Each context is satisfiable; no global assignment satisfies all three.
------------------------------------------------------------------------

tri-c₁ tri-c₂ tri-c₃ : Constraint 3
tri-c₁ = con (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) 𝟘
tri-c₂ = con (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) 𝟘
tri-c₃ = con (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) 𝟙

-- LOCAL CONSISTENCY: each context is individually satisfiable (different
-- assignments — that is exactly the contextuality, no single one serves all).
tri-local₁ : Σ (Vector 3) (λ s → satisfies s tri-c₁)
tri-local₁ = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl

tri-local₂ : Σ (Vector 3) (λ s → satisfies s tri-c₂)
tri-local₂ = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl

tri-local₃ : Σ (Vector 3) (λ s → satisfies s tri-c₃)
tri-local₃ = (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl

-- THE OBSTRUCTION, KEPT AS DATA (the carry): the XOR of the three contexts
-- is the unsatisfiable "0 = 1" — the nonzero Čech H¹ class, computed not flagged.
tri-obstruction : Constraint 3
tri-obstruction = (tri-c₁ ⊕ᶜ tri-c₂) ⊕ᶜ tri-c₃

tri-obstruction-is-0=1 : tri-obstruction ≡ con (𝟎ⱽ {3}) 𝟙
tri-obstruction-is-0=1 = refl

------------------------------------------------------------------------
-- 5. CONTEXTUALITY, constructively. No global section exists — and the proof
--    is the connecting map applied to the would-be section, landing on the
--    obstruction (a genuine P ⊢ ⊥, not LEM).
------------------------------------------------------------------------

TriGlobalSection : Set
TriGlobalSection =
  Σ (Vector 3) (λ s → satisfies s tri-c₁ × satisfies s tri-c₂ × satisfies s tri-c₃)

tri-contextual : ¬ TriGlobalSection
tri-contextual (s , e₁ , e₂ , e₃) =
  zero-one-unsat s
    (⊕ᶜ-satisfies {s = s} (tri-c₁ ⊕ᶜ tri-c₂) tri-c₃
       (⊕ᶜ-satisfies {s = s} tri-c₁ tri-c₂ e₁ e₂) e₃)
