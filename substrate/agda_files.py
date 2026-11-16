# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Enumerate the `.agda` sources under a root — THE enumeration authority, packaged.

⚑⚑⚑ THIS IS A PROMOTION OF `scratch/agda_lex.agda_files`, NOT A SECOND AUTHORITY. The origin
stays in place and keeps its attribute reads across the tree (`attr_reads agda_lex.*` is the
reader); what moves here is the one function that blocks the package. Operator ruling, this
tick: *"Promote agda_lex into substrate/"* — taken incrementally, the way `climode` was,
because the origin spans 37 definitions and hand-retyping a file nobody has read whole is the
silent-deletion shape with no guard (gate-G338).

⚑⚑ THE BLOCKER IS PACKAGING, AND IT IS MEASURED RATHER THAN ASSUMED. `substrate/
agda_tree_state.py` reached `agda_lex` by BARE name, which resolves only under a `sys.path`
insert into `scratch/`, and that is not a package. `adopter_import` reported the consequence
twice over: `agda_tree_state` failed outright, and `agda_census_run` failed TRANSITIVELY
through it, so one unpackaged name held two modules. The operator's standing ruling forbids
the cheap route (*"NOO. No sys.path modification."*), and an insert would hide the debt
rather than pay it.

⚑ WHY THIS FUNCTION AND NOT THE MODULE. `agda_tree_state` reads exactly one name from the
origin, and `agda_files` is self-contained: a tree walk, the suffix, and a private
per-process memo. Promoting it costs one file and releases two modules; promoting the module
costs a drain arc the size of `bibstruct`'s. The rest follows when its own consumers drain.

⚑⚑⚑ AND THE PER-FILE GATE REFUSED A TRANSCRIPTION, WHICH IS THE PROMOTION WORKING. The
origin is `os.path`-based with a positional boolean; ported verbatim it drew `PTH100`,
`FBT001` and `FBT002`. Reading those as obstacles would have produced a copy carrying the
origin's idiom into a package that does not want it — so the walk is `Path`-based and the
flag is keyword-only here. **That makes this a port rather than a copy, and a port must be
DIFFERENCED against its origin rather than believed**, which is what
`agda_files_selftest` does on the live tree.

⚑⚑ THE ORIGIN'S OWN ARGUMENT FOR EXISTING IS PRESERVED BELOW, because it is the reason this
is an authority rather than a convenience: four modules once defined `agda_files()` with
DIFFERENT BODIES, one filtering `_build` and sorting while another did neither, and it reads
as reuse at every call site.
"""

from __future__ import annotations

from pathlib import Path

# The Agda source extension. Named rather than spelled, because the origin measured the
# suffix strip written THREE ways across roughly 50 sites: a bare `[:-5]`, a
# `[:-len(".agda")]`, and `with_suffix`. The bare form carries a magic 5 that silently
# truncates a name if the extension ever changes.
SUFFIX = ".agda"

# The directory holding build artifacts, pruned from the walk unless a caller asks for it.
_BUILD = "_build"

# ⚑ MEMOISED PER (root, include_build) PER PROCESS. This is the SHARED NODE of the census
# DAG: eleven ratchet gates each walk the same tree, so the enumeration is fanned out from
# one root and was being recomputed once per consumer. Fixing it in the AUTHORITY fixes every
# consumer; fixing it in a gate would have fixed one, which is the whole argument for having
# an authority.
#
# ⚑ AND THIS IS WHY A THREAD POOL OVER THE GATES BOUGHT NOTHING. It measured slower than
# serial, because concurrency over an unbalanced DAG parallelises the fan-out while leaving
# the shared root duplicated. Dependency structure first, then parallelism over what actually
# remains independent; the two are not alternatives.
#
# Per-process and never invalidated: these tools are short-lived and read a tree nobody is
# editing mid-run. A long-lived caller that EDITS the tree would need invalidation, and would
# be a different kind of consumer.
_FILES_CACHE: dict[tuple[str, bool], list[str]] = {}


def agda_files(root: str, *, include_build: bool = False) -> list[str]:
    """Return every `.agda` source under `root`, sorted — THE enumeration authority.

    ⚑ MANY FILES ENUMERATE THE CORPUS THREE WAYS (`glob **`, a walk plus endswith, `rglob`)
    AND MOST OF THEM HAVE NO `_build` FILTER. That is harmless TODAY only because
    `agda/_build/` holds `.agdai` and zero `.agda`, so the agreement is LUCK rather than
    construction. The first `.agda` to land under `_build` (a fixture, a vendored copy, a
    generated module) splits the guarded routes from the unguarded ones, and since
    PRE-COMMIT GATES sit on the unguarded side their census inflates while the build
    generator's does not. A gate-versus-gate divergence, armed and waiting.

    ⚑ `root` IS THE PARAMETER, AND IT MATTERS: callers legitimately scope differently. Most
    pass `agda/Substrate`, while `iface_shape` passes `agda/`, which also catches the root
    aggregator `agda/Substrate.agda`. A subdirectory-scoped tool is a COMPLIANT CALLER with a
    narrower root, never an exception, which is what keeps the rederivation census honest
    rather than exemption-ridden.

    ⚑⚑ A SHARED NAME IS NOT A SHARED AUTHORITY. `agda_files()` was already defined FOUR times
    with DIFFERENT BODIES (`check_carrier_locality`, `check_claims`, `paydown`,
    `claim_census`), one filtering `_build` and sorting while another did neither, and it
    reads as reuse at every call site. This is the one to import.

    ⚑ THE ROOT IS AN ARGUMENT, RESOLVED ONCE AT THE BOUNDARY, NOT DISCOVERED HERE. Computing
    it from this file's `__file__` works only while the library sits inside the repo it
    operates on; installed from a package index it lands in site-packages, nowhere near the
    tree, and every path silently comes out wrong. That hazard is why this module is worth
    packaging at all, so reintroducing it here would defeat the move.

    ⚑⚑ THE RETURN IS `str`, NOT `Path`, AND THAT IS DELIBERATE. Every consumer of the origin
    takes strings, so returning `Path` would make the promotion a behaviour change wearing a
    move's clothes — the one thing a promotion must not be. The walk is `Path`-based because
    the gate asked for it; the SURFACE matches the authority it is promoting.
    """
    base = Path(root)
    key = (str(base.resolve()), include_build)
    if key in _FILES_CACHE:
        return list(_FILES_CACHE[key])
    found = (path for path in base.rglob(f"*{SUFFIX}") if include_build or _BUILD not in path.parts)
    # ⚑ A COPY IS RETURNED, ALWAYS. Callers mutate the list they get back (`files.extend(…)`,
    # sorting in place); handing out the cached object would let one consumer corrupt every
    # later one, and a cache that changes answers is worse than no cache.
    _FILES_CACHE[key] = sorted(str(path) for path in found)
    return list(_FILES_CACHE[key])
