------------------------------------------------------------------------
-- Substrate.WitnessTower.FaceSet
--
-- BUILD the higher faces as OBJECTS, not just counts. WitnessTower.FaceCount
-- counts the k-faces of Δⁿ; this CONSTRUCTS them. A face of the rung-n
-- simplex is a SUBSET of its n+1 vertices — an F₂-vector indicator, reusing
-- Substrate.Algebra.F2.Vector (Vector (suc n) = Vec F₂ (suc n)). The type IS
-- the complete Boolean lattice: EVERY indicator is a face, none excluded —
-- the narration's "fully connected simplex if you flatten it" (user): flatten
-- the cone hierarchy and exactly all subsets of the vertices remain.
--
-- THE HODGE ★ IS A WEDGE RESIDUE, not a classical complement (user, twice):
-- `map not` would be "what is NOT in S" — a law-of-excluded-middle reading
-- the substrate rejects. The constructive object is what is LEFT of the
-- universe after wedging S out of it: ★ S = universe +ⱽ S. That is exactly
-- the wedge's residue r in the reconstruction `universe = recon 1 S r`
-- (Algebra.F2.Wedge: recon q b r = scale q b + r; here q=1, scale 1 S = S,
-- and + is F₂ XOR). `wedge-recon` proves S +ⱽ ★ S ≡ universe — S and its
-- residue reconstruct the universe — so ★ S is literally "what S is missing
-- to be everything", computed, not negated. The involution ★★ = id and the
-- pairing nothing ↔ universe then follow from the F₂-vector ADDITIVE GROUP
-- laws already proved in Algebra.F2.Vector — reused, not re-proved.
--
-- F₂ⁿ-GRADING REVIVAL (re the conjecture ledger): the bottom-up study KILLED
-- an F₂ⁿ grading at the PERMUTATION/support level (it grades by ℕ). At the
-- FACE level it is HONEST: faces ARE F₂-vectors and ★ IS the F₂ residue —
-- where conjectures #2/#3/#4 (graded-GF(2) / Morton-cocycle) may genuinely
-- attach (at the cells, not the permutations). Recorded; not yet built.
--
-- Zero postulates, --safe --without-K. All algebraic laws imported.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FaceSet where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Vec using (Vec; _∷_; replicate; head; tail)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector
  using (Vector; _+ⱽ_; 𝟎ⱽ;
         +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-comm; +ⱽ-assoc; +ⱽ-self-inverse)

------------------------------------------------------------------------
-- 1. Faces as subsets. A face of Δⁿ is a subset of its n+1 vertices: an
--    F₂-vector in Vector (suc n). The type is the COMPLETE lattice —
--    every indicator inhabits it, so the simplex is fully connected by
--    construction (every subset of vertices spans a face).
------------------------------------------------------------------------

Face : ℕ → Set
Face n = Vector (suc n)

-- the empty face — "in the beginning there was nothing": no vertex chosen.
nothing-face : (n : ℕ) → Face n
nothing-face n = 𝟎ⱽ

-- the full simplex — every vertex chosen ("the universe").
universe : (n : ℕ) → Face n
universe n = replicate (suc n) 𝟙

------------------------------------------------------------------------
-- 2. The cone construction on faces. A face of the (n+1)-simplex is its
--    apex bit followed by a base face: coned over the apex (𝟙) or
--    inherited from the base (𝟘). Every higher face decomposes thus,
--    UNIQUELY — the set-level Pascal split behind FaceCount.cone-step.
------------------------------------------------------------------------

-- the base face coned over the new apex (apex included).
with-apex : {n : ℕ} → Face n → Face (suc n)
with-apex f = 𝟙 ∷ f

-- the base face inherited, apex NOT included.
without-apex : {n : ℕ} → Face n → Face (suc n)
without-apex f = 𝟘 ∷ f

-- the apex bit and the base face of a higher face.
apex-bit : {n : ℕ} → Face (suc n) → F₂
apex-bit = head

base-face : {n : ℕ} → Face (suc n) → Face n
base-face = tail

-- every higher face IS its apex bit ∷ its base face (the cone split is
-- exhaustive and unique): with/without-apex cover Face (suc n).
cone-split : {n : ℕ} (f : Face (suc n)) → (apex-bit f ∷ base-face f) ≡ f
cone-split (b ∷ f) = refl

------------------------------------------------------------------------
-- 3. The Hodge ★ as the WEDGE RESIDUE. ★ S = what is left of the universe
--    after wedging S out of it = universe +ⱽ S. Constructive (a residue,
--    not a negation). All laws below are the F₂-vector additive group laws
--    from Algebra.F2.Vector — reused, never re-proved.
------------------------------------------------------------------------

★ : {n : ℕ} → Face n → Face n
★ {n} S = universe n +ⱽ S

-- THE WEDGE EQUATION at the faces: S and its residue ★ S reconstruct the
-- universe — `universe = recon 1 S (★ S)` in F₂ (scale 1 S = S, + = XOR).
-- So ★ S is genuinely the residue: what S is missing to be everything.
wedge-recon : {n : ℕ} (S : Face n) → (S +ⱽ ★ S) ≡ universe n
wedge-recon {n} S =
  trans (cong (S +ⱽ_) (+ⱽ-comm (universe n) S))
  (trans (sym (+ⱽ-assoc S S (universe n)))
  (trans (cong (_+ⱽ universe n) (+ⱽ-self-inverse S))
         (+ⱽ-identityˡ (universe n))))

-- ★★ = id: wedging out the residue returns S (F₂ self-inverse), so the
-- cell-level duality is a clean BIJECTION — count-preserving, unlike the
-- grade-LABEL reversal of WitnessTower.Hodge.dual-grade.
★-involution : {n : ℕ} (S : Face n) → ★ (★ S) ≡ S
★-involution {n} S =
  trans (sym (+ⱽ-assoc (universe n) (universe n) S))
  (trans (cong (_+ⱽ S) (+ⱽ-self-inverse (universe n)))
         (+ⱽ-identityˡ S))

------------------------------------------------------------------------
-- 4. ★ pairs the beginning (nothing) with the universe (full simplex).
--    The narration's first ★ — "the first point witnessed the universe,
--    nothing else to differentiate against" — at the cell level: the
--    residue of nothing IS the whole universe.
------------------------------------------------------------------------

-- ★ (nothing) = the universe: the residue of the empty face is everything.
★-nothing : (n : ℕ) → ★ (nothing-face n) ≡ universe n
★-nothing n = +ⱽ-identityʳ (universe n)

-- ★ (universe) = nothing: wedging the universe out of itself leaves nothing.
★-universe : (n : ℕ) → ★ (universe n) ≡ nothing-face n
★-universe n = +ⱽ-self-inverse (universe n)
