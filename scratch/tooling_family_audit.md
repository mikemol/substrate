# Tooling family catalog + usage-contract audit

**Census window: 2026-08-03T22:15:57-04:00 → 22:19:04-04:00 (local).** Every count below
is an observation inside that window, not a property of the repo. Another session was
editing the tree concurrently (~6000 uncommitted insertions, ~200 untracked paths), so
any number here may already be stale. Where a claim is a count, the exact command that
produced it is given.

**Method: READ, not RUN.** No repo script was executed to learn its behaviour. Every
`__main__` contract below was determined from source. The only executables run were the
four sanctioned read-only instruments (full command log at the end).

---

## PART 0 — Findings, ranked by consequence

### F1 (CRITICAL, gate-wired) — `spool.py --selftest` returns success on the skip path, and the pre-commit gate reads it as a pass

`scratch/spool.py:157-159`:

```python
if _queue("t") is None:
    print("selftest: 0/0 (persist-queue absent — cases UNRUN, not passed)")
    return True
```

The prose is scrupulously honest — "UNRUN, not passed" — but the **return value contradicts
the prose**. `spool.py:203` is `sys.exit(0 if _selftest() else 1)`, so a missing
`persist-queue` yields **exit 0**.

This is not confined to a hand-run. `.githooks/pre-commit:79` wires
`scripts/run_selftests.py --quiet` as a blocking gate, and that runner classifies a suite by
scraping stdout (`scripts/run_selftests.py:54`):

```python
RESULT = re.compile(r"selftest:\s*(\d+)\s*/\s*(\d+)")
```

`selftest: 0/0` **matches** this regex. The runner then computes `bad = ok != all_`
(`run_selftests.py`, `run_one` result loop) — which for `0/0` is `0 != 0` → `False`. The
suite is counted green and contributes `0` to both `total_ok` and `total_all`.

The runner explicitly defends against the *adjacent* failure and misses this one. Its own
comment:

> `# No counted line: the suite did not report, which is itself a failure — a silent selftest is indistinguishable from a passing one.`

That guard catches a suite printing *nothing*. It does not catch a suite printing a
**vacuous denominator**. `0/0` is precisely "indistinguishable from a passing one" arriving
through the one path the guard does not cover.

Consequence: on any machine without `persist-queue`, spool's eight real assertions — the
bounded-depth cap and the drop-the-oldest guarantee at `spool.py:179-189`, the cases whose
own comment says *"a spool that grows without limit is the second store this must not
become"* — never execute, and the commit gate reports success. Ranked first because it is
gate-wired, silent, and environment-dependent (it passes loudly on a dev box with the dep
and vacuously on one without).

Note the contrast with a sibling that gets this right: `bibstruct --roundtrip` returns
`1 if rows else 0` **and** prints an explicit disclaimer that a total read "does NOT say the
parser's kernel is empty; it says nothing in THIS file fell into it." That is the same
distinction spool draws in prose and drops in its return value.

### F2 (CRITICAL, latent) — `synth_wire.py` writes `MEMORY.md` at MODULE SCOPE, with no `__main__` guard

```
python3 scratch/pycodemod.py --binding __name__ catalog/memory/synth_wire.py
→ __name__: 0 binding(s) in 0 of 1 file(s)
```

Zero `__name__` bindings — the file has **no `if __name__ == "__main__":` block at all**.
Its final statements execute on load (`synth_wire.py`, tail):

```python
open(root_path, "w").write(txt)
print(f"wrote {root_path}: {linked} concept→apex links, ...")
```

So this module rewrites the memory-corpus root **on `import synth_wire`**, not merely on
invocation. Any tool that imports it to reuse a helper, any `unittest discover` that reaches
it, any introspection that loads it, performs a corpus write. `run_selftests.py`'s docstring
already records that this hazard class is live in the tree — its comment notes "several
modules execute at import, one rewrites files from module scope," which is why it runs each
suite in its own interpreter. That mitigation protects the *runner*; it does not make the
module safe to import from anywhere else.

`synth_gate.py` shares the module-scope-execution shape (its `paths = sys.argv[1:] or
sorted(glob(...))` / `sys.exit(...)` run on load) but is **read-only**, so it is a
consistency defect, not a data-loss one.

### F3 (HIGH) — `synth_apex.py` writes on bare invocation, defaulting to a silent hardcoded phrase

`catalog/memory/synth_apex.py`, tail:

```python
if __name__ == "__main__":
    phrase = sys.argv[1] if len(sys.argv) > 1 else "never discard residue"
    ctx = build_context()
    p = build_apex(phrase, ctx)
```

and `build_apex` ends with `open(path, "w").write(...)` into `synth/<slug>.md`.

Bare invocation therefore **writes a file**, with no flag, no dry-run, and no prompt —
and the operand it writes for is a **hardcoded default phrase**, so the write is not even
obviously connected to what the operator typed. This directly inverts the repo's documented
convention for its structural readers ("run bare to list its modes"), which is what makes it
a trap: the convention teaches that bare invocation is the safe discovery move, and here
that exact move mutates the corpus.

Compounding it: `build_apex` computes `slug` from the phrase and globs `HERE` for members,
so the *content* is a function of whichever corpus directory the file sits in. There are two
copies of this corpus (repo and `~/.claude/projects/`), so the same command produces
different, equally plausible-looking output depending on location — an apex whose witness
list cites memories that exist in the other tree. This is fabrication that passes the
project's own content gate.

### F4 (HIGH, gate-wired) — `py_files` is a live 3-body reimplementation feeding two gates

```
python3 scratch/pycodemod.py --rivals py_files
→   REIMPLEMENTS  scratch/band_sppf.py:33    3 statement(s)
    REIMPLEMENTS  scratch/claim_census.py:69  1 statement(s)
    REIMPLEMENTS  scratch/pycodemod.py:266    3 statement(s)
  py_files: 3 def(s) — 3 reimplementing, 0 delegating
```

**Verified as reported by the lead.** Three independent bodies, **zero** delegating. Since
each body defines its own traversal and exclusion set (`__pycache__`, `bazel-*`, `_build`,
generated), the three answer *"what is the Python corpus?"* differently — and that question
is the denominator of every census built on them. `check_mypy_ratchet.py` and
`check_scratch_independence.py` are both pre-commit-wired (`.githooks/pre-commit:188` and
`:225`), so a corpus-definition drift moves a **gate baseline** without any policy change.

The contrast case shows this is payable, not inherent:

```
python3 scratch/pycodemod.py --rivals agda_files
→   REIMPLEMENTS  scratch/agda_lex.py:367      6 statement(s)
    DELEGATES     scratch/claim_census.py:57    -> _agda_files
    DELEGATES     scratch/paydown.py:67         -> _agda_files
    DELEGATES     scripts/check_carrier_locality.py:128 -> _agda_files
    DELEGATES     scripts/check_claims.py:85    -> _agda_files
  agda_files: 5 def(s) — 1 reimplementing, 4 delegating
```

**Also verified as reported: 1 reimplementing, 4 delegating.** `agda_files` converged on a
single authority with four delegators; `py_files` did not. The repo records `agda_files`
having once had four bodies under one name, two feeding pre-commit gates — i.e. `py_files`
today is sitting in the exact configuration `agda_files` was already paid down out of. The
paydown pattern is established and demonstrated in-tree.

### F5 (MEDIUM) — `pycodemod --key` has no denominator; the lead's diagnosis was right, the mechanism is not what was described

**Refined, and partly refuted.** The suspicion was that `--key` reports `0 file(s)` for a
file `--binding` reads as `1 of 1`. I could not reproduce that specific pair — both modes
reported `0` files on my probe:

```
python3 scratch/pycodemod.py --key     scripts/check_mypy_ratchet.py
→ '/home/.../check_mypy_ratchet.py': 0 read(s), 0 declaration(s) in 0 file(s)
python3 scratch/pycodemod.py --binding scripts/check_mypy_ratchet.py
→ /home/.../check_mypy_ratchet.py: 0 binding(s) in 0 of 743 file(s)
```

But that pair exposes the real defect, which is more general. **Both modes consume their
first positional as the search NAME, not as a path** — so both commands above searched the
whole corpus for a key/name literally spelled `/home/.../check_mypy_ratchet.py`. The
underlying contract difference is visible in the source.

`--key` (`pycodemod.py:3447-3448`):

```python
print(f"{name!r}: {len(reads)} read(s), {len(decls)} declaration(s) in "
      f"{len({p for p, _, _, _ in rows})} file(s)")
```

The file count is derived **from the matched rows**. When `rows` is empty it is
structurally `0`, and there is **no `of m` term at all**. `--key` therefore cannot
distinguish *no matches* from *no files read* — for any query, not just malformed ones.
Two well-formed probes confirm the count stays `0 file(s)` rather than reporting the corpus:

```
python3 scratch/pycodemod.py --key baseline scripts/check_mypy_ratchet.py
→ 'baseline': 0 read(s), 0 declaration(s) in 0 file(s)
python3 scratch/pycodemod.py --key code     scripts/check_mypy_ratchet.py
→ 'code': 0 read(s), 0 declaration(s) in 0 file(s)
```

`--binding` (`_print_bindings`, `pycodemod.py:3018-3034`) does it correctly, and its comment
names the exact rule `--key` violates:

```python
    # ⚑ `n of m`, ALWAYS.  "There are no sweeps, only censuses" — a bare list
    # cannot distinguish "no bindings" from "no files searched" ...
    print(f"{name}: {total} binding(s) in {shown} of {len(files)} file(s)")
```

So: **the reported symptom is not reproducible as stated, but the underlying finding is
confirmed and is broader** — `--key`'s denominator is unreliable by construction, against a
rule stated verbatim in its own sibling ten mode-blocks away. Treat `--key` counts as
lower bounds. (Per Rule 2, I suspected the tree first and re-measured before concluding;
the divergence here is in the *mechanism*, not the tree.)

### F6 (LOW, positive) — the ratchet family is CLEAN on flag validation

`scripts/ratchet.py:29` `check_argv` is a genuine shared authority, adopted by 14 call sites:

```
python3 scratch/pycodemod.py --calls check_argv
→ check_argv: 1 def(s), 14 call(s)
```

covering `check_ban_ratchet`, `check_cap_ratchet`, `check_carrier_locality`, `check_claims`,
`check_discharge_ratchet`, `check_feature_coverage`, `check_mypy_ratchet`,
`check_private_ratchet`, `check_public_ratchet`, `check_rederive_ratchet`,
`check_snapshot_guard`, `check_sumtype_ratchet`, `run_selftests`, `worklist_gate`.

Cross-checked against `.githooks/pre-commit`: **every python ratchet gate the hook runs
through `run` appears in that adopter list.** Unknown-flag rejection (exit 2) is uniform
across the gate-wired set, and `UNIVERSAL_FLAGS` means the authority declares its own
vocabulary so a new gate inherits `--dry-run` without knowing. This family is a real
success — say so plainly.

The write-authority is equally disciplined: `set_ratchet` has 11 callers, and baseline
rewriting is confined to the commit path by `SUBSTRATE_RATCHET_WRITE=1`, exported at
`.githooks/pre-commit:46` with a comment recording two measured incidents of an audit run
lowering a baseline. That is a correctly-placed guard against exactly the hazard this audit
was told to avoid.

### F7 (INFORMATIONAL) — the snapshot-guard population has moved well past the figure in the hook comment

`.githooks/pre-commit:151-154` records "MEASURED 2026-08-01: 43 tools read-then-write an
Agda source; only 9 armed `edit_snapshot`."

```
python3 scratch/pycodemod.py --calls guard scripts scratch
→ guard: 1 def(s), 55 call(s)
```

Filtering that output to genuine `call` sites of `edit_snapshot.guard` (excluding the
`ref`-only duplicates and the `scratch/eliza/**/sequitur.py` hits, which are a **different
`guard`** — an unrelated local symbol, not `edit_snapshot`'s), the Agda-source transformers
in `scratch/` are broadly armed: `split_*`, `rewire_*`, `fix_*`, `prune_*`, `narrow_*`,
`seal_*`/`unseal_defs`, `telescope_migrate*`, `strip_using`, `respell_typealias`,
`recover_presplit`, `repair_mod_tip`/`retire_mod_tip`, `reparameterize_record`,
`collapse_carrier_nesting`, `topup_leaves`, plus `scripts/decl_shape_tag`,
`gen_build_makefiles`, `set1_ratchet_cores`, `sppf_node_index`, `worklist.py`.

This is the ratio moving in the right direction under a gate whose population is
*discovered* rather than declared. **Caveat, and it is why this is informational rather
than a clean result:** `--calls guard` matches on the bare name, and the eliza hits prove
that name is not unique in the tree. I did not verify each call site's import binding, so
treat the adoption set as indicative. The exact per-tool arming census is
`scripts/check_snapshot_guard.py`'s job — **UNVERIFIED here**, as running it is outside the
sanctioned instrument set.

---

## PART 1 — The catalog, grouped topologically

Grouped by the artifact each tool reads/writes and what it composes with. Counts of
directory contents are from `ls` at the timestamps above.

### Family A — structural readers (one per artifact kind)

The `struct-tools` family proper, named by `.claude/skills/struct-tools/SKILL.md:54-60`.

| path | purpose | CLI/lib |
|---|---|---|
| `scratch/pycodemod.py` | lossless (libcst) Python structural reader/transformer; `--calls --dead --binding --imports --rivals --source --key --attr --available --roundtrip` | both |
| `scratch/mdstruct.py` | markdown structure (pandoc/panflute for AST modes); `--headers --spans --tables --items --coherence --superseded` | both |
| `scratch/bibstruct.py` | BibTeX warrants claim-DAG; reads file *and* engine whitelist, reports the difference | both |
| `scratch/agda_lex.py` | Agda lexer/section machinery; `--by-op` and repair helpers | both |
| `scratch/agda_defs.py` | Agda name→home authority (`def_index()`); ~19 tools resolve through it | both |
| `scratch/tsdbprobe.py` | HTTP/OTLP metrics surface reader (cassian VM) — **not run** per brief | CLI |
| `scratch/agda_imports.py`, `agda_types.py` | Agda import/type readers adjacent to the above | lib |

**Composition:** `agda_defs.def_index()` is the shared authority the Agda transformers
(Family C) resolve names through; `agda_lex` supplies their section/span parsing.

### Family B — ratchet / gate checkers

Authority: `scripts/ratchet.py` (`check_argv`, `set_ratchet`, `UNIVERSAL_FLAGS`).
Pre-commit-wired members, in hook order (`.githooks/pre-commit`): `run_selftests.py:79`,
`check_feature_coverage.py:80`, `check_def_proof_separation.sh:82`, `check_up_nonvacuity.sh:91`,
`gen_build_makefiles.py --check:95`, `query_defs.py --check:100`, `worklist.py --check:107`,
`sppf_node_index.py --check:111`, `check_import_shape.py:115`, `decl_shape_tag.py:119`,
`check_carrier_locality.py:125`, `check_ban_ratchet.py:135`, `check_claims.py:138`,
`check_rederive_ratchet.py:143`, `check_discharge_ratchet.py:148`, `check_snapshot_guard.py:155`,
`check_sumtype_ratchet.py:161`, `check_public_ratchet.py:167`, `check_private_ratchet.py:174`,
`check_mypy_ratchet.py:188`, `law_motif_apex.py --check:193`, `collapse_check.py:201` (advisory),
`set1_ratchet_cores.py:334`, `check_cap_ratchet.py:345`, `reuse_sweep.py --gate:354` (advisory).
Conditional: `jea_regression_gate.py:208`, `jea_metalanguage_gate.py:217`,
`check_scratch_independence.py:225`, `check_scratch_runtime.py:230`.
Non-wired siblings present in `scripts/`: `gate_preflight.py`, `gate_status.py`,
`gate_keys.py`, `gate_ledger.py`, `check_capstone_shape.py`, `check_file_sizes.sh`,
`check_categorical_grounding.sh`, `witness_sanity.py`, `tautology_advisory.py`,
`untethered_disjunct_advisory.py`.

### Family C — Agda source transformers (`scratch/`)

The read-then-write cluster, governed by `edit_snapshot.guard` (F7). Sub-clusters by verb:
**split** (`split_lemmas`, `split_pipeline`, `split_telescoped`, `split_upstream`,
`split_graded`, `split_param_module`), **rewire** (`rewire_fcr`, `rewire_stale_module`,
`rewire_to_leaves`, `conduit_resolve`), **prune/narrow** (`prune_imports`,
`prune_leaf_opens`, `narrow_leaf_imports`, `narrow_leaf_opens`, `dedup_imports`,
`strip_using`, `drop_dead_renames`, `demand_imports`), **fix/resolve**
(`fix_notinscope`, `fix_ambiguous_import`, `fix_orphan_using`, `fix_stale_using`,
`fix_sections`, `fix_dead_fin_alias`, `resolve_notinscope`, `scope_fix`), **seal**
(`seal_defs`, `seal_ops`, `unseal_defs`), **telescope** (`telescope_lib`,
`telescope_migrate`, `telescope_migrate_gen`, `telescope_text`, `hoist_telescope_imports`),
**recover** (`recover_presplit`, `edit_snapshot`, `replay_pipeline`).

### Family D — cost & observability

`scripts/membudget` (+ `membudget-shrc`, `cgroup-scope`) — the universal capture point;
`scripts/buildtime.py` (genlop-style estimates over per-dir `.agda-times.tsv`);
`scripts/proofcost.py`; `scripts/decode_cost.py`; `scripts/cap_diagnose.py`;
`scripts/membudget_otlp.py`; `scratch/spool.py` (bounded local buffer for series —
see F1); `scratch/tsdbprobe.py`; `scripts/run_selftests.py`; `scripts/gate_ledger.py`
(ranks gates by measured failure rate).

### Family E — memory / corpus mechanizers (`catalog/memory/`) — DO NOT EXECUTE

`synth_apex.py`, `synth_scale.py`, `synth_wire.py`, `synth_gate.py`,
`synth_grammar_read.py`, `synth_pi_probe.py`, `synth_reverse_probe.py`,
`synth_typehole_probe.py`, `grammar_phrase_lattice.py`, `build_warrants.py`,
`cluster_memories.py`, `pcr_corpus_grammar.py`, `chamber_coord_probe.py`,
`regen_if_stale.sh`. Two corpus copies exist (repo + `~/.claude/projects/`); neither is a
sandbox.

### Family F — SPPF / interning / analysis

`jea/metalanguage/jea_pysim.py` (Python+`.agdai` internment, `--clusters --extract
--skeleton`), `jea_pyalg.py`, `jea_agdai.py`, `jea_ir_unify.py`, `jea_sppf_torsor.py`,
`jea_rigcat.py`, `jea_grammar_fixpoint.py`; `scripts/sppf_db.py`, `sppf_discover.py`,
`sppf_label.py`, `sppf_node_index.py`, `sppf_query.py`, `type_sppf.py`,
`type_sppf_crosslayer.py`; `scratch/band_sppf.py`, `dagcone.py`.
Query layer: `query_defs.py` (source of truth) → `query_sql.py` (generated cache) →
`query_builders.py` (runtime); staleness is gated at `.githooks/pre-commit:100`.

### Family G — catalog / reuse discovery

`scripts/gen_catalog.py` (single walk → renders), `reuse_catalog.py` (shared walk),
`gen_reuse_index.py`, `gen_reuse_graph.py`, `reuse_check.py`, `reuse_sweep.py`,
`reuse_tui.py`, `catalog_query.py`, `query_topo.py`, `primitive_catalogue.py`.
Renders staged by the hook at `.githooks/pre-commit:301-304`.

### Family H — build generation

`scripts/gen_build_makefiles.py` (authority for `MEM_CAP`), `gen_flat_makefile.py`,
`agda-shim`, `sched-batch`.

### Family I — figures / render, and ad-hoc probes

`scratch/figures/`, `scratch/chart*.py`, `scratch/eliza/`; the `verify_*.py` and `*_probe.py`
families in `scratch/`. Per the brief these were not executed and their contracts are
**UNVERIFIED** except where noted.

---

## PART 2 — Per-family conformance tables

Axes: (a) bare invocation, (b) `--selftest`, (c) exit codes, (d) `n of m` denominator,
(e) corpus/path args, (f) write modes, (g) shared helper vs reimplementation.

### Family A — structural readers

| tool | (a) bare | (b) selftest | (c) exits | (d) denominator | (f) writes |
|---|---|---|---|---|---|
| `pycodemod.py` | docstring/mode list, **exit 2** | yes | 0 ok / 1 findings (`--roundtrip`) / 2 usage | **mixed — `--binding` correct (`shown of len(files)`), `--key` absent (F5)** | `--apply` gated; `--roundtrip` is a gate |
| `mdstruct.py` | `print(__doc__)`, **exit 2** | yes | 0 / 1 (`--coherence` on orphans/dangling) / 2 | per-population counts; `--coherence` prints 3 populations, never one verdict | `--apply` (brief forbids) |
| `bibstruct.py` | `print(__doc__)` to stderr, **exit 2** | yes (`--selftest` first, short-circuits) | 0 / 1 (`--roundtrip` findings, failed write) / 2 usage | **yes, every mode** (`_n_of_m`), incl. explicit totality disclaimer | `--set`/`--add` **dry-run by default**, `--apply` required, `edit_snapshot.guard` armed, post-write round-trip + read-back verify |
| `agda_lex.py` | **runs `_selftest()`** — deviation | yes (it *is* bare behaviour) | `sys.exit(_selftest())` | `--by-op` prints `n distinct over m sites` | repair helpers write |
| `agda_defs.py` | requires `<name>`; `--provides <Mod>` | UNVERIFIED | UNVERIFIED | UNVERIFIED | read-only by design |
| `tsdbprobe.py` | UNVERIFIED (not run, not read — out of scope) | UNVERIFIED | UNVERIFIED | UNVERIFIED | network reads |

**Verdict:** strong but not uniform. Three of six exit 2 with a mode list on bare
invocation; `agda_lex.py` instead runs a selftest — harmless (read-only) but it means
"run it bare to discover modes" is not a family-wide law, and the skill file states it as
one. `bibstruct.py` is the **reference implementation** of the write contract: dry-run
default, explicit `--apply`, snapshot guard, and *two* post-write verifications
(round-trips **and** reads back) with recovery instructions on failure. The single
substantive defect is F5.

### Family B — ratchet / gate checkers

| axis | conformance |
|---|---|
| (a) bare | Gates run their census; `--quiet` is the hook form. Uniform. |
| (b) selftest | Discovered, not listed, by `run_selftests.py` — a new tool is covered by construction. Strong design. **But see F1**: discovery does not imply the discovered suite reports honestly. |
| (c) exits | 0 pass / 1 fail / **2 unknown-flag** — uniform across all 14 `check_argv` adopters. **Clean.** |
| (d) denominator | Ratchets compare census vs baseline (`*_baseline.txt`) — a real denominator by construction. |
| (e) corpus | `check_mypy_ratchet` **imports** its scope from `check_scratch_independence.ROOTS` rather than restating it — the correct one-place pattern. |
| (f) writes | Baseline writes fenced behind `SUBSTRATE_RATCHET_WRITE=1`, exported **only** at `.githooks/pre-commit:46`. `set_ratchet` read-only otherwise. **Clean, and correctly motivated.** |
| (g) helpers | `check_argv` 14 adopters, `set_ratchet` 11 — genuine convergence. Undercut by **F4** (`py_files`), which is the corpus definition *underneath* two of these gates. |

**Verdict: the cleanest family in the tree on flags, exits, and write-fencing (F6).** Its
exposure is not in the gate layer but one level down, in the un-converged `py_files`
corpus helper (F4) and in the selftest-honesty gap (F1).

### Family C — Agda source transformers

| axis | conformance |
|---|---|
| (a) bare | Not uniformly audited — **UNVERIFIED** across the ~40 members; would require reading each `__main__`. |
| (f) writes | Governed by `edit_snapshot.guard`; adoption now broad (F7), enforced by a gate whose population is *discovered* (`check_snapshot_guard.py`, hook line 155) rather than declared — the right mechanism, since one-by-one adoption is what produced the original 33-file loss. |
| (g) helpers | Resolve names through `agda_defs.def_index()`; `agda_files` converged 4-delegating/1-reimplementing. |

**Verdict:** structurally sound where measured; per-tool bare-invocation contract is the
main unaudited surface. Recommend a `--modes`-style census as the next mode, not a manual sweep.

### Family D — cost & observability

| tool | (a) bare | (b) selftest | (c) exits | notes |
|---|---|---|---|---|
| `spool.py` | `print(__doc__)`, **exit 2** (conformant) | **DEFECTIVE — F1**, `0/0` returns True | 0/1 selftest, 0 `--depth`, 2 bare | `--depth <name>` read-only |
| `run_selftests.py` | runs the suite | `--selftest` (self-vouching under `--last`) | 0 / 1 broken-or-stale / 2 unknown flag | adopts `check_argv`; writes `LEDGER` on pass **and** fail (correct — distinguishes "never measured" from "measured and BROKEN"); ledger write wrapped so it "must never fail a suite run" |
| `buildtime.py`, `proofcost.py`, `membudget*`, `tsdbprobe.py`, `gate_ledger.py` | **UNVERIFIED** (not run per brief; `membudget` is shell) | UNVERIFIED | UNVERIFIED | `membudget` is documented in `CLAUDE.md` as the universal capture point |

**Verdict:** `run_selftests.py` is well-constructed — parallel-by-subprocess with the
isolation rationale documented, order restored rather than inherited from the scheduler,
per-suite splits kept rather than summed away, and a self-vouching `--last`. Its one blind
spot is the vacuous-denominator class (F1), which is a defect in the *contract between*
runner and suite, not in either alone. The honest fix is symmetric: `spool._selftest`
should return False (or print no counted line) when cases are UNRUN, **and** the runner
should treat `all_ == 0` as not-a-pass.

### Family E — memory / corpus mechanizers

| tool | (a) bare invocation | write-on-bare? |
|---|---|---|
| `synth_wire.py` | **module scope — no `__main__` guard at all (F2)** | **YES, on import** |
| `synth_apex.py` | writes apex for a hardcoded default phrase (F3) | **YES** |
| `synth_scale.py` | regenerates every stale apex (per brief; consistent with siblings) | **YES** (not read — treated as DO-NOT-EXECUTE) |
| `grammar_phrase_lattice.py` | `rmtree(index/)` + rewrites `MEMORY.md` (per brief) | **YES, destructive** |
| `build_warrants.py` | writes `warrants.bib`, `MEMORY.candidate.md` (per brief) | **YES** |
| `synth_gate.py` | module-scope execution; **read-only**; `sys.exit(0 if all(results) else 1)` | no |

**Verdict: the worst-conforming family, and it inverts the repo's own convention.** Family A
teaches that bare invocation is the safe way to discover modes; here bare invocation — and
for `synth_wire.py`, mere **import** — mutates the corpus. None of these offer a dry-run
flag. Combined with two non-sandbox corpus copies (F3), the failure mode is not a crash but
**plausible fabricated output that passes the project's own content gate**. This family
needs `__main__` guards and an `--apply` convention borrowed directly from `bibstruct.py`,
which already demonstrates the correct pattern in this same repo.

Note the asymmetry worth naming: `.githooks/pre-commit:38-45` fences ratchet *baseline*
writes behind an env var precisely because an audit run once lowered a baseline. The memory
corpus has no equivalent fence, despite the same hazard and a worse blast radius.

### Families F–I

**UNVERIFIED** on axes (a)–(f). The SPPF/query layer (F) has a real staleness gate
(`query_defs.py --check`, hook line 100) enforcing that the generated `query_sql.py` cache
matches its `INTERN_BUILDERS` source of truth — the single-source-of-truth pattern, correctly
gated. Families G–I were catalogued but not contract-audited; auditing them would require
either running them (forbidden) or reading ~60 further `__main__` blocks (beyond this pass).

---

## Cross-family summary

| axis | best | worst |
|---|---|---|
| (a) bare invocation | A (exit 2 + mode list), B (census + `--quiet`) | **E (writes; `synth_wire` on import)** |
| (b) selftest | B (discovered, not listed) | **D (`spool` 0/0 passes — F1)** |
| (c) exit codes | **B (0/1/2 uniform across 14 adopters)** | E (no convention) |
| (d) `n of m` | `bibstruct` (every mode + totality disclaimer) | **`pycodemod --key` (no denominator — F5)** |
| (f) write modes | **`bibstruct` (dry-run → `--apply` → guard → round-trip → read-back)** | **E (no flag, no dry-run, no guard)** |
| (g) shared helper | `agda_files` (1 reimpl / 4 delegating), `check_argv` (14) | **`py_files` (3 reimpl / 0 delegating — F4)** |

The pattern: **the repo's conventions are excellent where they are enforced by a gate, and
absent where they are not.** Every clean result above sits behind a pre-commit gate; every
defect (F1–F5) sits in a place no gate inspects — a selftest's honesty, a module's import
side-effects, a mode's denominator, a helper's convergence.

---

## Commands executed (complete log)

Only the four sanctioned read-only instruments, plus `ls`/`tail`/`date`. No repo script was
executed to learn its behaviour. One command per call throughout (no `&&`, `;`, `|`, `for`,
or inline `python3 -c`).

```
date -Iseconds                                                   (×2, census bounds)
ls scratch/ ; ls scripts/ ; ls catalog/memory/ ; ls jea/metalanguage/   (separate calls)
tail -30 scratch/mdstruct.py
tail -25 scratch/agda_lex.py
tail -32 catalog/memory/synth_apex.py
tail -30 catalog/memory/synth_wire.py
tail -20 catalog/memory/synth_gate.py
grep -n "selftest|__main__|sys.exit|argv" scratch/spool.py
grep -n "^RESULT|RESULT =" scripts/run_selftests.py
grep -n '"--key"|"--binding"|__main__' scratch/pycodemod.py
grep -n "^RESULT" ...                                            (line-location only)

python3 scratch/pycodemod.py --source main scratch/bibstruct.py
python3 scratch/pycodemod.py --source main scratch/spool.py
python3 scratch/pycodemod.py --source main scratch/mdstruct.py
python3 scratch/pycodemod.py --source main scratch/pycodemod.py
python3 scratch/pycodemod.py --source main scripts/run_selftests.py
python3 scratch/pycodemod.py --source check_argv scripts/ratchet.py
python3 scratch/pycodemod.py --source _print_bindings scratch/pycodemod.py
python3 scratch/pycodemod.py --calls open scratch/spool.py
python3 scratch/pycodemod.py --calls check_argv
python3 scratch/pycodemod.py --calls set_ratchet
python3 scratch/pycodemod.py --calls guard scripts scratch
python3 scratch/pycodemod.py --rivals py_files
python3 scratch/pycodemod.py --rivals agda_files
python3 scratch/pycodemod.py --key     scripts/check_mypy_ratchet.py
python3 scratch/pycodemod.py --key baseline scripts/check_mypy_ratchet.py
python3 scratch/pycodemod.py --key code     scripts/check_mypy_ratchet.py
python3 scratch/pycodemod.py --binding scripts/check_mypy_ratchet.py
python3 scratch/pycodemod.py --binding __name__ catalog/memory/synth_wire.py

Read tool: .claude/skills/struct-tools/SKILL.md, .githooks/pre-commit,
           scratch/spool.py:140-211, scratch/pycodemod.py:3055-3084, :3430-3459
```

Note: one `grep -n` over `.py` files was **refused by the structural-query hook**
(correctly — it asks about a structured artifact textually). I complied and used `Read`
and `pycodemod --binding` instead; that refusal is itself evidence the hook is armed and
working as `CLAUDE.md` describes.

`mdstruct.py` was **not** run (no `--apply`, and no markdown-structure question arose that
`Read` did not answer). `bibstruct.py` and `agda_defs.py` were not run — no BibTeX or Agda
name-resolution question arose in this pass; their contracts above are from source.
`tsdbprobe.py`, `run_selftests.py`, `gate_preflight.py`, all `scripts/check_*.py`, all
`*_probe.py`, `figures/`, `jea/`, and **all of `catalog/memory/`** were never executed.

**File assertion: the only file created or modified by this pass is this report,
`scratch/tooling_family_audit.md`. No other file in the tree was written, and no repo
script capable of writing was executed.**
