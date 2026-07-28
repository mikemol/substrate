------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRig
--
-- ⟡pyrig — the rig of pyast rewrites under group action, as a REUSE of the
-- free-rig functor (Algebra.Semiring.SPPF) + the witness-tower Sₙ. The generators
-- are the generic POSITIONS (Fin n); pyast contributes ONLY an interpretation — a
-- CONSUMER valuation (Fin n → A) — never a bespoke sum type. ALL of the
-- categorical/algebraic structure is the library's. Everything here is a grounded
-- CONSTRUCTION: no sum types, no subtypes, no Σ-packaging — the coordinate spaces
-- are Fin / SPPF / Perm / LehmerPath.
--
-- THE SHARPENING: the group does NOT act on `SPPF`. It acts on the GENERATOR
-- POSITIONS (Fin n). Because `SPPF` is the FREE RIG FUNCTOR, its action on a
-- generator map lifts a position-permutation to a rig-ENDOMORPHISM BY
-- FUNCTORIALITY — the free extension writes itself (`mapSPPF`). So pyast content
-- lives in the generator set, symmetry in `Perm n ↷ Fin n`, and the free functor
-- performs the lift — none of the hard multiplicative-object labelling is needed.
--
-- THE GROUP ACTION (⟡pyrig-action). `act σ = mapSPPF (apply σ)` is a genuine
-- action (a functor Sₙ → End(Objpy n)): `act-id` / `act-∘` are the free
-- functoriality of `mapSPPF` over `apply`'s OWN group-homomorphy (apply-id /
-- apply-compose). Each `act σ` is a semantics-preserving rewrite BY CONSTRUCTION
-- (a relabelling of generator positions).
--
-- GROW THE GROUP ⇒ CONSEQUENCES FOR FREE: `act` is uniform in n and in the group
-- element, so a grown-group element `insert-at p σ : Perm (suc n)` (the witness
-- tower's Sₙ→Sₙ₊₁, a new generator at Lehmer slot p) acts by the SAME `act` under
-- the SAME laws with ZERO new definitions — the new rewrites are induced by
-- functoriality (Free preserves colimits), not enumerated or tabulated.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRig where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Semiring.SPPF using (SPPF; gen; one; _⊗_; _⊕_; inside)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.SnGroup using (apply; apply-id; apply-compose; apply-injective)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; decode)
open import Substrate.WitnessTower.Wedge.OrientationFixedPoint using (decode-injective)

-- SPPF is the FREE rig functor; its action on generator maps IS the free
-- extension: a relabelling G → H lifts to a rig-endomorphism SPPF G → SPPF H.
mapSPPF : {G H : Set} → (G → H) → SPPF G → SPPF H
mapSPPF f (gen g) = gen (f g)
mapSPPF f one     = one
mapSPPF f (a ⊗ b) = mapSPPF f a ⊗ mapSPPF f b
mapSPPF f (a ⊕ b) = mapSPPF f a ⊕ mapSPPF f b

-- Objects: pyast rig-terms over n generator positions (grade = n = the Sₙ degree).
-- The meaning of each position is supplied by the consumer (pyEval); Perm n acts on Fin n.
Objpy : ℕ → Set
Objpy n = SPPF (Fin n)

-- THE rewrite under group action: a witness-tower Perm n permutes the generator
-- positions, lifted to the whole term by the free functor.
act : {n : ℕ} → Perm n → Objpy n → Objpy n
act σ = mapSPPF (apply σ)

-- `act` is a genuine group action (functor Sₙ → End(Objpy n)): identity and
-- composition are respected, from the free functoriality of `mapSPPF` over the
-- apply-homomorphy (apply-id / apply-compose). No case analysis beyond the term.
act-id : {n : ℕ} (t : Objpy n) → act (id-perm n) t ≡ t
act-id (gen g) = cong gen (apply-id g)
act-id one     = refl
act-id (a ⊗ b) = cong₂ _⊗_ (act-id a) (act-id b)
act-id (a ⊕ b) = cong₂ _⊕_ (act-id a) (act-id b)

act-∘ : {n : ℕ} (σ τ : Perm n) (t : Objpy n) →
        act (compose σ τ) t ≡ act σ (act τ t)
act-∘ σ τ (gen g) = cong gen (apply-compose σ τ g)
act-∘ σ τ one     = refl
act-∘ σ τ (a ⊗ b) = cong₂ _⊗_ (act-∘ σ τ a) (act-∘ σ τ b)
act-∘ σ τ (a ⊕ b) = cong₂ _⊕_ (act-∘ σ τ a) (act-∘ σ τ b)

-- GROW THE GROUP ⇒ CONSEQUENCES FOR FREE. A grown-group element (Sₙ→Sₙ₊₁, a new
-- generator inserted at Lehmer slot p) acts by the SAME `act`, ZERO new code —
-- and it inherits `act-id` / `act-∘` verbatim at grade (suc n).
act-grown : {n : ℕ} → Fin (suc n) → Perm n → Objpy (suc n) → Objpy (suc n)
act-grown p σ = act (insert-at p σ)

------------------------------------------------------------------------
-- THE ORBIT COORDINATE (⟡pyrig-orbit). An orbit is NOT a collapse — `act`
-- generates it, but its points are genuinely DISTINCT, COORDINATIZED by a
-- RESIDUE. `a = recon q b r`: a point = an orbit representative `rep`
-- reconstructed with a residue `r : LehmerPath n` — the factoradic address whose
-- per-level `◂` digits ARE the orientations
-- ([[adjunction-is-the-wedge-residue-counit]]: r = counit-defect = orientation =
-- Lehmer digit). The coordinate space is `LehmerPath n` — a TOTAL CONSTRUCTION,
-- NOT a Σ-carved subset of connecting perms (no subtypes): the point IS its
-- residue, and `pyRecon rep` is the total map from coordinate to point. Different
-- points of one orbit = different residues; the residue is KEPT (never discarded),
-- so `(rep, r)` reconstructs the exact point losslessly. This is the coupling the
-- "unfused axes" reading misses: symmetry (WHICH point) and interpretation (its
-- meaning, supplied by the consumer via pyEval) meet at the point-within-the-orbit
-- — the meaning is orbit-invariant, the residue is exactly what the meaning forgets
-- and the interning must keep.
------------------------------------------------------------------------

pyRecon : {n : ℕ} → Objpy n → LehmerPath n → Objpy n
pyRecon rep r = act (decode r) rep

------------------------------------------------------------------------
-- ⟡pyrig-torsor — the residue is a GENUINE coordinate. On the position-SPINE
-- (each generator position used exactly once) distinct residues give distinct
-- points: `pyRecon (spine n)` is injective in the residue, so `LehmerPath n ≅`
-- the spine's orbit — a torsor. "Different points of one orbit" is then not a
-- slogan but a theorem, proved from the tower's OWN faithfulness
-- (apply-injective, decode-injective) via the free functoriality of mapSPPF.
------------------------------------------------------------------------

-- functoriality of the free extension: mapSPPF respects composition.
mapSPPF-∘ : {G H K : Set} (f : H → K) (g : G → H) (t : SPPF G) →
            mapSPPF f (mapSPPF g t) ≡ mapSPPF (λ x → f (g x)) t
mapSPPF-∘ f g (gen x) = refl
mapSPPF-∘ f g one     = refl
mapSPPF-∘ f g (a ⊗ b) = cong₂ _⊗_ (mapSPPF-∘ f g a) (mapSPPF-∘ f g b)
mapSPPF-∘ f g (a ⊕ b) = cong₂ _⊕_ (mapSPPF-∘ f g a) (mapSPPF-∘ f g b)

-- constructor injectivity (SPPF is non-indexed, so this is fine without-K).
gen-inj : {G : Set} {a b : G} → gen a ≡ gen b → a ≡ b
gen-inj refl = refl
⊕-injˡ : {G : Set} {a b c d : SPPF G} → (a ⊕ b) ≡ (c ⊕ d) → a ≡ c
⊕-injˡ refl = refl
⊕-injʳ : {G : Set} {a b c d : SPPF G} → (a ⊕ b) ≡ (c ⊕ d) → b ≡ d
⊕-injʳ refl = refl

-- the spine: gen 0 ⊕ gen 1 ⊕ … ⊕ gen (n-1) — every position exactly once, in order.
spine : (n : ℕ) → Objpy n
spine zero    = one
spine (suc n) = gen fzero ⊕ mapSPPF fsuc (spine n)

-- the spine SEPARATES: two relabellings that agree on it agree pointwise. (The
-- whole content of "each position appears once": the term witnesses every position.)
spine-sep : {n : ℕ} {B : Set} (f g : Fin n → B) →
            mapSPPF f (spine n) ≡ mapSPPF g (spine n) → (i : Fin n) → f i ≡ g i
spine-sep {suc n} f g eq fzero     = gen-inj (⊕-injˡ eq)
spine-sep {suc n} f g eq (fsuc i) =
  spine-sep (λ x → f (fsuc x)) (λ x → g (fsuc x))
    (trans (sym (mapSPPF-∘ f fsuc (spine n)))
           (trans (⊕-injʳ eq) (mapSPPF-∘ g fsuc (spine n)))) i

-- so the action is FREE on the spine (a permutation is recovered from its effect),
act-faithful-spine : {n : ℕ} (σ τ : Perm n) →
                     act σ (spine n) ≡ act τ (spine n) → σ ≡ τ
act-faithful-spine σ τ eq = apply-injective (spine-sep (apply σ) (apply τ) eq)

-- and therefore distinct residues give distinct points: the spine's orbit is a
-- LehmerPath-torsor. THIS is "what it means to be at different points in one orbit".
pyRecon-spine-injective : {n : ℕ} (r₁ r₂ : LehmerPath n) →
                          pyRecon (spine n) r₁ ≡ pyRecon (spine n) r₂ → r₁ ≡ r₂
pyRecon-spine-injective r₁ r₂ eq =
  decode-injective r₁ r₂ (act-faithful-spine (decode r₁) (decode r₂) eq)

-- The interpretation leg: the ONE universal fold into any rig. The MEANING of each
-- generator position is supplied by the CONSUMER as a valuation (Fin n → A) — the
-- module fixes only the generic rewrite machinery, never the pyast semantics. It IS
-- `inside`: every valid semantics-preserving readout is this universal fold.
pyEval : {A : Set} {n : ℕ} → Semiring A → (Fin n → A) → Objpy n → A
pyEval = inside
