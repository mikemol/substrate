# Ⓟ26a ⟡ratchet-seams — the decomposition plan for `scripts/ratchet.py`

**Status: PLAN ONLY. Nothing split. `ratchet.py` is unchanged on disk.**

## Why this file needs a plan and not an edit

- **1,416 lines · 215 findings · 20 call sites across 16 gates.** It is the shared core
  of the pre-commit gate surface; a half-finished split leaves sixteen gates importing a
  module mid-decomposition.
- `--closure scripts/` reports it a **LEAF at 215/215** — no dependencies, so it is
  convertible in principle. Nine `check_*` gates read 10,000+ almost entirely because of
  what sits above it.
- The `C901` / `PLR0915` / `PLR0912` / `PLR0913` / `PLR0917` findings are not style:
  they are the file reporting its own seams.

## The seam signal: `set_ratchet` takes TWELVE parameters

```
set_ratchet(cur, baseline_path, label, quiet=False, noun="entries",
            refuse_hint=None, write=None, list_keys=False, render=None,
            summary=None, dry_run=None, key_move=None)
```

⚑ **A function with twelve knobs is several functions wearing one name**, and this
file's own comments say which. Each parameter was added with a recorded incident:

| parameter | concern it belongs to | recorded reason |
|---|---|---|
| `cur`, `baseline_path`, `label` | **core** — set compare + baseline I/O | the ratchet itself |
| `write`, `dry_run` | **write policy** | *"running `check_sumtype_ratchet.py --quiet` rewrote its baseline 48 -> 45"*; `--dry-run` was the flag that did not exist, so the bypass became the only route |
| `render`, `list_keys`, `noun`, `quiet`, `summary`, `refuse_hint` | **presentation** | *"the measured difference between those four gates and this function is ONE LINE — how a key is rendered"* |
| `key_move` | **core** — decomposition-aware diffing | a split retires an old path-key and mints a new one for a byte-identical line |

## Proposed modules

Each is one reason to change. Names are provisional; the CONSUMER-FACING name does not
move.

1. **`ratchet_core.py`** — the set compare, baseline read/write, the four verdicts
   (record / refuse / auto-lower / frozen), and `key_move`. No printing, no argv, no env.
2. **`ratchet_policy.py`** — `may_write`, the `--dry-run` resolution, `SUBSTRATE_RATCHET_WRITE`.
   ⚑ The write-polarity rules and their two measured incidents live here.
3. **`ratchet_report.py`** — `render`, `list_keys`, `noun`, `quiet`, `summary`,
   `refuse_hint`. The one-line-per-key difference the four gates forked over.
4. **`ratchet_flags.py`** — `UNIVERSAL_FLAGS`, `TENANT_FLAGS`, `check_argv`.
   ⚑ **This module resolves Ⓗ1ᵈ** — see below.
5. **`ratchet_log.py`** — the VictoriaLogs jsonline ingest and its `_stream_fields`
   cardinality design. Unrelated to ratcheting; it is observability that lives here by
   accident.
6. **`ratchet.py`** — keeps `set_ratchet` as the composed entry point plus the CLI.

⚑ **THE SIXTEEN CONSUMERS DO NOT MOVE.** All 20 call sites use `ratchet.set_ratchet`;
it stays in `ratchet.py` and composes the four modules. The split is invisible to every
gate, which is what makes it landable incrementally instead of as one atomic rewrite.

## Ⓗ1ᵈ ⟡tenant-vocabulary dissolves in step 4

`ratchet.TENANT_FLAGS` and `store.TENANT_FLAGS` are the same tuple in two places —
**verified by `pycodemod --binding TENANT_FLAGS`: 2 bindings, `store.py:552` and
`ratchet.py:56`.** The file records why it was not fixed:

> *store.py's `ratchet` import is DEFERRED inside `tenant()`, deliberately; sourcing a
> MODULE-SCOPE constant from `ratchet` would force that import to module scope and change
> store.py's import-time behaviour.*

⚑ **That argument is about `ratchet`, not about the vocabulary.** A `ratchet_flags`
module with no dependencies can be imported at module scope by `store.py` without
pulling in the ratchet, so the cycle that forced the duplication stops existing. The
split is the fix; no separate arc is needed.

## Order, and why

⚑⚑ **THE ORDER INVERTED ON MEASUREMENT, AND THE FIRST DRAFT HAD IT BACKWARDS.** This
plan said "`ratchet_flags` first — no dependencies". **`check_argv` calls
`log_fallthrough`** (ratchet.py:587 and :624), so flags depend on the VictoriaLogs
ingest and the module is not dependency-free. Extracting flags first would have created
`ratchet_flags -> ratchet` — an import back into the module being decomposed, i.e. a
cycle, discovered only when the split failed to build.

⚑ `log_fallthrough` IS extractable and must go first: `--calls` reports **1 def, 6
calls, 0 refs**, every call inside `ratchet.py` itself. No external consumer, so moving
it changes nothing outside.

1. **`ratchet_log.py` first** — internal-only (6 calls, all in-file), no external
   consumers, and everything else depends on it.
2. **`ratchet_flags.py`** — `UNIVERSAL_FLAGS`, `TENANT_FLAGS`, `check_argv`,
   `mutating_argv`, `store_argv`. Depends on `ratchet_log`. Closes Ⓗ1ᵈ.
3. **`ratchet_policy.py`** — `may_write`, `--dry-run`, `SUBSTRATE_RATCHET_WRITE`.
4. **`ratchet_report.py`** — pure rendering.
5. **`ratchet_core.py`** — last: the part the sixteen gates exercise, once everything
   around it is out.

## ⚑ `check_argv` is WIDER than `set_ratchet`, which changes the risk

MEASURED (`--calls check_argv`): **1 def, 38 calls, 31 refs across 22 files** — versus
`set_ratchet`'s 20 calls across 16. And one caller is
**`jea/metalanguage/sorted_stream.py:635`**, outside `scripts/` entirely.

⚑ That cross-tree consumer is the ⟡closure-cross-tree finding arriving at this file: a
`scripts/` module with a `jea/` consumer cannot be moved without considering a tree that
is not a declared package. `check_argv` must keep its name and home in `ratchet.py` as a
re-export, exactly as `set_ratchet` does — the split stays invisible to all 22 files.

⚑ **VERIFY AFTER EACH STEP BY RUNNING GATES, NOT BY LINTING.** `--check-file` said CLEAN
on a `check_capstone_shape` whose output ordering I had broken, and on a
`migrate_to_foundation_v2` whose smoke roster was stale. The acceptance test for each
step is: run three `check_*` gates and diff their output against the pre-split run.

## ⚑ Two line citations in `ratchet.py`'s own comments are STALE

Its Ⓗ1ᵈ note cites `jea/metalanguage/store.py:284` for `TENANT_FLAGS` and `:368` for the
deferred `ratchet` import. **Neither is there now** — 284 is a keyring read, 368 is a
comment about sqlite. The binding is at **`store.py:552`**.

This is CLAUDE.md's recorded rule arriving in the file that most needs it: *cite a
SYMBOL, never a line.* A comment written to prevent drift became an instance of it, and
the same file's header already carries three dated status lines for exactly this class.
⚑ Whoever performs the split should re-derive both citations and spell them as symbols.

## What this plan does NOT decide

- ⚑ Whether `ratchet_log` belongs in `scripts/` at all. It is VictoriaLogs ingest sitting
  in the gate core; `membudget_otlp` and `run_selftests._emit_one` are the other two
  emitters, and CLAUDE.md records that the ledger→gauge shape is ONE capability with
  three hand-rolled bodies. Extracting it here may be feeding a fourth.
- Whether `set_ratchet`'s twelve parameters should become a config object. Composing four
  modules may leave the signature unchanged, which is fine — the parameters are honest
  once each belongs to a named module.
