---
name: project_makefile_per_dir_build
description: "per-directory recursive makefiles (generated) give a memory-confined per-file Agda build; make=dispatcher only, agda owns staleness; explicit file+subdir lists blow up loudly on drift"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The substrate's full-tree Agda check, replacing the un-runnable All.agda
(load-bound OOM, [[project_oom_load_bound_finding_2026_06]]).

**Mechanism (validated):**
- ONE `agda` process PER FILE (`+RTS -M1024m`, invoked from agda/ with
  `-i` back to the lib root). Peak RSS bounded by the single heaviest
  file's closure (~304 MB for PrimitiveInstances), never the sum. Tested:
  recursive subtree build green under a 1.5 GiB hard cgroup cap.
- make is a DISPATCHER ONLY. It does NOT track staleness: make's mtime
  model is unreliable for Agda because Agda staleness is TRANSITIVE
  (X.agdai newer than X.agda yet stale via a changed import — an edge make
  can't see). Verified: breaking a base module and rechecking only a
  dependent yields the type error → AGDA re-checks stale deps itself. So
  make ALWAYS invokes agda per file; agda no-ops fresh ones cheaply
  (0.08–0.74 s/file cached). This removes the silent-staleness failure
  mode that shard scripts have — the user's core distrust.
- ANTI-DRIFT: each generated Makefile lists its .agda FILES and its
  SUBDIRS EXPLICITLY (NO globs, per user preference). `check-sync` target
  blows up loudly if on-disk .agda ≠ listed FILES; a subdir without a
  Makefile errors loudly. New file OR new dir → build aborts naming the
  mismatch, never a silent skip. Tested both.

**Files:**
- `scripts/gen_build_makefiles.py` — generator. `--check` mode fails if any
  of the 208 makefiles is missing/stale (wired into .githooks/pre-commit).
- `agda/Makefile` + `agda/Substrate/**/Makefile` (208 total) — generated,
  marked "do not edit by hand".

**Usage (from agda/):** `make` (whole tree), `make -jN` (parallel, each
file still capped), `make -C Substrate/Groups` (subtree). Outer hard cap:
`systemd-run --user --scope -p MemoryMax=2G -p MemorySwapMax=0 make -j2`.
After adding/removing files or dirs: `python3
scripts/gen_build_makefiles.py` (or pre-commit reminds you via --check).

**Why makefile-per-dir is safe here** (vs "recursive make considered
harmful"): that critique is about make's partial dep graph causing stale
builds. Here make tracks NO deps — Agda owns the graph and re-checks
transitively. make only provides per-file process isolation + parallelism.
The known failure mode is structurally absent.

**Memory hygiene:** still NEVER run `agda All.agda`
([[feedback_never_build_all_agda]]); this build is the supported
whole-tree check. Cap calibrated to worst file (304 MB) × 3 = 1 GiB/file.
