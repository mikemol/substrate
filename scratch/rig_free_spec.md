# ⟡rig-UP-free — spec (2026-07-10). PROBE-CONFIRMED Set₀ (5th dissolution of my Set₁ call).

## Probe result (rig_free.py, numpy, verified)
- insert-at p σ ≡ ρ_p ∘ (X ⊕ σ)   where X = grade-1 generator (single element), ρ_p σ-INDEPENDENT.
  ρ_p : Fin(1+m) → Fin(1+m), ρ_p(0)=p, ρ_p(suc j)=punchIn p j.  It is the rotation cycle (0,p,..,1).
  Note X ⊕ σ = insert-at 0 σ (= 0 ∷ map suc σ), so equivalently insert-at p σ ≡ ρ_p ∘ (insert-at 0 σ).
- Every ordering at grade n is reachable from the identity (X⊕…⊕X) via adjacent-transposition
  braidings (all n≤5) → a hom respecting ⊕/braid is determined by the generator (uniqueness).
CONSEQUENCE: ◂ is a rig-term ⇒ any map respecting ⊕ and the braiding respects ◂ ⇒ the ◂-initiality
(fold-unique, COMMITTED) LIFTS to free-rig-algebra initiality where homs respect ONLY ⊕/⊗/braid. Set₀.

## Agda build (incremental; --safe --without-K, zero postulates; green-or-honest)
Step 1 (the HEART): define `ρ` (the rotation, as an image Vec / Perm) and prove
    insert-at-rot : insert-at p σ ≡ ρ p ∘perm (insert-at 0 σ)   -- via lookup-ext + punchIn defs
  (insert-at 0 σ = X ⊕ σ; check the existing _⊕_ on LehmerPath / decode to state the ⊕ side). This
  FORMALIZES "◂ is a rig-term (rotation ∘ ⊕-generator)" — the concrete dissolution.
Step 2: show ρ p is BRAIDING-generated — expressed via blockSwap / ⊕map composites (ρ p is the cycle
  moving the head to rank p = a composite of adjacent transpositions = blockSwap 1 1 lifted by ⊕map).
  Or minimally: ρ p is a permutation (IsPerm) reachable in the braid subgroup.
Step 3 (the UP): fold-braid (fold respects blockSwap) — the missing piece; then assemble: a rig-hom
  (respects ⊕ via fold-⊕, ⊗ via fold-⊗, braid via fold-braid) respects ◂ (Step 1) ⇒ unique by
  fold-unique + exists = fold. That is the free-rig-algebra UP (homs respect only ⊕/⊗/braid).
Reuse: OrientationSum (_⊕_), OrientationSumComm (blockSwap), OrientationHexagon (⊕map), Enumerate
(insert-at, Perm), IsPermutation (tail-val, lookup-map), Decompose (lookup-ext), Punctured (punchIn),
OrientationUniversal (fold, fold-unique, fold-⊕), OrientationRigUniversal (fold-⊗).
Prioritize Step 1 (highest value, most likely green). Report honestly if Step 2/3 wall.
