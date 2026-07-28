{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.LeibnizDetPerm — ⟡leibniz-det-perm-general.
--
-- THE ∀-n THEOREM: det (P σ) ≡ sign σ, for EVERY permutation σ.
--
-- `PermMatrixDet` (⟡leibniz-det-of-perm-matrix) verified this by `refl` at
-- n = 2, 3. Here it is the general theorem, over an arbitrary `Semiring A`
-- carrying a MULTIPLICATIVE square-root-of-unity `ε₂` (`ε₂ *A ε₂ ≡ 1A`) — the
-- μ₂ sign of ⟡leibniz-det-sum, reached by log / divide-by-two / antilog, NOT
-- fielded as an additive negation.
--
-- ⚑ THE SUM-COLLAPSE IS THE PROOF (steps 2 + 3).
-- `det (Pmat σ) = Σ_{τ∈Sₙ} signVal(sign τ)(mono τ (Pmat σ))`, and the monomial
-- of the permutation matrix is a KRONECKER INDICATOR:
--     mono τ (Pmat σ) = Πⱼ (Pmat σ)[j, τ j] = Πⱼ δ(τ j, σ j) = [τ = σ]
-- (via `LeibnizMonomialDirect.mono≡dprod` + `remQuot-combine`). So every off-
-- diagonal summand VANISHES (`indicator-0`, `prodFin-zero`, zero-absorb) and the
-- diagonal one survives as `signVal(sign σ)(1A)` — the one-hot `sumF` collapse
-- (`sumF-onehot`) over the Sₙ enumeration (`enumerate-surjective`/`-injective`).
-- The feared "minor of a permutation matrix" crux does NOT exist: the cofactor
-- fold is already the direct indexed product (`mono≡dprod`).
--
-- ⚑ THE TOWER ◂-STEP (`det-P-◂`). The proof does NOT reduce effort below the
-- sum-collapse (det IS that sum) — but the user's orbit-centric preference is
-- honored as an ARCHITECTURAL layer: `det ∘ P ∘ decode` is a PARITY CHARACTER
-- over the ordering tower. Each `_◂ p` multiplies the determinant by
-- ε₂^(finParity p) — the sign of the Lehmer digit's position — which is exactly
-- `InsertionParity.insertion-parity-B` (`signF (decode (l ◂ p)) ≡ finParity p +
-- signF (decode l)`, the proven group theory the tower attaches to its inductive
-- step). So `det-P-◂` exhibits `det∘P∘decode` as the fold of the sign algebra,
-- composably — the same shape the whole `Orientation*` tower runs.
--
-- ⚑ Pmat REDUNDANCY (honest). `PermMatrixDet.Pmat` is a nested-`with` pattern-
-- match (a self-contained refl witness at n = 2, 3); this module's `Pmat` is the
-- δ-based general form. They are the SAME permutation matrix; the concrete one is
-- kept as the concrete-arity check, this one carries the ∀-n proof. NOT unified —
-- the concrete refl witness has no ∀-n obligation and this one has no arity limit.
--
-- Zero postulates, zero holes. Pole at ℤ (via LeibnizDet's WithSign, ε₂ = -1)
-- lands `det (P σ) ≡ (-1)^(sign σ)` = the classical Leibniz determinant of the
-- permutation matrix, machine-checked at every n.
------------------------------------------------------------------------

module Substrate.WitnessTower.LeibnizDetPerm where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.WitnessTower.Enumerate using (Perm; perms; lengthL)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.LehmerPath
  using (LehmerPath; _◂_; encode; decode; decode-encode; decode-is-perm)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.LehmerTowerMorphism using (finParity; lehmer-graded; F₂-target)
open import Substrate.WitnessTower.InsertionParity
  using (insertion-parity-B; sign-lehmer-morphism-unconditional)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.Graded.Morphism
  using (GradedDivStrMorphism; comp-gdsm; map-C)
open import Substrate.WitnessTower.Sn
  using (enumerate; enumerate-is-perm; enumerate-injective; enumerate-surjective)
import Substrate.WitnessTower.LeibnizDet as LD
import Substrate.WitnessTower.LeibnizMonomialDirect as Dir

open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid    using (Monoid; semigroup; ε)
open import Substrate.Algebra.Semiring
  using (Semiring; +-monoid; *-monoid; zero-absorb-left; zero-absorb-right)

module DetPerm (A : Set) (S : Semiring A) (ε₂ : A)
               (ε₂-sq : (Magma._·_ (magma (semigroup (*-monoid S)))) ε₂ ε₂ ≡ ε (*-monoid S)) where

  private
    _+A_ = Magma._·_ (magma (semigroup (+-monoid S)))
    0A   = ε (+-monoid S)
    _*A_ = Magma._·_ (magma (semigroup (*-monoid S)))
    1A   = ε (*-monoid S)
    +-idˡ = Monoid.ε-left  (+-monoid S)
    +-idʳ = Monoid.ε-right (+-monoid S)
    *-idˡ = Monoid.ε-left  (*-monoid S)
    *-assoc = Semigroup.·-assoc (semigroup (*-monoid S))
    *-absˡ = zero-absorb-left  S
    *-absʳ = zero-absorb-right S

  open LD.Det A S using (Mat; sumF)
  open LD.Det.WithSign A S ε₂ ε₂-sq using (det; signVal)
  open Dir.Direct A _*A_ 1A using (dprod; mono; mono≡dprod; prodFin; prodFin-cong)

  ------------------------------------------------------------------------
  -- Kronecker δ, and the clean permutation matrix Pmat.
  ------------------------------------------------------------------------

  δ : {n : ℕ} → Fin n → Fin n → A
  δ a b with a ≟ b
  ... | yes _ = 1A
  ... | no  _ = 0A

  δ-same : {n : ℕ} (a : Fin n) → δ a a ≡ 1A
  δ-same a with a ≟ a
  ... | yes _  = refl
  ... | no ¬e = ⊥-elim (¬e refl)

  δ-diff : {n : ℕ} {a b : Fin n} → ¬ (a ≡ b) → δ a b ≡ 0A
  δ-diff {a = a} {b} ¬e with a ≟ b
  ... | yes e = ⊥-elim (¬e e)
  ... | no  _ = refl

  Pmat : {n : ℕ} → Perm n → Mat n
  Pmat {n} σ k = δ (proj₂ (remQuot {n} n k)) (lookup σ (proj₁ (remQuot {n} n k)))

  ------------------------------------------------------------------------
  -- prodFin over ones / with a zero.
  ------------------------------------------------------------------------

  prodFin-ones : {k : ℕ} (f : Fin k → A) → ((i : Fin k) → f i ≡ 1A) → prodFin f ≡ 1A
  prodFin-ones {zero}  f h = refl
  prodFin-ones {suc k} f h =
    trans (cong₂ _*A_ (h zero) (prodFin-ones (λ i → f (suc i)) (λ i → h (suc i))))
          (*-idˡ 1A)

  prodFin-zero : {k : ℕ} (f : Fin k → A) (j₀ : Fin k) → f j₀ ≡ 0A → prodFin f ≡ 0A
  prodFin-zero {suc k} f zero     fz =
    trans (cong (_*A prodFin (λ i → f (suc i))) fz) (*-absˡ _)
  prodFin-zero {suc k} f (suc j₀) fz =
    trans (cong (f zero *A_) (prodFin-zero (λ i → f (suc i)) j₀ fz)) (*-absʳ _)

  ------------------------------------------------------------------------
  -- dprod l (Pmat σ) ≡ prodFin (λ j → δ (decode l j) (σ j)), via remQuot-combine.
  ------------------------------------------------------------------------

  dprod-Pmat : {n : ℕ} (l : LehmerPath n) (σ : Perm n) →
               dprod l (Pmat σ) ≡ prodFin {n} (λ j → δ (lookup (decode l) j) (lookup σ j))
  dprod-Pmat {n} l σ =
    prodFin-cong {n}
      (λ j → cong (λ pr → δ (proj₂ pr) (lookup σ (proj₁ pr)))
                  (remQuot-combine {n} {n} j (lookup (decode l) j)))

  ------------------------------------------------------------------------
  -- THE INDICATOR: dprod l (Pmat σ) is 1A if decode l ≡ σ, else 0A.
  ------------------------------------------------------------------------

  indicator-1 : {n : ℕ} (l : LehmerPath n) (σ : Perm n) →
                decode l ≡ σ → dprod l (Pmat σ) ≡ 1A
  indicator-1 {n} l σ eq =
    trans (dprod-Pmat l σ)
      (prodFin-ones _
        (λ j → trans (cong (λ v → δ (lookup v j) (lookup σ j)) eq)
                     (δ-same (lookup σ j))))

  -- find a coordinate where two vectors differ. (element size m decoupled from
  -- the length n, since peeling a cons drops the length but not the element type.)
  find-diff : {m n : ℕ} (u v : Vec (Fin m) n) → ¬ (u ≡ v) →
              Σ (Fin n) (λ j → ¬ (lookup u j ≡ lookup v j))
  find-diff []      []      ne = ⊥-elim (ne refl)
  find-diff (x ∷ u) (y ∷ v) ne with x ≟ y
  ... | no  x≢y = zero , x≢y
  ... | yes refl with find-diff u v (λ e → ne (cong (x ∷_) e))
  ...   | j , d = suc j , d

  indicator-0 : {n : ℕ} (l : LehmerPath n) (σ : Perm n) →
                ¬ (decode l ≡ σ) → dprod l (Pmat σ) ≡ 0A
  indicator-0 {n} l σ ne with find-diff (decode l) σ ne
  ... | j₀ , d =
    trans (dprod-Pmat l σ)
          (prodFin-zero _ j₀ (δ-diff d))

  ------------------------------------------------------------------------
  -- sumF collapse: a one-hot function sums to its nonzero value.
  ------------------------------------------------------------------------

  sumF-allzero : {k : ℕ} (f : Fin k → A) → ((i : Fin k) → f i ≡ 0A) → sumF f ≡ 0A
  sumF-allzero {zero}  f h = refl
  sumF-allzero {suc k} f h =
    trans (cong₂ _+A_ (h zero) (sumF-allzero (λ i → f (suc i)) (λ i → h (suc i))))
          (+-idˡ 0A)

  sumF-onehot : {k : ℕ} (f : Fin k → A) (i₀ : Fin k) →
                ((i : Fin k) → ¬ (i ≡ i₀) → f i ≡ 0A) → sumF f ≡ f i₀
  sumF-onehot {suc k} f zero     h =
    trans (cong (f zero +A_) (sumF-allzero (λ i → f (suc i)) (λ i → h (suc i) (λ ()))))
          (+-idʳ (f zero))
  sumF-onehot {suc k} f (suc i₀) h =
    trans (cong₂ _+A_ (h zero (λ ()))
                      (sumF-onehot (λ i → f (suc i)) i₀
                        (λ i i≢ → h (suc i) (λ e → i≢ (suc-inj e)))))
          (+-idˡ (f (suc i₀)))
    where
      suc-inj : {i j : Fin k} → (suc i ≡ suc j) → i ≡ j
      suc-inj refl = refl

  ------------------------------------------------------------------------
  -- signVal 0A ≡ 0A (odd summands vanish).
  ------------------------------------------------------------------------

  signVal-zero : (b : F₂) → signVal b 0A ≡ 0A
  signVal-zero 𝟘 = refl
  signVal-zero 𝟙 = *-absʳ ε₂

  ------------------------------------------------------------------------
  -- THE THEOREM: det (P σ) ≡ sign σ (as ±1), for every permutation σ.
  ------------------------------------------------------------------------

  det-P : {n : ℕ} (σ : Perm n) → IsPerm σ → det {n} (Pmat σ) ≡ signVal (signF σ) 1A
  det-P {n} σ pf with enumerate-surjective n σ pf
  ... | i₀ , eq =
    trans (sumF-onehot summand i₀ off)
          diag
    where
      summand : Fin (lengthL (perms n)) → A
      summand i =
        signVal (signF (enumerate n i))
                (mono (encode (enumerate n i) (enumerate-is-perm n i)) (Pmat σ))

      -- off-diagonal: for i ≢ i₀, the monomial vanishes (enumerate i ≠ σ).
      off : (i : Fin (lengthL (perms n))) → ¬ (i ≡ i₀) → summand i ≡ 0A
      off i i≢ =
        trans (cong (signVal (signF (enumerate n i)))
                    (trans (mono≡dprod (encode (enumerate n i) (enumerate-is-perm n i)) (Pmat σ))
                           (indicator-0 (encode (enumerate n i) (enumerate-is-perm n i)) σ
                             (λ dl≡σ →
                               i≢ (enumerate-injective n
                                     (trans (trans (sym (decode-encode (enumerate n i) (enumerate-is-perm n i)))
                                                   dl≡σ)
                                            (sym eq)))))))
              (signVal-zero (signF (enumerate n i)))

      -- diagonal: summand i₀ ≡ signVal (signF σ) 1A.
      diag : summand i₀ ≡ signVal (signF σ) 1A
      diag =
        trans (cong (signVal (signF (enumerate n i₀)))
                    (trans (mono≡dprod (encode (enumerate n i₀) (enumerate-is-perm n i₀)) (Pmat σ))
                           (indicator-1 (encode (enumerate n i₀) (enumerate-is-perm n i₀)) σ
                             (trans (decode-encode (enumerate n i₀) (enumerate-is-perm n i₀)) eq))))
              (cong (λ b → signVal b 1A) (cong signF eq))

  ------------------------------------------------------------------------
  -- THE TOWER ◂-STEP: det (P (decode l)) is a PARITY CHARACTER over the tower.
  -- Each ◂ multiplies the determinant by ε₂^(finParity p) — the sign of the
  -- Lehmer digit's position — which is exactly `insertion-parity-B` (the
  -- proven group theory the tower attaches to its inductive step). This exhibits
  -- det∘P∘decode as the fold of the parity algebra, i.e. as sign, composably.
  ------------------------------------------------------------------------

  signVal-hom : (a b : F₂) (x : A) → signVal (a +F b) x ≡ signVal a (signVal b x)
  signVal-hom 𝟘 b x = refl
  signVal-hom 𝟙 𝟘 x = refl
  signVal-hom 𝟙 𝟙 x =
    -- signVal 𝟘 x ≡ signVal 𝟙 (signVal 𝟙 x), i.e. x ≡ ε₂ *A (ε₂ *A x).
    sym (trans (sym (*-assoc ε₂ ε₂ x))
               (trans (cong (λ w → w *A x) ε₂-sq) (*-idˡ x)))

  det-P-◂ : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
            det {suc n} (Pmat (decode (l ◂ p)))
            ≡ signVal (finParity p) (det {n} (Pmat (decode l)))
  det-P-◂ l p =
    trans (det-P (decode (l ◂ p)) (decode-is-perm (l ◂ p)))
      (trans (cong (λ b → signVal b 1A) (insertion-parity-B l p))
        (trans (signVal-hom (finParity p) (signF (decode l)) 1A)
          (cong (signVal (finParity p)) (sym (det-P (decode l) (decode-is-perm l))))))

  ------------------------------------------------------------------------
  -- THE COVER (⟡det-P-graded-morphism): det∘P∘decode as a GradedDivStrMorphism.
  --
  -- `det-P-◂` IS `respects-recon` for a morphism out of the Lehmer tower into a
  -- constant-A target whose grade-raising recon is `signVal r a` (multiply by the
  -- Lehmer-digit's ε₂-sign). So `det ∘ Pmat ∘ decode` is a FIRST-CLASS graded
  -- morphism, not a per-step lemma — the tower-character reading made a term.
  --
  -- ⚑ IT FACTORS (the generative unification). `signVal-hom` IS `respects-recon`
  -- for the μ₂ CHARACTER morphism `χ : F₂-target → det-sign-target` (χ b = signVal
  -- b 1A). So `det-sign-morphism` composes as `χ ∘ (the proven sign graded
  -- morphism)` — `det-factors-through-sign` (= `det-P`) exhibits det∘P∘decode as
  -- the sign tower morphism post-composed with the μ₂ character. Two threads
  -- previously separate — the graded SIGN morphism and the Leibniz determinant —
  -- are one composite. det IS the μ₂-character image of the tower's sign cocycle.
  ------------------------------------------------------------------------

  -- det ∘ Pmat ∘ decode, with n pinned via `Pmat {n}` (Mat n = Fin (n*n) is a
  -- non-injective index, so the grade must be supplied explicitly).
  detPd : {n : ℕ} → LehmerPath n → A
  detPd {n} l = det {n} (Pmat {n} (decode l))

  -- the constant-A target: grade-raising recon = multiply by the digit's ε₂-sign.
  det-sign-target : GradedDivStr (λ _ → A) (λ _ → F₂)
  det-sign-target = record { recon = λ n a r → signVal r a }

  -- det ∘ Pmat ∘ decode, as a graded morphism (respects-recon = det-P-◂).
  det-sign-morphism : GradedDivStrMorphism lehmer-graded det-sign-target
  det-sign-morphism = record
    { map-C          = detPd
    ; map-R          = λ {n} p → finParity {suc n} p
    ; respects-recon = λ n l p → det-P-◂ l p
    }

  -- the μ₂ character χ b = signVal b 1A, as a graded morphism F₂-target →
  -- det-sign-target (respects-recon = signVal-hom): a group hom (F₂,+,𝟘)→(A,*A,1A).
  χ-morphism : GradedDivStrMorphism F₂-target det-sign-target
  χ-morphism = record
    { map-C          = λ b → signVal b 1A
    ; map-R          = λ r → r
    ; respects-recon = λ n b r → signVal-hom r b 1A
    }

  -- THE FACTORISATION: det∘P∘decode ≡ χ ∘ (the proven sign graded morphism).
  -- (= det-P, at the map-C level: det (Pmat (decode l)) ≡ signVal (signF (decode l)) 1A.)
  det-factors-through-sign :
    {n : ℕ} (l : LehmerPath n) →
    map-C det-sign-morphism l
    ≡ map-C (comp-gdsm χ-morphism sign-lehmer-morphism-unconditional) l
  det-factors-through-sign l = det-P (decode l) (decode-is-perm l)
