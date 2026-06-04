------------------------------------------------------------------------
-- Substrate.WitnessTower.Diagonal
--
-- ONE ATOM, THREE FACES (user, 2026-06-04): "this is diagonalization, too;
-- the same disagreement that happens at a diagonal is the disagreement that
-- happens at grades is the disagreement that happens between the cone's apex
-- and its base."
--
-- The atom is the F₂ fact `𝟙 + b ≢ b`: the residue at a coordinate ALWAYS
-- disagrees with its source there. (Constructive negation — a derivation of
-- ⊥ from the equation via constructor disjointness, reusing Algebra.F2's
-- 𝟙≢𝟘 / 𝟘≢𝟙 — not absence-of-proof.) It is `flip-disagrees`. Its three
-- instantiations, all the SAME atom:
--
--   * APEX vs BASE (the cone). The Hodge residue ★ (FaceSet) flips the apex
--     bit: head (★ (b ∷ f)) = 𝟙 + b, which disagrees with the original head
--     b. The newest (apex) coordinate at each dimension is the cone's own
--     diagonal entry — ★ flips it. `apex-disagrees`.
--   * GRADES (no fixed point). Hence the cell-level ★ has NO fixed face:
--     ★ S ≡ S is impossible, because they already disagree at the apex.
--     `★-no-fixpoint`. (The grade-LABEL shadow is Hodge.witness-distinct.)
--   * THE DIAGONAL (Cantor). Given rows M i, the witness D whose i-th bit is
--     the flip 𝟙 + (M i)ᵢ differs from EVERY row at coordinate i — so D is
--     not among the rows. `cantor-diagonal`. Same flip, run along i.
--
-- So Cantor's diagonal, the grade ★'s fixed-point-freeness, and the cone's
-- apex/base distinction are one phenomenon: the residue disagreeing with the
-- quotient at the distinguished coordinate. The disagreement is exactly the
-- wedge residue (FaceSet.★) refusing to vanish.
--
-- Zero postulates, --safe --without-K. All algebra imported.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Diagonal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; head; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; 𝟙≢𝟘; 𝟘≢𝟙; +-assoc)
open import Substrate.Algebra.F2.Vector
  using (Vector; _+ⱽ_; +ⱽ-assoc; +ⱽ-comm; +ⱽ-self-inverse; +ⱽ-identityˡ)
open import Substrate.WitnessTower.FaceSet using (Face; ★)
open import Substrate.Category.Lawvere
  using (FixedPointFree; diag; diag-not-in-family; InvolutiveResidue;
         CommutingInvolutions)

------------------------------------------------------------------------
-- 1. THE ATOM. The residue 𝟙 + b never equals its source b. Constructive:
--    case on b routes to F₂'s existing constructor-disjointness refutations.
------------------------------------------------------------------------

flip-disagrees : (b : F₂) → 𝟙 + b ≡ b → ⊥
flip-disagrees 𝟘 eq = 𝟙≢𝟘 eq    -- 𝟙 + 𝟘 = 𝟙, so the equation is 𝟙 ≡ 𝟘
flip-disagrees 𝟙 eq = 𝟘≢𝟙 eq    -- 𝟙 + 𝟙 = 𝟘, so the equation is 𝟘 ≡ 𝟙

------------------------------------------------------------------------
-- 2. APEX vs BASE. ★ flips the apex bit (head (★ (b ∷ f)) = 𝟙 + b), so the
--    residue disagrees with the face at the apex — the cone's diagonal entry.
------------------------------------------------------------------------

apex-disagrees : {n : ℕ} (b : F₂) (f : Vector n) → ★ (b ∷ f) ≡ (b ∷ f) → ⊥
apex-disagrees b f eq = flip-disagrees b (cong head eq)

------------------------------------------------------------------------
-- 3. GRADES (no fixed point). The cell-level ★ has no fixed face: a face is
--    always a cons (apex ∷ base), and they disagree at the apex.
------------------------------------------------------------------------

★-no-fixpoint : {n : ℕ} (S : Face n) → ★ S ≡ S → ⊥
★-no-fixpoint (b ∷ f) eq = apex-disagrees b f eq

------------------------------------------------------------------------
-- 4. THE DIAGONAL (Cantor). Any D whose i-th bit is the flip of row i's
--    i-th bit differs from row i — at coordinate i. The same atom, indexed
--    by i along the diagonal. No row equals D ⟹ D is not in the list.
------------------------------------------------------------------------

cantor-diagonal :
  {n : ℕ} (M : Fin n → Vector n) (D : Vector n)
  (is-flip : (i : Fin n) → lookup D i ≡ 𝟙 + lookup (M i) i)
  (i : Fin n) → D ≡ M i → ⊥
cantor-diagonal M D is-flip i eq =
  flip-disagrees (lookup (M i) i)
    (trans (sym (is-flip i)) (cong (λ v → lookup v i) eq))

------------------------------------------------------------------------
-- 5. ALL THREE ARE LAWVERE'S THEOREM (Category.Lawvere). The atom is the
--    δ-free of a fixed-point-free endo on F₂; the diagonal is the Set
--    instance of diag-not-in-family. So the cone apex/base distinction, the
--    grade ★'s fixed-point-freeness, and Cantor are not three theorems — they
--    are this one base theorem, read over F₂. (The wedge residue is the δ;
--    the certified r<b would make δ canonical over every carrier = keystone.)
------------------------------------------------------------------------

-- F₂ with the residue δ = (𝟙 +_) is a fixed-point-free carrier; its δ-free
-- IS flip-disagrees. The whole arc's atom, packaged as a Lawvere instance.
F₂-fpf : FixedPointFree F₂
F₂-fpf = record { δ = 𝟙 +_ ; δ-free = flip-disagrees }

-- the diagonal, re-derived as Lawvere's theorem at V = F₂ (function form):
-- no family I → (I → F₂) contains its own diagonal twist.
cantor-lawvere : {I : Set} (M : I → I → F₂) (i : I) → diag F₂-fpf M ≡ M i → ⊥
cantor-lawvere = diag-not-in-family F₂-fpf

-- F₂'s residue is moreover a fixed-point-free INVOLUTION (δ² = id, the green
-- double-negation): 𝟙 + (𝟙 + b) = b by +-assoc (𝟙 + 𝟙 = 𝟘, then 𝟘 + b = b).
-- So the collapse∘lift round-trip is its own inverse — the graded flip, and the
-- Z/2 that contains both ends (degree 1 = the diagonal, degree 0 = the return).
F₂-ir : InvolutiveResidue F₂
F₂-ir = record
  { δ       = 𝟙 +_
  ; δ-free  = flip-disagrees
  ; δ-invol = λ b → sym (+-assoc 𝟙 𝟙 b)
  }

-- THE GAUGE V₄ (one of TWO V₄ kinds). F₂² = the tetrahedron's 4 vertices; the
-- two coordinate-translation flips e₁ +ⱽ_ and e₂ +ⱽ_ are commuting involutions
-- (reusing Algebra.F2.Vector's group laws), so {id, +e₁, +e₂, +e₁₂} is Klein
-- four — the NORMAL "gauge" V₄ of all double-transpositions (the translation
-- regular rep). It is NOT the whole V₄ story: S₄ also has three INTERFACE V₄s
-- (one double-transposition d + two transpositions), and gauge ∩ interface =
-- a shared V₂ = ⟨d⟩ — the seam (WitnessTower.B3Split splits the 4 Klein-fours
-- by cycle type; WitnessTower.SharedMiddle models the shared-middle V₂ on the
-- certified Groups.V4; the EXACT intersection is posited there, not yet built).
-- So: one graded flip = one Z/2; this gauge V₄ = two commuting flips; the
-- shared V₂ between gauge and interface is one common flip d.
e₁ e₂ : Vector 2
e₁ = 𝟙 ∷ 𝟘 ∷ []
e₂ = 𝟘 ∷ 𝟙 ∷ []

F₂²-V₄ : CommutingInvolutions (Vector 2)
F₂²-V₄ = record
  { δ₁ = e₁ +ⱽ_
  ; δ₂ = e₂ +ⱽ_
  ; δ₁-inv = λ v → trans (sym (+ⱽ-assoc e₁ e₁ v))
                   (trans (cong (_+ⱽ v) (+ⱽ-self-inverse e₁)) (+ⱽ-identityˡ v))
  ; δ₂-inv = λ v → trans (sym (+ⱽ-assoc e₂ e₂ v))
                   (trans (cong (_+ⱽ v) (+ⱽ-self-inverse e₂)) (+ⱽ-identityˡ v))
  ; commute = λ v → trans (sym (+ⱽ-assoc e₂ e₁ v))
                    (trans (cong (_+ⱽ v) (+ⱽ-comm e₂ e₁)) (+ⱽ-assoc e₁ e₂ v))
  }

------------------------------------------------------------------------
-- THE TWO V₄s SHARING A V₂, on the FLIP FOUNDATION (not group enumeration).
-- The gauge V₄ above is the translations — every non-identity flip is
-- fixed-point-FREE. An INTERFACE V₄ shares the V₂ ⟨d⟩ (d = +e₁₂, the double-
-- transposition) but its OTHER generator σ (coordinate swap) FIXES a point.
-- So the shared element is exactly the fixed-point-free one: the flip atom
-- (δ-free) IS the discriminator that locates the seam — gauge ∩ interface =
-- the free part of the interface = ⟨d⟩. (The full subgroup-set intersection
-- as 4-element sets is the remaining concrete step; the WHY is now atomic.)
------------------------------------------------------------------------

-- the shared double-transposition d = translation by e₁₂ = e₁ +ⱽ e₂.
e₁₂ : Vector 2
e₁₂ = 𝟙 ∷ 𝟙 ∷ []

-- the interface's transposition: swap the two coordinates. It is an
-- involution, and it FIXES the origin (unlike a translation).
σ : Vector 2 → Vector 2
σ (a ∷ b ∷ []) = b ∷ a ∷ []

σ-involution : (v : Vector 2) → σ (σ v) ≡ v
σ-involution (a ∷ b ∷ []) = refl

-- σ FIXES a point — so it is NOT a free flip (NOT a translation/gauge element).
σ-fixes-origin : σ (𝟘 ∷ 𝟘 ∷ []) ≡ (𝟘 ∷ 𝟘 ∷ [])
σ-fixes-origin = refl

-- σ commutes with the shared d (so the interface is a V₄).
σ-commutes-d : (v : Vector 2) → σ (e₁₂ +ⱽ v) ≡ e₁₂ +ⱽ (σ v)
σ-commutes-d (a ∷ b ∷ []) = refl

-- the INTERFACE V₄ = ⟨shared d, σ⟩: two commuting involutions, one shared
-- with the gauge (d) and one that fixes a point (σ).
interface-V₄ : CommutingInvolutions (Vector 2)
interface-V₄ = record
  { δ₁ = e₁₂ +ⱽ_                 -- the SHARED V₂ generator d
  ; δ₂ = σ                       -- the transposition (fixes the origin)
  ; δ₁-inv = λ v → trans (sym (+ⱽ-assoc e₁₂ e₁₂ v))
                   (trans (cong (_+ⱽ v) (+ⱽ-self-inverse e₁₂)) (+ⱽ-identityˡ v))
  ; δ₂-inv = σ-involution
  ; commute = σ-commutes-d
  }

-- THE SEAM, atomic. The shared d is fixed-point-FREE (a genuine flip), via the
-- flip atom at coordinate 0 — so it lies in the (all-free) gauge V₄. σ is NOT
-- (σ-fixes-origin). So among the interface's non-identity elements, exactly the
-- shared d is free: gauge ∩ interface = ⟨d⟩, located by δ-free alone.
shared-d-free : (v : Vector 2) → (e₁₂ +ⱽ v) ≡ v → ⊥
shared-d-free (a ∷ b ∷ []) eq = flip-disagrees a (cong head eq)
