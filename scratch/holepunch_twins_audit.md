# Hole-punch instruments, twins, and capability-parity gaps

**Observation window:** 2026-08-03T23:15:40-04:00 → 2026-08-03T23:34-04:00 (local).
**Tree state during the run:** another session was editing concurrently (`scratch/pycodemod.py`
mtime `Aug 3 23:11`, i.e. ~4 minutes before this audit began; `scratch/band_sppf.py` 22:47,
`scratch/agda_lex.py` 22:12). Every census below is a **timestamped observation, not a
standing fact.** Where a number here disagrees with a later run, suspect the tree first.

**Files modified by this audit: exactly one — this report.** No repo script was run to
"see what it does"; interfaces were established by reading. See the command log at the end.

---

## PART 1 — The hole-punch instruments

The unifying operation is **abstract a position so instances unify** — Π skeleton + Σ of
fillers. Below, each instrument is placed in the realization it implements. Realization (i)
is a single implementation reached by two front-ends; (ii) and (iii) are families.

### (i) ABSTRACT-A-DIFFERENCE — the typeholer

| Path | Unit | Corpus reached | Surface |
|---|---|---|---|
| `jea/metalanguage/jea_pysim.py:550` | `Corpus.typehole(node_ids, depth, max_depth)` | **Both** (Python + Agda) | library + CLI |
| `jea/metalanguage/jea_pysim.py:602` | `Corpus._filler_repr` — the Σ side (what fills the hole) | both | library |
| `jea/metalanguage/jea_pysim.py:96–128` | `Corpus.add_file` — Python front-end | Python | library |
| `jea/metalanguage/jea_pysim.py:148` | `Corpus.add_agdai` — **Agda front-end into the SAME interner** | Agda | library |
| `jea/metalanguage/jea_pysim.py:130` | `Corpus.carrier_qnames_of` — ⟨CARRIER⟩ pre-pass for `--unhold` | Agda | library |
| `scratch/band_sppf.py` | bands the SPPF by shared-face support | reads what is interned | CLI, print-only |
| `jea/metalanguage/typeholer_path.py` | typeholer path machinery (name-level witness; not exercised in this audit) | UNVERIFIED | UNVERIFIED |

**Correction to the brief (measured):** `typehole` has **7 call sites, not 8.**

```
$ python3 scratch/pycodemod.py --calls typehole jea/metalanguage/jea_pysim.py scratch/*.py scripts/*.py
call  jea/metalanguage/jea_pysim.py:252, 367, 574, 599, 696, 906, 928
def   jea/metalanguage/jea_pysim.py:550
typehole: 1 def(s), 7 call(s)
```
Two of the seven (574, 599) are `typehole`'s own recursion; 906/928 are the CLI readouts
(`--json` and the `--clusters/--skeleton` path). Scope of that scan was
`jea/metalanguage/jea_pysim.py` + `scratch/*.py` + `scripts/*.py`; a caller outside that
scope would be invisible to it.

#### Does (i) reach Agda via `add_agdai`? — **YES, verified two ways.**

**By reading.** `jea_pysim.py:148-172`, docstring verbatim:

> *"Φ4b: ingest an Agda `.agdai` interface as units = its DEFINITIONS' elaborated core terms.
> Drives `jea_agdai.core_intern_agdai` (agdai_shim -> the full child-edge core DAG) into
> **THIS same interner** … The readouts below are front-end-agnostic — they read
> (kind, role, op, lit) + children, and Agda core nodes carry `kind='AgdaCore'` … so the
> typeholer/S(g)/clusters run on Agda exactly as on Python."*

The mechanism is checkable, not just claimed: line 159 passes `self.I` (the Corpus's own
`Intern`) into `core_intern_agdai`, and lines 165-172 build `Unit`s and register
`node_units` through the **same** `self._support` / `self.node_units` path `add_file` uses
(lines 121-128). There is no second forest. Dispatch is by extension in `main`:
`if f.endswith(".agdai"): C.add_agdai(f) else: C.add_file(f)`.

**By measurement.** `.agdai` cores DO exist under `agda/_build/`:
`find agda/_build -name '*.agdai' -printf 'X' -quit` → `X`; e.g. twelve under
`agda/_build/2.8.0/agda/Substrate/Algebra/CayleyDickson/Curve/`. And a **mixed** run
(Agda cores + two `.py` files in one invocation) interned into one forest — see the
cross-substrate finding in Part 2, where the forest total (290 nodes) is *less* than the
sum of the separate runs (123 + 2029 over larger input sets), and Agda clusters and Python
clusters are reported side by side from a single `Corpus`.

**Which modes write.** Read of `main` (`jea_pysim.py:829-997`) confirms **only `--persist DB`
writes** (it calls `sppf_db.build(cores, args.persist)`). `--clusters --extract --skeleton
--recursive --metalanguage --shape --json --unhold` are print-only. I ran only the former set.

### (ii) ADMIT-A-GAP — the missing-proof holes

The instruments that *census* admitted gaps, and their gate-wiring (read from
`.githooks/pre-commit`, never run):

| Path | Purpose | Corpus | Gate-wired? |
|---|---|---|---|
| `scripts/check_discharge_ratchet.py` | undischarged level-polymorphic carriers — "∃ a" without "and here it is" | Agda | **YES**, `.githooks/pre-commit:148` (blocking ratchet) |
| `scripts/check_rederive_ratchet.py` | rederivation debt | Agda | **YES**, `:143` |
| `scripts/check_claims.py` | claims census | mixed | **YES**, `:138` |
| `scripts/worklist.py` | tracker of deferred/TODO items | markdown | **YES**, `:107` (`--check`, integrity only) |
| `scripts/collapse_check.py` | newly-added Agda modules imported by nothing + def-name overlap | Agda | `:208`, **ADVISORY** (`|| true`, and `return 0 # ADVISORY: never blocks`) |
| `scripts/tautology_advisory.py` | tautology advisory | mixed | UNVERIFIED (not located in the pre-commit read) |
| `scripts/sppf_label.py` | labelling over the SPPF | mixed | UNVERIFIED |

`check_discharge_ratchet.main` is a paydown-only ratchet over a materialized census
(`ratchet.set_ratchet(census(), BASELINE, …)`), matching the standing "policy is a ratchet
over a census" pattern.

### (iii) EXCISE-A-REGION — the excision family

Nine members, all `scratch/`, all Agda-source rewriters, all **CLI-only, none argparse**
(`pycodemod --calls add_argument` over the nine → `0 def(s), 0 call(s)`), all write in place:

`prune_imports.py`, `strip_using.py`, `drop_dead_renames.py`, `retire_mod_tip.py`,
`unseal_defs.py`, `seal_defs.py`, `narrow_leaf_imports.py`, `narrow_leaf_opens.py`,
`prune_leaf_opens.py`.

None is wired into `.githooks/pre-commit` (they are paydown instruments, not gates); the
gates they *feed* are `check_ban_ratchet.py` (`:135`), `check_import_shape.py` (`:115`),
`check_public_ratchet.py` (`:174`), `check_private_ratchet.py` (`:181`).

---

## PART 2 — The twin hunt

Instrument: `jea_pysim`'s interned forest. Not textual comparison.

### 2.1 EXACT DUPLICATION (identical interned node, fan-in 6, zero holes) — **highest consequence**

```
$ python3 jea/metalanguage/jea_pysim.py scratch/prune_imports.py scratch/strip_using.py \
    scratch/drop_dead_renames.py scratch/retire_mod_tip.py scratch/unseal_defs.py \
    scratch/seal_defs.py scratch/narrow_leaf_imports.py scratch/narrow_leaf_opens.py \
    scratch/prune_leaf_opens.py --clusters --extract
corpus: 45 units across 9 file(s); forest 2029 interned nodes

  cluster 0 (6 units) -- IDENTICAL (1 shared nodes, 0 holes) -- one concept, no parameters
    scratch/narrow_leaf_imports.py::_snapshot_once:10
    scratch/prune_leaf_opens.py::_snapshot_once:26
    scratch/retire_mod_tip.py::_snapshot_once:22
    scratch/seal_defs.py::_snapshot_once:27
    scratch/strip_using.py::_snapshot_once:52
    scratch/unseal_defs.py::_snapshot_once:16
```

**Projection:** exact duplication — one interned node, fan-in 6, `IDENTICAL`, no hole
needed to unify. Confirmed independently by `pycodemod --binding _snapshot_once` over the
same nine (6 bindings in 6 of 9 files, line numbers agreeing exactly).

This is the **`edit_snapshot` arming guard** — the recovery hook whose own docstring records
what its absence cost: *"This tool rewrites files it read — the shape that made 33 files
unrecoverable (Coxeter/Core.agda 76 lines -> 3)."* Six byte-identical copies, including the
comment. Consequence is high not because six copies are expensive but because **the
duplication is what hides the three files that do not have it** (§3.1).

### 2.2 SAME NAME, DIFFERENT BODIES — the `agda_files()`-was-four-bodies hazard, live

```
  cluster 1 (2 units) -- PARTIAL orbit (50% shared, 1 independent hole(s))
    scratch/narrow_leaf_opens.py::split_rest:49
    scratch/retire_mod_tip.py::split_rest:90
    -- common semantics (skeleton) + distinctions (typed holes):
      FunctionDef
        <HOLE:FunctionDef:variadic> varies: {split_rest}
```

**Projection:** same-name/different-bodies. Two functions named `split_rest`, 50% shared,
and the hole is `variadic` — *they do not even agree on arity*. Both parse the tail of an
Agda import/open statement. This is the exact hazard shape named in the brief, currently
live in the excision family.

### 2.3 k-HOLE NEAR-DUPLICATION, Agda side (k = 1)

```
$ python3 jea/metalanguage/jea_pysim.py \
    'agda/_build/2.8.0/agda/Substrate/Algebra/CayleyDickson/Curve/*.agdai' --clusters
corpus: 14 units across 16 file(s); forest 123 interned nodes

  cluster 1 (2 units) -- STRONG orbit (93% shared, 1 independent hole(s)) -- one parametric concept
    …Curve/GrayDecodeStep.agdai::…GrayDecodeStep.gray-decode′
    …Curve/GrayStep.agdai::…GrayStep.gray′
    SHAPE S(g)=[(0,1.0),(1,1.0),(2,1.0),(3,1.0),(4,0.93)]  carrier-holes @depths [4]
      AgdaCore(Defn) / Pi / Clause / Vec._∷_ / Bool.Xor._xor_ …
              <HOLE:AgdaCore> varies: {AgdaCore, Substrate.Foundation.Bool.Xor._xor_}
```

**Projection:** k = 1 near-duplication. `gray′` (encode step) and `gray-decode′` (decode
step) are **the same term modulo one node** — the hole is precisely "is there an extra
`_xor_` here". The shape curve is flat 1.0 to depth 3 and only breaks at depth 4: this is a
genuine parametric concept split across two modules, not a coincidence. Candidate for a
single parameterized step with the encode/decode difference as its argument.

### 2.4 k-HOLE NEAR-DUPLICATION, Agda side (k = 3) — a carrier-hole family

```
  cluster 0 (3 units) -- PARTIAL orbit (57% shared, 3 independent hole(s))
    …CrossoverGrayWins.agdai::…crossover-gray-wins
    …GrayJump.agdai::…gray-jump
    …MortonJump.agdai::…morton-jump
      AgdaCore(Defn) / Substrate.Foundation.Eq._≡_ / Level
        <HOLE:AgdaCore> varies: {…Semiring.NatInf.ℕ∞, …Foundation.Nat.Nat.ℕ}
        <HOLE:AgdaCore> varies: {…Curve.Crossover.crossover, …Grade.Popcount.popcount}
        <HOLE:AgdaCore> varies: {AgdaCore, …Semiring.NatInf.ℕ∞.fin}
```

**Projection:** k = 3 near-duplication with an interior **carrier** hole. Three statements
of one shape — *an equality over ⟨carrier⟩ of ⟨measure⟩* — where the holes are exactly
(carrier ℕ vs ℕ∞) × (measure crossover vs popcount) × (the `fin` lift). The three holes are
the product structure; the skeleton is the single theorem.

### 2.5 CROSS-SUBSTRATE — one forest, two front-ends, one query

```
$ python3 jea/metalanguage/jea_pysim.py \
    'agda/_build/2.8.0/agda/Substrate/Algebra/CayleyDickson/Curve/*.agdai' \
    scratch/unseal_defs.py scratch/seal_defs.py --clusters
corpus: 18 units across 18 file(s); forest 290 interned nodes
  cluster 0 …  (Agda: crossover-gray-wins / gray-jump / morton-jump)
  cluster 1 …  (Agda: gray-decode′ / gray′)
  cluster 2 (2 units) -- IDENTICAL (1 shared nodes, 0 holes)
    scratch/seal_defs.py::_snapshot_once:27
    scratch/unseal_defs.py::_snapshot_once:16
```

**Projection:** cross-substrate capability, **verified**. Agda `AgdaCore` units and Python
`FunctionDef` units co-inhabit one `Corpus`, one `Intern`, one cluster list, one typeholer.
Cross-language comparison here is a *query over one interned forest*, exactly as the brief's
key fact asserts — and the `[agda-skip]` diagnostics prove the Agda path executed rather
than being silently ignored.

**Honest negative:** no cluster in this run *straddled* the two front-ends (no
Agda-unit-with-Python-unit cluster appeared). That is a fact about **this input set and this
`--min-shared 0.6` threshold**, not about the substrate. The capability is demonstrated; a
straddling twin was not found by these three commands.

### 2.6 A stale-core observation (timestamped)

Two cores refused to decode, in both Agda runs:
```
[agda-skip] …Curve/GrayDecodeStepGrayStep.agdai: … a stale / older-version interface
            decodes to Nothing; rebuild it (`agda --safe ...`).
[agda-skip] …Curve/GrayRoundtrip.agdai: … (same)
```
Both files are `AM` (added, modified-unstaged) in the session-start git status — i.e. the
concurrently-editing session's working set. **Read as tree state at 23:30, not as a defect
in `add_agdai`.** Consequence: any `.agdai`-based census taken right now is incomplete by
at least these two units, and will not say so unless you read stderr.

---

## PART 3 — Capability-parity asymmetry tables

### 3.1 The excision family (realization iii) — 9 members

Ranked first because these tools **rewrite Agda source in place** and their own comments
record 33 files gutted.

| capability | prune_imports | strip_using | drop_dead_renames | retire_mod_tip | seal_defs | unseal_defs | narrow_leaf_imports | narrow_leaf_opens | prune_leaf_opens |
|---|---|---|---|---|---|---|---|---|---|
| `edit_snapshot` arming guard | ✗ | ✓ :52 | ✗ | ✓ :22 | ✓ :27 | ✓ :16 | ✓ :10 | ✗ | ✓ :26 |
| `if __name__` guard (import-safe) | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | ✓ :123 | **✗** | **✗** | UNVERIFIED | UNVERIFIED |
| a `main()` function at all | ✗ | ✗ | ✓ :395 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| argparse CLI | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| dry-run / preview flag | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `agda_lex`-backed span authority (`_span_end`) | UNVERIFIED | **imported, never called** | ✗ | ✗ | ✗ | ✗ | ✓ :46 | ✗ | ✗ |
| `agda_defs.def_index` authority | ✓ :32,:421 | ✗ | ref :149 | ✗ | ✓ :33 | ✗ | ✓ :33 | ✗ | ✗ |
| REFUSES on a name it cannot find | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | ✓ :115 | **✗** | UNVERIFIED | UNVERIFIED | UNVERIFIED |

**Witnesses / queries.**

- Snapshot row — one command, both directions:
  `pycodemod --binding _snapshot_once <the nine>` → `6 binding(s) in 6 of 9 file(s)`, with
  the six `path:line` shown. The three ✗ (`prune_imports`, `drop_dead_renames`,
  `narrow_leaf_opens`) are the files **absent from that output**, and cross-checked against
  the 6-way `IDENTICAL` cluster in §2.1, which lists the same six. (Per the brief's warning
  about `--key`, this row is corroborated by two independent instruments, not one count.)
- `main()` row: `pycodemod --binding main <the nine>` → `1 binding(s) in 1 of 9 file(s)`,
  `drop_dead_renames.py:395`.
- argparse row: `pycodemod --calls add_argument <six of the nine>` → `0 def(s), 0 call(s)`.
- dry-run row: `pycodemod --binding DRY <the nine>` → `0 binding(s) in 0 of 9 file(s)`.
  ⚑ This query only catches a flag *named* `DRY*`; a differently-named preview would be
  invisible. Treat the ✗ row as "no `DRY`-named preview found by that query."
- `_span_end` row: `pycodemod --calls _span_end <the nine>` →
  `ref scratch/narrow_leaf_imports.py:5` + `call …:46`; `ref scratch/strip_using.py:5` with
  **no call**. `0 def(s), 1 call(s)`.
- `__name__` / REFUSES rows: `pycodemod --binding __name__ <the nine>` returned
  `0 binding(s) in 0 of 9 file(s)` **despite `seal_defs.py:123` demonstrably containing
  `if __name__ == "__main__":`** — the mode tracks *bindings*, and `__name__` is only ever
  read. That is a second `pycodemod` mode-limitation alongside the known `--key` defect;
  those two rows are therefore filled from direct Read evidence where I read the file
  (`seal_defs.py`, `unseal_defs.py`, `narrow_leaf_imports.py`) and UNVERIFIED elsewhere.

**The consequential asymmetries, in order:**

1. **`unseal_defs.py` vs `seal_defs.py` — the sharpest gap in this audit.** They are an
   explicit inverse pair (`unseal_defs.py:2`: *"the inverse of seal_defs.py"*). `seal_defs`
   has a `seal()` function, an `if __name__ == "__main__":` guard (`:123`), and **refuses**
   on a name it cannot find (`:115` `raise SystemExit(f"REFUSING: {path} has no top-level
   definition(s) …")`). `unseal_defs` has **none of the three**: `sys.argv` is read at
   module level (`:37`), the file is read, rewritten and `open(path,"w")` executed at
   **import time** (`:53-54`), and a name it cannot find is silently reported as
   `(none)` (`:55`) after the file has already been rewritten. **`import unseal_defs`
   destroys a file.** This is the same hazard class the brief warns about in
   `catalog/memory/synth_wire.py`, and it is sitting in the excision family.
2. **`narrow_leaf_imports.py` has the same import-time-write shape** (`:31`
   `PREFIX=os.environ["PREFIX"]` at module level; `:66` `open(f,"w")` inside a top-level
   loop) — and additionally hard-requires an env var, so importing it raises `KeyError`
   before it can write. Different failure, same missing guard.
3. **Three of nine rewriters lack the recovery guard** whose absence is the documented cause
   of the 33-file loss — `prune_imports.py`, `drop_dead_renames.py`, `narrow_leaf_opens.py`.
   `prune_imports.py` is the largest of the nine (25 KB) and `drop_dead_renames.py` the
   only one with a `main()`; the guard's absence in the two most-developed members suggests
   it was retrofitted to the others and these were missed, rather than deliberately omitted.
4. **`strip_using.py` imports the span authority and never uses it.** `:5` imports
   `_span_end` with the comment *"THE statement-span authority (agda_lex-backed); never
   re-derive"*; `:47` separately imports `agda_lex` with the identical comment; no call to
   `_span_end` exists. Lines 1-5 sit **above the shebang and the module docstring** — a
   mechanical-rewrite artifact (the shebang at `:6` is now inert). So the file carries two
   copies of "the authority" and exercises neither through `_span_end`. Whether its actual
   span logic is correct is UNVERIFIED — but `narrow_leaf_imports.py:41-45` records that
   re-deriving this exact rule is what gutted Coxeter/Core.agda 76→3.

### 3.2 Realization (ii) — gap-admission censuses, by gate reach

| capability | check_discharge_ratchet | check_rederive_ratchet | check_claims | collapse_check | tautology_advisory |
|---|---|---|---|---|---|
| wired into pre-commit | ✓ `:148` | ✓ `:143` | ✓ `:138` | ✓ `:208` | UNVERIFIED |
| **blocking** (vs advisory) | ✓ | ✓ | ✓ | **✗** (`\|\| true` at `:208`; `return 0 # ADVISORY: never blocks`) | UNVERIFIED |
| paydown-only ratchet over a census | ✓ (`ratchet.set_ratchet(census(), BASELINE, …)`) | UNVERIFIED | UNVERIFIED | ✗ (no baseline; recomputed each run) | UNVERIFIED |
| `--list` mode (name the population) | ✓ (`list_keys="--list" in sys.argv`) | UNVERIFIED | UNVERIFIED | ✗ (prints findings unconditionally) | UNVERIFIED |
| `--quiet` mode | ✓ | ✓ (`--quiet` passed at `:143`) | ✓ (`:138`) | ✗ (no flag parsing in `main`) | UNVERIFIED |
| custom `render=` for the census keys | ✓ (`_render`, decorates the AUTHORITY's keys) | UNVERIFIED | UNVERIFIED | ✗ | UNVERIFIED |
| `refuse_hint` (says how to pay down) | ✓ | UNVERIFIED | UNVERIFIED | ✗ | UNVERIFIED |

**The asymmetry that matters here:** `collapse_check.py` is the one member of this family
that hunts **duplication** — its `name_overlaps` finds def-name collisions across modules,
and its own closing advice is *"`jea_pysim.py --cluster` finds same-content duplicates under
a different name"* (`collapse_check.py:141-143`). It is also the **only** non-blocking member,
has no ratchet baseline, no `--list`, no `--quiet`, and no `refuse_hint`. So the substrate's
duplication-detection gate is the weakest-instrumented of its ratchet family — while the
tool it defers to (`jea_pysim`) is not wired into the hook at all, at any strength.

⚑ Note a citation defect worth one line: `collapse_check.py:142` advises `--cluster`
(singular). `jea_pysim`'s argparse defines `--clusters` (read at `jea_pysim.py:844`). The
advised command would `error: unrecognized arguments`. Fix not applied (audit is read-only).

### 3.3 Realization (i) — the typeholer's own reach

| capability | Python front-end (`add_file`) | Agda front-end (`add_agdai`) |
|---|---|---|
| drives the shared `Intern` | ✓ `:121-128` | ✓ `:159` (passes `self.I`) |
| produces `Unit`s the readouts see | ✓ `:122-128` | ✓ `:166-172` |
| typeholer / S(g) / clusters apply | ✓ | ✓ (measured, §2.3–2.4) |
| `⟨CARRIER⟩` un-hold normalization | **✗** — `carrier_qnames_of:137` does `if not p.endswith(".agdai"): continue` | ✓ |
| records `copy=` provenance per unit | **✗** (`add_file` constructs `Unit` without `copy=`) | ✓ (`:168`, `copies.get(name, False)`) |
| survives a stale input | ✓ (Python parse) | degrades loudly — `[agda-skip]` to **stderr**, run continues with fewer units |
| carries a line number | ✓ (`lineno=node.lineno`) | ✗ (`lineno=-1`) |

**The consequential asymmetry:** `--unhold` — the mode that catches
redundancy-under-inversion, the `UPArrow²↔rig-cat` duplicate class — is **structurally
Agda-only.** `carrier_qnames_of` skips every non-`.agdai` path by construction, so on a
pure-Python corpus `--unhold` prints `[unhold] abstracting 0 carrier qname(s)` and changes
nothing. The docstring for the flag does not scope itself to Agda. The claim "the readouts
are front-end-agnostic" is true of the *readouts* and false of this *pre-pass*.

Second: the `[agda-skip]` degradation goes to **stderr while the run exits 0** and the
stdout census reports a unit count with no `n of m` denominator — the same shape as the
`--key` defect. A `.agdai` census that silently lost two units (§2.6) reads identically to
a complete one if stderr is not captured.

---

## Residue — what I did not verify

- `jea/metalanguage/typeholer_path.py` was located by name only; its relation to
  `Corpus.typehole` is UNVERIFIED.
- `scripts/tautology_advisory.py`, `scripts/sppf_label.py` — realization-(ii) membership
  inferred from a directory-level `grep -l postulate`; contents not read, gate-reach UNVERIFIED.
- No straddling Agda↔Python cluster was found (§2.5). Fact about these inputs and this
  threshold, not about the substrate.
- The excision family's *correctness* (do they excise the right region?) is entirely out of
  scope; this audit measured guards and authorities, not behaviour.
- Whether the three guard-less rewriters are reachable from any current workflow is
  UNVERIFIED — I did not trace their callers.

---

## Command log — every command run

```
date -Iseconds                                                     # 23:15:40 and later
ls -la /home/mikemol/github/substrate/scratch/
ls /home/mikemol/github/substrate/jea/metalanguage/
python3 scratch/pycodemod.py --source main jea/metalanguage/jea_pysim.py
python3 scratch/pycodemod.py --calls typehole jea/metalanguage/jea_pysim.py scratch/*.py scripts/*.py
python3 scratch/pycodemod.py --source main scripts/collapse_check.py
python3 scratch/pycodemod.py --source main scripts/check_discharge_ratchet.py
python3 scratch/pycodemod.py --calls add_argument <6 excision members>
python3 scratch/pycodemod.py --source main scratch/prune_imports.py
python3 scratch/pycodemod.py --source main scratch/unseal_defs.py
python3 scratch/pycodemod.py --binding /home/mikemol/github/substrate/scratch/unseal_defs.py
python3 scratch/pycodemod.py --binding _snapshot_once <the nine>
python3 scratch/pycodemod.py --binding __name__ <the nine>
python3 scratch/pycodemod.py --binding main <the nine>
python3 scratch/pycodemod.py --binding DRY <the nine>
python3 scratch/pycodemod.py --calls def_index <seven of the nine>
python3 scratch/pycodemod.py --calls _span_end <the nine>
python3 scratch/pycodemod.py --dead scratch/strip_using.py
grep -nE 'scratch/|scripts/|\.py' .githooks/pre-commit                 # READ the hook; never ran it
grep -rln 'postulate' scripts/                                         # directory-level locate only
grep -rln 'postulate|trustMe|TODO|{! ' scripts/ scratch/*.py
find agda/_build -name 'Crossover*.agdai' -o -name 'Gray*.agdai'
find agda/_build -name '*.agdai' -printf 'X' -quit
timeout 900 python3 jea/metalanguage/jea_pysim.py <9 excision .py> --clusters --extract
timeout 900 python3 jea/metalanguage/jea_pysim.py 'agda/_build/.../Curve/*.agdai' --clusters
timeout 900 python3 jea/metalanguage/jea_pysim.py 'agda/_build/.../Curve/*.agdai' \
    scratch/unseal_defs.py scratch/seal_defs.py --clusters
```
Read tool (no execution): `jea_pysim.py` (2 ranges), `unseal_defs.py`, `seal_defs.py`,
`narrow_leaf_imports.py`, `strip_using.py` (head).

**Nothing under `catalog/memory/` was run or imported. No `scripts/check_*.py`,
`run_selftests.py`, `gate_preflight.py`, `*_probe.py`, or `scratch/figures/` was executed.
No `uv run --with`, no pip, no venv. `jea_pysim` was invoked only in modes confirmed
read-only by reading its `main` first. `--persist` was never passed.**

**Files created or modified by this audit: `scratch/holepunch_twins_audit.md` only.**
