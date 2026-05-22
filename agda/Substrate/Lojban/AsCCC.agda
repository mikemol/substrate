------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC
--
-- L10 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- The bridge to the R-arc lambda-VM CCC ([[project-rarc-lambda-vm-recognition]],
-- Substrate.Category.OpcodeAlgebra). Per the arc plan, this slice is
-- the deliberate **seam** where Toki Pona's FreeLinearization side
-- will eventually intersect via universal properties — the discrete/
-- linear bridge ([[project-linguistic-rosetta-arc]]) lands here by
-- construction, without forcing intersection now.
--
-- The bridge proceeds in three layers:
--
-- 1. For any State : Set and any `gismu-as-opcode : Gismu → State →
--    State`, the endo-monoid (State → State, ∘, id) admits a free-
--    monoid extension from LojbanWord (via L8's WithTarget). Each
--    LojbanWord becomes a state-transforming program.
--
-- 2. The same data instantiates `Substrate.Category.OpcodeAlgebra`
--    with `Opcode = Gismu` and `apply = gismu-as-opcode`. So the
--    Lojban fragment plugs straight into the CCC infrastructure
--    that the codec arc already established.
--
-- 3. The free-monoid homomorphism property (extend-merge from L8)
--    is exactly the substrate-categorical promise that
--    `execute alg s (w₁ ++ w₂) ≡ execute alg (execute alg s w₁) w₂`,
--    i.e., program composition is associative — and that promise is
--    discharged here, not assumed.
--
-- The eventual Toki Pona arc will swap `M = State → State` for
-- `M = LinearMap V V` and the basis-map for vector-valued semantics;
-- the free-linear extension consumes the same universal-property
-- shape ([[project-freelinearization-names-linear-from-images]]).
-- The seam is structurally invariant.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec)
  renaming ([] to []ᵥ; _∷_ to _∷ᵥ_)
open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; sym)

open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Lojban.Gismu using (Gismu)
open import Substrate.Lojban.Word Gismu
  using (LojbanWord; ε; single; free-merge)
open import Substrate.Lojban.WordAlgebra
  using (MonoidLaws; module WithTarget)

open import Substrate.Category.OpcodeAlgebra
  using (OpcodeAlgebra; mkAlgebra; OpcodeCategory; substrate-native; execute)

------------------------------------------------------------------------
-- 1. The endo-monoid on a state carrier.
--
-- (State → State) under function composition with identity is a
-- monoid; the laws are definitional in Agda (η-equality on
-- functions + reflexivity of composition).
------------------------------------------------------------------------

module EndoMonoid (State : Set) where

  endo-comp : (State → State) → (State → State) → (State → State)
  endo-comp f g = λ s → g (f s)

  endo-id : State → State
  endo-id s = s

  endo-Monoid : MonoidLaws (State → State) endo-comp endo-id
  endo-Monoid = record
    { ·-assoc = λ _ _ _ → refl
    ; ·-id-l  = λ _ → refl
    ; ·-id-r  = λ _ → refl
    }

------------------------------------------------------------------------
-- 2. The bridge.
--
-- Given a State + a per-gismu state transformer, we get:
--   * A free-monoid extension LojbanWord → (State → State)
--     ("program") via L8's WithTarget.
--   * An OpcodeAlgebra instance with Opcode = Gismu.
--   * The execute function from OpcodeAlgebra agrees with the
--     program for Vec-shaped (rather than Word-shaped) inputs.
------------------------------------------------------------------------

module Bridge
  (State : Set)
  (gismu-as-opcode : Gismu → State → State)
  where

  open EndoMonoid State public

  ----------------------------------------------------------------------
  -- 2a. Lift to (State → State) via the free-monoid universal property.
  ----------------------------------------------------------------------

  open WithTarget (State → State) endo-comp endo-id endo-Monoid
                  gismu-as-opcode
    using (extend; extend-ε; extend-merge) public

  program : LojbanWord → State → State
  program = extend

  ----------------------------------------------------------------------
  -- 2b. Program composition (Grothendieck coherence at the CCC layer).
  --
  -- A direct corollary of L8's extend-merge — concatenating words
  -- composes their programs.
  ----------------------------------------------------------------------

  program-merge :
    (w₁ w₂ : LojbanWord) (s : State) →
    program (free-merge w₁ w₂) s ≡ program w₂ (program w₁ s)
  program-merge w₁ w₂ s = cong (λ f → f s) (extend-merge w₁ w₂)

  program-ε :
    (s : State) → program ε s ≡ s
  program-ε _ = refl

  ----------------------------------------------------------------------
  -- 2c. Plug into Substrate.Category.OpcodeAlgebra.
  --
  -- The Lojban fragment IS an OpcodeAlgebra: each gismu is a
  -- substrate-native opcode acting on State. The CCC structure of
  -- OpcodeAlgebra (per [[project-rarc-lambda-vm-recognition]])
  -- transfers to the Lojban side by this instantiation.
  ----------------------------------------------------------------------

  Lojban-OpcodeAlgebra : OpcodeAlgebra Gismu State
  Lojban-OpcodeAlgebra = mkAlgebra
    (λ _ → substrate-native)
    gismu-as-opcode

  ----------------------------------------------------------------------
  -- 2d. Agreement between `program` (Word view) and `execute`
  -- (Vec view).
  --
  -- A LojbanWord of n gismu, run as a program, produces the same
  -- final state as the same n-vector run via execute. Both are
  -- folds; the agreement holds by induction. This is the bridge's
  -- soundness witness — it certifies that the free-monoid extension
  -- and the OpcodeAlgebra execution semantics agree.
  ----------------------------------------------------------------------

  word→vec : (w : LojbanWord) → ℕ
  word→vec []      = zero
  word→vec (_ ∷ w) = suc (word→vec w)

  word→vec-data : (w : LojbanWord) → Vec Gismu (word→vec w)
  word→vec-data []      = []ᵥ
  word→vec-data (g ∷ w) = g ∷ᵥ word→vec-data w

  program-execute-agree :
    (s : State) (w : LojbanWord) →
    program w s ≡ execute Lojban-OpcodeAlgebra s (word→vec-data w)
  program-execute-agree s []      = refl
  program-execute-agree s (g ∷ w) =
    program-execute-agree (gismu-as-opcode g s) w

------------------------------------------------------------------------
-- 3. Capstone.
--
-- L10 closes the 10-slice arc: every fragment expression has a
-- categorical home in the substrate's lambda-VM CCC, with program
-- composition discharging Grothendieck coherence at the CCC layer.
-- The Toki Pona arc's FreeLinearization side will instantiate the
-- analogous bridge over a vector-space target — same universal
-- property, same seam, different carrier.
------------------------------------------------------------------------
