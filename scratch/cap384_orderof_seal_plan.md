# ⟡cap-384 — the OrderOf opaque-seal sub-arc (COMPACTION-SAFE plan)

## STATE (2026-07-23)
- **Jacobian paydown COMMITTED** (⟡jac-lit1-wire): retired JacobianLiteral1/1A/1B (763MB old f₁ proof),
  wired JacCubeNorm.identify₁ (128MB) into the hub JacobianEncodingLiteral. Whole Algebra/Q subtree
  passes -M256m. (This commit is at the 1024m gate; the cap-tightening is DEFERRED to land with OrderOf.)
- **cap-tightening REVERTED from the tree** (not yet landed — gated on OrderOf): membudget AGDA_MB_MAX→384,
  full_build_check MEM→256m (env-overridable AGDA_FBC_MEM), CLAUDE.md 1536/1024→384/256 doc sweep. All
  documented here; re-apply WITH the OrderOf fix so the whole tree fits and the gate stays green.
- **User directive**: strict maxRSS 384 / -M256m gate, THEN decrement to AGDA_FBC_MEM=128m (tighten further).

## THE BLOCKER — measured, diagnosed
Cold `-M256m` full build (2003 modules): **2000/2003 PASS**. 3 FAILs, ALL one root:
`Substrate/Groups/Capabilities/CoxeterFin.agda` (Capabilities.agda + Manifest.agda only fail because they
RECOMPILE CoxeterFin inline when its .agdai is missing — fix CoxeterFin ⇒ all 3 pass).

**Root cause (measured, not guessed):**
- `HasOrderPerm σ k = HasFixedOrder σ k = ∀ x → iterate k σ x ≡ x` (`Foundation/Function/Iterate.agda:38`;
  Fin re-export shim `Foundation/Fin/Iterate.agda:34-35` `HasOrderPerm = F.HasFixedOrder`). A **Π type,
  NOT a record** (so it's NOT eta-blowup).
- The order proofs are **cheap everywhere they're BUILT (82 MB)** — Fin-from-Cyclic (82), Z7/Z5-Coxeter-Fin
  (81) — because they're built with σ **ABSTRACT** (a module parameter), so `iterate k σ` never reduces.
- The `CoxeterFinCapability` record field `σ-aⁿ=ε : HasOrderPerm σ n` is instantiated at the **CONCRETE**
  `σ₇ = Fin-from-Cyclic.σ {6}`. Forming the field type `∀ x → iterate 7 σ₇ x ≡ x` **NORMALIZES the 7-fold
  concrete permutation power** → **307 MB**. Even a SINGLE cap-Z₇ alone = 308 (per-file split does NOT help).
- Verified: record WITHOUT the σ-aⁿ=ε field = 82 MB (the field IS the entire cost).
- FAILED fixes: retire-value (value already cheap 82); opaque-at-USE-site `opaque ord₇ = <proof>` (timed
  out — the block still checks the alias against the reducing type); σ-alignment (pass σ₇ not cyclic-suc,
  still 307). The **VALUE is cheap; the TYPE normalizes** — so the seal must be on the TYPE.

## THE FIX — opaque the TYPE (the cross-module elaboration memo, one layer up from the Jacobian case)
Define `OrderOf` as an **opaque alias** for HasOrderPerm so the field type is a NON-REDUCING token:
```agda
opaque
  OrderOf : {A : Set} → (A → A) → ℕ → Set
  OrderOf f k = HasFixedOrder f k        -- (or HasOrderPerm at the Fin layer)
```
- Change `CoxeterFinCapability`'s field `σ-aⁿ=ε : HasOrderPerm σ n` → `σ-aⁿ=ε : OrderOf σ n`.
  Outside the opaque block `OrderOf σ₇ 7` does NOT unfold → the field type never normalizes `iterate 7 σ₇`.
- The order proofs must be produced AS `OrderOf σ k`, wrapped at **ABSTRACT σ** (in Fin-from-Cyclic, where
  `OrderOf σ k` unfolds to `HasOrderPerm σ k` cheaply — σ abstract, no iterate normalization). Under
  `unfolding OrderOf`, `σ-HasOrderPerm-sealed : OrderOf σ k = σ-HasOrderPerm`. Cost stays ~82 MB.
- cap-Zₙ construction: field type `OrderOf σ₇ 7` (opaque) matched against the wrapped proof's type
  `OrderOf σ₇ 7` — SYNTACTIC match, NO iterate normalization → ~82 MB. Fits -M256m AND -M128m (82 < 128).

## SATURATED EDIT LIST (agent aa3bcbc, read-only, all file:line-verified) — TURN-KEY, 4 edits

**KEY IDIOM FINDING:** the repo uses `opaque` blocks but **NEVER the `unfolding` keyword** (all "unfolding"
hits are prose). The established `--safe --without-K` pattern (exemplars: `F2/Linear/FromImages/Permutation/
Cyclic.agda:60-74` `cyclic-Linear` + `cyclic-HasOrder`; `F2/Linear/FromImages.agda:163` `linear-from-images`)
is: **seal the def AND its conversion lemmas INSIDE one opaque block** (block members see each other's
defs); callers use the lemmas, never `unfolding`. The Cyclic.agda:47-59 header is verbatim our rationale
("sealed... type-checked ONCE at abstract n... a consumer instantiates at concrete n, references them as
black boxes, NEVER normalises"). So the seal uses `seal-order`/`unseal-order` conversion fns, NOT `unfolding`.

**HOST (low uncertainty):** `Foundation.Fin.Iterate` (the Fin layer, `HasOrderPerm : (Fin n→Fin n)→ℕ→Set`),
NOT the generic `Function.Iterate` — the whole Coxeter chain uses the Fin form. Single import site.

**FACTS:** `HasOrderPerm {n} = F.HasFixedOrder {Fin n}`, `HasFixedOrder f k = ∀ x → iterate k f x ≡ x`
(`Function/Iterate.agda:37-38`, `Fin/Iterate.agda:34-35`). The abstract-σ proof is at
`Groups/Coxeter/Cyclic/Base.agda:84-88` (`σ = cyclic-suc {n}`; `σ-HasOrderPerm = cyclic-suc-HasOrderPerm {n}`,
n = module param = ABSTRACT = cheap). It rides a `public` re-export chain Base→Existential→Core→NthPower→
Cyclic→Fin-from-Cyclic→each Zn-Coxeter-Fin (so a NEW `σ-OrderOf` propagates with NO intermediate edits).
Consumers of `.σ-aⁿ=ε`: **NONE** outside CoxeterFin (3 hits: field decl 46, builder param 64, assign 75) —
seal is fully transparent, no downstream `unfolding` ever needed. `Capabilities.agda` `Provides`/`complete`
just names the record TYPE / returns the built `cap-Zₙ` value → inherits cap cost, no independent heaviness.
`Manifest.agda` pure imports. NEITHER needs edits. ⚠ Do NOT touch `Cyclic/Core.agda:72` (`σ-HasOrderPerm k`
— a DIFFERENT computational use; keep `σ-HasOrderPerm` unchanged, only ADD `σ-OrderOf`).

**EDIT 1 — `Foundation/Fin/Iterate.agda`** (after line 35, the HasOrderPerm def):
```agda
opaque
  OrderOf : ∀ {n} → (Fin n → Fin n) → ℕ → Set
  OrderOf f k = HasOrderPerm f k
  seal-order   : ∀ {n} {f : Fin n → Fin n} {k} → HasOrderPerm f k → OrderOf f k
  seal-order   p = p
  unseal-order : ∀ {n} {f : Fin n → Fin n} {k} → OrderOf f k → HasOrderPerm f k
  unseal-order p = p
```
**EDIT 2 — `Groups/Coxeter/Cyclic/Base.agda`** (after line 88; extend the line 17-18 import to add
`OrderOf; seal-order`): `σ-OrderOf : OrderOf σ (suc n)` ; `σ-OrderOf = seal-order σ-HasOrderPerm`. (Leave
`σ-HasOrderPerm` intact — Core uses it.)
**EDIT 3 — the 5 `Zn-Coxeter-Fin.agda`** (Z2:1, Z3:2, Z4:3, Z5:4, Z7:6 — the `Fin-from-Cyclic <n-1>` arg):
add one rename to each `renaming(…)` block, e.g. Z7 after line 21: `; σ-OrderOf to σ₇-OrderOf-from-Z7-Coxeter`.
**EDIT 4 — `Groups/Capabilities/CoxeterFin.agda`**: line 21 import `OrderOf` (drop `HasOrderPerm` if unused);
line 46 field → `σ-aⁿ=ε : OrderOf σ n`; line 64 builder param → `(σ-aⁿ=ε : OrderOf σ n) →`; lines
95/105/115/125/135 replace each `Zₙ-Fin.σₙ-HasOrderPerm-from-Zn-Coxeter` → `Zₙ-Fin.σₙ-OrderOf-from-Zn-Coxeter`.

NO edits to Coxeter-Fin-Generic / Fin-from-Cyclic / Cyclic.agda / Capabilities.agda / Manifest.agda.

**-M128m follow-on seal candidates (light, order-2, same shape):** `F2/HodgeDim4/HodgeStar.agda:125`
`complement-HasOrderPerm`; `GL3F2/GaugeGenerators.agda:66` `σ₂-HasOrderPerm`;
`F2/HodgeDim4/ReservedBridge/AlternativesAsOrbit.agda:83` `σ-swap12-HasOrderPerm`. (Heavy dense-Linear
relatives `cyclic-Linear`/`linear-from-images` are ALREADY opaque-sealed.) `σ-aⁿ=ε` is the ONLY record
field of this type tree-wide.

**ALTERNATIVE (rejected):** wrap at the instances `(seal-order Zₙ-Fin.σₙ-HasOrderPerm-…)` — makes the field
check trivial too, but the abstract-σ wrap (Edit 2) guarantees the concrete instances never touch `iterate`.
Use Edits 1-4 as written.

## OTHER -M128m OFFENDERS (the tightening pass, AFTER 256m green)
The census is unreliable — after OrderOf lands -M256m green, run the cold build at `AGDA_FBC_MEM=128m` to
enumerate the next tier. Each new offender: same discipline — is it a heavy VALUE (retire/prove-cheaper) or
a heavy NEUTRAL-in-a-TYPE (opaque-seal the type)? The `OrderOf` pattern generalizes: any `HasOrderPerm`/
`iterate`/`normalize`-shaped neutral instantiated at concrete args in a widely-checked type → opaque-seal it.

## VERIFICATION (per step, then whole)
- Isolate each edited module under `-M256m` (and later `-M128m`) with `/usr/bin/time -v agda --safe -i.
  <mod> +RTS -M256m -RTS` from `agda/`; confirm cap-Z₇ (largest) fits.
- Then the cold gate: `rm -rf agda/_build; AGDA_FBC_MEM=256m python3 scripts/full_build_check.py -j6`
  → 2003/2003 PASS. Then `AGDA_FBC_MEM=128m` → enumerate/fix the next tier.
- Commit cap-384 WHOLE (membudget-384 + full_build_check-256m + OrderOf seal + CLAUDE.md docs) ONE gate-green
  commit. The membudget-384 + gate must land TOGETHER with the seal (else make/gate reds on CoxeterFin).

## THE META (user Q, answered): elaboration hash-cons = opaque the TYPE
The `.agdai` memoizes a module's checked signature, but a downstream module that RE-STATES a type re-elaborates
its heavy neutrals. Opaque-ing the TYPE (OrderOf, detNF-style) makes it a content-addressed non-reducing
handle — the cross-module elaboration memo. The strict per-module heap cap (-M256m/-M128m) is the GATE that
FORCES this (a module re-elaborating a heavy neutral overflows → must seal or prove-cheaper). NOT "extract to
a leaf" (proven insufficient — the type still re-reduces).
