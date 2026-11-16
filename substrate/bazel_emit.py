# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Emit bazel BUILD targets for the Agda tree, from the SAME model `make_emit` reads.

⚑⚑⚑ THIS IS THE PROOF THAT THE SEAM IS REAL. `agda_dag` (the import graph) and `build_targets`
(the gate roster) were extracted on the claim that they are backend-INDEPENDENT — that a
different build system reads them unchanged and only the emitter is replaced. A claim like that
is cheap until a second emitter exists; this is the second emitter, and it imports neither
`make_emit` nor anything make-shaped.

⚑⚑ AND THE TWO EMITTERS SHARE NO CODE, DELIBERATELY. A common base class would be the wrong
abstraction: make and bazel disagree about almost everything at the grammar level (tabs vs
parentheses, mtime vs content hashing, phony targets vs no such concept), and the ONE thing they
share is the model, which is already shared. Factoring their differences into a hierarchy would
manufacture coupling the migration exists to remove.

⚑ WHAT BAZEL CHANGES ABOUT THE BUILD, stated rather than assumed. Staleness becomes
content-hashed rather than mtime-based, so the makefile's `&& touch $@` — which exists to align
make's mtime model with agda's content-hash interface validity — has no counterpart rather than
a translation. There is no `.PHONY`, so the gate roster becomes test targets, a different shape
and not a rename.

⚑⚑ NOTHING HERE IS WIRED INTO A BUILD, AND THAT IS THE HONEST STATE. This emits text. Whether
the emitted text builds the tree is UNMEASURED — no bazel is installed in this checkout and no
workspace exists — so the module states what it produces and refuses to imply more. A generator
whose output nobody has run is a HYPOTHESIS about a build, and calling it a migration would be
the demo-proven-wired defect exactly.
"""

from __future__ import annotations

from substrate import agda_dag

# The rule symbol each module's target uses. ⚑ NOT DEFINED HERE — an emitter writes call sites;
# the rule implementation is a `.bzl` file and a separate decision.
RULE = "agda_module"

# Where the generated targets declare their sources from, relative to the workspace root.
PACKAGE = "//agda"

# ⚑ THE COMPILE FLAGS, CARRIED FROM THE MAKEFILE'S OWN CONTRACT (`AGDA_FLAGS ?= --safe
# --without-K`). Read from the live rule rather than retyped: `make_rules --target` on any
# module shows the invocation, and these are the flags it passes.
FLAGS = ("--safe", "--without-K")

# ⚑⚑⚑ WHAT THIS EMITTER DOES NOT KNOW, NAMED IN THE OUTPUT RATHER THAN OMITTED. Each is a real
# design decision the migration must make, and a generator that silently picked one would bury
# the choice in emitted text nobody reviews as a decision.
UNRESOLVED = (
    # ⚑⚑⚑ THIS ENTRY ONCE ENDED *"and the two together would double-bound"*, AND THAT WAS
    # MEASURED FALSE — by a peer, against their own live bazel build, while this text was being
    # emitted into every generated file. `resource_set` is a SCHEDULING HINT: it tells bazel how
    # many actions may run at once and BOUNDS NONE OF THEM. So there was never a double-bound to
    # fear, and the half I filed as undecided is decided in membudget's favour: bazel SCHEDULES,
    # cgroups BOUND, and the semaphore remains the only enforcement layer.
    #
    # ⚑⚑ THE CORRECTION IS KEPT IN THE ENTRY RATHER THAN SWAPPED SILENTLY, because this text is
    # the emitter's statement of what it does not know — and a wrong entry that quietly becomes a
    # right one teaches the next reader that these strings are opinions. What it does not know is
    # now NARROWER and stated as such.
    (
        "the memory cap: `+RTS -M` binds the GHC heap per module while bazel's resource model only "
        "SCHEDULES concurrency — measured, `resource_set` bounds nothing — so membudget's cgroup "
        "remains the enforcement layer and what is undecided is how the two are WIRED, not which "
        "one governs"
    ),
    (
        "the interface tree: make writes `_build/<ver>/agda/<Mod>.agdai` and agda resolves "
        "imports by searching it, which is a shared mutable directory a sandbox does not "
        "provide for free"
    ),
    (
        "the stamp chain: `.ingested`/`.promoted`/`.drained` hang off `.agdai` as real files "
        "carrying store state, and a stamp is a claim about postgres held on the filesystem — "
        "which is what a hermetic build model refuses"
    ),
)


def target_name(module: str) -> str:
    """Return the bazel target name for a module.

    ⚑ DOTS BECOME UNDERSCORES because a bazel label may not contain a dot in its name, while an
    Agda module name is dot-separated by construction. The mapping must be INJECTIVE or two
    modules collide into one target, so a case checks it rather than assuming it.
    """
    return module.replace(".", "_")


def source_label(rel: str) -> str:
    """Return the workspace label for a source relpath."""
    return f"{PACKAGE}:{rel}"


def rule_for(module: str, dag: agda_dag.Dag) -> list[str]:
    """Render one module's rule call, with its direct imports as deps."""
    deps = sorted(target_name(d) for d in dag.deps.get(module, frozenset()))
    flags = ", ".join(f'"{flag}"' for flag in FLAGS)
    out = [
        f"{RULE}(",
        f'    name = "{target_name(module)}",',
        f'    src = "{dag.disk[module]}",',
    ]
    if deps:
        out.append("    deps = [")
        out.extend(f'        ":{dep}",' for dep in deps)
        out.append("    ],")
    out.append(f"    flags = [{flags}],")
    out.append(")")
    return out


def header() -> list[str]:
    """Render the file header, including what this emitter does not resolve.

    ⚑⚑ THE UNRESOLVED LIST IS EMITTED INTO THE FILE, not kept in this module's docstring. A
    reader of generated output should not have to find the generator to learn that three design
    questions are open — the bounds-in-band discipline, applied to a build file.
    """
    out = [
        "# GENERATED by substrate/bazel_emit.py — do not edit.",
        "#",
        "# Emitted from the SAME model the make backend reads (`substrate/agda_dag.py`).",
        "# The import graph is source-parsed from `open import`, so it is a sound SUPER-SET",
        "# of the build's real dependencies.",
        "#",
        "# ⚑ UNRESOLVED — this generator does not decide these, and the emitted graph is",
        "#   correct about IMPORTS while silent about all three:",
    ]
    out.extend(f"#   * {line}" for line in UNRESOLVED)
    out.append("")
    out.append(f'load("//bazel:agda.bzl", "{RULE}")')
    out.append("")
    return out


def build_text(dag: agda_dag.Dag) -> str:
    """Render the whole BUILD file for the parsed tree."""
    out = header()
    for module in sorted(dag.disk):
        out.extend(rule_for(module, dag))
        out.append("")
    return "\n".join(out)


USAGE = """\
bazel_emit.py — emit bazel BUILD targets for the Agda tree.

  bazel_emit.py --build     the BUILD file for the whole tree
  bazel_emit.py --sample    the first few rules, to read the shape
  bazel_emit.py --open      what this emitter does NOT resolve
  bazel_emit.py --selftest  the cases

⚑ NOTHING HERE IS WIRED INTO A BUILD. This emits text. Whether the text builds the tree is
  UNMEASURED — there is no workspace and no bazel in this checkout — so the emitted file names
  its own open questions rather than implying they are settled.
"""


def build_mode() -> str:
    """Render the whole BUILD file from a fresh parse."""
    return build_text(agda_dag.parse())


def sample_mode() -> str:
    """Render a few rules, so the shape can be read without the whole tree."""
    dag = agda_dag.parse()
    out = header()
    for module in sorted(dag.disk)[:3]:
        out.extend(rule_for(module, dag))
        out.append("")
    out.append(f"# … {len(dag.disk)} module(s) total; --build for all of them")
    return "\n".join(out) + "\n"


def open_mode() -> str:
    """Render the design questions this emitter leaves undecided."""
    out = ["what this emitter does NOT resolve:"]
    out.extend(f"  * {line}" for line in UNRESOLVED)
    out.append("")
    out.append("  ⚑ the emitted graph is correct about IMPORTS and silent about these.")
    return "\n".join(out) + "\n"


MODES = {
    "--build": build_mode,
    "--sample": sample_mode,
    "--open": open_mode,
}


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code."""
    import sys  # noqa: PLC0415 — kept local so importing this module costs nothing

    if "--selftest" in argv:
        from substrate import bazel_emit_selftest  # noqa: PLC0415

        return 0 if bazel_emit_selftest.selftest() else 1

    flags = [a for a in argv[1:] if a.startswith("--")]
    mode = MODES.get(flags[0]) if flags else None
    if mode is None:
        sys.stdout.write(USAGE)
        return 2

    sys.stdout.write(mode())
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
