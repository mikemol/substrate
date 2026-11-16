# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.swap_readiness` — including the file whose sizing it got wrong.

⚑⚑⚑ THIS READER SHIPPED WITH A DEFECT AND ONLY A LIVE RUN CAUGHT IT (gate-F78). Pointed at the
gate it was built to bless, it answered NOT READY: `from scripts import ratchet` records the
module as `scripts` with no dot, and a rule keyed on dots called the packaged spelling
unpackaged. No fixture I would have written first would have found that, because I would have
written the fixture from the same wrong model as the code.

⚑⚑ SO THE LOAD-BEARING ARMS ARE THE TWO LIVE GATES, IN OPPOSITE DIRECTIONS. One file was swapped
and must read READY; one defeated hand-sizing and must read NOT READY, naming the dependency a
per-module query could not see. Either arm alone is satisfiable by a stuck reader — one that
always passes, or one that always blocks — and a stuck reader is worse than none here, because
this is the instrument that decides which swap to attempt next.

⚑ THE FIXTURES COVER WHAT THE LIVE FILES CANNOT. UNKNOWN has no instance in this tree's gates,
and a local import inside a function has none either — both are real classifications, so both get
a constructed case rather than an untested branch.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, swap_readiness


def _probe(root: Path, name: str, body: str) -> Path:
    """Write a fixture module under a fixture repo and return its path."""
    path = root / "substrate" / name
    path.write_text(body, encoding="utf-8")
    return path


def _fixture_root(tmp: str) -> Path:
    """Build a miniature repo: a manifest, a package tree, and an unpackaged tree.

    ⚑ THE MANIFEST IS WHAT THE READER FINDS THE ROOT BY, so a fixture without one would make
    every classification depend on where the suite happened to run.
    """
    root = Path(tmp)
    (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (root / "substrate").mkdir()
    (root / "scratch").mkdir()
    (root / "scratch" / "agda_lex.py").write_text("x = 1\n", encoding="utf-8")
    return root


def _kind_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for how each import shape is classified."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_root(tmp)
        probe = _probe(
            root,
            "probe.py",
            "import os\n"
            "from substrate import corpus\n"
            "import substrate.corpus\n"
            "import agda_lex\n"
            "import nonesuch_distribution_xyz\n",
        )
        found = {d.name: d.kind for d in swap_readiness.deps_of(probe)}
        blocks = {d.name: d.blocks for d in swap_readiness.deps_of(probe)}

        check("a stdlib import is EXTERNAL", passed=found.get("os") == swap_readiness.EXTERNAL)

        # ⚑⚑⚑ BOTH QUALIFIED FORMS, because keying on the module string alone got this wrong.
        # `from X import Y` records `X` undotted and is nonetheless packaged.
        check(
            "a from-import of a package is PACKAGED",
            passed=found.get("substrate") == swap_readiness.PACKAGED,
        )
        check(
            "and a dotted import of the same package is too",
            passed=found.get("substrate.corpus") == swap_readiness.PACKAGED,
        )

        # ⚑⚑ THE SUBJECT: the same module by a BARE name resolves only under a path insert.
        check(
            "a bare name naming a tree module is UNPACKAGED",
            passed=found.get("agda_lex") == swap_readiness.UNPACKAGED,
        )

        # ⚑⚑⚑ THE THIRD OUTCOME, and it must BLOCK.
        check(
            "an unclassifiable name is UNKNOWN",
            passed=found.get("nonesuch_distribution_xyz") == swap_readiness.UNKNOWN,
        )
        check(
            "and UNKNOWN blocks a repoint", passed=blocks.get("nonesuch_distribution_xyz") is True
        )
        check("as does UNPACKAGED", passed=blocks.get("agda_lex") is True)

        # ⚑ THE CONTROLS: neither stdlib nor a packaged import may block, or every file reads
        # NOT READY and the reader says nothing at all.
        check("a stdlib import does not block", passed=blocks.get("os") is False)
        check("and a packaged import does not either", passed=blocks.get("substrate") is False)

    return out


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for import shapes the live gates do not exercise."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_root(tmp)

        # ⚑ A LOCAL IMPORT IS STILL A DEPENDENCY — a swap that missed one would fail only on
        # the branch that reaches it.
        local = _probe(root, "local.py", "def f() -> int:\n    import agda_lex\n    return 1\n")
        check(
            "an import inside a function is still found",
            passed=any(d.name == "agda_lex" for d in swap_readiness.deps_of(local)),
        )

        # ⚑ A RELATIVE IMPORT NAMES NO MODULE TO RESOLVE, so classifying it would report a fact
        # about nothing.
        rel = _probe(root, "rel.py", "from . import corpus\n")
        check("a relative import is not classified", passed=swap_readiness.deps_of(rel) == [])

        # ⚑⚑ AN UNPARSEABLE FILE YIELDS NOTHING, and the renderer says that is about the READER.
        # Returning an empty list that a caller reads as "no dependencies" would call a broken
        # file READY — the false green in the most dangerous direction.
        broken = _probe(root, "broken.py", "def (\n")
        check(
            "an unparseable file yields no dependency", passed=swap_readiness.deps_of(broken) == []
        )
        check(
            "and the report says that is about the reader",
            passed="fact about the READER" in swap_readiness.render("broken.py", []),
        )

        # ⚑ AND A MISSING FILE IS THE SAME, rather than raising into a caller's survey.
        check(
            "a missing file yields no dependency",
            passed=swap_readiness.deps_of(root / "substrate" / "absent.py") == [],
        )

    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the two live gates — the wrong sizing and the right one.

    ⚑⚑⚑ THESE ARE THE ARMS A FIXTURE CANNOT MAKE, and the reason is not convenience. A fixture
    is written from the same model as the code, so it agrees with a wrong model. These two files
    are what the model was WRONG ABOUT: one defeated hand-sizing by hiding a fifth dependency on
    its own import line, and the other was misread by this very reader's first cut.

    ⚑⚑ BOTH DIRECTIONS, OR THE VERDICT MEANS NOTHING. A reader stuck at READY blesses every
    swap; one stuck at NOT READY blocks every swap while looking rigorous. Only the pair
    distinguishes a working reader from either.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    swapped = corpus.ROOT / "scripts" / "check_ban_ratchet.py"
    if swapped.exists():
        found = swap_readiness.deps_of(swapped)
        check(
            "the SWAPPED gate reads READY", passed=bool(found) and not any(d.blocks for d in found)
        )
        # ⚑ AND IT IS NOT READY BY EMPTINESS. A reader returning nothing would satisfy the arm
        # above, so the population must be non-empty for it to mean anything.
        check("and its imports were actually read", passed=len(found) > 1)
    else:
        check("the swapped gate is absent, so its arm is SKIPPED", passed=True)

    blocked = corpus.ROOT / "scripts" / "check_discharge_ratchet.py"
    if blocked.exists():
        blocking = {d.name for d in swap_readiness.deps_of(blocked) if d.blocks}
        check("the UNSWAPPED gate reads NOT READY", passed=bool(blocking))
        # ⚑⚑ AND IT NAMES THE IMPORT THE HAND METHOD MISSED. Asserting only that it blocks would
        # pass against a reader that blocks everything.
        check(
            "naming the dependency a per-module query could not see", passed="agda_defs" in blocking
        )
    else:
        check("the unswapped gate is absent, so its arm is SKIPPED", passed=True)

    # ⚑⚑⚑ THE TWO GATES DIFFER ON THE EDIT AXIS TOO, and that is what the import axis alone
    # could not see (gate-F80). The swapped one is writable; the one this reader ranked first is
    # not, which is why its "one blocking import" was a verdict nobody could act on.
    if swapped.exists():
        state, _why = swap_readiness.editability(str(swapped))
        check("the SWAPPED gate is editable", passed=state == "CLEAN")
    # ⚑⚑⚑ THIS ARM ONCE NAMED `check_rederive_ratchet.py` AND ASSERTED IT WAS DIRTY (gate-G285).
    # The file was repaired and the arm inverted — a case pinning a MUTABLE debt state cannot hold
    # a stable polarity, which is the rule this repo already carries for witnesses, arriving in a
    # suite. What is durable is the PROPERTY: a dirty file reports DIRTY and says how much, and
    # the origin of that debt is whichever file happens to carry it today.
    dirty = corpus.ROOT / "scratch" / "mdstruct.py"
    if dirty.exists():
        state, why = swap_readiness.editability(str(dirty))
        check(f"a file the gate refuses reads DIRTY: {state}", passed=state == "DIRTY")
        # ⚑ AND THE REASON CARRIES A COUNT, so a reader sizing the drain does not re-run the
        # checkers to learn how big it is.
        check(f"and its refusal states how much debt: {why}", passed="finding" in why)
    else:
        check("no dirty file to measure, so the arm is SKIPPED", passed=True)

    return out


def _render_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what the report puts on the page."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    ready = [swap_readiness.Dep(name="os", kind=swap_readiness.EXTERNAL, line=1)]
    check("a clean file renders READY", passed="READY" in swap_readiness.render("f.py", ready))

    blocked = [swap_readiness.Dep(name="agda_lex", kind=swap_readiness.UNPACKAGED, line=3)]
    text = swap_readiness.render("f.py", blocked)
    check("a blocked file renders NOT READY", passed="NOT READY" in text)
    # ⚑ THE BLOCKER IS NAMED, or a reader must re-derive the population the report already holds
    # — which is exactly the hand-sizing this tool replaces.
    check("and names the blocking import", passed="agda_lex" in text)

    # ⚑⚑⚑ THE SECOND CONJUNCT, AND ITS ABSENCE COST A REFUSED EDIT (gate-F80). Clean imports do
    # NOT mean the file can be written: the per-file gate refuses an edit to a dirty file
    # whatever its imports look like, so a one-axis READY is a verdict nobody can act on.
    both = swap_readiness.render("f.py", ready, ("CLEAN", "would accept"))
    check("clean imports AND a clean file are SWAP READY", passed="SWAP READY" in both)

    dirty = swap_readiness.render("f.py", ready, ("DIRTY", "103 finding(s)"))
    check("clean imports with a DIRTY file are NOT swappable", passed="NOT SWAPPABLE" in dirty)
    # ⚑ AND THE COUNT IS CARRIED, or a reader must re-run the checkers to learn the size.
    check("and the report carries the finding count", passed="103" in dirty)

    # ⚑⚑ THE THIRD OUTCOME PROPAGATES. A file whose checkers could not RUN is not swappable
    # either — treating UNKNOWN as clean would schedule an edit on an unmeasured file.
    unknown = swap_readiness.render("f.py", ready, ("UNKNOWN", "ruff did not run"))
    check("an UNMEASURED file is not swappable", passed="NOT SWAPPABLE" in unknown)

    # ⚑⚑ AND OMITTING THE AXIS SAYS SO, rather than letting a partial answer wear a whole
    # verdict's clothes — which is precisely what the first cut of this reader did.
    partial = swap_readiness.render("f.py", ready)
    check("the import-only report says the edit axis was NOT ASKED", passed="NOT ASKED" in partial)
    check("and does not claim swappability", passed="SWAP READY" not in partial)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _kind_cases() + _shape_cases() + _live_cases() + _render_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"swap-readiness selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
