# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.rev_read` — the absent/broken split, against a real repository.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT A BAD REVISION AND A MISSING PATH REPORT DIFFERENTLY. That is
the defect the origin shipped: both returned a collapsed `None`, so a typo'd sha told the caller
"this file is new". Every other case here could pass against that defect — only the pair asserted
side by side sees it, which is why they are written as a pair and not as two independent arms.

⚑⚑ THE CASES DRIVE THE LIVE REPOSITORY rather than a constructed fixture. A fixture tree would
only prove the module agrees with my model of `pygit2`, and the whole reason this seam exists is
that the model was wrong twice — a locale-dependent decode and a collapsed exit code. The one
thing a fixture is used for is the arm that needs a directory that is NOT a repository, which the
live tree cannot supply.

⚑⚑⚑ AND DRIVING THE LIVE TREE ALREADY EARNED ITSELF. The first draft named `pyproject.toml` as a
file "certain to exist at any revision" — chosen from its importance rather than from its being
tracked. It is staged and uncommitted, so it reads ABSENT at HEAD, and the suite failed while the
module told the truth. A fixture would have agreed with the assumption.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from substrate import file_read as fr
from substrate import rev_read as rr
from substrate.file_read import Presence

#: A path tracked at every revision of this repository — the always-loaded working instructions.
LIVE = "CLAUDE.md"

#: A path present in the WORKING TREE and absent at HEAD — a file added but not yet committed.
#: Named because it is the reader's whole reason for being, not merely a second fixture.
UNCOMMITTED = "pyproject.toml"

#: A path certain to exist at NO revision. Named rather than spelled inline so the two absence
#: cases below are visibly asking about the same subject.
GHOST = "no/such/file/anywhere.txt"

#: A revision no repository resolves. Not a plausible-looking sha, because a 40-hex string that
#: happens to exist would make this case pass for the wrong reason.
BAD_REV = "definitely-not-a-revision-xyzzy"


def _root() -> Path:
    """Return this repository's root, derived from where this suite file sits.

    ⚑ THE SUITE MAY DERIVE A ROOT AND THE MODULE MAY NOT, and that asymmetry is deliberate rather
    than an oversight. A test must know which tree it is testing; a library must be TOLD, because
    the library runs in trees nobody anticipated. Deriving it here is what lets `rev_read` refuse
    to derive it at all.
    """
    return Path(__file__).absolute().parent.parent


def _split_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the absent/broken split — the defect this module exists for."""
    out: list[tuple[str, bool]] = []
    root = _root()

    missing = rr.read(GHOST, rr.Rev(root))
    out.append(
        (
            f"a path absent at a good revision is ABSENT: {missing.presence}",
            missing.presence is Presence.ABSENT,
        )
    )

    typo = rr.read(GHOST, rr.Rev(root, BAD_REV))
    out.append(
        (
            f"the SAME path at a bad revision is BROKEN: {typo.presence}",
            typo.presence is Presence.BROKEN,
        )
    )

    # ⚑⚑⚑ THE PAIR IS THE CASE. Each arm above passes against a reader that collapses both into
    # one outcome, provided it picks that arm's outcome. Only their DIFFERENCE is the property.
    out.append(
        (
            f"and the two differ: {missing.presence} vs {typo.presence}",
            missing.presence is not typo.presence,
        )
    )

    # ⚑ AND A LIVE PATH AT A BAD REVISION IS ALSO BROKEN — the revision is judged before the path,
    # so path-existence cannot rescue a bad revision. An implementation that looked up the path
    # first would pass every arm above and fail this one.
    live_bad = rr.read(LIVE, rr.Rev(root, BAD_REV))
    out.append(
        (
            f"a PRESENT path at a bad revision is still BROKEN: {live_bad.presence}",
            live_bad.presence is Presence.BROKEN,
        )
    )
    return out


def _two_source_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the disagreement between the two readers.

    ⚑⚑⚑ THIS IS THE READER'S WHOLE REASON FOR BEING: a file can be in the working tree and NOT at
    HEAD. `file_read` says PRESENT and `rev_read` says ABSENT, and both are correct — the pair is
    the only thing that can express "added since the last commit".

    ⚑⚑ WRITTEN AS A PROPERTY, NEVER AS A PIN ON `UNCOMMITTED`'s CURRENT STATE (gate-G285). That
    file will be committed one day, at which point a case asserting it is absent at HEAD would
    invert — a witness reading mutable state cannot hold a stable polarity. So the claim is the
    IMPLICATION: whenever the two readers disagree about this path, the disagreement is exactly
    present-on-disk and absent-at-HEAD; when they agree there is nothing to assert, and the case
    says so rather than vacating silently.
    """
    out: list[tuple[str, bool]] = []
    root = _root()
    on_disk = fr.read(root / UNCOMMITTED)
    at_head = rr.read(UNCOMMITTED, rr.Rev(root))

    if on_disk.presence is not at_head.presence:
        both = f"{on_disk.presence} on disk vs {at_head.presence} at HEAD"
        out.append(
            (
                f"a disagreement is present-here and absent-at-HEAD: {both}",
                on_disk.presence is Presence.PRESENT and at_head.presence is Presence.ABSENT,
            )
        )
    else:
        out.append(
            (f"both readers agree on {UNCOMMITTED}: {on_disk.presence} — nothing to assert", True)
        )

    # ⚑ AND THE TRACKED FILE MUST AGREE ACROSS BOTH READERS, which is the control: without it,
    # a reader reporting ABSENT for everything would satisfy the disagreement arm above.
    tracked_disk = fr.read(root / LIVE)
    tracked_head = rr.read(LIVE, rr.Rev(root))
    agree = f"{tracked_disk.presence} on disk / {tracked_head.presence} at HEAD"
    out.append(
        (
            f"a committed file is PRESENT to both: {agree}",
            tracked_disk.presence is Presence.PRESENT and tracked_head.presence is Presence.PRESENT,
        )
    )
    return out


def _present_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for an ordinary read at HEAD, against the live tree."""
    out: list[tuple[str, bool]] = []
    got = rr.read(LIVE, rr.Rev(_root()))

    out.append(
        (f"a tracked file reads PRESENT at HEAD: {got.presence}", got.presence is Presence.PRESENT)
    )
    out.append((f"and `bool` is present-ness: {bool(got)}", bool(got)))
    out.append(
        (
            f"and the bytes are non-empty: {len(got.data or b'')}",
            got.data is not None and len(got.data) > 0,
        )
    )
    # ⚑ RAW BYTES, NOT TEXT. The origin decoded with the LOCALE codec over a corpus dense in
    # non-ASCII mathematical symbols, which cost four wrong cause-hypotheses before it was found.
    # The caller chooses the codec here, so the environment cannot pick it.
    out.append((f"and the data is bytes: {type(got.data).__name__}", isinstance(got.data, bytes)))
    out.append((f"and the read names its source: {got.why()}", "rev HEAD" in got.why()))
    return out


def _source_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the source travelling on the result.

    ⚑ AN ABSENCE AT A REVISION MUST NOT READ LIKE AN ABSENCE ON DISK — that is the whole reason
    the result carries a source, and the arm that would catch its loss is this one.
    """
    out: list[tuple[str, bool]] = []
    at_rev = rr.read(GHOST, rr.Rev(_root(), "HEAD"))

    out.append((f"an absence names the revision: {at_rev.why()}", "rev HEAD" in at_rev.why()))
    out.append(
        (f"and the source is the Rev itself: {at_rev.source!r}", isinstance(at_rev.source, rr.Rev))
    )
    # ⚑⚑ AND `require()` RAISES `FileNotFoundError`, NOT A GIT-SHAPED EXCEPTION. This arm FAILED
    # on the first run with a bare `KeyError`, because the absent branch stored it — see the
    # comment at that branch. The two readers must raise alike or a caller's `except` splits.
    try:
        at_rev.require()
    except FileNotFoundError as exc:
        out.append(
            (
                f"and require() raises FileNotFoundError naming the revision: {exc}",
                "rev HEAD" in str(exc),
            )
        )
    else:
        out.append(("and require() raises FileNotFoundError naming the revision", False))
    return out


def _root_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the root being an argument with no fallback.

    ⚑⚑ THIS IS THE ARC'S OWN PROPERTY. `Rev` must not be constructible without a tree, because the
    fallback it replaces is what makes a borrowing checkout read the wrong repository while every
    path still resolves.
    """
    out: list[tuple[str, bool]] = []

    try:
        rr.Rev()  # type: ignore[call-arg]
    except TypeError:
        out.append(("Rev REFUSES to be built without a root", True))
    else:
        out.append(("Rev REFUSES to be built without a root", False))

    # ⚑ AND A DIFFERENT ROOT IS A DIFFERENT ANSWER, which is what makes the argument load-bearing
    # rather than ceremonial. A non-repository directory must report BROKEN, not ABSENT.
    with tempfile.TemporaryDirectory() as tmp:
        elsewhere = rr.read(LIVE, rr.Rev(tmp))
        out.append(
            (
                f"a non-repository root is BROKEN: {elsewhere.presence}",
                elsewhere.presence is Presence.BROKEN,
            )
        )
        out.append(
            (
                f"and the reason says so: {elsewhere.error}",
                "not a git repository" in str(elsewhere.error),
            )
        )
    return out


def _relpath_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the tree key spelling."""
    out: list[tuple[str, bool]] = []
    root = _root()

    out.append(
        (
            f"an absolute path becomes root-relative: {rr.relpath(root / 'a' / 'b.py', root)}",
            rr.relpath(root / "a" / "b.py", root) == "a/b.py",
        )
    )
    out.append(
        (
            f"a relative path is left alone: {rr.relpath('a/b.py', root)}",
            rr.relpath("a/b.py", root) == "a/b.py",
        )
    )
    # ⚑ FORWARD SLASHES ALWAYS — a git tree is keyed in POSIX spelling on every platform, and
    # handing it an OS separator reports a present file as absent.
    out.append(
        (
            f"and the key is forward-slashed: {rr.relpath(Path('a') / 'b.py', root)}",
            "\\" not in rr.relpath(Path("a") / "b.py", root),
        )
    )
    return out


def _text_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the convenience reader's asymmetry."""
    out: list[tuple[str, bool]] = []
    root = _root()

    got = rr.text(LIVE, rr.Rev(root))
    out.append((f"a present file decodes: {type(got).__name__}", isinstance(got, str)))
    out.append(
        (
            f"an absent file is None: {rr.text(GHOST, rr.Rev(root))}",
            rr.text(GHOST, rr.Rev(root)) is None,
        )
    )

    # ⚑⚑ AND A BAD REVISION RAISES rather than joining the None branch. A caller writes one branch
    # for "not there", and a defect in its own argument must not arrive down it.
    try:
        rr.text(GHOST, rr.Rev(root, BAD_REV))
    except ValueError as exc:
        out.append((f"a bad revision RAISES: {exc}", "bad revision" in str(exc)))
    else:
        out.append(("a bad revision RAISES rather than returning None", False))
    return out


def _cache_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the resolution being cached, errors included.

    ⚑ THE ERROR MUST CACHE TOO. If only success were cached, a bad revision would be re-attempted
    per path and could report differently on the hundredth read than on the first — making the
    failure depend on which path was asked for.
    """
    out: list[tuple[str, bool]] = []
    bad = rr.Rev(_root(), BAD_REV)

    first_tree, first_err = bad.resolve()
    second_tree, second_err = bad.resolve()
    out.append((f"a failed resolve caches its error: {second_err}", first_err is second_err))
    out.append((f"and stays unresolved: {second_tree}", first_tree is None and second_tree is None))

    good = rr.Rev(_root())
    out.append(("a successful resolve caches its tree", good.resolve()[0] is good.resolve()[0]))
    return out


def _origin_says(root: Path, path: str, rev: str) -> str | None:
    """Return the origin's verdict word for `path` at `rev`, or None when it could not run.

    ⚑⚑⚑ THE EXIT CODE IS NOT THE VERDICT, AND KEYING ON IT COST A FALSE PASS IN THIS VERY
    FUNCTION. A first cut returned None whenever `returncode != 0`, so the BROKEN case — which the
    origin reports on stderr with **exit 2** — was scored UNTRACED and the differential's most
    important arm silently measured nothing while the suite read 30/30.
    ⚑⚑ THAT IS THE EXIT-CODE-COLLAPSE CLASS COMMITTED INSIDE THE CHECK WRITTEN TO VERIFY A READER
    WHOSE WHOLE SUBJECT IS EXIT-CODE COLLAPSE. The origin was agreeing the entire time.

    ⚑ SO THE DISCRIMINATOR IS THE VERDICT WORD ON THE OUTPUT, and both streams are read because
    the origin prints PRESENT to stdout and BROKEN to stderr. UNTRACED is reserved for the case
    where no verdict word appears at all — a CLI that genuinely moved.
    """
    origin = root / "scratch" / "vfs.py"
    if not origin.exists():
        return None
    probe = subprocess.run(  # noqa: S603 - a fixed argv naming a file in this repo; no shell
        [sys.executable, str(origin), "--read", path, "--at", rev],
        capture_output=True,
        check=False,
        cwd=str(root),
    )
    said = probe.stdout.decode("utf-8", "replace") + probe.stderr.decode("utf-8", "replace")
    for word in said.split():
        if word in {p.name for p in Presence}:
            return word
    return None


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for agreement with the ORIGIN this module replaces.

    ⚑⚑⚑ A DRAIN THAT QUIETLY CHANGES A VERDICT IS A REWRITE WEARING A REFACTOR'S CLOTHES. Every
    other case here asserts what I believe the behaviour should be; this one asserts it is the
    ORIGIN'S, which is a different claim and the one a replacement actually owes. The origin runs
    as a SUBPROCESS rather than being imported, because importing it would need the `sys.path`
    insert this drain exists to remove — a differential that required the defect it verifies.

    ⚑⚑ AND IT COMPARES VERDICTS, NOT PAYLOADS. A first cut compared the origin's stdout against my
    `.data` and would have been meaningless: `--read` prints `PRESENT <path> (rev HEAD)` and a byte
    count, never the file. The gate refused that draft for an unrelated reason and the real output
    was read afterwards — the comparison would otherwise have shipped, red, with a plausible story.

    ⚑ A PROBE THAT CANNOT RUN REPORTS UNTRACED, NEVER AGREEMENT. That is the third outcome: an
    origin whose CLI moved must not be silently scored as concurring.
    """
    out: list[tuple[str, bool]] = []
    root = _root()
    wanted = (
        (LIVE, "HEAD", Presence.PRESENT),
        (GHOST, "HEAD", Presence.ABSENT),
        (LIVE, BAD_REV, Presence.BROKEN),
    )

    for path, rev, want in wanted:
        said = _origin_says(root, path, rev)
        mine = rr.read(path, rr.Rev(root, rev))
        if said is None:
            out.append((f"UNTRACED — the origin could not be run for {path} at {rev}", True))
            continue
        both = f"{said} / {mine.presence}"
        out.append(
            (
                f"origin and replacement agree on {path} at {rev}: {both}",
                said == str(mine.presence) == str(want),
            )
        )

    # ⚑⚑⚑ AND THE DIFFERENTIAL MUST BE SHOWN TO HAVE RUN. An UNTRACED arm passes, which is right
    # as a third outcome and indistinguishable from agreement in the total — which is exactly how
    # the exit-code defect above read as a full green. So the number of arms that actually
    # COMPARED is asserted against the case table, and a differential measuring nothing now fails
    # rather than scoring full marks. ⚑ The expected count is DERIVED from `wanted`, never typed:
    # a constant beside a table is a second roster that drifts the first time the table grows.
    compared = sum(1 for label, _ in out if "agree on" in label)
    out.append(
        (
            f"the differential compared rather than skipping: {compared} of {len(wanted)}",
            compared == len(wanted),
        )
    )
    return out


def _no_write_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the deliberate absence of a write.

    ⚑⚑ AN ABSENCE NEEDS A CASE OR IT IS NOT A DESIGN, IT IS AN OMISSION. Someone adding `write`
    here later would be adding a lie in the type — git history is not writable — and nothing but
    this arm would say so.
    """
    return [
        (
            f"the module exposes no write: {[n for n in dir(rr) if 'write' in n]}",
            not [n for n in dir(rr) if "write" in n],
        )
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _split_cases()
        + _two_source_cases()
        + _present_cases()
        + _source_cases()
        + _root_cases()
        + _relpath_cases()
        + _text_cases()
        + _cache_cases()
        + _differential_cases()
        + _no_write_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"rev-read selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
