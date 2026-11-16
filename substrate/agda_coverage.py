# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Which tracked `.agda` files are inside the tree's enumeration root — and which are not.

⚑⚑⚑ THREE INSTRUMENTS SHARE ONE ENUMERATION ROOT, SO THEIR AGREEMENT CARRIES NO COVERAGE.
`gen_build_makefiles.SRC`, the public-ratchet census (via `check_carrier_locality.agda_files`),
and the def-index all walk `agda/Substrate/`. A file outside that directory is invisible to all
three AT ONCE — not exempted by any of them, but outside their DOMAIN — and because they are
correlated, no amount of cross-checking one against another can surface it. Coverage is the
UNION of blind spots, and these three have the same one.

⚑⚑ MEASURED: `agda/Substrate.agda`, the tree's own top-level module, carries
`open import Substrate.Cocycle public` — a wholesale re-export the public ratchet exists to
forbid — and has never appeared in its baseline. It is tracked, has exactly one commit, and is
built by nothing: the flat makefile's generator walks the same subdirectory, so it is not a node
in the build DAG at all. A survivor of the pre-flat-DAG layout, stranded when the root moved.

⚑ AND NO COUNT COULD HAVE FOUND IT. The generator reports its module total as the length of its
own walk, so the figure reads identically whether the file exists or not. That is the shape a
census cannot self-detect: the population and the instrument are the same set.

⚑ THIS REPORTS, IT DOES NOT ADJUDICATE. A file outside the root may be dead source, a
deliberately unbuilt scratch module, or a real gap — and deciding which is a judgement with
consequences (deleting a tracked file, or widening three enumeration roots at once). The reader
names what is outside; an operator decides what that means.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from substrate import corpus

# The directory every current instrument walks. ⚑ NAMED HERE AS THE THING BEING TESTED, not
# borrowed from one of them: this module's whole job is to ask what that root excludes, so
# taking the value from a tool under test would make the answer trivially empty.
ENUMERATION_ROOT = "agda/Substrate"

# Where Agda source lives at all — the wider set the root is a subset of.
AGDA_DIR = "agda"

# ⚑ THE BUILD'S OWN OUTPUT IS NOT SOURCE. `_build` holds generated artifacts; counting them as
# uncovered source would report the build directory as a coverage gap on every machine.
SKIP_PARTS = frozenset({"_build"})


def tracked_agda() -> list[str]:
    """Return every tracked `.agda` path under the agda directory, repo-relative.

    ⚑ TRACKED, NOT PRESENT ON DISK. An untracked file is a working-tree artifact — a scratch
    experiment, a half-finished split — and reporting it as an uncovered module would make this
    reader noisy exactly when someone is mid-edit. What matters is what the repo CARRIES.
    """
    proc = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
        ["git", "ls-files", "--", AGDA_DIR],  # noqa: S607 - resolved via PATH by design
        cwd=corpus.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return sorted(
        line
        for line in proc.stdout.splitlines()
        if line.endswith(".agda") and not SKIP_PARTS.intersection(Path(line).parts)
    )


def outside_root(root: str = ENUMERATION_ROOT) -> list[str]:
    """Return the tracked `.agda` files that `root` does not contain.

    ⚑ THE ANSWER IS EXPECTED TO BE SMALL AND MUST NOT BE EMPTY BY CONSTRUCTION. A reader that
    took its root from the instrument it audits would always return nothing and would look like
    a passing check — the false-green shape this whole family refuses.
    """
    prefix = f"{root}/"
    return [p for p in tracked_agda() if not p.startswith(prefix)]


def covered(root: str = ENUMERATION_ROOT) -> list[str]:
    """Return the tracked `.agda` files that `root` does contain."""
    prefix = f"{root}/"
    return [p for p in tracked_agda() if p.startswith(prefix)]


def render(root: str = ENUMERATION_ROOT) -> str:
    """Render the coverage reading: what the enumeration root omits."""
    missed = outside_root(root)
    inside = covered(root)
    out = [
        f"enumeration root: {root}",
        f"  tracked .agda inside:  {len(inside)}",
        f"  tracked .agda OUTSIDE: {len(missed)}",
    ]
    if not missed:
        out.append("  ⚑ every tracked module is inside the root.")
        return "\n".join(out) + "\n"
    out.append(
        "  ⚑ INVISIBLE to the build generator, the ratchet censuses, and the "
        "def-index — all three walk this root:"
    )
    out.extend(f"      {p}" for p in missed)
    out.append(
        "  ⚑ A file outside the root is not EXEMPT from a gate; it is outside that "
        "gate's DOMAIN, which no count of the root can distinguish from clean."
    )
    return "\n".join(out) + "\n"
