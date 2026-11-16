# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.witness_rekey` — including the LIVE ledger, read-only.

⚑⚑⚑ THE PRESERVATION ARM IS THE ONE THAT MATTERS, AND IT ASSERTS BYTES RATHER THAN STRUCTURE.
The failure this module exists to avoid is a rewriter keeping only what its parser recognised — a
peer measured exactly that, silently destroying three prose comments between bib entries while
their parse guard passed because the result was still valid. So the cases do not check that the
result parses: they check that the output differs from the input in EXACTLY the key token and
nowhere else, which is a claim a parse-level assertion cannot make.

⚑⚑ AND THE LIVE ARM NEVER WRITES. It runs `rekey` over the real ledger's source in memory and
throws the result away, which is the only honest way to test an anchor against the population it
will actually meet — a fixture only contains what I put in it, and the anchor's whole job is to
be unique among the real entries and a great deal of prose.

⚑ THE REFUSAL ARMS CARRY AS MUCH WEIGHT AS THE SUCCESS ARM. A re-key that silently did nothing,
or that renamed the wrong one of two matches, is worse than one that fails: the roster would look
edited and the witness would be reachable under neither spelling.

⚑⚑⚑ AND THE LIVE ARM NAMES NO PARTICULAR KEY, WHICH IS A REPAIR OF MY OWN CASES. A first cut
asserted that `tmi-F6` anchors once and that re-keying it WOULD succeed — true while that re-key
was pending, false the moment it landed. It landed, the suite fell from 29/29 to 25/27, and the
polarity probe caught it by refusing to file a finding whose witness had gone red. A case that
tracks REMAINING WORK fails when the work arrives; what is pinned now is that the anchor is
unique for whatever keys the roster currently holds, which survives every future rename.

⚑⚑ A SECOND FALSE PREMISE WAS CORRECTED THE SAME WAY EARLIER. I asserted `tmi-F1` anchors once,
reasoning that the bib carries `tmi-F1-…` so a bare stem must exist. It does not — the witness is
`tmi-F1-revision-recall-is-30-not-precision-100` and `findings.py tmi-F1` refuses as an ambiguous
prefix over eleven keys. The bare stems were only F15 through F18.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import witness_rekey as wr

#: The live ledger this module is built to edit — read here, never written.
LEDGER = corpus.ROOT / ".claude" / "agents" / "findings.py"

#: Every witness definition site, as the roster spells them — the same shape `anchor_for` builds,
#: so the arm that checks uniqueness is reading the population the module will actually edit.
KEY_LINE = re.compile(r'\n {4}"([A-Za-z0-9_-]+)": ')

#: A miniature roster carrying the shapes the real one does: a comment between entries, a key
#: that is a strict prefix of another, and a note containing the bare key as prose.
FIXTURE = (
    'WITNESSES = {\n'
    '    # ⚑ A HAND-WRITTEN COMMENT that no re-emitter should be trusted to reproduce.\n'
    '    "tmi-F1": _standing("a note mentioning tmi-F1 and tmi-F10 in prose"),\n'
    '    "tmi-F10": _standing("the longer key whose stem the shorter one prefixes"),\n'
    '    "keep-me": _standing("untouched"),  # noqa: E501 — a directive, also preserved\n'
    '}\n'
)


def _diff_span(before: str, after: str) -> int:
    """Return how many bytes of `before` lie strictly between the shared prefix and suffix.

    ⚑⚑ THE TRAILING SCAN MUST NOT RE-ENTER THE MATCHED PREFIX, and my first cut did. It bounded
    the backward walk against `len(before) - lead` while indexing from the END of each string, so
    on inputs of different lengths it ran past the leading region and reported a changed span
    wider than the edit. Three arms failed at once and the module was correct — the measuring
    helper was the defect, which is the shape a case exists to catch.
    """
    lead = 0
    while lead < len(before) and lead < len(after) and before[lead] == after[lead]:
        lead += 1
    tail = 0
    while (tail < len(before) - lead and tail < len(after) - lead
           and before[-1 - tail] == after[-1 - tail]):
        tail += 1
    return len(before) - lead - tail


def _rename_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a successful re-key over the fixture."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    found = wr.rekey(FIXTURE, "tmi-F1", "tmi-F1-the-long-descriptive-key")
    check("a re-key over the fixture succeeds", passed=found.outcome is wr.Outcome.WOULD)
    if found.text is None:
        return [*out, ("the re-key returned no text, so nothing further can be asserted", False)]

    grew = len("tmi-F1-the-long-descriptive-key") - len("tmi-F1")
    check("the file grows by exactly the key's growth",
          passed=len(found.text) - len(FIXTURE) == grew)
    # ⚑⚑⚑ THE CHANGED SPAN IS ZERO, NOT THE OLD KEY'S LENGTH, AND I ASSERTED THE WRONG NUMBER.
    # The new key EXTENDS the old one — which is the shape of every spelling pair here — so the
    # shared prefix runs through `tmi-F1` and the edit is a pure INSERTION. Asserting
    # `span == len(old)` failed on both the fixture and the live ledger, and the module was
    # right in both. The property that actually holds, and the one worth pinning, is that
    # nothing of `before` is REPLACED: every original byte survives in order.
    check("and no original byte is replaced — the edit is a pure insertion",
          passed=_diff_span(FIXTURE, found.text) == 0)

    # ⚑ EACH SURVIVING SHAPE IS NAMED, so a failure says WHICH kind of content was lost — the
    # peer's incident lost prose comments specifically, and a single "output unchanged" arm
    # would not have distinguished them from a directive or a body.
    check("the hand-written comment survives",
          passed="# ⚑ A HAND-WRITTEN COMMENT" in found.text)
    check("the noqa directive survives", passed="# noqa: E501" in found.text)
    check("the untouched entry survives", passed='"keep-me": _standing("untouched")' in found.text)

    # ⚑⚑ THE PREFIX KEY IS NOT TOUCHED, which is the anchor's whole point: `tmi-F1` is a strict
    # prefix of `tmi-F10`, so a bare-substring rename would corrupt the longer entry.
    check("the longer key that the stem prefixes is NOT renamed",
          passed='"tmi-F10": _standing(' in found.text)
    # ⚑ AND THE BARE KEY INSIDE PROSE IS NOT TOUCHED — a note mentioning the key is not a
    # definition site, and renaming it would rewrite a recorded measurement.
    check("the key mentioned in a note's prose is NOT renamed",
          passed="a note mentioning tmi-F1 and tmi-F10 in prose" in found.text)
    check("and the new key IS present as a definition",
          passed='"tmi-F1-the-long-descriptive-key": _standing(' in found.text)

    return out


def _refusal_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every precondition, each refusing with its own reason."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def refused(old: str, new: str, needle: str) -> bool:
        got = wr.rekey(FIXTURE, old, new)
        return got.outcome is wr.Outcome.REFUSED and got.text is None and needle in got.reason

    # ⚑ AN ABSENT KEY REFUSES RATHER THAN SILENTLY DOING NOTHING. A no-op that reports success is
    # the shape that lets a caller believe a rename landed.
    check("an absent key refuses, naming that there is no definition site",
          passed=refused("no-such-key", "whatever-new", "no definition site"))
    # ⚑⚑ RENAMING ONTO A LIVE KEY IS REFUSED — it would collapse two witnesses into one position
    # and drop whichever the replacement did not keep.
    check("a rename onto an existing key refuses",
          passed=refused("tmi-F1", "keep-me", "already a witness key"))
    check("a no-op rename refuses", passed=refused("tmi-F1", "tmi-F1", "already the key"))
    # ⚑ THE CHARSET IS THE READER'S, NOT A PREFERENCE: bibstruct parses the emitted source.
    check("a key outside the charset refuses",
          passed=refused("tmi-F1", 'bad key"with quotes', "[A-Za-z0-9_-]"))
    check("and so does a bad OLD key", passed=refused('has"quote', "fine-key", "[A-Za-z0-9_-]"))

    # ⚑⚑ A REFUSAL CARRIES NO TEXT, so a caller cannot write a result it did not get. Asserted
    # rather than assumed, because the None is the only thing stopping a careless write.
    check("every refusal carries None for text",
          passed=wr.rekey(FIXTURE, "no-such-key", "x").text is None)

    return out


def _file_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the file-level wrapper and its apply contract."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "roster.py"
        path.write_text(FIXTURE, encoding="utf-8")

        # ⚑⚑⚑ THE DRY RUN MUST NOT WRITE, and the case reads the FILE back rather than trusting
        # the return value — a wrapper that wrote and then reported "would" is exactly the defect
        # a return-value assertion cannot see.
        dry = wr.rekey_file(path, "tmi-F1", "tmi-F1-long", apply=False)
        check("a dry run reports WOULD", passed=dry.outcome is wr.Outcome.WOULD)
        check("and the file on disk is UNCHANGED",
              passed=path.read_text(encoding="utf-8") == FIXTURE)

        wrote = wr.rekey_file(path, "tmi-F1", "tmi-F1-long", apply=True)
        check("an applied run reports WROTE", passed=wrote.outcome is wr.Outcome.WROTE)
        landed = path.read_text(encoding="utf-8")
        check("and the file on disk CHANGED", passed=landed != FIXTURE)
        check("with the new key present", passed='"tmi-F1-long": _standing(' in landed)
        check("and the comment still there", passed="# ⚑ A HAND-WRITTEN COMMENT" in landed)
        # ⚑ NO TEMP FILE IS LEFT BEHIND — the write is atomic via replace, so a stray `.py.tmp`
        # would mean the rename did not happen and the roster is duplicated on disk.
        check("no temp file survives the write",
              passed=not list(Path(tmp).glob("*.tmp")))

        # ⚑ AN UNREADABLE PATH REFUSES rather than raising, so a caller gets a reason.
        gone = wr.rekey_file(Path(tmp) / "absent.py", "a", "b")
        check("a missing file refuses with a reason", passed=gone.outcome is wr.Outcome.REFUSED)

    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the REAL ledger — read-only, never written.

    ⚑⚑⚑ THIS IS WHERE THE ANCHOR IS ACTUALLY TESTED. A fixture proves the anchor works among
    shapes I chose; only the live roster proves it is unique among the real population, which is
    the property that makes a rename safe. The result is computed and discarded.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    if not LEDGER.exists():
        return [("the live ledger is absent, so the live arm is SKIPPED, not passed", True)]
    src = LEDGER.read_text(encoding="utf-8")

    # ⚑ NARROWED AT THE MATCH, because `Match.group` is `Any` and every read off it would then
    # type-check against nothing — the same seam a dynamically loaded module presents.
    keys: list[str] = [str(m.group(1)) for m in KEY_LINE.finditer(src)]
    check("the live roster yields keys, so the arm is not vacuous", passed=len(keys) > 1)
    # ⚑⚑ EVERY key anchors exactly once — the uniqueness claim the whole module rests on,
    # asserted over the entire real population rather than one hand-picked member, so it cannot
    # go stale when a particular re-key lands.
    duped = sorted({k for k in keys if src.count(wr.anchor_for(k)) != 1})
    check(f"every live key anchors exactly once (e.g. {duped[:3]})", passed=not duped)

    # ⚑⚑ AND A STEM THAT IS NOT A DEFINITION SITE ANCHORS ZERO TIMES, which is the arm that
    # replaced a false premise of mine: `tmi-F1` is NOT a witness key — the roster spells it
    # `tmi-F1-revision-recall-is-30-not-precision-100` and `findings.py tmi-F1` refuses as an
    # ambiguous prefix over eleven keys. So the anchor must find nothing, and a rename of it
    # must REFUSE rather than silently match a longer entry.
    check("a stem that is not a definition site anchors zero times",
          passed=src.count(wr.anchor_for("tmi-F1")) == 0)
    check("and re-keying it is REFUSED rather than matched",
          passed=wr.rekey(src, "tmi-F1", "tmi-F1-new").outcome is wr.Outcome.REFUSED)

    # ⚑ THE BYTE-PRESERVATION ARM RUNS AGAINST WHATEVER KEY THE ROSTER HOLDS FIRST, so it keeps
    # measuring the real file without depending on any pending work existing.
    probe = keys[0] if keys else ""
    suffix = "-probe-suffix-never-written"
    found = wr.rekey(src, probe, probe + suffix)
    check(f"a re-key of a live key ({probe}) would succeed",
          passed=found.outcome is wr.Outcome.WOULD)
    if found.text is not None:
        check("and no original byte of the ledger is replaced",
              passed=_diff_span(src, found.text) == 0)
        # ⚑ THE POSITIVE CONTROL: the ledger is large, so a span of zero would also satisfy a
        # carelessly written arm. Assert the file actually grew by the key's growth.
        check("and the result is longer by exactly the new key's extra bytes",
              passed=len(found.text) - len(src) == len(suffix))

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _rename_cases() + _refusal_cases() + _file_cases() + _live_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"witness-rekey selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
