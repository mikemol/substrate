------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.MetricGauge.GenericBridge
--
-- Bridges the dim-4 specific SymBilinForm-4 (Vector 10 packing) to the
-- generic SymBilinForm at n=4 (Fin 4 → Fin 4 → F₂ + symmetry).
--
-- Mirror of HodgeDim3.MetricGauge.GenericBridge at dim 4.
--
-- After this slice:
--
--   * `SymBilinForm-4-to-generic M : BilinForm 4` — convert the
--     Vector 10 packing into a 4×4 matrix function.
--   * `is-symmetric-bridged-4` — the bridged matrix is automatically
--     symmetric.
--   * `bilinear-form-of-bridge-4` — the dim-4 specific
--     bilinear-form-of-4 (with its left-associated 16-term expansion)
--     equals the generic bilinear-form-of (with its right-associated
--     double sum-F₂) modulo associativity / +-identityʳ cleanups.
--   * `metric-id-4-eq-bridged` — the dim-4 metric-id-4 bridges to the
--     generic metric-id pointwise.
--   * `bilinear-form-of-metric-id-4-bridge` — direct equality at
--     metric-id-4.
--
-- Enables (deferred):
--
--   * Demote `·F-eq-metric-id-4-bilin` in HodgeDim4.MetricGauge.HodgeRecast.
--
-- Per `feedback_categorical_name_first`: bridge between dim-4-specific
-- representation (Vector 10 packing) and n-parametric representation.
--
-- Convention reminder. Vector 10 packing of SymBilinForm-4:
--   diagonal (a, b, c, d) at positions 0, 1, 2, 3
--   off-diagonal in lex order:
--     e = M(0,1), f = M(0,2), g = M(0,3),
--     h = M(1,2), i = M(1,3),
--     j = M(2,3)
--   at positions 4..9.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.MetricGauge.GenericBridge where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using ([]; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge
  using (SymBilinForm-4; bilinear-form-of-4; metric-id-4;
         entry-a; entry-b; entry-c; entry-d;
         entry-e; entry-f; entry-g; entry-h; entry-i; entry-j)

-- Generic infrastructure.
open import Substrate.Algebra.F2.SymBilinForm
  using () renaming (BilinForm to BilinForm-generic;
                     IsSymmetric to IsSymmetric-generic;
                     bilinear-form-of to bilinear-form-of-generic;
                     metric-id to metric-id-generic)

------------------------------------------------------------------------
-- N-1: SymBilinForm-4-to-generic — convert Vector 10 packing into
-- a Fin 4 → Fin 4 → F₂ matrix function. 16 cases.
--
-- Matrix layout:
--   [[ a  e  f  g ]
--    [ e  b  h  i ]
--    [ f  h  c  j ]
--    [ g  i  j  d ]]
------------------------------------------------------------------------

SymBilinForm-4-to-generic : SymBilinForm-4 → BilinForm-generic 4
-- Row 0
SymBilinForm-4-to-generic M zero                   zero                   = entry-a M
SymBilinForm-4-to-generic M zero                   (suc zero)             = entry-e M
SymBilinForm-4-to-generic M zero                   (suc (suc zero))       = entry-f M
SymBilinForm-4-to-generic M zero                   (suc (suc (suc zero))) = entry-g M
-- Row 1
SymBilinForm-4-to-generic M (suc zero)             zero                   = entry-e M
SymBilinForm-4-to-generic M (suc zero)             (suc zero)             = entry-b M
SymBilinForm-4-to-generic M (suc zero)             (suc (suc zero))       = entry-h M
SymBilinForm-4-to-generic M (suc zero)             (suc (suc (suc zero))) = entry-i M
-- Row 2
SymBilinForm-4-to-generic M (suc (suc zero))       zero                   = entry-f M
SymBilinForm-4-to-generic M (suc (suc zero))       (suc zero)             = entry-h M
SymBilinForm-4-to-generic M (suc (suc zero))       (suc (suc zero))       = entry-c M
SymBilinForm-4-to-generic M (suc (suc zero))       (suc (suc (suc zero))) = entry-j M
-- Row 3
SymBilinForm-4-to-generic M (suc (suc (suc zero))) zero                   = entry-g M
SymBilinForm-4-to-generic M (suc (suc (suc zero))) (suc zero)             = entry-i M
SymBilinForm-4-to-generic M (suc (suc (suc zero))) (suc (suc zero))       = entry-j M
SymBilinForm-4-to-generic M (suc (suc (suc zero))) (suc (suc (suc zero))) = entry-d M

------------------------------------------------------------------------
-- N-2: Symmetry of the bridged matrix. 16 cases (all refl).
------------------------------------------------------------------------

is-symmetric-bridged-4 : (M : SymBilinForm-4) →
                         IsSymmetric-generic (SymBilinForm-4-to-generic M)
-- Row 0 ↔ Row 0
is-symmetric-bridged-4 M zero                   zero                   = refl
is-symmetric-bridged-4 M zero                   (suc zero)             = refl
is-symmetric-bridged-4 M zero                   (suc (suc zero))       = refl
is-symmetric-bridged-4 M zero                   (suc (suc (suc zero))) = refl
is-symmetric-bridged-4 M (suc zero)             zero                   = refl
is-symmetric-bridged-4 M (suc zero)             (suc zero)             = refl
is-symmetric-bridged-4 M (suc zero)             (suc (suc zero))       = refl
is-symmetric-bridged-4 M (suc zero)             (suc (suc (suc zero))) = refl
is-symmetric-bridged-4 M (suc (suc zero))       zero                   = refl
is-symmetric-bridged-4 M (suc (suc zero))       (suc zero)             = refl
is-symmetric-bridged-4 M (suc (suc zero))       (suc (suc zero))       = refl
is-symmetric-bridged-4 M (suc (suc zero))       (suc (suc (suc zero))) = refl
is-symmetric-bridged-4 M (suc (suc (suc zero))) zero                   = refl
is-symmetric-bridged-4 M (suc (suc (suc zero))) (suc zero)             = refl
is-symmetric-bridged-4 M (suc (suc (suc zero))) (suc (suc zero))       = refl
is-symmetric-bridged-4 M (suc (suc (suc zero))) (suc (suc (suc zero))) = refl

------------------------------------------------------------------------
-- N-3: bilinear-form-of-bridge-4 — the two definitions agree.
--
-- Dim-4 specific bilinear-form-of-4 M v w (M = (a, b, c, d, e, f, g,
-- h, i, j), v = (v₀, v₁, v₂, v₃), w = (w₀, w₁, w₂, w₃)) expands as
-- left-assoc 4-row sum, each row's inner being left-assoc 4-term:
--
--   (((v₀ · (((a·w₀ + e·w₁) + f·w₂) + g·w₃)
--      + v₁ · (((e·w₀ + b·w₁) + h·w₂) + i·w₃))
--      + v₂ · (((f·w₀ + h·w₁) + c·w₂) + j·w₃))
--      + v₃ · (((g·w₀ + i·w₁) + j·w₂) + d·w₃))
--
-- Generic bilinear-form-of (SymBilinForm-4-to-generic M) v w expands
-- as a double sum-F₂; each row right-associated with trailing 𝟘:
--
--   v₀ · (a·w₀ + (e·w₁ + (f·w₂ + (g·w₃ + 𝟘)))) +
--   (v₁ · (e·w₀ + (b·w₁ + (h·w₂ + (i·w₃ + 𝟘)))) +
--   (v₂ · (f·w₀ + (h·w₁ + (c·w₂ + (j·w₃ + 𝟘)))) +
--   (v₃ · (g·w₀ + (i·w₁ + (j·w₂ + (d·w₃ + 𝟘)))) + 𝟘)))
--
-- Bridge: per row, right-assoc-with-trailing-𝟘 → left-assoc-no-𝟘
-- (drop +𝟘, then 2 +-assoc reassociations for 4-term inner).
-- Outer: drop +𝟘, then 2 +-assoc reassociations for 4 rows.
------------------------------------------------------------------------

bilinear-form-of-bridge-4 :
  (M : SymBilinForm-4) (v w : Vector 4) →
  bilinear-form-of-4 M v w
    ≡ bilinear-form-of-generic (SymBilinForm-4-to-generic M) v w
bilinear-form-of-bridge-4
    (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ g ∷ h ∷ i ∷ j ∷ [])
    (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ [])
    (w₀ ∷ w₁ ∷ w₂ ∷ w₃ ∷ []) =
  trans LHS→canonical (sym RHS←canonical)
  where
    -- Canonical row form (right-assoc with trailing 𝟘 — matches RHS).
    row-canonical : (p q r s : F₂) → F₂
    row-canonical p q r s = p + (q + (r + (s + 𝟘)))

    -- Per-row bridge LHS-row → canonical.
    -- LHS row: ((p + q) + r) + s; canonical: p + (q + (r + (s + 𝟘))).
    row-LHS→canonical :
      (p q r s : F₂) → ((p + q) + r) + s ≡ p + (q + (r + (s + 𝟘)))
    row-LHS→canonical p q r s =
      trans (+-assoc (p + q) r s)
      (trans (+-assoc p q (r + s))
             (cong (p +_)
                   (cong (q +_)
                         (cong (r +_) (sym (+-identityʳ s))))))

    row-bridge :
      (vᵢ p q r s : F₂) →
      vᵢ · (((p + q) + r) + s) ≡ vᵢ · row-canonical p q r s
    row-bridge vᵢ p q r s = cong (vᵢ ·_) (row-LHS→canonical p q r s)

    -- LHS → row-canonical-form: apply row-bridge to each of the 4 rows.
    LHS→canonical :
      (((v₀ · (((a · w₀ + e · w₁) + f · w₂) + g · w₃)
         + v₁ · (((e · w₀ + b · w₁) + h · w₂) + i · w₃))
         + v₂ · (((f · w₀ + h · w₁) + c · w₂) + j · w₃))
         + v₃ · (((g · w₀ + i · w₁) + j · w₂) + d · w₃))
      ≡
      (((v₀ · row-canonical (a · w₀) (e · w₁) (f · w₂) (g · w₃)
         + v₁ · row-canonical (e · w₀) (b · w₁) (h · w₂) (i · w₃))
         + v₂ · row-canonical (f · w₀) (h · w₁) (c · w₂) (j · w₃))
         + v₃ · row-canonical (g · w₀) (i · w₁) (j · w₂) (d · w₃))
    LHS→canonical =
      cong₂ _+_
        (cong₂ _+_
          (cong₂ _+_ (row-bridge v₀ (a · w₀) (e · w₁) (f · w₂) (g · w₃))
                     (row-bridge v₁ (e · w₀) (b · w₁) (h · w₂) (i · w₃)))
          (row-bridge v₂ (f · w₀) (h · w₁) (c · w₂) (j · w₃)))
        (row-bridge v₃ (g · w₀) (i · w₁) (j · w₂) (d · w₃))

    -- Row abbreviations for the outer RHS bridge.
    row₀ row₁ row₂ row₃ : F₂
    row₀ = v₀ · row-canonical (a · w₀) (e · w₁) (f · w₂) (g · w₃)
    row₁ = v₁ · row-canonical (e · w₀) (b · w₁) (h · w₂) (i · w₃)
    row₂ = v₂ · row-canonical (f · w₀) (h · w₁) (c · w₂) (j · w₃)
    row₃ = v₃ · row-canonical (g · w₀) (i · w₁) (j · w₂) (d · w₃)

    -- RHS canonical form (right-assoc 4 rows + trailing 𝟘):
    --   row₀ + (row₁ + (row₂ + (row₃ + 𝟘)))
    -- ≡ ((row₀ + row₁) + row₂) + row₃   [drop 𝟘, re-assoc twice]
    RHS←canonical :
      row₀ + (row₁ + (row₂ + (row₃ + 𝟘)))
        ≡ ((row₀ + row₁) + row₂) + row₃
    RHS←canonical =
      trans (cong (row₀ +_)
                  (cong (row₁ +_) (cong (row₂ +_) (+-identityʳ row₃))))
      (trans (sym (+-assoc row₀ row₁ (row₂ + row₃)))
             (sym (+-assoc (row₀ + row₁) row₂ row₃)))

------------------------------------------------------------------------
-- N-4: metric-id-4 bridge — the dim-4 metric-id-4 maps to the generic
-- metric-id pointwise. 16 cases.
------------------------------------------------------------------------

metric-id-4-eq-bridged :
  (i j : Fin 4) →
  SymBilinForm-4-to-generic metric-id-4 i j ≡ metric-id-generic i j
-- All 16 cases by refl (both sides reduce to 𝟙 on diagonal, 𝟘 off).
metric-id-4-eq-bridged zero                   zero                   = refl
metric-id-4-eq-bridged zero                   (suc zero)             = refl
metric-id-4-eq-bridged zero                   (suc (suc zero))       = refl
metric-id-4-eq-bridged zero                   (suc (suc (suc zero))) = refl
metric-id-4-eq-bridged (suc zero)             zero                   = refl
metric-id-4-eq-bridged (suc zero)             (suc zero)             = refl
metric-id-4-eq-bridged (suc zero)             (suc (suc zero))       = refl
metric-id-4-eq-bridged (suc zero)             (suc (suc (suc zero))) = refl
metric-id-4-eq-bridged (suc (suc zero))       zero                   = refl
metric-id-4-eq-bridged (suc (suc zero))       (suc zero)             = refl
metric-id-4-eq-bridged (suc (suc zero))       (suc (suc zero))       = refl
metric-id-4-eq-bridged (suc (suc zero))       (suc (suc (suc zero))) = refl
metric-id-4-eq-bridged (suc (suc (suc zero))) zero                   = refl
metric-id-4-eq-bridged (suc (suc (suc zero))) (suc zero)             = refl
metric-id-4-eq-bridged (suc (suc (suc zero))) (suc (suc zero))       = refl
metric-id-4-eq-bridged (suc (suc (suc zero))) (suc (suc (suc zero))) = refl

------------------------------------------------------------------------
-- N-5: Direct equality at metric-id-4.
--
-- Chain the general bridge at M = metric-id-4 with sum-F₂-cong applied
-- via metric-id-4-eq-bridged.
------------------------------------------------------------------------

open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)

bilinear-form-of-metric-id-4-bridge :
  (v w : Vector 4) →
  bilinear-form-of-4 metric-id-4 v w
    ≡ bilinear-form-of-generic metric-id-generic v w
bilinear-form-of-metric-id-4-bridge v w =
  trans (bilinear-form-of-bridge-4 metric-id-4 v w)
        (sum-F₂-cong {4} (λ i →
          cong (lookup v i ·_)
               (sum-F₂-cong {4} (λ j →
                 cong (_· lookup w j) (metric-id-4-eq-bridged i j)))))

------------------------------------------------------------------------
-- N-6: Capstone documentation.
--
-- The dim-4 metric-gauge layer is now bridgeable to the n-parametric
-- SymBilinForm layer, symmetrically with the dim-3 bridge:
--
--   * Type:        SymBilinForm-4 → SymBilinForm 4 via
--                  (SymBilinForm-4-to-generic, is-symmetric-bridged-4).
--   * Evaluation:  bilinear-form-of-4 M v w ≡ bilinear-form-of-generic
--                  (bridged M) v w, at any M.
--   * Metric-id-4: bilinear-form-of-4 metric-id-4 v w ≡
--                  bilinear-form-of-generic metric-id-generic v w.
--
-- Enables (follow-on slices):
--
--   * Demote `·F-eq-metric-id-4-bilin` in HodgeDim4.MetricGauge.HodgeRecast
--     to a one-line derivation:
--       ·F-eq-metric-id-4-bilin v w
--         = trans (·F-eq-metric-id-bilin-generic v w)
--                 (sym (bilinear-form-of-metric-id-4-bridge v w))
--
--   * Eventual congruence-act bridge at dim 4 (mirror of dim-3) +
--     congruence-compose-4 if dim-4 stabiliser work needs it.
--
--   * Σ-level coupling: with both dim-3 and dim-4 bridges in place,
--     substrate code can interchange representations at either dim
--     based on which side of the bridge is more ergonomic.
------------------------------------------------------------------------
