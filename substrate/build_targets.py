# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The build's invariant-check targets, DECLARED as data rather than spelled into make syntax.

⚑⚑⚑ THE ROSTER IS RESTATED THREE TIMES IN THE GENERATOR AND NOTHING RECONCILES THEM. In
`gen_build_makefiles.root_text` the same eleven gates appear in the `.PHONY` line, again in the
`check:` aggregate's prerequisites, and a third time as the recipe blocks themselves — three
hand-maintained lists whose only relationship is that a human typed them consistently. Adding a
gate means editing three places in a file the per-file gate refuses to let anyone edit; missing
one is silent, because a target absent from `.PHONY` still runs and a target absent from `check:`
simply never fires.

⚑⚑ AND THAT IS WHY THE ROSTER IS THE FIRST THING OUT. The emitters (`flat_text` at 392 lines,
`root_text` at 128) are make-SYNTAX and do not survive a backend change; this roster is the
build's POLICY and survives every backend. A bazel migration rewrites the emitter and reads this
unchanged — the same seam `agda_dag` cut for the import graph, one level up.

⚑ EACH ROW CARRIES ITS OWN RATIONALE, because the comment above a recipe is the only place the
build says WHY a gate exists, and a roster that dropped it would make the emitted makefile less
informative than the code it replaced. The comment is data here, not decoration.

⚑ THE COMMAND IS A LIST, NOT A STRING. A recipe is argv; keeping it as a list means the emitter
decides the quoting and a caller can ask what a gate RUNS without parsing shell.
"""

from __future__ import annotations

from dataclasses import dataclass

# The advisory target's name, which the aggregate deliberately excludes.
ADVISE = "advise"


@dataclass(frozen=True, slots=True)
class Target:
    """One make target: its name, the argv it runs, and why it exists."""

    name: str
    command: tuple[str, ...]
    why: tuple[str, ...]

    @property
    def is_blocking(self) -> bool:
        """Whether a failure refuses the build.

        ⚑ ADVISORY TARGETS ARE NOT A WEAKER GATE, THEY ARE A DIFFERENT KIND. Each has real
        false positives, so it informs and never refuses; folding them into `check` would train
        a reader to ignore a red build.
        """
        return self.name != ADVISE


# ⚑⚑ THE GATES, IN THE ORDER THE AGGREGATE RUNS THEM. Declared ONCE: the `.PHONY` line, the
# `check:` prerequisites and the recipe bodies are all DERIVED from this, so the three lists that
# used to drift are one list that cannot.
CHECKS = (
    Target(
        name="check-makefiles",
        command=("python3", "../scripts/gen_build_makefiles.py", "--check"),
        why=("Verify Flat.mk + the root Makefile are in sync with the source tree.",),
    ),
    Target(
        name="check-defproof",
        command=("../scripts/check_def_proof_separation.sh",),
        why=("Verify def/proof separation (definition-providers import no proof modules).",),
    ),
    Target(
        name="check-vacuity",
        command=("../scripts/check_up_nonvacuity.sh",),
        why=("Verify no vacuous (top-collapse) universal properties beyond the sanctioned two.",),
    ),
    Target(
        name="check-index",
        command=("python3", "../scripts/sppf_node_index.py", "--check"),
        why=("Verify the shape-node collision index is current (names to shapes, visible).",),
    ),
    Target(
        name="check-import",
        command=("python3", "../scripts/check_import_shape.py", "--quiet"),
        why=("Ratchet: no NEW bare imports of genuinely-ambiguous names (specialize by shape).",),
    ),
    Target(
        name="check-decltag",
        command=("python3", "../scripts/decl_shape_tag.py"),
        why=("Every genuinely-ambiguous declaration carries a visible shape tag.",),
    ),
    Target(
        name="check-carrier",
        command=("python3", "../scripts/check_carrier_locality.py", "--quiet"),
        why=("Canonical operators live in their carrier's home, one-per-file (no forks).",),
    ),
    Target(
        name="check-sumtype",
        command=("python3", "../scripts/check_sumtype_ratchet.py", "--quiet"),
        why=("Ratchet: duplicate type-declarations are DEBT (paydown-only); no NEW copy.",),
    ),
    # ⚑⚑⚑ THE MIGRATED GATE (⟡retire-public-origin). Its census and entry moved into the
    # package — `substrate/public_gate.py` replaces `scripts/check_public_ratchet.py`, which did
    # census + entry + selftest in one file behind `sys.path` mutation. Invoked as a MODULE from
    # the repo root, so the recipe never names where the checkout sits.
    #
    # ⚑⚑ AND THE REPLACEMENT SEES ONE VIOLATION THE ORIGIN CANNOT: `agda/Substrate.agda` is the
    # tree's top-level module, outside the enumeration root the origin scanned, and it carries a
    # wholesale re-export. A census that cannot reach a file reports a clean tree there.
    Target(
        name="check-public",
        command=("cd", "..", "&&", "python3", "-m", "substrate.public_gate", "--quiet"),
        why=(
            "Ratchet: a WHOLESALE `open ... public` re-export is DEBT (paydown-only) — module",
            "application COPIES, so it re-materializes the upstream API into every consumer.",
        ),
    ),
    Target(
        name="check-cap",
        command=("python3", "../scripts/check_cap_ratchet.py", "--quiet"),
        why=(
            "Ratchet: a module's elaboration PEAK over the cap is DEBT (paydown-only) — the",
            "census that lets MEM_CAP descend mechanically. SHARD/split/seal a new offender;",
            "never raise the cap.",
        ),
    ),
    Target(
        name="check-apex",
        command=("python3", "../scripts/law_motif_apex.py", "--check"),
        why=(
            "Apex gate: every relational law-motif (>=3 instances) must have a parametric",
            "apex (a parameterizable module, NOT an index). No baseline — build the apex.",
        ),
    ),
)

# ⚑ ADVISORY, AND DELIBERATELY OUTSIDE `check`. Judgment reports with real false positives.
ADVISORY = Target(
    name=ADVISE,
    command=("../scripts/check_file_sizes.sh",),
    why=(
        "ADVISORY (non-blocking): judgment reports, deliberately NOT in `check` /",
        "the hook (each has real false positives, so they inform, never gate):",
        "  * theorem-per-file pressure (signature counts)",
        "  * categorical grounding (domain algebraic modules w/ no Category dep)",
    ),
)


def names() -> tuple[str, ...]:
    """Return every blocking check target's name, in run order."""
    return tuple(target.name for target in CHECKS)


def by_name(name: str) -> Target | None:
    """Return one target by name, or None when nothing declares it."""
    for target in CHECKS:
        if target.name == name:
            return target
    return None
