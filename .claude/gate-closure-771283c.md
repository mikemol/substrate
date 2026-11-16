# Gate closure at 771283c (R1 manifest, for review before pinning)

Derived by the gate-oracle (read-only), 2026-11-16, from git objects at 771283c only.
Walker: scratchpad clo/closure2.py (AST import resolution + tracked-path token matching, fixpoint;
.agda excluded as tree-under-test). [measured] = read in code or found by walker; [inferred] otherwise.

## Facts at 771283c [measured]
- No pyproject.toml, uv.lock, .python-version, or substrate/ package. No config to pin.
- No gate_ledger.py / gate_census.py in the closure; the hook never calls them.
- The hook runs bare `python3`; no $PY/venv.

## Manifest
Driver: .githooks/pre-commit; .githooks/prepare-commit-msg (report fold only, verdict-neutral).
post-commit is NOT part of the verdict (advisories only).

Check scripts (direct):
scripts/check_def_proof_separation.sh, scripts/check_up_nonvacuity.sh, scripts/gen_build_makefiles.py,
jea/metalanguage/query_defs.py, scripts/worklist.py, scripts/sppf_node_index.py,
scripts/check_import_shape.py, scripts/decl_shape_tag.py, scripts/check_carrier_locality.py,
scripts/check_sumtype_ratchet.py, scripts/check_public_ratchet.py, scripts/law_motif_apex.py,
scripts/collapse_check.py (advisory), jea/jea_regression_gate.py (if ^jea/jea_.*\.py$ staged),
jea/metalanguage/jea_metalanguage_gate.py (if jea/metalanguage/*.py or root Σ modules staged),
scripts/check_scratch_independence.py + scripts/check_scratch_runtime.py (if ^(jea|el-atlas)/ staged),
scripts/gen_catalog.py (post-build, advisory, git-adds), scripts/set1_ratchet_cores.py,
scripts/check_cap_ratchet.py (post-build), scripts/reuse_sweep.py (post-build advisory, needs catalog.db).

Build path: agda/Makefile (make -C agda -j), agda/Flat.mk (all: check-sync $(AGDAI); ingest NOT in all),
scripts/agda-shim/agda (via absolute SHIM_DIR), scripts/membudget, scripts/proofcost.py.

Imported modules: scripts/{_agdatext,_content_addr,ratchet,buildtime,decode_cost,sppf_db,sppf_query,
rig_coherence,reuse_catalog,gen_reuse_index,gen_reuse_graph,reuse_tui}.py;
jea/metalanguage/{query_builders,query_registry,query_sql,graded_orbit,jea_rigcat,jea_agdai,jea_pysim,
jea_pyalg,jea_cuda,jea_extrude_ir,jea_grammar_fixpoint,jea_haskell_trace,jea_ir_unify,jea_mat260_verify,
jea_octave_gen,jea_omml,jea_omml_octave,jea_omml_render,jea_picircuit,jea_seam_provenance,jea_sppf_torsor,
jea_sympy_bridge,spectral_view}.py;
jea/{jea_agda_bridge,jea_agda_dag,jea_agda_voucher,jea_bitkernel,jea_branchless,jea_carrier,
jea_carrier_base,jea_check,jea_circuit,jea_core,jea_cost,jea_dag_gen,jea_divstr,jea_edge_states,
jea_engine,jea_eval,jea_generator_dag,jea_generator_strat,jea_generator_unified,jea_graded,jea_limb_gpu,
jea_mega,jea_mega_eval,jea_navigator,jea_omml_domain,jea_oneforest,jea_onegraph,
jea_parity_species_probe,jea_resident,jea_strictify_gcalc,jea_strictify_kirchhoff,jea_strictify_rotation,
jea_trace_window,jea_zsppf}.py;
el-atlas/tools/{live_dispatcher,perf_graph_integrated,kron_reduction,thermal_gate,topology_breakers,
aspm_link,dma_path,dmi_intern,host_probe,host-topology-nedge-pilot,igpu_contention,kirchhoff_nedge}.py
(via _TOOLS, Λ8b path only). Regression SLOW list (--full only) not pinned.

Baselines: scripts/{set1_baseline_cores,cap_ratchet_baseline,carrier_locality_baseline,
sumtype_ratchet_baseline,public_ratchet_baseline}.txt; scratch/sppf_collision_index.md (read vs named: [inferred]).
check_import_shape has no baseline file.
worklist.py literal reads [inferred]: CLAUDE.md, jea/metalanguage/SEAM_PARTITION.md,
jea/metalanguage/BEZOUT_READOUT.md, scratch/commuting_sphere.md, scratch/omega4_reflex_sweep.md.
Gate OUTPUTS (written + git-added, not inputs): catalog/reuse-index.md, reuse-graph.{dot,md},
reuse-sitemap.xml, usage-stats.md, import-graph.{dot,md}.

## External dependencies (named, not pinned)
system python3; make/bash/git/coreutils; agda 2.8.0 on PATH past the shim; cupy/sympy/CUDA (checks
SKIP with exit 0 when absent); systemd-run --user or writable cgroup (membudget refuses otherwise);
membudget ledger ($MEMBUDGET_FILE or ~/.cache/membudget/budget.cotype); gitignored agda/.agda-times.tsv,
.agda-profile.tsv; agda/_build/2.8.0 cores; .full-build-stamp (7-day throttle); catalog/catalog.db;
untracked binary jea/metalanguage/agdai_shim; staged index; env: _PRECOMMIT_TEE, AGDA_MB,
MEMBUDGET_*, SPPF_CATALOG_DB, DECODE_COST_LEDGER, CUDA_PATH, DMI_DUMP, PATH, TMPDIR, HOME.
No postgres found in sppf_db.py / query_builders.py at this commit (fact about two files searched).

## Gaps (block "run the original gate against the merge tree as data")
1. The gate reads its OWN location: ROOT from BASH_SOURCE / __file__ / git rev-parse. Pinned files
   must be OVERLAID INTO the tree under test, not run beside it.
2. agda/Makefile and agda/Flat.mk:12 hard-code SHIM_DIR := /home/mikemol/github/substrate/scripts/agda-shim,
   so another checkout runs the LIVE shim; gen_build_makefiles --check depends on checkout location [inferred].
3. sys.path inserts and _TOOLS computed paths (listed in the oracle's report with file:line).
4. Bare-name subprocess module lists (jea_regression_gate.py:18,20,25; check_scratch_runtime.py:72,75).
5. os.walk/glob populations over the data tree decide each gate's coverage.
6. worklist.py --check evaluates arbitrary predicates: full read set unknown.
7. agdai_shim binary is a build product the manifest cannot pin.
8. Λ8b/regression gates exit 0 without cupy: pinned != executed on a GPU-less host.

## Findings for the rebuilt gate (the frozen original stays unedited)
- F1. The original hook's refusal line advertises its own evasion: "pre-commit: one or more checks
  failed; commit aborted (use --no-verify to override)." (probe log blob 5081ff18, line 11829). The
  fleet refuses --no-verify; the rebuilt gate drops the advice (gcalculus removed the same line
  2026-11-16). Raised by github-cb.
