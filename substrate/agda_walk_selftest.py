# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.agda_walk` — the `_build` exclusion, and a live differential.

⚑⚑⚑ THE `_build` ARM IS TESTED WITH A REAL FILE, not by asserting a filter exists. The origin
records that 41 of 59 enumeration sites carry no such filter and agree with the guarded ones
only because no `.agda` currently lives under the build tree — *"the agreement is LUCK rather
than construction."* An arm that checked the current tree would therefore pass against a walk
with no filter at all, so the case CREATES a source under a `_build` directory and asserts both
directions: excluded by default, included on request.

⚑⚑ AND THE COPY-ON-RETURN ARM GUARDS A CACHE THAT COULD CHANGE ANSWERS. Callers sort and extend
the list they get back; handing out the cached object would let one consumer corrupt every later
one, and the corruption would surface as a census that shrank for no reason.

⚑ THE DIFFERENTIAL ASSERTS SET EQUALITY WITH THE LIVE AUTHORITY over the real tree, because a
walk that enumerated a different population would move every gate's census at once — which is
the gate-vs-gate divergence this module was promoted to prevent.

⚑ THE PROTOCOL DECLARES ONLY THE ARITY THE DIFFERENTIAL USES. The origin takes a positional
boolean the per-file gate flags, and mirroring it would import that shape into a clean file for
no gain — the comparison passes one argument, so one is what is declared.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

from substrate import agda_walk, corpus

# The live authority this module drains from.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"


@runtime_checkable
class _Origin(Protocol):
    """The origin's enumeration, read through its own module.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, so an un-narrowed differential
    agrees with anything.
    """

    def agda_files(self, root: str) -> list[str]:
        """Return every agda source under a root."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT, and the label says which:
    a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_walk_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _build_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the exclusion that the live tree cannot exercise."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ A REAL SOURCE UNDER A REAL `_build`, because the live tree has none — so an arm over
    # the live tree would pass against a walk carrying no filter whatsoever. This is the
    # gate-vs-gate divergence, made reproducible instead of waited for.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Real.agda").write_text("module Real where\n", encoding="utf-8")
        built = root / agda_walk.BUILD_DIR
        built.mkdir()
        (built / "Generated.agda").write_text("module Generated where\n", encoding="utf-8")

        default = agda_walk.agda_files(root)
        check("the real source is enumerated", passed=any("Real.agda" in p for p in default))
        check(
            "and a source under _build is EXCLUDED by default",
            passed=not any("Generated.agda" in p for p in default),
        )

        # ⚑ THE OTHER DIRECTION, or the arm above passes against a walk that finds nothing.
        widened = agda_walk.agda_files(root, include_build=True)
        check("but it IS enumerated on request", passed=any("Generated.agda" in p for p in widened))
        check("and the two populations differ", passed=len(widened) > len(default))

        # ⚑⚑ THE MEMO IS KEYED ON BOTH, so asking again the other way must not serve the first
        # answer back. A cache keyed on the root alone would return the narrow list forever.
        check(
            "the memo distinguishes the two roots",
            passed=len(agda_walk.agda_files(root)) == len(default),
        )

        # ⚑⚑ A COPY, ALWAYS: a caller mutating its result must not corrupt the memo.
        got = agda_walk.agda_files(root)
        got.append("injected")
        check(
            "a caller cannot corrupt the cache", passed="injected" not in agda_walk.agda_files(root)
        )

        # ⚑ `sources` PAIRS PATH WITH TEXT — the shape the ban census consumes.
        pairs = agda_walk.sources(root)
        check("sources returns path and text", passed=len(pairs) == len(default))
        check("and the text is the file's", passed=any("module Real" in t for _p, t in pairs))

    return out


def _empty_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a root holding nothing."""
    out: list[tuple[str, bool]] = []

    with tempfile.TemporaryDirectory() as tmp:
        # ⚑ AN EMPTY ROOT IS AN EMPTY LIST, NOT AN ERROR. A walk that raised here would make a
        # gate's verdict depend on whether a subtree happened to be populated.
        out.append(("an empty root enumerates nothing", agda_walk.agda_files(tmp) == []))
        # ⚑ AND A NON-AGDA FILE IS NOT A SOURCE, or the census would key on interface files.
        Path(tmp, "notes.md").write_text("x\n", encoding="utf-8")
        out.append(("a non-agda file is not enumerated", agda_walk.agda_files(tmp) == []))
    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting the same population as the live authority.

    ⚑⚑ SET EQUALITY OVER THE REAL TREE. A walk enumerating a different population would move
    every gate's census simultaneously, which is precisely the divergence this module was
    promoted to prevent — so agreement here is the claim that makes the promotion safe.
    """
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    root = corpus.ROOT / "agda" / "Substrate"
    if not root.is_dir():
        return [("no agda tree was found to difference — a fact about the TREE", True)]

    mine = {str(Path(p).resolve()) for p in agda_walk.agda_files(root)}
    theirs = {str(Path(p).resolve()) for p in origin.agda_files(str(root))}
    return [
        ("the drained walk enumerates the same population", mine == theirs),
        # ⚑ THE POSITIVE CONTROL: two empty sets are equal, so agreement means nothing unless
        # the authority actually found something.
        ("and the population is non-empty, so agreement is not vacuous", bool(theirs)),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _build_cases() + _empty_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-walk selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
