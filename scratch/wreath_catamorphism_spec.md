# ⟡rig-UP-wreath — the one catamorphism: complete spec + proof recipe (2026-07-10)

## Established (numpy, verified m,n≤4, against the REAL insert-at = p ∷ map (punchIn p) σ)
The ⊗-over-◂ recursion EXISTS — ⊗ IS a ◂-recursion (the one catamorphism). Two equivalent forms:
- POINTWISE: `(insert-at p σ) ⊗ τ` at `combine i j` = `combine ((insert-at p σ)[i]) (τ[j])`
  = ⊗-combine + insert-at lookup. (i=0 → p ; i=suc i' → punchIn p (σ[i'])).
- CONS: `(insert-at p σ) ⊗ τ = [p·n+τ block] ++ blockPunchIn_{p,n}(σ⊗τ)`, blockPunchIn skips
  the value-block [p·n, p·n+n).
Scripts: scratch/rig_cata3.py, rig_cata4.py (both forms verified).

## The KEYSTONE arithmetic identity (the whole proof reduces to this, via the toℕ route)
`combine (punchIn p x) y ≡ blockPunchIn p n (combine x y)`   -- x:Fin m, y:Fin n, p:Fin(suc m)
where blockPunchIn p n : Fin(m*n) → Fin(suc m * n) skips the block [p·n, p·n+n).
PROOF (toℕ, exactly like Foundation.Fin.Combine.Assoc.combine-assoc):
  toℕ(combine (punchIn p x) y) = toℕ(punchIn p x)·n + toℕ y
     = (toℕ x < toℕ p ? toℕ x : suc(toℕ x))·n + toℕ y
  toℕ(blockPunchIn p n (combine x y)) : combine x y has toℕ = toℕ x·n + toℕ y ;
     < p·n  iff  toℕ x < toℕ p  (since toℕ y < n) ; so skip adds n exactly when toℕ x ≥ toℕ p.
  Both sides equal ⇒ toℕ-injective closes it.  Reuse: toℕ-combine (Combine.Assoc), toℕ of
  punchIn (may need a small toℕ-punchIn lemma: toℕ(punchIn p j) = toℕ j or suc(toℕ j) by <).

## Machinery to REUSE (all exists, --safe, proven)
- ⊗-combine (OrientationProductLaws): lookup(σ⊗τ)(combine i j) ≡ combine(lookup σ i)(lookup τ j)
- tail-val (WitnessTower.IsPermutation): lookup(insert-at p σ)(suc i) ≡ punchIn p (lookup σ i)
- lookup-map (IsPermutation), lookup-ext (WitnessTower.Decompose), lookup∘tabulate
- toℕ-combine, toℕ-subst (Foundation.Fin.Combine.Assoc) ; toℕ-injective ; combine-remQuot
- pattern to MIRROR: decode-⊕-inject/raise (OrientationSumNaturality) — the ⊕-side analog,
  proven by lookup-insert-suc + punchIn-inject+ + induction. The ⊗-side is the combine analog.

## Construction (target: a single fold respecting BOTH ⊕ and ⊗ = the rig-hom)
1. Define blockPunchIn p n : Fin(m*n) → Fin(suc m·n) (skip block) — or as combine∘(punchIn on the
   quotient digit): blockPunchIn p n k = combine (punchIn p (proj₁(remQuot n k))) (proj₂(remQuot n k)).
   [Then blockPunchIn = combine ∘ (punchIn p ×id) ∘ remQuot — clean, reuses remQuot/combine.]
2. Prove the KEYSTONE identity above (toℕ route).
3. Prove ⊗-◂ recursion: lookup((insert-at p σ)⊗τ)(combine (suc i) j) ≡ ... via ⊗-combine +
   tail-val + keystone ; and the head (i=0) block via ⊗-combine + insert-at head (=p). Assemble
   by lookup-ext into: (insert-at p σ)⊗τ ≡ <cons form>.
4. Define ⊗ˡ : LehmerPath m → LehmerPath n → LehmerPath (m·n) mirroring the block-cons (n rungs
   per ◂-step), OR state fold-⊗ via decode-agreement: decode(l₁⊗ˡl₂) ≡ decode l₁ ⊗ decode l₂.
5. RigAlgebra C = LehmerAlgebra C + { one : C 1 ; times : C i → C j → C(i·j) ; + block-step compat }.
   Prove the single fold respects ⊗ (fold(l₁⊗ˡl₂) ≡ fold l₁ `times` fold l₂) by ◂-induction,
   mirroring fold-⊕. This fold is SIMULTANEOUSLY the ⊕-hom (fold-⊕, done) and ⊗-hom = the ONE
   catamorphism (common witness = the tower rung acting on both: 1 insert ↔ 1 τ-block).

## Bar: --safe --without-K, ZERO postulates, membudget for any heavy compile. Extends
OrientationUniversal (fold, fold-⊕, LehmerAlgebra). New module e.g. OrientationRigUniversal.agda.

---
## fold-⊗ (the single catamorphism) — routes + the crux (2026-07-10, after keystone committed)

KEYSTONE IS COMMITTED (OrientationProductInsert.agda): ⊗-insert-head/tail + decode-⊗ˁ green.
The remaining rung = a SINGLE fold respecting ⊗. Two routes analysed:

### Route 1 — parametric fold-⊗ (mirror fold-⊕ EXACTLY; block-step law as a HYPOTHESIS)
fold-⊕ does NOT prove ⊕ᶜ-base/⊕ᶜ-step for a concrete C — it TAKES them as parameters and shows
fold preserves ⊕. Mirror: fold-⊗ takes `_⊗ᶜ_`, `⊗ᶜ-absorb : base ⊗ᶜ y ≡ base` (0·n=0), and a
BLOCK-STEP law, and proves `fold (l₁ ⊗ˡ l₂) ≡ fold l₁ ⊗ᶜ fold l₂` by induction on l₁. This needs
⊗ˡ STRUCTURAL (not the transport one shipped). The block-step law mirrors ⊕ᶜ-step:
  ⊕ᶜ-step : (step x p) ⊕ᶜ y ≡ step (x ⊕ᶜ y) (inject+ n p)     -- ONE step
  ⊗ᶜ-step : (step x p) ⊗ᶜ y ≡ <n-fold blockStep of (x ⊗ᶜ y)>  -- n steps (the τ-block)

### Route 2 — factor-through-decode (fold = φ∘decode, φ = fold∘encode; prove φ respects ⊗)
fold l = fold(encode(decode l)) [encode-decode]. Prove `fold(encode(σ⊗τ)) ≡ fold(encode σ) ⊗ᶜ
fold(encode τ)` by induction on encode's structure / on l₁ with σ=decode l₁, using ⊗-insert-head/
tail at the ◂-step. Same crux surfaces (below).

### THE CRUX (both routes hit it) — the CONS form as a path-combinator
Clean structural recursion (rig_cata4, verified): with σ:Perm m, τ:Perm n, p:Fin(suc m),
  (insert-at p σ) ⊗ τ  ≡  headBlock p τ  ++  map (blockPunchIn p n) (σ ⊗ τ)
    headBlock p τ = tabulate (λ j → combine p (lookup τ j))   : Vec (Fin(suc m·n)) n
    (blockPunchIn p n : Fin(m·n)→Fin(suc m·n) already proven in OrientationProductInsert)
Prove this Perm-level cons via lookup-ext (splitAt n: head j → ⊗-insert-head ; tail → ⊗-insert-
tail). THEN lift to LehmerPath: `l₁ ⊗ˡ l₂` structural = the encode of this cons. The path-level
combinators (headBlock-prepend + blockPunch as ◂-rung sequences with decode proofs) are the ONLY
genuinely-new machinery; everything else reuses the committed keystone. This IS intricate (the
Lehmer encoding of a ++/blockPunch perm) — the honest research edge, NOT a trivial dissolve. The
keystone (⊗ IS a ◂-recursion) is the mathematical heart and is DONE; fold-⊗ packages it into one map.

REUSE bar: --safe --without-K, zero postulates. Extend OrientationProductInsert + OrientationUniversal.

---
## THE UNLOCK — block digits have a CLEAN closed form (2026-07-10, rig_cata6.py verified m,n≤3)

The n block-insert digits d_{n-1}(outer)..d_0(inner) that build (insert-at p σ)⊗τ from σ⊗τ are:
    d_k = p·n + encodeDigit_k(τ)          -- quotient stays p ; mantissa = the k-th Lehmer digit of τ
i.e. THE BLOCK IS l₂'s OWN LehmerPath, replayed with each digit offset by p·n. (Since encode(decode
l₂)=l₂, τ's Lehmer code = l₂'s own ◂-choices.) This is the user's "witness the interior generator's
synchronized action through tower growth": ⊗ replays l₂'s tower inside the product, synced with l₁'s
growth, offset by p. NOT the ad-hoc punchOut chain the prior agents feared — l₂'s own structure.

### Construction with the closed form
Define, by recursion on l₁:
    start      ⊗ˢ l₂ = start
    (l₁ ◂ p)   ⊗ˢ l₂ = replayOffset p l₂ (l₁ ⊗ˢ l₂)
where `replayOffset p l₂ base : LehmerPath(m·n) → LehmerPath(suc m·n)` adds n rungs (grade m·n+n =
suc m·n), replaying l₂'s digits offset by p·n — a recursion on l₂'s LehmerPath structure. Each added
rung j has grade suc(m·n+j), digit = p·n + (l₂'s j-th Lehmer digit), Fin-typed accordingly.
decode-agreement: prove decode(replayOffset p l₂ base) ≡ headBlock p (decode l₂) ++ map (blockPunchIn
p n) (decode base), which by ⊗-insert-cons (COMMITTED) = insert-at p (decode-of-base-preimage) ⊗
decode l₂. Then fold-⊗ (parametric, mirror fold-⊕): fold(replayOffset ...) reduces through fold's
◂-recursion (n steps) — the ⊗ᶜ-step law is exactly "n fold-steps replaying l₂ offset by p".

VERIFIED FORMULA (rig_cata6.py): d_k = p*n + encodeDigit_k(τ). Sample p=1,τ=(2,0,1),n=3: [5,3,3].
