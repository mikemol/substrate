# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Emit the thin root `agda/Makefile`, faithfully and then tenant-parameterized.

⚑⚑⚑ DRAINED FROM `gen_build_makefiles.root_text` (⟡promote-path A, step 3). The origin carries
292 findings and the per-file gate refuses every edit, so the root emitter moves here. As with
`flat_emit`, the FAITHFUL mode comes first and a differential case holds it to the working-tree
`agda/Makefile` byte for byte; only then does a second mode change anything.

⚑⚑ THE FAITHFUL MODE IS A LITERAL PORT, NOT `make_emit.gate_section`. `make_emit` derives the gate
section from `build_targets`, and its own docstring records that the origin's `check:` aggregate
and recipe blocks list the gates in DIFFERENT orders. A roster-derived section therefore cannot
reproduce today's file, and using it here would make the differential fail on a known, intended
reordering and hide any unintended change behind it.

⚑ Two emitted characters (DOWN TACK and GREATER-THAN OR EQUAL TO) are written as named unicode
escapes, because ruff's ambiguous-character rule reads them as typos. The emitted bytes are
identical; the escape states that the character is meant.

⚑ THE PARAMETERIZED MODE changes exactly three things:
  · `TENANT ?= live` after the shim block, exported and guarded to `live|sandbox`;
  · `reconcile` runs for EITHER tenant, because `Flat.mk`'s reconcile is now tenant-aware
    (`stamp_reconcile_run`), so the root has no live-only step left to fence;
  · `catalog` (a batched store WRITE that names no tenant) runs through `store_launch` on the
    project venv for live, and REFUSES off-live: it states no tenant a sandbox run could honour.
"""

from __future__ import annotations

from substrate import build_settings

_TOP = (
    (
        "# Top-level entry: per-file, memory-confined Agda build. `all` delegates to the flat "
        "import-DAG"
    ),
    (
        "# makefile (Flat.mk); root-only invariant/catalog/advise targets live here. Correctness "
        "is Agda's"
    ),
    (
        "# (transitive re-check); make bounds RAM + orders by import DAG. See "
        "scripts/gen_build_makefiles.py."
    ),
    "",
)

_PHONY = (
    ".PHONY: all clean shim catalog sourced promote drain reconcile check check-makefiles "
    "check-defproof check-vacuity check-index check-import check-decltag check-carrier "
    "check-sumtype check-public check-cap check-apex advise"
)

_DELEGATES = (
    "all:",
    "\t@$(MAKE) -f Flat.mk reconcile",
    "\t@$(MAKE) -f Flat.mk all",
    "# Delete every ingest stamp the store's own `core_fp` token does not back (ONE query).",
    "reconcile:",
    "\t@$(MAKE) -f Flat.mk reconcile",
    "clean:",
    "\t@$(MAKE) -f Flat.mk clean",
    (
        "# ⟡gqs-catalog-engine: (re)build the .agdai shim (iff agdai_shim.hs changed) + "
        "catalog.db from the"
    ),
    (
        '# interned SPPF. `catalog` = the BATCHED controller/actuator build (sppf_db ""): ONE '
        "process models the"
    ),
    (
        "# topology once, then rides the decode-parallelism roofline INTERNALLY — per window it "
        "co-reads the LIVE"
    ),
    (
        "# contention and decodes via a ThreadPool of shim subprocesses sized to the free CPU "
        "(interner+DB insert"
    ),
    (
        "# serial → NO python-spawn tax), self-skipping unchanged cores. Cheaper than per-core "
        "`make -f Flat.mk"
    ),
    (
        "# ingest' for the common incremental case (no spawn tax) and it self-parallelizes the "
        "full rebuild."
    ),
    "shim:",
    "\t@$(MAKE) -C ../jea/metalanguage shim",
    "catalog: shim",
)

CATALOG_FAITHFUL = '\t@$(MEMBUDGET) run 1024 catalog -- python3 ../scripts/sppf_db.py "" --argperm'

_PASSTHROUGH = (
    "sourced:",
    "\t@$(MAKE) -f Flat.mk sourced",
    "promote:",
    "\t@$(MAKE) -f Flat.mk promote",
    "drain:",
    "\t@$(MAKE) -f Flat.mk drain",
)

_GATES = (
    "# Aggregate invariant GATE (same checks the pre-commit hook runs):",
    "# def/proof separation + makefile-tree sync + UP non-vacuity + shape index. Blocking.",
    (
        "check: check-defproof check-makefiles check-vacuity check-index check-import "
        "check-decltag check-carrier check-sumtype check-public check-cap check-apex"
    ),
    "\t@echo 'all invariant checks passed.'",
    "# Verify Flat.mk + the root Makefile are in sync with the source tree.",
    "check-makefiles:",
    "\t@python3 ../scripts/gen_build_makefiles.py --check",
    "# Verify def/proof separation (definition-providers import no proof modules).",
    "check-defproof:",
    "\t@../scripts/check_def_proof_separation.sh",
    (
        "# Verify no vacuous (\N{DOWN TACK}-collapse) universal properties outside the "
        "sanctioned two."
    ),
    "check-vacuity:",
    "\t@../scripts/check_up_nonvacuity.sh",
    "# Verify the shape-node collision index is current (names→shapes, visible).",
    "check-index:",
    "\t@python3 ../scripts/sppf_node_index.py --check",
    "# Ratchet: no NEW bare imports of genuinely-ambiguous names (specialize by shape).",
    "check-import:",
    "\t@python3 ../scripts/check_import_shape.py --quiet",
    "# Every genuinely-ambiguous declaration carries a visible shape tag.",
    "check-decltag:",
    "\t@python3 ../scripts/decl_shape_tag.py",
    "# Canonical operators live in their carrier's home, one-per-file (no forks/buckets).",
    "check-carrier:",
    "\t@python3 ../scripts/check_carrier_locality.py --quiet",
    "# Ratchet: duplicate type-declarations are DEBT (paydown-only); no NEW forked copy.",
    "check-sumtype:",
    "\t@python3 ../scripts/check_sumtype_ratchet.py --quiet",
    "# Ratchet: a WHOLESALE `open … public` re-export is DEBT (paydown-only) — module",
    "# application COPIES, so it re-materializes the upstream API into every consumer.",
    "check-public:",
    "\t@python3 ../scripts/check_public_ratchet.py --quiet",
    "# Ratchet: a module's elaboration PEAK over 128MB is DEBT (paydown-only) — the census",
    (
        "# that lets MEM_CAP descend mechanically. SHARD/split/seal a new offender; never raise "
        "the cap."
    ),
    "check-cap:",
    "\t@python3 ../scripts/check_cap_ratchet.py --quiet",
    (
        "# Apex gate: every relational law-motif (\N{GREATER-THAN OR EQUAL TO}3 instances) "
        "must have a parametric"
    ),
    "# apex (a parameterizable module, NOT an index). No baseline — build the apex.",
    "check-apex:",
    "\t@python3 ../scripts/law_motif_apex.py --check",
    "# ADVISORY (non-blocking): judgment reports, deliberately NOT in `check` /",
    "# the hook (each has real false positives, so they inform, never gate):",
    "#   * theorem-per-file pressure (signature counts)",
    "#   * categorical grounding (domain algebraic modules w/ no Category dep)",
    "advise:",
    "\t@../scripts/check_file_sizes.sh",
    "\t@../scripts/check_categorical_grounding.sh",
    "",
)

#: Lines the parameterized mode inserts after the shim block (sub-makes inherit TENANT).
TENANT_BLOCK = (
    "TENANT ?= live",
    "export TENANT",
    "$(if $(filter $(TENANT),live sandbox),,$(error TENANT must be live or sandbox))",
    # ⚑ ABSOLUTE via make's `abspath` — a relative `../.venv` makes python warn about sys.prefix.
    "PYTHON := $(abspath ../.venv/bin/python)",
)

#: ⚑ `catalog` names no tenant, so off-live it refuses; on live it goes through store_launch,
#: which is what lets it reach luthen's tenant instead of the retired 127.0.0.1 listener.
CATALOG_PARAMETERIZED = (
    (
        "\t@$(if $(filter live,$(TENANT)),,$(error catalog writes the store with no tenant flag; "
        "live only))"
    ),
    (
        "\t@$(MEMBUDGET) run 1024 catalog -- $(PYTHON) -m substrate.store_launch "
        '../scripts/sppf_db.py "" --argperm'
    ),
)


#: ⚑ THE GENERATOR'S OWN CHECK RUNS ON THE VENV (operator, 2026-09-23): the generator is drained
#: into `substrate/`, which the system python3 cannot import from a script path.
CHECK_MAKEFILES_FAITHFUL = "\t@python3 ../scripts/gen_build_makefiles.py --check"
CHECK_MAKEFILES_VENV = "\t@$(PYTHON) ../scripts/gen_build_makefiles.py --check --parameterized"


def text(*, parameterized: bool = False) -> str:
    """Render the root `agda/Makefile`: the origin's exactly, or the tenant-parameterized one."""
    shim = build_settings.shim_block()
    tenant = list(TENANT_BLOCK) if parameterized else []
    catalog = list(CATALOG_PARAMETERIZED) if parameterized else [CATALOG_FAITHFUL]
    gates = [
        CHECK_MAKEFILES_VENV if parameterized and line == CHECK_MAKEFILES_FAITHFUL else line
        for line in _GATES
    ]
    return "\n".join(
        [
            build_settings.MARKER,
            *_TOP,
            *shim,
            *tenant,
            _PHONY,
            *_DELEGATES,
            *catalog,
            *_PASSTHROUGH,
            *gates,
        ]
    )
