{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.LeibnizMonomial — ⟡leibniz-det-alg.
--
-- THE LEIBNIZ MONOMIAL AS A `LehmerAlgebra`: for a permutation σ presented as
-- a `LehmerPath`, the unsigned product Πᵢ M[i, σ i] is the FOLD of a graded
-- algebra whose step is one cofactor expansion along row 0.
--
-- ⚑ WHY THIS IS THE TOWER'S OWN SHAPE, NOT A BESPOKE RECURSION.
-- `decode (l ◂ p) = insert-at p (decode l) = p ∷ map (punchIn p) (decode l)`
-- (LehmerPath:68, Enumerate:67). So extending a Lehmer path by the digit p
-- says exactly: row 0 takes column p, and every later row takes its old column
-- REINDEXED BY `punchIn p` (i.e. skipping column p). That IS the cofactor step,
-- and it is forced by the tower — nothing here is chosen.
--
-- ⚑ THE CARRIER IS FLAT (`Fin (n * n) → A`), ON THE ⊗ GRADING — NOT `Vec (Vec A n) n`.
-- The multiplicative index is primary and the additive/pair view is recovered
-- from it by the PROVEN bijection `*↔× : Fin (m * n) ↔ (Fin m × Fin n)`
-- (`combine` / `remQuot`, both round-trips proven). Presenting the nested view
-- as primary would put the derived side first and force the reconstruction of
-- the product structure. The flat form is also UNIFORM in n, which is what
-- `LehmerAlgebra.step`'s generic-n field requires (cf. ObjectUniverse:25-28).
--
-- ⚑ THE SIGN IS DELIBERATELY ABSENT FROM THIS ALGEBRA — kept as a graded residue,
-- not fused into the value. The Leibniz summand factors as
--     summand σ M  =  sign σ  ·  Πᵢ M[i, σ i]
-- and the LEFT factor is ALREADY PROVEN in the tower: `sign-alg` /
-- `sign-is-fold` / `sign-unique-◂-character` (SignUniqueCharacter) show that any
-- ◂-respecting mod-2 character IS `signF ∘ decode`. So the sign half needs no
-- new construction and none is made here; this module supplies only the
-- monomial half, and `mono-alg` correspondingly needs only a MONOID (_*A_, 1A)
-- — no negation, no ring.
--
-- ⚑ WHAT THIS DOES NOT YET BUILD (labelled, not smuggled):
--   ⟡leibniz-det-sum — det M = Σ over Sₙ of the signed summands. Needs the
--     existing enumeration (`Sn.enumerate` / `perms n`) and a sum; the fold here
--     gives ONE summand per permutation, which is the per-σ term, not the sum.
--   ⟡leibniz-det-of-perm-matrix — with the sum in hand, det (P σ) ≡ sign σ.
--     That would close a boundary the substrate states explicitly today:
--     OrientationRigCatPermSignChirality:8-13 records that `det(P_σ) = sign(σ)`
--     is "a NAME-COINCIDENCE here: the substrate has NO permutation matrix and
--     NO Leibniz determinant… We do NOT build a fake permutation determinant."
--     This module is the first half of making that a theorem rather than a
--     coincidence; the header there should be revisited when it lands.
--
-- Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.WitnessTower.LeibnizMonomial where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold)

------------------------------------------------------------------------
-- 1. THE FLAT MATRIX CARRIER, and the graded monomial-reader over it.
--
-- Only a MONOID is required (_*A_, 1A) — the sign is not this algebra's job.
------------------------------------------------------------------------

module Mono (A : Set) (_*A_ : A → A → A) (1A : A) where

  -- an n×n matrix over A, flat: the index is Fin (n * n), row-major through
  -- `combine` / `remQuot` (the proven *↔× bijection).
  Mat : ℕ → Set
  Mat n = Fin (n * n) → A

  -- the graded carrier: at grade n, a reader of n×n matrices.
  MonoC : ℕ → Set
  MonoC n = Mat n → A

  ------------------------------------------------------------------------
  -- 2. THE FACE MAP: the (0,p) minor, at the flat index.
  --
  -- Drop row 0 (shift the row digit by `suc`) and drop column p (reindex the
  -- column digit by `punchIn p`). Both halves are proven Foundation primitives;
  -- only the assembly is new.
  --
  -- ⚑ THE IMPLICITS OF `combine` MUST BE PINNED. `Mat n = Fin (n * n) → A` hides
  -- the grade behind multiplication, which is NOT injective, so Agda cannot
  -- recover n from the carrier type — leaving the blocked constraint
  -- `_m * suc n = n * suc n`. Writing `combine {suc n} {suc n}` resolves it.
  -- (This is the price of the flat carrier; it is a typing nuisance, not a
  -- mathematical one, and the flat form remains right for the ⊗-native reason
  -- given in the header.)
  ------------------------------------------------------------------------

  minor : {n : ℕ} → Fin (suc n) → Mat (suc n) → Mat n
  minor {n} p M k =
    M (combine {suc n} {suc n}
         (suc (proj₁ (remQuot {n} n k)))
         (punchIn p (proj₂ (remQuot {n} n k))))

  ------------------------------------------------------------------------
  -- 3. THE ALGEBRA. base = the empty product; step = one cofactor expansion.
  ------------------------------------------------------------------------

  mono-alg : LehmerAlgebra MonoC
  mono-alg = record
    { base = λ _ → 1A
    ; step = λ {n} c p → λ M → M (combine {suc n} {suc n} zero p) *A c (minor {n} p M)
    }

  -- the Leibniz monomial of the permutation `decode l`: Πᵢ M[i, (decode l) i].
  mono : {n : ℕ} → LehmerPath n → Mat n → A
  mono = fold mono-alg

------------------------------------------------------------------------
-- 4. NON-VACUITY POLES — the algebra COMPUTES the classical products.
--
-- A graded algebra is cheap to state and easy to get subtly wrong (an off-by-one
-- in `punchIn`, a transposed `combine`), so the poles are concrete numerals at
-- ℕ, checked by `refl`, at two grades. Grade 3 is included because only there
-- does `minor` produce a genuine 2×2 minor — grade 2 alone would not exercise
-- the reindexing at depth.
------------------------------------------------------------------------

open Mono ℕ _*_ 1

-- M2 = [[2,3],[5,7]]
M2 : Mat 2
M2 zero                   = 2
M2 (suc zero)             = 3
M2 (suc (suc zero))       = 5
M2 (suc (suc (suc zero))) = 7

id2 swap2 : LehmerPath 2
id2   = start ◂ zero ◂ zero
swap2 = start ◂ zero ◂ suc zero

-- the identity permutation picks the diagonal: 2 * 7
mono-id2 : mono id2 M2 ≡ 14
mono-id2 = refl

-- the transposition picks the anti-diagonal: 3 * 5
mono-swap2 : mono swap2 M2 ≡ 15
mono-swap2 = refl

-- M3 = [[1,2,3],[4,5,6],[7,8,10]]
M3 : Mat 3
M3 zero                                     = 1
M3 (suc zero)                               = 2
M3 (suc (suc zero))                         = 3
M3 (suc (suc (suc zero)))                   = 4
M3 (suc (suc (suc (suc zero))))             = 5
M3 (suc (suc (suc (suc (suc zero)))))       = 6
M3 (suc (suc (suc (suc (suc (suc zero)))))) = 7
M3 (suc (suc (suc (suc (suc (suc (suc zero))))))) = 8
M3 (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))) = 10

id3 swap3 : LehmerPath 3
id3   = start ◂ zero ◂ zero ◂ zero
swap3 = start ◂ zero ◂ zero ◂ suc zero

-- identity: 1 * 5 * 10 — the outer step takes M[0,0] and folds the 2×2 minor
-- [[5,6],[8,10]] on its diagonal.
mono-id3 : mono id3 M3 ≡ 50
mono-id3 = refl

-- the digit `suc zero` at the top sends row 0 to column 1 and reindexes the
-- rest by punchIn, giving σ = [1,0,2]: M[0,1] * M[1,0] * M[2,2] = 2 * 4 * 10.
-- (The minor here is [[4,6],[7,10]] — column 1 genuinely dropped.)
mono-swap3 : mono swap3 M3 ≡ 80
mono-swap3 = refl
