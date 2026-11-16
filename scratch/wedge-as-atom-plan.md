# Plan: wedge-as-atom — make `recon` primitive, derive ℕ (`suc` = the ordered difference `1 ⊖ 0`)

*(This plan supersedes the earlier DuckDuckJoke-incident plan, which is complete. It is a
compaction-survival freeze: everything load-bearing is in this file. Three read-only Explore
agents are saturating the term-level detail — see "Agent saturation" below; fold their findings
into the marked sections when they land. **Grade everything by TERMS, not the repo's comments —
substrate prose is stale, bidirectionally.**)*

## Context

The design conversation converged on a foundational move for `~/github/substrate`: make the
**wedge / `DivStr` the atom**. Currently the tower sits *on* Agda's built-in ℕ (`LehmerPath : ℕ →
Set`, `WSimplex : ℕ → Set`, `GradedDivStr`'s `recon : C n → R n → C (suc n)` — all index by ℕ).
The move: invert it so the **ordered difference — the residue `r` in `recon q b r` — is primitive**,
and `suc` is *derived* as the unit residue (`recon` of the `(1,0)` difference), with **ℕ = the
tower's own depth (`steps`)** rather than an imported primitive.

**Why it matters.** One atom then grounds ℕ *and* the Lehmer tower *and* the μ↔ν fusion *and* the
transport: Peano becomes the 1-generator instance of the same `recon` that runs everything, and the
session's "no-residue = no-substance" residue becomes literally the atom of *number* (`suc` = one
unit of substance). It's the difference-first / torsor-first inversion; points (`0`,`1`,`suc n`)
become frame-choices on a torsor whose only primitive datum is the step.

**Two deliverables the user approved ("both sound awesome"):**
1. **Existence check** — is the flip already-done / partial / owed, judged by terms?
2. **De-index refactor sketch** — the minimal `data W` (`base`/`step`) + `ℕ ≅ W` + `suc = step = ◂
   = unit residue` + re-route grading through `steps`; and *how small the owed derivation is*
   (bounded refactor vs deep rewrite).

Companion design note (fuller context, term-status §9, prose-drift §10):
`…/scratchpad/orientation-residue-context-recall-design.md` (session scratchpad; relocate to
`substrate/scratch/` when convenient).

## The forced structural core (committed — this is the math, independent of the audit)

- `DivStr A = (carrier A, z : A, recon : A→A→A→A)`; `a = recon q b r` (group leg `q·b·r`). `r` is
  the **ordered difference** (directional). `suc = recon` of the `(1,0)` wedge → the unit residue.
- ℕ = **free monoid on one ordered difference** (the abelian case). The **Lehmer digit** is the same
  ordered difference in the *non-abelian* setting (Sₙ). So **ℕ is the abelianization of the general
  wedge-tower**, and `decode`/`steps` (digit-sum) is the abelianization bridge. One atom, two
  commutativity settings: `suc` and the Lehmer digit are the same primitive.
- ℕ-induction becomes **derived** from the tower's *structural* induction (path-recursion, which is
  ℕ-independent), via `ℕ = steps`. Legitimate, but a derivation now owed rather than assumed.
- Self-reference (the ground): "ℕ = the tower's own depth" **is** the `μΦ≅νΦ` fixed point already
  inhabited (`Core.agda` `steps (walk k) ≡ k`; `OrientationFixedPoint.agda` `decode-encode`/
  `encode-decode`). So the wedge-as-atom is the fixed point the tower already *is*, read as ground.
- Honest edge: this **relocates** the primitive to one generating residue (the unit difference); it
  does not abolish primitivity. And `suc`-as-difference = `suc`-as-constructor is a *re-reading* of
  ℕ, not a new ℕ — the value is the unification, not a different arithmetic.

## Known term-grounded facts (this session; grade-by-terms)

- Tower is **ℕ-indexed today** (sits on Peano): `WSimplex : ℕ → Set` (`Core.agda:38`),
  `LehmerPath : ℕ → Set` (`LehmerPath.agda:54`, `_◂_ : LehmerPath k → Fin (suc k) → LehmerPath (suc
  k)`), `GradedDivStr` `recon : C n → R n → C (suc n)` (`Algebra/Wedge/Graded.agda:49`).
- **Self-index already recovers ℕ on top**: `Path`/`walk`/`steps`, `steps (walk k) ≡ k`
  (`Core.agda:52,79`). `fold`/`fold-unique` = catamorphism on the *path* (`OrientationUniversal.agda`).
- Inhabited (§9 of the design note): μ↔ν bridge, `RealTrace≅νΦ`, two-tower lockstep (`νΦ-pair`),
  parity-V₄ (`coemit-trace-v4-genuine`), `fold-⊗`, `Trace≅μΦ`, `Y-fix`, universal self-interpreter.

## Agent saturation (fold findings in when they land — READ-ONLY, term-level)

- **`afa4857c` — Existence check → DONE. VERDICT: the flip is genuinely OWED** (term-grounded):
  - External Peano `data ℕ` with `{-# BUILTIN NATURAL #-}` (`Foundation/Nat.agda:19-23`); every tower
    `open import … Nat using (ℕ; zero; suc)` and indexes on it. No un-indexed `data W : Set`
    (base + self-`step`, Nat-free spine) exists anywhere.
  - `steps : ∀{k} → Path k → ℕ` maps **tower → ℕ** (`Core.agda:75`); `steps-walk : steps (walk k) ≡ k`
    (`:79`) *presupposes* the assumed `k : ℕ`, does not construct ℕ. `walk : (k:ℕ) → Path k`,
    `_◂_ : LehmerPath k → Fin (suc k) → LehmerPath (suc k)` both **consume external `suc`** in the
    index; **`◂`/`walk` is never identified with `suc` by a term** (the link is analogy-in-comments).
  - No `suc := recon(unit residue)` term. `GradedDivStr.recon : (n:ℕ) → C n → R n → C (suc n)`
    (`Graded.agda:47-53`) — grade is `n : ℕ`, raised by external `suc`; grade **never decoupled** from ℕ.
    `ℕ-div = record { z=zero; recon = λ q b r → q*b+r }` (`Wedge.agda:153`) *uses* ℕ arithmetic — the
    reverse of the goal.
  - **`Action.agda` "obstruction" — DOWNGRADED to a comment under review (per user "NGeh"):** it *claims*
    an un-indexed carrier "cannot express the `Perm n / Fin (suc n)` link." But that is prose about the
    **concrete `Perm`/`Fin` payload**, and Agent 2 found the **abstract `GradedDivStr` atom is
    arithmetic-free & carrier-parametric** (`ℕ→Set ⟶ W→Set`, `suc↦step`, bodies unchanged). So the
    obstruction most likely binds **only the `tower-graded : GradedDivStr Perm (λ n → Fin(suc n))`
    instance**, not the atom — which is fine, because that instance lives in the DEEP tier we keep on ℕ
    anyway (the abelianization target). **RESOLVED by `a58da7a2` (below): instance-only — the abstract
    `GradedDivStr` atom is grade-parametric and *dissolves* the `Perm/Fin` link structurally; the atom
    de-index is a mechanical `ℕ→Set ⟶ W→Set` / `suc↦step` swap. The `Action.agda` comment does not bind
    the atom.**
  - Exact gap (3 owed terms): (a) un-indexed `data W : Set` (`base`, self-`step`); (b) `ℕ` defined as
    `W`-depth (or `W ≅ ℕ`, `W` primary); (c) `suc := recon/◂ of the unit residue`. Scaffolding to host
    it (`Path`, `steps`, `steps-walk`, `walk`, `◂`, `GradedDivStr.recon`, `ResidueAtom`'s ℕ-torsor) all
    present, all currently *depend on* `Foundation.Nat.ℕ`.
- **`a5e633a8` — Refactor surface → DONE. VERDICT: two-tier, split by "ℕ carries arithmetic vs only a count":**
  - **PIVOT: `data W where base;step` ≡ `Foundation.Nat.ℕ` renamed** (`zero↦base`, `suc↦step`). So
    `W ≅ ℕ` is `refl`, `suc = step` is **definitional**; `steps` (`Core.agda:75`) IS the fold,
    `steps-walk` its correctness. The de-index is a **re-reading of ℕ**, not a new type.
  - **BOUNDED tier (cheap, ~8–10 files, mostly mechanical) — the part the goal is actually about:**
    the spine-as-atom + initial-algebra/UP layer is **already path-structural & ℕ-independent** —
    `Core`, the `GradedDivStr` atom (`Algebra/Wedge/Graded.agda:47`), `tower-graded`,
    `fold`/`fold-unique` (`OrientationUniversal.agda:53,101` — recurse on **path** constructors, not ℕ),
    `OrientationRigInitial/FreeUP/Universal`, `decode`, `decode-injective`. Change = swap family kind
    `ℕ→Set ⟶ W→Set` + `suc↦step` (bodies unchanged) + **re-cut `encode`** (`LehmerPath.agda:79`, the
    ONE core map that recurses on the ℕ index) to path/`steps` recursion. **ℕ-induction over the tower
    is derivable from `fold`/`fold-unique`** (confirmed).
  - **DEEP tier (expensive, essential) — OUT OF SCOPE; keep on ℕ as the abelianization target:**
    ℕ-as-ARITHMETIC-in-an-index — `_◂_`'s `Fin (suc k)` digit-bound → dependent `Fin (suc (steps l))`;
    `_⊕_`'s `m+n` (`OrientationSum.agda:46`), `_⊗ˢ_`'s `m*n` (`OrientationProductStructural.agda:87`),
    `offsetDigit`'s `fromℕ<`/`Nat.Properties`, `inject+`, and all of `Enumerate` (`perms/words/factorial/^`;
    `Sn` sits on it). De-indexing these = rebuild `+`/`*`/`≤`/`fromℕ<`/`Fin` over `W`, against a 138-file
    `Foundation.Nat` dependency + the hard **NATPLUS/NATTIMES binding-ban** (`Nat.agda:25-34`, Agda-2.8.0
    internal error). **Per the abelianization insight, ℕ-arithmetic IS the commutative quotient — so
    keeping ⊕/⊗ on ℕ is CORRECT, not a shortfall.**
  - Choke points: `Agda.Builtin.Nat` imported in exactly **one** place (`Foundation/Nat.agda:23`);
    `LehmerPath` imported by ~55 files (the live spine), `Core` by only 4 (nearly a leaf).
- **`a11fce45` — Ordered-difference math → DONE. Reuse-vs-add ledger:**
  - **REUSE verbatim (inhabited terms):** the shared `DivStr`/`GradedDivStr`/`GradedDivStrMorphism`
    interface; `lehmer-graded : GradedDivStr LehmerPath (λ n → Fin(suc n))` with `recon = ◂`
    (`LehmerTowerMorphism.agda:66`) — **the ordered difference IS `recon`**; the **unit-step corner**
    `corner-eq`/`residue-wedge` with residue `r = (0,start) = z` (`OrientationRigResidue.agda:111,129`)
    — "no defect at the unit step"; the **digit-sum→ℕ** `invcount-graded` + `invcount-insert`
    (`SignZ2Coordinates.agda:257,177`) and `decode-morphism` (`LehmerTowerMorphism:77`); the **Z/2
    abelianization as a REAL group hom** `sign-parity-lifts`/`mod2-lifts` (`GradeMapInvariant.agda:153`)
    + `twisted-lehmer-sign-morphism` (`…Discharged:44`); `steps-walk` **retraction** (`Core:79`); the
    `decode`/`encode` **bijection** + `witness-reconstructs` (**step = recon**, `OrientationFixedPoint:55`).
  - **MUST ADD (conceptual — no term today):** (1) that `invcount-graded`/ℕ⁺ is *the abelianization*
    (universal property + kernel=commutator + monoid-hom over ⊗) — it's a `respects-recon` morphism,
    **not** a hom; (2) ℕ as a commutative-quotient **group-hom** of the ⊗-tower (**only Z/2 is proven**);
    (3) an actual `μΦ`/`νΦ` fixed-point term (ν deferred to `Trace.Final`) if "the tower already *is* ℕ"
    is to be more than the retraction + bijection it currently rests on.
  - **`suc = recon(1,0)` on the abelian ℕ carrier is DEFINITIONAL only** (`ℕ-div`, `Wedge.agda:152`;
    `suc n = 1*n+1`) — **no named term** → the plan's Deliverable *adds* that named term.
  - `git grep abelian` → only `Algebra/Abelian/*` (V₄/Z6/Z30 PFG), unrelated — no abelianization-of-Sₙ term exists.

- **`a58da7a2` — GradedDivStr/GradedWedge machinery → DONE. VERDICT: the abstract atom is GRADE-PARAMETRIC;
  the de-index is mechanical; the `Action.agda` obstruction is INSTANCE-ONLY (the "NGeh" confirmed).**
  - `GradedDivStr` (`Algebra/Wedge/Graded.agda:47-53`): `C R : ℕ → Set` are **module PARAMETERS, not
    fields**; single field `recon : (n) → C n → R n → C (suc n)`. `GradedWedge` (`:63-69`): fields
    `rem : R n`, `wedge-eq : a ≡ recon G n b rem` — **no `quot` field**. `GradedDivStrMorphism`
    (`Morphism.agda:47-50`): `map-C`/`map-R`/`respects-recon` naturality square. **ZERO ℕ-arithmetic**
    (`+`/`*`/`≤`/`Fin`/`Nat.Properties`) in any atom body or law; ℕ/`suc` appear ONLY as the family
    index and the codomain bump `C (suc n)`.
  - **The recipe is exactly supported: `ℕ→Set ⟶ W→Set`, `suc↦step`, bodies unchanged.** Grade not yet
    abstracted (every instance literally `ℕ→Set`) but nothing consumes ℕ-arithmetic → mechanical swap.
    Only arithmetic in the folder is the `flatten`/`gpower` connectors (`qn*i+j`, `Morphism.agda:103`)
    — the OPPOSITE direction (collapse grading → plain wedge), not the atom.
  - **`Action.agda` obstruction RESOLVED = instance-only:** true about the *un-indexed plain* `DivStr`
    (one un-indexed `C`) + the concrete `Perm`/`Fin(suc n)` choice, NOT the atom. GradedDivStr already
    DISSOLVES it — `StepWedge n` (carries `quot : ℕ`) is recovered as `GradedWedge tower-graded n` with
    `quot` GONE (it was `suc n = |Fin(suc n)|`, read off the grade); `recon-is-insert-at = refl`. The
    payload-arity link is **structural in the grade, needs no arithmetic.**

## Approach — FINAL (all four agents saturated)

**Feasibility verdict:** the flip is OWED, but the tier the goal actually needs is a **bounded, mostly-
mechanical refactor (~8–10 files)**, because (a) `data W ≡ ℕ` renamed → `W ≅ ℕ` is `refl`, `suc = step`
definitional; (b) the `GradedDivStr`/`GradedWedge`/`Morphism` **atom is grade-parametric with ZERO
ℕ-arithmetic** → `ℕ→Set ⟶ W→Set`, `suc↦step` is a body-unchanged swap (`a58da7a2`); (c) `fold`/
`fold-unique`/`decode` are path-structural → **ℕ-induction is derivable**, nothing circular; (d) the
`Action.agda` obstruction is instance-only and the atom dissolves it. The expensive ℕ-arithmetic tier
(⊕/⊗/`Fin`-digit/`Enumerate`) **stays on ℕ by design** — it's the abelianization target, not a gap.

**Deliverable 1 — existence check: DONE = OWED** (no un-indexed `W`, no ℕ-from-tower, no `suc=recon(unit)`
term; scaffolding present but ℕ-dependent).

**Deliverable 2 — the de-index, minimal & bounded:**
1. **Spine/atom (mechanical):** re-read ℕ as `data W { base ; step }` (or a `W`-view of ℕ); `W ≅ ℕ` =
   `refl`, `suc = step`. Re-grade the atom — `GradedDivStr`/`GradedWedge`/`Morphism`/`Adjunction`
   `C R : ℕ→Set ⟶ W→Set`, `suc↦step`, **bodies unchanged** (`a58da7a2` confirms zero-arithmetic).
2. **The named unit-residue term (the actual point):** define `suc := recon` of the `(1,0)` difference —
   today only *definitional* (`ℕ-div`, `Wedge:152`, `suc n = 1*n+1`) and via the Lehmer unit-corner
   `residue-wedge` with residue `r = (0,start) = z` (`OrientationRigResidue:111,129`). ADD the named
   `suc = recon(unit)` term (unit ordered difference, residue `z`).
3. **Induction ground (reuse):** ℕ-induction ← the tower's path-structural `fold`/`fold-unique`
   (`OrientationUniversal:53,101`) — reuse verbatim; **re-cut `encode`** (`LehmerPath:79`, the one
   ℕ-index-recursive core map) to recurse on the path/`steps`.
4. **Keep the deep tier on ℕ (abelianization target):** ⊕/⊗/`Fin`-digit/`Enumerate` unchanged;
   `steps` + `invcount-graded` (`SignZ2Coordinates:257`) as the digit-sum bridge; respect NATPLUS/NATTIMES ban.

**Optional stretch (the 3 must-add theorems — only if the flip is to be *grounded*, not just *hosted*):**
(1) `invcount-graded`/ℕ⁺ is *the abelianization* (universal property + kernel=commutator + ⊗-hom);
(2) ℕ-as-commutative-quotient group-hom of the ⊗-tower (only **Z/2** proven, `GradeMapInvariant:153`);
(3) a real `μΦ`/`νΦ` fixed-point term (ν deferred to `Trace.Final`) upgrading retraction+bijection into
"the tower already IS ℕ." **These are additions, not blockers — the bounded refactor stands without them.**

Both approved items are covered: Deliverable 1 *is* the "does it exist" check (OWED); Deliverable 2 *is*
the de-index sketch, now bounded and file-level precise. Reuse the existing `Core`/`LehmerPath`/`Graded`
spine (`walk`/`steps`/`fold`); do NOT rewrite the tower.

## Verification

- Read-only only in substrate (mid-refactor, uncommitted). **I do not build/typecheck substrate; the
  user does.** Verification = the user runs `make -C agda` (or the targeted module) after the change
  and confirms `--safe --without-K` green, plus: `ℕ ≅ W` round-trips (`refl`/proven), `suc' = step`
  and `suc' = recon(1,0)` typecheck, `fold` still initial, and downstream (`Sn`, `decode`) unbroken.
- Grade the result by **term inhabitation**, not comments (the whole session's rule).

## Durability / provenance

This plan is the freeze; the three agents are the saturation; grade by terms. If a compaction
occurred and an agent finding is still marked PENDING above, re-dispatch that agent's question
(prompts are recoverable from this file's "Agent saturation" section) rather than guessing. Nothing
in substrate was or will be modified during planning — read-only throughout.
