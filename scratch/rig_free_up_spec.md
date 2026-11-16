# ⟡rig-UP-free-UP — the generic free-rig-algebra UP record (spec, 2026-07-10)

## Goal
Package the committed ⟡rig-UP-free core (OrientationRigFree: ◂ = ρ_p ∘ (X⊕·)) into a GENERIC
universal property where a hom respects ONLY ⊕/⊗/braid(rotation)/one — NOT ◂ directly. Then
uniqueness = fold-unique, existence = fold, and ◂ is respected BECAUSE it is derived.

## Committed inputs (reuse, do NOT reprove)
- OrientationRigFree: `ρ`, `insert-at-rot : insert-at p σ ≡ map (ρ p)(insert-at zero σ)`,
  `ρ-perm`, `gen-⊕-is-◂0 : (X ⊕ l) ≡ (l ◂ zero)` [by refl!], `decode-◂-rot`.
- OrientationUniversal: `LehmerAlgebra`, `fold`, `fold-unique`, `fold-⊕`.
- OrientationRigUniversal: `fold-⊗`, `replayᶜ`.  OrientationRigInitial: `RigAlgebra` (pattern to extend).

## Design — the DERIVED-STEP braided-rig-algebra
record FreeRigAlgebra C fields: base:C 0 ; one:C 1 ; _⊕ᶜ_ ; _⊗ᶜ_ ; rotᶜ : ∀{n}→Fin(suc n)→C(suc n)→C(suc n)
  ; the ⊕ᶜ / ⊗ᶜ coherence laws (as in RigAlgebra) BUT with the DERIVED step
      stepᶜ x p := rotᶜ p (one ⊕ᶜ x)
  ; so the record must field whatever coherence makes stepᶜ satisfy fold-⊕'s ⊕ᶜ-step and fold-⊗'s
    ⊗ᶜ-step (these become rotation-compat laws — the genuinely-new coherence).
From it: build a LehmerAlgebra (base, stepᶜ) ; foldF = fold on it.

## Steps (incremental, green-or-honest; --safe --without-K, zero postulates)
S1: `rotᴸ : ∀{n}→Fin(suc n)→LehmerPath(suc n)→LehmerPath(suc n)` (= encode ∘ map(ρ p) ∘ decode, or a
    structural form) + prove `◂-as-rot : l ◂ p ≡ rotᴸ p (X ⊕ l)` at the LehmerPath level (using
    gen-⊕-is-◂0 + insert-at-rot through decode/encode iso; decode-injective may close it). THE CRUX.
S2: FreeRigAlgebra record + build-LehmerAlgebra + foldF. Prove foldF respects ⊕ᶜ (fold-⊕) & ⊗ᶜ (fold-⊗)
    given the record's coherence fields.
S3: foldF-free-unique — a map g respecting (⊕ᶜ via g-⊕, rotᶜ via g-rot, one via g-one) respects stepᶜ
    (via ◂-as-rot: g(l◂p)=g(rotᴸ p (X⊕l))=rotᶜ p (g(X⊕l))=rotᶜ p (one ⊕ᶜ g l)=stepᶜ(g l,p)) ⇒ =foldF
    by fold-unique. THE UP: fold is the unique ⊕/⊗/braid/one-preserving map. (This is the free-rig-
    algebra initiality where homs need NOT mention ◂.)

## Honest flags
- S1 (◂-as-rot at LehmerPath level) is the crux; the rotᴸ transport may make g-respects-rotᴸ awkward —
  if so, report the exact obstruction. Prioritize S1 (it's the load-bearing lemma).
- This is ELEGANT PACKAGING of committed results (rig-algebra initiality already gives a Set₀ UP); the
  gain is a hom notion that doesn't mention the generating ◂. Marginal new reach; real new coherence.
