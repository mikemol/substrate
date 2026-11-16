---
name: witness-tower
description: >-
  Fire this BEFORE answering any question about the WitnessTower — what it is, what a rung or
  grade or "index n" means, which way a dependency points between the tower and an algebra
  (especially F₂), where the Cantor/Lawvere diagonalisation lives, or what the orientation rig,
  Lehmer coding, or simplicial boundary machinery does — and the instant you catch yourself
  about to say the tower DERIVES something, that a diagonalisation is missing, or that a
  tower-territory name means what it appears to mean. It routes to the `witness-tower` agent,
  which re-derives the map from the owning tools. It exists because this surface is LARGE (349
  modules, the repo's biggest Agda subtree, ~1500 internal edges), because its vocabulary is
  overloaded four and five ways, and because the dependency direction is currently the OPPOSITE
  of the intended design — so anyone answering from appearance answers backwards.
---

# The WitnessTower oracle

**Route the question; do not answer it from this file.** Dispatch the `witness-tower` agent
(`Agent` tool, `subagent_type: "witness-tower"`). It starts fresh, reads the census below, and
runs the owning tools against the tree as it is *now*. This file carries only what a reader must
not get wrong on the way there.

## When this fires

- **What the tower IS** — the witnessed-simplex primitive, rungs, paths, what a `WSimplex k` is.
- **Direction questions** — does the tower derive X, or consume it? Especially anything phrased
  "the tower gives us F₂ / parity / sign / the diagonal".
- **Cantor / Lawvere / diagonalisation** — where it lives, what is proved, what is unwired.
- **Territory** — orientation rig, Lehmer/factoradic coding, simplicial boundary, sign cocycles,
  codeword counting, the M40 study, the EEA tower.
- **Index / rung / grade / level** arithmetic — before building anything that depends on one.
- **On your own tells:** "the tower derives", "at index 2", "that's just the tower's X", "there's
  no diagonalisation for", "the wedge here means", "rung n is Sₙ".

## The four facts to not get wrong

**1. The dependency runs F₂ → tower, not tower → F₂ — by roughly 80:1.**
Measured **167** edges tower→`Algebra.F2` against **2** the other way. The entire reverse arrow
is `WitnessTower.PhiMultiplicity` (cyclotomic multiplicity arithmetic), consumed by two
`Algebra.F2.Linear.Spectral*` modules. And `WitnessTower/Diagonal.agda:63-65` defines the
diagonal atom by **pattern-matching F₂'s constructors**, so the tower's general `FixedPointFree`
interface is *populated by* F₂ rather than deriving it.

⚑ The intended design is the reverse — F₂ as an instance of the tower. That is a DIRECTION, not
the state. Repairing an `F2Graded` bridge cements the current arrow; it is not neutral
maintenance.

**2. The carrier-generic Cantor engine is not in the tower — it is `Substrate.Category.Lawvere`.**
Its own header calls it *"the common substructure of three things WitnessTower.Diagonal found
equal at F₂"* (`Lawvere.agda:4-8`). A `--grep 'antor|awvere|iagonal'` returns 22 names across
**five** homes: `WitnessTower.Diagonal`, `Category.Lawvere`, and three
`Category.UniversalProperty.Diagonal*` siblings. Naming only the first misses four.

**3. ⚑ `r<b` DOES NOT BLOCK `FixedPointFree`, and reading `Lawvere.agda:12-17` alone gets this
backwards — that comment has been RETRACTED IN-TREE.**
`Lawvere.agda:12-17` says the certified residue `r<b` is "the keystone" that will populate
`FixedPointFree` generically. But `Lawvere.agda:245-270` already carries the generic populator —
`TorsorAtom` / `translate-fpf` / `prove-or-correct` — whose hypothesis is **cancellation, not
`r<b`**. And `Algebra/Wedge/ResidueAtom.agda:20-31` states the correction by name: *"the keystone
is NOT 'still open'… What remains is only the certified (r<b) CANONICALITY of that residue — a
smallness refinement, not a missing identity. Both halves are MECHANIZED."*
`ResidueAtom/Properties.agda:4-6` calls itself *"the overclaim fix."*

So **`r<b` buys residue UNIQUENESS, a different theorem.** Any cancellative wedge carrier can be
given `FixedPointFree` today, in ~6 lines, by packaging a `TorsorAtom`.

**`FixedPointFree` has at least SIX inhabitants across FOUR carriers**, not one: `F₂-fpf`,
`F₂-ir` (`Diagonal.agda:119,131`), `F₂²-V₄`/`interface-V₄` (`:153,198`, Vector 2),
`bool-fpf`/`bool-ir` (`DiagonalLawvere.agda:43,46`), and — built GENERICALLY via `translate-fpf`
— `F₂-residue-fpf` and `ℕ-residue-fpf` (`ResidueAtom.agda:70,88`). Of ~19 `DivStr`/`GradedDivStr`
carriers only two are packaged as `TorsorAtom`s; `ℤ-div` is the obvious next.

⚑ THIS FACT WAS ITSELF A CENSUS DEFECT.  An earlier version of this block asserted "blocked on
the `r<b` keystone" and "exactly one inhabitant" — propagating the very claim `ResidueAtom` was
written to retract.  A comment is a hypothesis; the module that corrects it is two directories
away and does not backlink.

**4. Five words are overloaded here, and each is a live trap.**
- **"Tower"** names four things: **Ⓣ₁ = Sₙ**, **Ⓣ₂ = ℚ/Cayley–Dickson**, **Ⓣ₃ = the algebra
  ladder**, and the raw `Core.WSimplex k`. So **"index 2" is ambiguous** between `WSimplex 2`
  and tower Ⓣ₂ — different objects. Ask which.
- **"Rung"** is off-by-one against group order, inconsistently: S₄ = rung 3 in
  `CodewordSignStep.agda:16`, rung 4 in `B3Split.agda:20`, and `AlgebraLadder.agda:93` runs a
  separate Magma=0…AbelianGroup=4 ladder.
- **"Diagonal"** means Cantor's diagonal, the *matrix* diagonal in Leibniz determinant expansion,
  kernel-as-diagonal of a detector cochain, and the **AB-diagonal of V₄** — all inside the tower.
- **"Wedge"** here is a FOURTH sense beyond the three `sql-relalg` documents: the orientation rig
  category (~150 modules), the division-algebra sense specialised to orientations.
- **"Witness"** in `Core.agda` is a structural constructor (a node witnessing the simplex below),
  not path:line evidence and not a proof object — though `FamilyWitness` uses the third sense.

## Absence claims need a witness

Two live examples, both currently true:

- **The Cantor engine is built and UNWIRED.** `WitnessTower.Diagonal` does not appear in the
  `--consumers` by-module ranking: nothing in the repo consumes `cantor-diagonal`,
  `cantor-lawvere`, or `F₂-fpf`. That is a fact about wiring, not about the proof.
- **No tower-derives-F₂ construction exists** under the spellings `F₂-from|F2From|from-tower|
  tower→|rung→F|at-index|index-2|derive` — all 8 hits are unrelated. State the spellings; the
  absence is scoped to them.

Report presence with witnesses; say "no entry for that spelling", never "no such construction".

## The census — GENERATED, do not edit

Regenerate with the commands listed in the block. Every figure is derived from the tool that owns
it. **A generated block nobody regenerates is worse than no block: it reads as authoritative
precisely because it looks derived.**

--- BEGIN tower-census ---
⚑ **DERIVED, NOT TYPED.** Every figure below came from the command beside it. Re-run before
asserting any of them; this surface is mid-repair and moves.

```
── SHAPE
   349 module(s) · ~1493 internal edges · 107 inbound from 47 external importers · 3548 outbound
   depends on 61 packages / 217 modules   ·   consumed by 11 packages / 30 modules
   ⚑ THE TOWER IS OVERWHELMINGLY A CONSUMER.
     agda_defs --under Substrate.WitnessTower · --cluster Substrate.WitnessTower

── DIRECTION (⚑ the headline)
   WitnessTower → Algebra.F2 ....... 167 edge(s), ~135 modules   (F₂ ranks 6th of its deps)
   Algebra.F2   → WitnessTower .....   2 edge(s),    1 module    (PhiMultiplicity, cyclotomic)
     agda_defs --depends Substrate.WitnessTower · --depends Substrate.Algebra.F2
     agda_defs --importers Substrate.WitnessTower.PhiMultiplicity
   ⚑ INTENDED DIRECTION IS THE REVERSE — but NOT blocked on `r<b`; see fact 3.  The generic
     populator (TorsorAtom/translate-fpf, Lawvere.agda:245-270) needs CANCELLATION, and two
     carriers are already packaged.  `r<b` buys residue UNIQUENESS, a different theorem.

── THE CANTOR ENGINE
   WitnessTower/Diagonal.agda — imports SIX Algebra.F2 modules (:42-48)
     flip-disagrees (:63) → apex-disagrees (:72) → ★-no-fixpoint (:80)
     → cantor-diagonal (:89) · F₂-fpf (:108) · cantor-lawvere (:113) · F₂-ir (:120)
   Substrate.Category.Lawvere — 33 names, the carrier-generic layer, OUTSIDE the tower
   ⚑ 22 Cantor/Lawvere/diagonal names across FIVE homes
     agda_defs --grep 'antor|awvere|iagonal|urject|owerset'
   ⚑ Diagonal.agda COMPILES (ⓉDIAGONAL-FIX): `𝟙 +_` → `𝟙 +F_` at :109 and :122.  The error
     read "Operators used in the grammar: None" — no `+` in scope at all, F₂'s addition being
     `_+F_`; a rename left two sections stranded.  While it stood, F₂-fpf did not exist, so the
     tower's ONLY concrete FixedPointFree instance was absent and cantor-lawvere/F₂-ir could
     not load.  23 names now export.
   ⚑ AND STILL 0 IMPORTERS — now a genuine wiring fact, not a consequence of the break.
     agda_defs --importers Substrate.WitnessTower.Diagonal

── LOAD-BEARING (by consumer count)
   Wedge.OrientationBimonoidal 14 · .Properties 12 · LehmerPath.LehmerPath 11
   SimplicialBoundary.DelAt 9 · Wedge.OrientationUniversal 8 · Wedge.OrientationSum 6
   Hodge 5 · FaceSet 3 (the carrier Diagonal diagonalises over)
     agda_defs --consumers Substrate.WitnessTower

── SUBTREES
   Wedge.* ~150 (orientation rig, PyAstRig*) · SignZ2Coordinates.* ~37
   CodewordCountTies.* ~28 · Enumerate.* ~19 · LehmerPath.*/LehmerTowerMorphism.* ~17
   SimplicialBoundary.* ~15 · M40* 7 · EEA* 3
   apexes: WholeTower · Complete · FactorisationApex · ParityCoordIsoApex · SharedMiddle
           TowerLiftSplit · GradeMapInvariant · Link · ResidueBridge · UniquenessBridge
   ⚑ NO Manifest / Registry / Index module and NO README (searched all 349).

── HEALTH
   0 postulates · 0 holes · 0 --safe violations   (37 modules widen with --guardedness)
     agda_defs --trust Substrate.WitnessTower
   ⚑ compilation is MID-REPAIR; sample only, not a census.
     split_pipeline.py --verify <paths…> · --why <path> · --census

── WHO OWNS WHICH QUESTION
   scratch/agda_defs.py            structure, names, prose, history (--at <rev>)
   scratch/split_pipeline.py       does it compile, and why not
   agda/Substrate/WitnessTower/Core.agda          the primitive, narrated
   agda/Substrate/Category/Lawvere.agda           the carrier-generic Cantor atom
   agda/Substrate/WitnessTower/Diagonal.agda      the F₂ instance of it
   agda/Substrate/WitnessTower/SnVersusTwoPowTowers.agda   the Ⓣ₁/Ⓣ₂ family co-apex
   agda/Substrate/WitnessTower/AlgebraLadder.agda          Ⓣ₃, the law ladder
```
--- END tower-census ---

## Growing this

A missing mode is WORK, not a finding. Named gaps as of writing:

- **No mode reports the edge count BETWEEN two prefixes.** The direction finding above took two
  `--depends` runs and a hand-comparison. `agda_defs --between <PfxA> <PfxB>` would make the
  question one call — and this is the single most-asked question of this surface.
- **This census is not gated.** `sql-relalg`'s equivalent has `--check-census` in pre-commit;
  this one has no generator and no drift gate, so it can rot silently. Building
  `--sync-census`/`--check-census` for it is the same shape of work.
- **No prose statement of tower purpose was found in any `.md`** — only module headers. A
  successor should run `mdstruct` over `docs/`/`notes/` before concluding none exists; that
  search was not done.
- ⚑ **No mode lists the INHABITANTS of a record type**, and this cost a wrong census figure. The
  six `FixedPointFree` values were found by `--grep 'fpf|-ir$'` — a SPELLING-scoped census, which
  missed `coemit-pflip-fpf` and `fpf₀` until they surfaced incidentally. `agda_defs --inhabitants
  <Record>` (or `--instances`) is the mode. The same gap makes `--grep 'DivStr'` unable to
  separate a record DECLARATION from an instance VALUE; that had to be done by reading.
- ⚑ **A retraction does not backlink.** `ResidueAtom.agda:20-31` corrects `Lawvere.agda:12-17`,
  two directories away, and `Lawvere` carries no pointer to it — so a reader who stops at the
  first comment banks the retracted claim. A mode that finds "comments correcting a claim made
  elsewhere" is not obviously buildable, but the HAZARD is: when a header states an open problem,
  search for a module whose name or header says *fix*, *correction*, *overclaim*, or *Properties*
  before repeating it.
