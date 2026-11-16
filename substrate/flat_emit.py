# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Emit `agda/Flat.mk` — the flat import-DAG makefile — from the graph model (⟡promote-path A).

⚑⚑⚑ WHY THIS EXISTS: THE CHAIN MUST TAKE A TENANT, AND THE ORIGIN CANNOT BE EDITED.
`gen_build_makefiles.flat_text` emits `.agdai → .ingested → .promoted → .drained` with `--live`
hard-coded and a bare `python3` that bypasses `store_launch`. The operator chose to parameterize
that chain rather than keep a second build path for the sandbox (t102). The origin carries 292
findings, so the per-file gate refuses even a one-line edit; the emitter is therefore DRAINED
here, faithfully first, and parameterized in a second, separately-cased step.

⚑⚑ FAITHFUL FIRST, AND A PROGRAM SAYS SO. The suite's first case is differential: with the origin's
own graph and constants this module's output must equal the committed `agda/Flat.mk` byte for
byte. A port that "looks equivalent" is a rewrite wearing a refactor's clothes; only the diff can
say which it is. ⚑ Long emitted lines are split into PARENTHESISED adjacent literals, which Python
joins at compile time — the bytes are unchanged, and the differential is what proves it.

⚑ THE CONSTANTS ARE INPUTS, NOT RESTATEMENTS. `MEM_CAP`, the shim directory, the membudget path and
the build version belong to the origin until step 3 drains them; `Settings` carries them in, so
this module holds no second copy of a build figure.

⚑ THE GRAPH IS A `Dag`. Acyclicity is `agda_dag.topo`'s verdict, returned rather than exited, so a
cycle refuses with its members named instead of killing the caller.
"""

from __future__ import annotations

from dataclasses import dataclass

from substrate import agda_dag


class CycleError(ValueError):
    """The import graph has a cycle, so no makefile can order it."""


@dataclass(frozen=True, slots=True)
class Settings:
    """The build figures the makefile embeds — read from their owner, never typed here."""

    marker: str
    shim_dir: str
    membudget: str
    mem_cap: str
    ver: str
    #: False renders the origin's makefile exactly (the differential's mode); True renders the
    #: tenant-parameterized chain (⟡promote-path A).
    parameterized: bool = False


_HEADER = (
    (
        "# ⟡make-import-dag: SINGLE flat makefile. REAL-FILE target — "
        "each _build/<ver>/agda/<Mod>.agdai"
    ),
    (
        "# depends on its own .agda source AND the .agdai of every module it imports "
        "(SOURCE-PARSED from"
    ),
    (
        "# `open import`/`import`, NOT catalog.db). make tracks staleness by mtime over "
        "the EXPLICIT import"
    ),
    (
        "# DAG: a warm build is a near-instant mtime check; a change rebuilds only the "
        "affected subtree;"
    ),
    "# `make -j` runs the frontier concurrently. `&& touch $@` aligns make's mtime with agda's",
    (
        "# content-hash interface validity. Invoked from agda/. "
        "Regenerate: scripts/gen_build_makefiles.py."
    ),
    "",
)

_SHIM_NOTE = (
    (
        "# membudget agda-shim → make is the controlled+instrumented build path "
        "(RAM-budgeted + proof-cost"
    ),
    (
        "# profiled). Idempotent (findstring); exported to recipes + sub-makes. "
        "MEMBUDGET_NOPROFILE=1 to skip"
    ),
    "# profiling; `make AGDA=…` to pin a different agda.",
)

_STAMPS = (
    "AGDAI := $(patsubst %,$(BUILD)/%.agdai,$(subst .,/,$(MODULES)))",
    "INGESTED := $(AGDAI:.agdai=.ingested)",
    "PROMOTED := $(AGDAI:.agdai=.promoted)",
    "DRAINED := $(AGDAI:.agdai=.drained)",
    "SOURCED := $(AGDAI:.agdai=.sourced)",
    "ITARGETS := $(MODULES:%=i/%)",
    "",
    (
        ".PHONY: all check-sync sourced ingest promote drain reconcile clean "
        "$(MODULES:%=m/%) $(ITARGETS)"
    ),
    "",
    "all: check-sync $(AGDAI) $(PROMOTED)",
    "",
)

_CHECK_SYNC = (
    "# Blow up if the on-disk .agda set differs from the generated MODULES (new/removed file →",
    "# regenerate). Both sides normalised through newline-list + drop-empties + sort.",
    "check-sync:",
    "\t@disk=`find Substrate -name '*.agda' | sed 's#/#.#g; s#\\.agda$$##' | sort`; \\",
    "\t listed=`printf '%s\\n' $(MODULES) | tr ' ' '\\n' | sed '/^$$/d' | sort`; \\",
    '\t if [ "$$disk" != "$$listed" ]; then \\',
    "\t   echo 'ERROR: on-disk .agda set differs from Flat.mk MODULES.'; \\",
    "\t   echo '  Run scripts/gen_build_makefiles.py.'; exit 1; \\",
    "\t fi",
    "",
    (
        "# ── compile: <Mod>.agdai : <Mod>.agda + <direct-import>.agdai ─ "
        "real file; touch aligns mtime ──"
    ),
)

_COMPILE = (
    "\t@$(AGDA) $(AGDA_FLAGS) +RTS -M$(MEM_CAP) -RTS -i $(AGDA_ROOT) $(AGDA_ROOT)/{src}"
    " > $@.log 2>&1 || {{ rc=$$?; cat $@.log >&2; exit $$rc; }}"
)

_CHAIN = (
    "# ── sourced: the ⟡ladder's tier-0 — <Mod>.sourced : <Mod>.agdai ──",
    "sourced: $(SOURCED)",
    "$(BUILD)/%.sourced: $(BUILD)/%.agdai",
    (
        "\t@$(MEMBUDGET) run auto ingest-source -- "
        "python3 $(SCRIPTS)/sppf_db.py --ingest-source $< --live --apply"
    ),
    "\t@touch $@",
    "# ── ingest: SPPF internment as a DEPENDENCY — <Mod>.ingested : <Mod>.agdai ──",
    "ingest: $(INGESTED)",
    "$(BUILD)/%.ingested: $(BUILD)/%.agdai",
    (
        "\t@$(MEMBUDGET) run auto ingest-core -- "
        "python3 $(SCRIPTS)/sppf_db.py --ingest-core $< --live --apply"
    ),
    "\t@touch $@",
    "# ── promote: the packing fold as a DEPENDENCY — <Mod>.promoted : <Mod>.ingested ──",
    "promote: $(PROMOTED)",
    "$(BUILD)/%.promoted: $(BUILD)/%.ingested",
    (
        "\t@$(MEMBUDGET) run auto promote-core -- "
        "python3 $(SCRIPTS)/sppf_db.py --promote-core $(@:.promoted=.agdai) --live --apply"
    ),
    "\t@touch $@",
    "# ── drain: the retire as a DEPENDENCY — <Mod>.drained : <Mod>.promoted ──",
    "drain: $(DRAINED)",
    "$(BUILD)/%.drained: $(BUILD)/%.promoted",
    (
        "\t@$(MEMBUDGET) run auto drain-core -- "
        "python3 $(SCRIPTS)/sppf_db.py --drain-core $(@:.drained=.agdai) --live --apply"
    ),
    "\t@touch $@",
    "reconcile:",
    (
        "\t@$(MEMBUDGET) run 256 reconcile-stamps -- "
        "python3 $(SCRIPTS)/sppf_db.py --reconcile-stamps $(BUILD)"
    ),
)

_TAIL = ("", "clean:", "\t@true", "")


#: The per-module stamp kinds whose names carry the tenant.
STAMP_KINDS = ("sourced", "ingested", "promoted", "drained")

#: Lines inserted after `SCRIPTS := …` in the parameterized makefile.
TENANT_BLOCK = (
    "TENANT ?= live",
    "$(if $(filter $(TENANT),live sandbox),,$(error TENANT must be live or sandbox))",
    "TSFX := $(if $(filter live,$(TENANT)),,.$(TENANT))",
    # ⚑ ABSOLUTE, via make's own `abspath`: a `../.venv/bin/python` launched from `agda/` makes
    # python warn that sys.prefix is not the venv it expected (measured t118).
    "PYTHON := $(abspath ../.venv/bin/python)",
    "STORE_RUN ?= $(PYTHON) -m substrate.store_launch $(SCRIPTS)/sppf_db.py",
)

#: ⚑⚑ THE TENANT-AWARE RECONCILE (t109), replacing a t107 `$(error)` guard. The old reconciler
#: (`sppf_decode._reconcile_over`) matches `*.ingested` alone and derives the core by stripping it,
#: so a sandbox reconcile would have judged every LIVE stamp against the SANDBOX store and deleted
#: nearly all of them; the guard refused it off-live until this existed.
#:
#: ⚑ THE TENANT-AWARE RECONCILE (t109). `substrate/stamp_reconcile_run` walks only the stamps whose
#: name ends in THIS tenant's suffix (`stamp_reconcile.stamp_suffix`, the one owner) and reads THIS
#: tenant's store through the clean connector — so a sandbox reconcile can no longer see, or delete,
#: a live stamp. It replaces `sppf_db --reconcile-stamps`, whose helpers hard-code `.ingested`.
RECONCILE_RECIPE = (
    "\t@$(MEMBUDGET) run 256 reconcile-stamps -- $(PYTHON) "
    "-m substrate.stamp_reconcile_run $(BUILD) --tenant $(TENANT) --apply"
)


def _tenantize(line: str) -> str:
    """Rewrite one chain line: tenant-suffixed stamps, the store_launch runner, the tenant flag."""
    for kind in STAMP_KINDS:
        line = line.replace(f"%.{kind}", f"%.{kind}$(TSFX)")
        line = line.replace(f".agdai=.{kind})", f".agdai=.{kind}$(TSFX))")
        line = line.replace(f"$(@:.{kind}=", f"$(@:.{kind}$(TSFX)=")
    return line.replace("python3 $(SCRIPTS)/sppf_db.py", "$(STORE_RUN)").replace(
        " --live ", " --$(TENANT) "
    )


def _agdai(src: str) -> str:
    """Return the `.agdai` target for a source relpath (`Substrate/…/X.agda`)."""
    return "$(BUILD)/" + src[: -len(agda_dag.SUFFIX)] + ".agdai"


def _preamble(mods: list[str], settings: Settings) -> list[str]:
    """Return every line before the per-module compile rules."""
    lines = _faithful_preamble(mods, settings)
    if not settings.parameterized:
        return lines
    at = lines.index("SCRIPTS := ../scripts") + 1
    return [*lines[:at], *TENANT_BLOCK, *(_tenantize(x) for x in lines[at:])]


def _chain(settings: Settings) -> list[str]:
    """Return the store-touching links, tenant-parameterized when asked."""
    if not settings.parameterized:
        return list(_CHAIN)
    out: list[str] = []
    for line in _CHAIN:
        if "--reconcile-stamps" in line:
            out.append(RECONCILE_RECIPE)
        else:
            out.append(_tenantize(line))
    return out


def _faithful_preamble(mods: list[str], settings: Settings) -> list[str]:
    """Return the origin's preamble, byte-for-byte."""
    return [
        settings.marker,
        *_HEADER,
        *_SHIM_NOTE,
        f"SHIM_DIR := {settings.shim_dir}",
        "ifeq (,$(findstring $(SHIM_DIR),$(PATH)))",
        "export PATH := $(SHIM_DIR):$(PATH)",
        "endif",
        f"MEMBUDGET := {settings.membudget}",
        "",
        "AGDA ?= agda",
        "AGDA_FLAGS ?= --safe --without-K",
        f"MEM_CAP ?= {settings.mem_cap}",
        "AGDA_ROOT := .",
        f"BUILD := _build/{settings.ver}/agda",
        "SCRIPTS := ../scripts",
        "",
        "MODULES := " + " ".join(mods),
        *_STAMPS,
        *_CHECK_SYNC,
    ]


def text(dag: agda_dag.Dag, settings: Settings) -> str:
    """Render `Flat.mk` for `dag` — refusing a cyclic graph rather than emitting a hang."""
    walked = agda_dag.topo(dag)
    if isinstance(walked, agda_dag.Cycle):
        raise CycleError(walked.message)
    mods = sorted(dag.disk)
    out = _preamble(mods, settings)
    for m in mods:
        src = dag.disk[m]
        pre = " ".join(_agdai(dag.disk[d]) for d in sorted(dag.deps[m]))
        out.append(f"{_agdai(src)}: $(AGDA_ROOT)/{src} {pre}".rstrip())
        out.append("\t@mkdir -p $(@D)")
        out.append(_COMPILE.format(src=src))
        out.append("\t@touch $@")
        out.append(f"m/{m}: {_agdai(src)}")
    out.append("")
    out.extend(_chain(settings))
    stamp = ".ingested$(TSFX)" if settings.parameterized else ".ingested"
    out.extend(f"i/{m}: {_agdai(dag.disk[m])[: -len('.agdai')]}{stamp}" for m in mods)
    out.extend(_TAIL)
    return "\n".join(out)


def from_origin(disk: dict[str, str], deps: dict[str, set[str]]) -> agda_dag.Dag:
    """Wrap the origin's `(disk, deps)` pair as a `Dag`, so both emitters read one graph."""
    return agda_dag.Dag(disk=dict(disk), deps={m: frozenset(v) for m, v in deps.items()})
