#!/usr/bin/env python3
"""set1_ratchet_cores.py — the Set₁ policy gate, a COLUMN READ over the interned SPPF (⟡gqs-ratchet-query).

WHY NOT GREP (read before changing)
  The predecessor grepped `Set₁` in stripped source. That counts SOURCE TOKENS, not
  definitions: one `record R : Set₁` token yields ~4 Set₁ definitions in the core
  (the record, its constructor, and Agda's generated transp-/hcomp- helpers), and
  Set₁-TYPED FUNCTIONS carry no token at all. A sort is elaborated information; source
  text is elaboration's INPUT.

THE MEASURE
  A definition inhabits Set₁ iff the codomain sort of its type (Πs peeled; when the
  codomain is itself `Sort s`, that s) is `Type` at level >= 1. The shim emits this per
  defmark as {"sort":"Type","level":n}; write_events persists it as unit_obs.level, so the
  census is `set1_count` = COUNT(unit_obs WHERE level>=1) over catalog.db — NOT a ~94s
  per-core decode (this replaces the decode predecessor, ⟡gqs-ratchet-query). The pre-commit
  runs `make catalog` first (⟡gqs-precommit-reorder), so this queries a FRESH DB; standalone,
  it freshens catalog.db itself (INCREMENTAL — only mtime-advanced cores re-decode, via
  core_fp; auto-migrates a stale schema via write_events' version net).

THREE GUARDS (each preserved as a query — a silently-undercounting census is the exact
failure this gate exists to prevent; "cannot measure" is never "no debt"):
  (1) LEVEL POPULATED — unit_obs.level must carry values. A level-blind intern (a shim that
      emits no `level` — the repo's 2.8.0 shim predates the field, ⟡shim-upstream) makes
      every def look non-Set₁ and would silently lower the baseline to 0. The query-form of
      the old assert_shim_reports_sorts.
  (2) COMPLETENESS — every on-disk .agdai must be ingested (present in core_fp). An
      undecodable core is skipped by write_events → absent from core_fp → surfaced here.
      An incomplete census is not a low count.
  (3) DENOMINATOR — the core count must match the baseline's; a moving denominator is not a
      ratchet (a Set₁ count over a different core set is not comparable).

BASELINE  scripts/set1_baseline_cores.txt holds "<defs> <cores>" (a 1-field legacy "<defs>"
  is read with the denominator guard dormant). RATCHET: the count may only drop — it
  auto-lowers on a decrease, refuses on an increase, freezes at baseline.

NO RAW SQL — every read is a named query_builders builder (⟡gqs-nolawsql): core_fp_ids,
  level_populated, set1_count. Only the incremental freshen (write_events) writes.
"""
import os, sys, glob, base64, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import sppf_db
import query_builders as QB

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set1_baseline_cores.txt")


def _freshen(cores, base, catalog_db):
    """Incremental event-tier freshen (no projection — the census reads unit_obs directly). A NO-OP after
    `make catalog` (core_fp all current); else re-decodes only mtime-advanced cores; auto-migrates a stale
    schema (write_events forces --full on a version mismatch)."""
    con = sqlite3.connect(catalog_db)
    sppf_db.write_events(cores, con, base, prune=True)
    con.commit(); con.close()


def census_gate(cores, base, catalog_db, baseline_path, quiet=False, freshen=True):
    """The Set₁ ratchet as a query. Returns a process exit code (0 pass / 1 fail). `freshen=False` skips the
    incremental re-ingest (for testing an injected fault against a pre-built DB)."""
    on_disk = {sppf_db._b64(os.path.relpath(c, base)): c for c in cores}   # core_id → path (base64 reversible)
    if freshen:
        _freshen(cores, base, catalog_db)
    con = sqlite3.connect(catalog_db)

    # Guard (2) — COMPLETENESS: every on-disk core must be ingested; an undecodable one is absent from core_fp.
    ingested = {r[0] for r in QB.run(con, "core_fp_ids")}
    undec = set(on_disk) - ingested
    if undec:
        print(f"set1-ratchet: {len(undec)} of {len(on_disk)} cores UNDECODABLE — census incomplete.")
        for cid in list(undec)[:3]:
            try: print("  " + base64.b64decode(cid).decode("utf-8", "replace"))
            except Exception: pass
        print("  An incomplete census is not a low count. Rebuild cores (`make catalog`); do not certify.")
        con.close(); return 1

    # Guard (1) — LEVEL POPULATED: a level-blind intern cannot certify Set₁ debt.
    if QB.run(con, "level_populated").fetchone()[0] == 0:
        print("set1-ratchet: unit_obs.level is empty — the shim emits no `level`, so Set₁ debt cannot be measured.")
        print("  Rebuild a level-emitting shim (make -C jea/metalanguage shim), then `make catalog`.")
        con.close(); return 1

    n = QB.run(con, "set1_count").fetchone()[0]
    ncores = len(on_disk)
    con.close()

    # ── baseline compare / auto-lower (semantics identical to the decode version) ──
    if os.path.exists(baseline_path):
        parts = open(baseline_path).read().split()
        base_n, base_cores = int(parts[0]), (int(parts[1]) if len(parts) > 1 else None)
    else:
        open(baseline_path, "w").write(f"{n} {ncores}\n")
        print(f"set1-ratchet: baseline recorded = {n} Set₁ definitions over {ncores} cores")
        return 0

    # Guard (3) — DENOMINATOR.
    if base_cores is not None and base_cores != ncores:
        print(f"set1-ratchet: CORE SET CHANGED — {ncores} cores now, baseline took {base_cores}.")
        print(f"  Set₁ count {n} is not comparable to baseline {base_n} over a different denominator.")
        print("  Rebuild the full tree, then re-baseline. (A moving denominator is not a ratchet.)")
        return 1

    if n > base_n:
        print(f"set1-ratchet: BROKEN — {n} > baseline {base_n} Set₁-inhabiting definitions.")
        print("  Set₁ is policy debt: do not FIELD a Set-valued carrier/relation — PARAMETERIZE it")
        print("  (see Substrate.Category.Lawvere's carrier-generic atoms).")
        return 1
    if n < base_n:
        open(baseline_path, "w").write(f"{n} {ncores}\n")
        print(f"set1-ratchet: baseline LOWERED {base_n} -> {n} (debt paid down)")
    elif not quiet:
        print(f"set1-ratchet: at baseline {base_n} ({ncores} cores, legacy debt, frozen)")
    return 0


def main():
    quiet = "--quiet" in sys.argv
    base = sppf_db.substrate_core_root(os.path.join(ROOT, "agda"))
    cores = sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
    if not cores:
        print("set1-ratchet: NO CORES — cannot measure, so cannot certify.")
        print("  build the tree first (agda/Makefile / `make catalog`).")
        sys.exit(1)
    sys.exit(census_gate(cores, base, sppf_db.CATALOG_DB, BASELINE, quiet=quiet))


if __name__ == "__main__":
    main()
