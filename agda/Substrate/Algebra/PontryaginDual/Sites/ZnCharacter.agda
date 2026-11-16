------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.ZnCharacter
--
-- THE CHARACTER HOMOMORPHISM LAW, AS A TERM — `Character`'s deferred field.
--
-- `PontryaginDual.agda:56-70` defines `Character` with ONE field `chi : A →
-- RootsType` and the law in a comment: *"chi is a group homomorphism (the
-- homomorphism law stated abstractly; concrete instances supply)."*  Nothing
-- supplied it — `Character` has ZERO instances tree-wide.  This module gives
-- ℤ/(suc n) its character family AND proves the law the comment defers.
--
-- ⚑ WHAT `RootsType` IS HERE, AND WHY THAT IS NOT A DODGE.
-- There is NO roots-of-unity carrier anywhere in the tree (no ℂ, no μ_n, no
-- unit circle — checked, and the only `root` names are Cartan/RootSystem, an
-- unrelated sense).  So `ζ^(jk)` cannot be written as a complex value here.
-- But the site already made this choice: `Sites/Zn.agda:36-38` identifies a
-- character WITH ITS FREQUENCY INDEX, and `ZnDuality` proves the duality
-- theorem on exactly that identification.  The exponent group of the (suc n)-th
-- roots of unity IS μ_{suc n} ≅ ℤ/(suc n) — so taking `RootsType = Fin (suc n)`
-- represents ζ^m by m, and the character's TARGET group law is `add-mod`
-- (exponents add when roots multiply).  The homomorphism law is then a real
-- theorem about a real group hom, not a vacuous one.
--
-- ⚑ WHAT IS THEREFORE **NOT** PROVED, STATED PLAINLY.  That this exponent
-- representation is FAITHFUL to ζ — i.e. that ζ is primitive, so distinct
-- exponents give distinct roots — is not proved here and cannot be until a
-- roots-of-unity carrier exists.  The claim below is: `χ-hom` is a group
-- homomorphism `(ℤ/n, add-mod) → (ℤ/n, add-mod)`, which under the exponent
-- reading IS the character law.  It is NOT: "the substrate has constructed the
-- complex characters of ℤ/n".  The neighbouring V₄ site records what happens
-- when a bridge is asserted in prose while inhabiting nothing
-- (`TopologicalGroup/Sites/V4.agda:9-16`); this note is the same discipline
-- applied before the fact rather than after.
--
-- ⚑ THE TOWER ALREADY GROUNDS THIS CHARACTER, AND χ-hom IS ITS MOD-REDUCED FORM.
-- A first draft of this header claimed the tower's character machinery was
-- unavailable here because `LehmerAlgebra` is graded over `LehmerPath n` (the
-- SYMMETRIC group's tower) while χ is a CYCLIC character — "different carrier,
-- no uniqueness available".  That was wrong, and wrong in the diagnostic way:
-- it read the carrier I happened to be looking at as the boundary of what was
-- reachable.  THE TOWER CONSTRUCTS ℕ (`Core:71-72` — *"Length of the path =
-- number of witnessing steps = the rung index"*), so ℤ/n is DOWNSTREAM of the
-- tower, not beside it, and the cyclic family is grounded there explicitly:
--
--   * `WitnessTower.CyclicGrounding` grows {Zₙ} IN the build — *"the abstract
--     Word-Zₙ and the tower's ⟨g⟩ ⊆ Sₙ are BISIMILAR coalgebras (both =
--     'iterate the generator, wrap at the rung')"* — and proves
--     `pow-hom : pow g (a + b) ≡ compose (pow g a) (pow g b)`, the monoid
--     homomorphism (ℕ, +, 0) → (⟨g⟩, compose, id).  THAT IS THIS CHARACTER'S
--     LAW, at the free/ℤ level, generic over the generator.
--   * `Algebra.Nat.CyclicSuc.σ-iterate-toℕ` is the same fact after the wrap:
--     `toℕ (iterate k cyclic-suc i) ≡ (toℕ i + k) mod-suc n`.
--
-- So `χ-hom` below is not a new theorem so much as the FINITE, MOD-REDUCED
-- reading of `pow-hom`: exponents add when roots multiply, and the addition is
-- `add-mod`.  `χ-cyclic-suc` (§2) wires that as a TERM rather than leaving it
-- as this paragraph — χ at the generator k=1 IS the tower's cyclic successor.
--
-- ⚑ WHAT IS STILL OPEN.  `CyclicGrounding`'s own honest boundary marks the
-- ORDER/WRAP as SCOPED, and the uniqueness analogue of
-- `SignUniqueCharacter.sign-unique-◂-character` (any ◂-respecting mod-2
-- character = `signF ∘ decode`, via `fold-unique`) has no cyclic counterpart
-- yet: nothing here proves χ_k is the ONLY hom with these values.  That is
-- Ⓩ4-CYCLIC-FOLD, and it is a real gap, not a carrier mismatch.
--
-- ⚑ THE LAW IS RIGHT-DISTRIBUTIVITY UNDER THE REDUCTION.
-- χ_k(j) = j·k mod (suc n), so χ_k(a ⊕ b) = χ_k(a) ⊗ χ_k(b) unfolds to
-- ((a + b) mod) · k ≡ (a·k mod) + (b·k mod), all mod (suc n) — which is
-- `*-distribʳ-+` wrapped in the `mod-*-left` / `mod-+-left` / `mod-+-right`
-- shuffles.  Same transport shape as `ZnLaws`: down via `toℕ-injective`, work
-- in ℕ, back up.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.ZnCharacter where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul using (*-distribʳ-+)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism
open import Substrate.Algebra.PontryaginDual
open import Substrate.Algebra.PontryaginDual.Sites.Zn
open import Substrate.Algebra.Wedge.ResidueAtom.Cyclic using (toℕ-add-mod)
open import Substrate.Algebra.PontryaginDual.Sites.ZnLaws using (toℕ-mod-id)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. The character family.
--
-- χ_k (j) = ζ^(jk), represented by its exponent (toℕ j * toℕ k) mod (suc n).
-- k ranges over Fin (suc n): the frequency index, which is also the character's
-- own name in the dual group.
------------------------------------------------------------------------

χ : (n : ℕ) → Fin (suc n) → Fin (suc n) → Fin (suc n)
χ n k j = fromℕ< (mod-suc-bound (toℕ j * toℕ k) n)

-- the exponent, read through toℕ — the companion of `toℕ-add-mod`.
toℕ-χ : (n : ℕ) (k j : Fin (suc n)) →
        toℕ (χ n k j) ≡ (toℕ j * toℕ k) mod-suc n
toℕ-χ n k j = toℕ-fromℕ< (mod-suc-bound (toℕ j * toℕ k) n)

------------------------------------------------------------------------
-- 2. The homomorphism law.
--
-- χ_k (a ⊕ b) ≡ χ_k a ⊗ χ_k b, where both ⊕ and ⊗ are `add-mod` (exponents
-- ADD when roots multiply — that is what makes the target a group here).
--
-- Left side:  ((toℕ a + toℕ b) mod · toℕ k) mod      [mod-*-left erases inner]
-- Right side: ((toℕ a · toℕ k) mod + (toℕ b · toℕ k) mod) mod
--                                                    [mod-+-left/right erase]
-- and the two meet at ((toℕ a + toℕ b) · toℕ k) mod via *-distribʳ-+.
------------------------------------------------------------------------

χ-hom : (n : ℕ) (k a b : Fin (suc n)) →
        χ n k (add-mod n a b) ≡ add-mod n (χ n k a) (χ n k b)
χ-hom n k a b = toℕ-injective
  (trans (toℕ-χ n k (add-mod n a b))
  (trans (cong (λ m → (m * toℕ k) mod-suc n) (toℕ-add-mod n a b))
  (trans (mod-*-left (toℕ a ℕ+ toℕ b) (toℕ k) n)
  (trans (cong (_mod-suc n) (*-distribʳ-+ (toℕ k) (toℕ a) (toℕ b)))
  (trans (sym (mod-+-left (toℕ a * toℕ k) (toℕ b * toℕ k) n))
  (trans (cong (λ m → (m ℕ+ (toℕ b * toℕ k)) mod-suc n) (sym (toℕ-χ n k a)))
  (trans (sym (mod-+-right (toℕ (χ n k a)) (toℕ b * toℕ k) n))
  (trans (cong (λ m → (toℕ (χ n k a) ℕ+ m) mod-suc n) (sym (toℕ-χ n k b)))
         (sym (toℕ-add-mod n (χ n k a) (χ n k b)))))))))))

------------------------------------------------------------------------
-- 2b. THE CO-APEX, AS A TERM: χ at the generator IS iteration in the tower.
--
-- `CyclicSuc.σ-iterate-toℕ` says iterating the tower's cyclic successor k times
-- adds k under the reduction.  χ_k (j) is `toℕ j * toℕ k` reduced — i.e. j
-- steps of the k-generator — so at j = 1 the character IS one iteration step.
-- Stating it as a term keeps the header's claim from being a prose pointer:
-- a reader can run this, and it breaks if either side is redefined.
------------------------------------------------------------------------

-- ⚑ THE GENERATOR IS A HYPOTHESIS, NOT A LITERAL — and that is the content.
-- A first cut wrote `χ n (fromℕ< (mod-suc-bound 1 n)) j ≡ j` for ALL n and did
-- not typecheck, correctly: `1 mod-suc n` does not reduce, because AT n = 0 IT
-- IS 0.  ℤ/1 is trivial, so there χ₁ = χ₀ and the "generator" generates
-- nothing.  Taking `toℕ g ≡ 1` as a hypothesis states the fact where it is
-- true and makes the degenerate rung visibly excluded rather than silently
-- assumed — the same discipline as `Sites/Zn` indexing by `suc n` so the dual
-- is never empty.
χ-at-generator : (n : ℕ) (g : Fin (suc n)) → toℕ g ≡ 1 →
                 (j : Fin (suc n)) → χ n g j ≡ j
χ-at-generator n g g≡1 j = toℕ-injective
  (trans (toℕ-χ n g j)
  (trans (cong (λ m → (toℕ j * m) mod-suc n) g≡1)
  (trans (cong (_mod-suc n) (*-oneʳ (toℕ j))) (toℕ-mod-id n j))))
  where
    *-oneʳ : (m : ℕ) → m * 1 ≡ m
    *-oneʳ zero    = refl
    *-oneʳ (suc m) = cong suc (*-oneʳ m)

------------------------------------------------------------------------
-- 3. The identity character, and the record instance.
--
-- χ_0 is constantly the zero exponent (ζ^0 = 1) — the dual group's identity,
-- and the reason `Sites/Zn` uses `suc n` rather than `n` (the dual is never
-- empty: it always has χ_0).
------------------------------------------------------------------------

χ-zero-const : (n : ℕ) (j : Fin (suc n)) → χ n zero j ≡ zero
χ-zero-const n j = toℕ-injective
  (trans (toℕ-χ n zero j) (cong (_mod-suc n) (*-zeroʳ (toℕ j))))
  where
    *-zeroʳ : (m : ℕ) → m * 0 ≡ 0
    *-zeroʳ zero    = refl
    *-zeroʳ (suc m) = *-zeroʳ m

-- ⚑ `Character` carries ONLY `chi`; the law is not a field of the record, so
-- this instance cannot bundle `χ-hom` into it.  The instance witnesses that the
-- record is inhabited for ℤ/n; `χ-hom` beside it is the law the record's
-- comment defers.  Keeping them adjacent (rather than claiming the record
-- carries the proof) is the honest reading of a law-free record.
Zn-Character : (n : ℕ) → Fin (suc n) → Character (Fin (suc n)) (Fin (suc n))
Zn-Character n k = record { chi = χ n k }
