------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid
--
-- ◆ip-cox-braid + ◆ip-cox-commute — the two general-n Coxeter RELATIONS for
-- the adjacent transpositions sadj, completing the Coxeter presentation of Sₙ
-- (the involution sᵢ² = id is already `sadj-involution`, SignAbelianization).
--
--   · cox-braid   : sᵢ sᵢ₊₁ sᵢ ≡ sᵢ₊₁ sᵢ sᵢ₊₁                 (the braid relation)
--   · cox-commute : Sep a b → sₐ s_b ≡ s_b sₐ                  (disjoint commute)
--
-- At grade suc (suc n) the position-i / position-(i+1) generators are
-- `sadj (suc n) (inj1 i)` and `sadj (suc n) (suc i)` (inj1 i and suc i are the
-- two adjacent positions in Fin (suc n)). `Sep a b` witnesses b ≥ a+2 — the
-- gap that makes the transpositions (a,a+1) and (b,b+1) disjoint (one
-- orientation; commute is symmetric, so the flip is the caller's `sym`).
--
-- The ONLY new content is two pure-Fin lemmas on the index map `tp`:
--   · tp-braid   — tp (inj1 i)(tp (suc i)(tp (inj1 i) x)) ≡ tp (suc i)(tp (inj1 i)(tp (suc i) x))
--   · tp-commute — Sep a b → tp a (tp b x) ≡ tp b (tp a x)
-- each a `cong suc` induction with all bases `refl` (needs only tp's DEFINITION,
-- not tp-inv). The Perm lift is the `sadj-involution` template (SignAbelianization
-- :69-74): `apply-injective` + descend each composition to the tp form via
-- `apply-compose` + `sadj-realizes` (the `duo`/`tri` helpers), bridge with the
-- Fin lemma, climb back up the other side.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose)
open import Substrate.WitnessTower.SnGroup using (apply; apply-compose; apply-injective)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (tp; sadj-realizes)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral using (sadj; inj1)

------------------------------------------------------------------------
-- 1. Sep a b — the "b is at least 2 above a" gap witness (disjointness of the
--    adjacent transpositions (a,a+1) and (b,b+1)).
------------------------------------------------------------------------

data Sep : {m : ℕ} → Fin m → Fin m → Set where
  sep0 : {m : ℕ} (k : Fin m) → Sep {suc (suc m)} zero (suc (suc k))
  sepS : {m : ℕ} {a b : Fin m} → Sep a b → Sep (suc a) (suc b)

------------------------------------------------------------------------
-- 2. THE TWO PURE-Fin LEMMAS on the index transposition tp (cong-suc inductions,
--    all bases refl — the whole combinatorial content lives here).
------------------------------------------------------------------------

-- the braid identity on indices (6 clauses: 4 concrete at i=zero, 2 at i=suc).
tp-braid : {n : ℕ} (i : Fin n) (x : Fin (suc (suc n))) →
           tp (inj1 i) (tp (suc i) (tp (inj1 i) x))
           ≡ tp (suc i) (tp (inj1 i) (tp (suc i) x))
tp-braid zero    zero                = refl
tp-braid zero    (suc zero)          = refl
tp-braid zero    (suc (suc zero))    = refl
tp-braid zero    (suc (suc (suc x))) = refl
tp-braid (suc i) zero                = refl
tp-braid (suc i) (suc x)             = cong suc (tp-braid i x)

-- the disjoint-commute identity on indices (5 clauses: 3 at sep0, 2 at sepS).
tp-commute : {m : ℕ} {a b : Fin m} → Sep a b → (x : Fin (suc m)) →
             tp a (tp b x) ≡ tp b (tp a x)
tp-commute (sep0 k) zero          = refl
tp-commute (sep0 k) (suc zero)    = refl
tp-commute (sep0 k) (suc (suc x)) = refl
tp-commute (sepS s) zero          = refl
tp-commute (sepS s) (suc x)       = cong suc (tp-commute s x)

------------------------------------------------------------------------
-- 3. The descent helpers: reduce a compose to the tp form via apply-compose +
--    sadj-realizes (the sadj-involution template, factored). Generic over grade.
------------------------------------------------------------------------

private
  -- two-fold: apply (A ∘ B) x = fA (fB x), given each apply reduces to its tp.
  duo : {N : ℕ} (A B : Perm N) (fA fB : Fin N → Fin N) →
        ((x : Fin N) → apply A x ≡ fA x) → ((x : Fin N) → apply B x ≡ fB x) →
        (x : Fin N) → apply (compose A B) x ≡ fA (fB x)
  duo A B fA fB rA rB x =
    trans (apply-compose A B x)
      (trans (rA (apply B x)) (cong fA (rB x)))

  -- three-fold: apply (A ∘ (B ∘ A)) x = fA (fB (fA x)).
  tri : {N : ℕ} (A B : Perm N) (fA fB : Fin N → Fin N) →
        ((x : Fin N) → apply A x ≡ fA x) → ((x : Fin N) → apply B x ≡ fB x) →
        (x : Fin N) → apply (compose A (compose B A)) x ≡ fA (fB (fA x))
  tri A B fA fB rA rB x =
    trans (apply-compose A (compose B A) x)
      (trans (cong (apply A) (apply-compose B A x))
        (trans (rA (apply B (apply A x)))
          (cong fA (trans (rB (apply A x)) (cong fB (rA x))))))

------------------------------------------------------------------------
-- 4. THE DELIVERABLES: the braid + commute relations at the Perm level.
------------------------------------------------------------------------

-- ◆ip-cox-braid — sᵢ sᵢ₊₁ sᵢ ≡ sᵢ₊₁ sᵢ sᵢ₊₁ (i : Fin n, at grade suc (suc n)).
cox-braid : {n : ℕ} (i : Fin n) →
  compose (sadj (suc n) (inj1 i)) (compose (sadj (suc n) (suc i)) (sadj (suc n) (inj1 i)))
  ≡ compose (sadj (suc n) (suc i)) (compose (sadj (suc n) (inj1 i)) (sadj (suc n) (suc i)))
cox-braid {n} i = apply-injective (λ x →
  trans (tri (sadj (suc n) (inj1 i)) (sadj (suc n) (suc i)) (tp (inj1 i)) (tp (suc i))
             (sadj-realizes (suc n) (inj1 i)) (sadj-realizes (suc n) (suc i)) x)
    (trans (tp-braid i x)
      (sym (tri (sadj (suc n) (suc i)) (sadj (suc n) (inj1 i)) (tp (suc i)) (tp (inj1 i))
                (sadj-realizes (suc n) (suc i)) (sadj-realizes (suc n) (inj1 i)) x))))

-- ◆ip-cox-commute — sₐ s_b ≡ s_b sₐ for disjoint (Sep a b) positions.
cox-commute : {n : ℕ} {a b : Fin (suc n)} → Sep a b →
  compose (sadj (suc n) a) (sadj (suc n) b) ≡ compose (sadj (suc n) b) (sadj (suc n) a)
cox-commute {n} {a} {b} sep = apply-injective (λ x →
  trans (duo (sadj (suc n) a) (sadj (suc n) b) (tp a) (tp b)
             (sadj-realizes (suc n) a) (sadj-realizes (suc n) b) x)
    (trans (tp-commute sep x)
      (sym (duo (sadj (suc n) b) (sadj (suc n) a) (tp b) (tp a)
                (sadj-realizes (suc n) b) (sadj-realizes (suc n) a) x))))
