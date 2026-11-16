#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.attr_reads` — every binding form, and the zero that was banked.

⚑⚑⚑ THE PROPERTY IS PINNED, NOT A VICTIM FILE. The defect was found at
`substrate/ratchet_suites.py:46` reading `ratchet_flags.selftest`, and by the time the repair was
written that file had been rewritten to derive its roster through `importlib` — the site was gone.
A case naming it would now be green for the wrong reason, which is the expiry this session has
measured TWICE. So `every_documented_binding_form_resolves` iterates `attr_reads.BINDING_FORMS`
and fails if any one of them stops resolving: adding a form to the roster without teaching the
resolver breaks the case, and the case cannot rot when the tree moves.

⚑⚑ THE NEGATIVES DISCRIMINATE RATHER THAN EXCUSING THE POPULATION. A resolver matching NOTHING
passes every *this must not be reported* case here — the unrelated receiver, the leaf-binding
import, the non-name receiver expression. Each is paired with a positive control proving the same
resolver still finds the real read.

⚑ AND THE BLINDNESS ITSELF IS A CASE. `unresolved` is the half that keeps a zero honest, so a
reader that stopped reporting the re-export chain or the dynamic import would silently restore the
exact collapse this module repairs — with the count still reading zero and nothing to say why.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live corpus measures today's tree, so it
would report the corpus rather than the reader — and go green the moment an unrelated file moved.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import attr_reads

# One fixture per documented binding form. ⚑ KEYED BY THE FORM CONSTANT so the matrix case can
# assert the roster and the fixtures agree — a form with no fixture is a hole the count cannot see.
_FIXTURES = {
    attr_reads.PLAIN: "import pkg.mod\n\nX = pkg.mod.selftest\n",
    attr_reads.ALIAS: "import pkg.mod as m\n\nX = m.selftest\n",
    attr_reads.FROM: "from pkg import mod\n\nX = mod.selftest\n",
    attr_reads.FROM_AS: "from pkg import mod as m\n\nX = m.selftest\n",
    attr_reads.RELATIVE: "from . import mod\n\nX = mod.selftest\n",
}

# The relative form binds only a BARE name, so it is queried without the package.
_BARE_FORMS = (attr_reads.RELATIVE,)

# A `from pkg.mod import leaf` binds the LEAF — no receiver exists to read off.
_LEAF_BINDING = "from pkg.mod import selftest\n\nX = selftest\n"

# A different module under the same package: must not match a query for `pkg.mod`.
_SIBLING = "from pkg import other\n\nX = other.selftest\n"

# A receiver that is an arbitrary expression, not a name path.
_EXPR_RECV = "import pkg.mod\n\nX = make().selftest\n"

# The re-export chain the reader cannot follow.
_CHAIN = "from mod import *\n"

# The runtime binding no static reader can resolve.
_DYNAMIC = "import importlib\n\nm = importlib.import_module(name)\n"

_TWO = 2


def _pairs(where: str, files: dict[str, str]) -> list[tuple[Path, str]]:
    """Materialise `files` under `where` and return `(path, label)` pairs."""
    out = []
    for label, text in files.items():
        path = Path(where) / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        out.append((path, label))
    return out


def _sites(files: dict[str, str], operand: str) -> tuple[attr_reads.Read, ...]:
    """Write fixture files under a temp root and read the attribute reads back."""
    with tempfile.TemporaryDirectory() as where:
        return attr_reads.sites(operand, _pairs(where, files))


def _blind(files: dict[str, str], operand: str) -> tuple[str, ...]:
    """Write fixture files under a temp root and read the unresolvable shapes back."""
    with tempfile.TemporaryDirectory() as where:
        return attr_reads.unresolved(operand, _pairs(where, files))


def every_documented_binding_form_resolves(out: list[str]) -> int:
    """Check every form in `BINDING_FORMS` binds the receiver for attribute resolution.

    ⚑⚑⚑ THE CASE THAT PINS THE PROPERTY. The origin resolved NO dotted receiver at all — the
    `<Recv>.<leaf>` spelling was documented and fell through to a comparison no attribute name can
    satisfy, so `--attr ratchet_flags.selftest` answered `0 of 1142 files` with the site present.
    Iterating the roster means a form added to it without a resolver breaks this case, and no
    named file has to stay put for the case to keep meaning something.
    """
    failed = []
    for form in attr_reads.BINDING_FORMS:
        if form not in _FIXTURES:
            failed.append(f"{form} (no fixture)")
            continue
        recv = "mod" if form in _BARE_FORMS else "pkg.mod"
        got = _sites({"a/one.py": _FIXTURES[form]}, f"{recv}.selftest")
        if len(got) != 1 or got[0].form != form:
            failed.append(f"{form} -> {got!r}")
    if failed:
        out.append("selftest: binding forms that did not resolve: " + "; ".join(failed))
        return 1
    return 0


def the_star_form_still_reports_every_attribute(out: list[str]) -> int:
    """Check `<Recv>.*` keeps working — the one dotted spelling the origin DID implement.

    ⚑ THE POSITIVE CONTROL FOR THE REPAIR. Folding three spellings into one predicate could have
    traded the missing form for the working one, which is the shape of a fix that measures green.
    """
    src = "from pkg import mod\n\nX = mod.selftest\nY = mod.other\n"
    got = _sites({"a/one.py": src}, "mod.*")
    if len(got) != _TWO or {r.attr for r in got} != {"selftest", "other"}:
        out.append(f"selftest: the star form did not report every attribute: {got!r}")
        return 1
    return 0


def the_leaf_form_stays_receiver_blind(out: list[str]) -> int:
    """Check a bare leaf query still reports reads off ANY receiver.

    ⚑ THE LEAF FORM IS A DIFFERENT QUESTION, NOT A LOOSER ONE. Its receiver is an arbitrary
    expression and is not decidable, so the origin's refusal to filter by a guess is correct and
    the dotted repair must not tighten it into a resolver.
    """
    src = "X = anything.selftest\nY = other.selftest\n"
    got = _sites({"a/one.py": src}, "selftest")
    if len(got) != _TWO:
        out.append(f"selftest: the leaf form was narrowed by the receiver repair: {got!r}")
        return 1
    return 0


def an_unrelated_receiver_is_not_matched(out: list[str]) -> int:
    """Check `from pkg import other` does not answer a query for `pkg.mod`.

    ⚑ THE RESOLUTION MUST NOT WIDEN INTO THE PACKAGE. Matching on the package alone would report
    every file importing it as reading off every module in it — a census with no discrimination
    left, which is a different way of saying nothing.
    """
    got = _sites({"a/one.py": _SIBLING}, "pkg.mod.selftest")
    if got != ():
        out.append(f"selftest: an unrelated receiver matched: {got!r}")
        return 1
    return 0


def a_leaf_binding_import_yields_no_receiver(out: list[str]) -> int:
    """Check `from pkg.mod import selftest` reports no attribute read.

    ⚑ IT BINDS THE LEAF, NOT THE MODULE — the consumer writes `selftest`, never `mod.selftest`.
    Reporting a read here would be a false FINDING, the opposite error from the false zero and
    just as wrong.
    """
    got = _sites({"a/one.py": _LEAF_BINDING}, "pkg.mod.selftest")
    if got != ():
        out.append(f"selftest: a leaf-binding import reported a receiver: {got!r}")
        return 1
    return 0


def a_non_name_receiver_is_not_resolved(out: list[str]) -> int:
    """Check `make().selftest` is not attributed to an imported module.

    ⚑ AN ARBITRARY EXPRESSION IS NOT A NAME. Attributing it to whichever module happens to be
    imported in the file is exactly the guess the leaf form refuses to make.
    """
    got = _sites({"a/one.py": _EXPR_RECV}, "pkg.mod.selftest")
    if got != ():
        out.append(f"selftest: a non-name receiver was resolved: {got!r}")
        return 1
    return 0


def a_bare_receiver_that_names_no_module_still_matches(out: list[str]) -> int:
    """Check `self.x` and `Row.field` keep working with no import in sight.

    ⚑ THE BARE RECEIVER ALWAYS BINDS ITSELF, or the repair would DELETE answers the origin's
    `Recv.*` already gave correctly — a regression hidden inside a fix for a false zero.
    """
    got = _sites({"a/one.py": "def f(self):\n    return self.waiting\n"}, "self.waiting")
    if len(got) != 1:
        out.append(f"selftest: a bare non-module receiver stopped matching: {got!r}")
        return 1
    return 0


def a_re_export_chain_is_reported_as_unresolvable(out: list[str]) -> int:
    """Check a star re-export is NAMED rather than absorbed into the count.

    ⚑⚑ THE HONEST-ZERO HALF. A consumer reaching `ratchet.selftest` through `ratchet.py`'s star
    re-export names the original module nowhere, so no single-file read can follow the chain. A
    reader that stayed silent would put back the collapse of *none* into *could not see* one layer
    below the fix for it.
    """
    got = _blind({"a/one.py": _CHAIN}, "mod.selftest")
    if not any(b.startswith(attr_reads.CHAIN) for b in got):
        out.append(f"selftest: a re-export chain was not reported: {got!r}")
        return 1
    return 0


def a_dynamic_import_is_reported_as_unresolvable(out: list[str]) -> int:
    """Check `importlib.import_module` is named as a shape the reader cannot see.

    ⚑ MEASURED ON THE LIVE TREE: the file that motivated this repair was rewritten to derive its
    roster dynamically, so the original static site really is gone. The reader reports zero AND
    names that file — which is the difference between an absence and a blind spot.
    """
    got = _blind({"a/one.py": _DYNAMIC}, "mod.selftest")
    if not any(b.startswith(attr_reads.DYNAMIC) for b in got):
        out.append(f"selftest: a dynamic import was not reported: {got!r}")
        return 1
    return 0


def a_relative_import_under_a_dotted_query_is_reported(out: list[str]) -> int:
    """Check a dotted query over a relative binding says it cannot confirm the package.

    ⚑ THE BARE QUERY RESOLVES AND THE DOTTED ONE CANNOT, and conflating them would either drop a
    real answer or invent a package. Both halves are cases; this is the one that keeps the guess
    from being made silently.
    """
    got = _blind({"a/one.py": _FIXTURES[attr_reads.RELATIVE]}, "pkg.mod.selftest")
    if not any(b.startswith(attr_reads.RELATIVE_PKG) for b in got):
        out.append(f"selftest: a relative import under a dotted query was not reported: {got!r}")
        return 1
    return 0


def the_leaf_form_reports_no_blindness(out: list[str]) -> int:
    """Check a receiver-blind query does not claim shapes it never depended on.

    ⚑ A CAVEAT THAT ALWAYS FIRES IS A CAVEAT NOBODY READS. The leaf form resolves no receiver, so
    an import it cannot follow costs it nothing — reporting one there would train a reader to skip
    the line that matters.
    """
    got = _blind({"a/one.py": _CHAIN + _DYNAMIC}, "selftest")
    if got != ():
        out.append(f"selftest: the leaf form reported irrelevant blindness: {got!r}")
        return 1
    return 0


def every_reading_file_is_reported(out: list[str]) -> int:
    """Check the census carries all sites, not just the first."""
    got = _sites(
        {"a/one.py": _FIXTURES[attr_reads.FROM], "b/two.py": _FIXTURES[attr_reads.FROM_AS]},
        "pkg.mod.selftest",
    )
    if len(got) != _TWO:
        out.append(f"selftest: not every reading file was reported: {got!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising.

    ⚑ ONE BAD FILE MUST NOT TAKE THE CENSUS DOWN — it would report nothing about the thousand that
    parse, a far larger error than the one file it skips.
    """
    got = _sites({"a/one.py": "def broken(:\n"}, "pkg.mod.selftest")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def the_render_prints_its_denominator_on_zero(out: list[str]) -> int:
    """Check an empty census still names how many files were scanned.

    ⚑⚑ `0 reads` AND `0 reads OF 1144 FILES` ARE THE SAME FINDING and only the second lets a
    reader see the scan happened. This is the line that makes a zero legible as a question about
    the reader rather than about the tree.
    """
    text = attr_reads.render("pkg.mod.selftest", (), 1144)
    if "of 1144 file(s)" not in text:
        out.append(f"selftest: an empty census omits its denominator:\n{text}")
        return 1
    return 0


def the_render_names_what_it_could_not_see(out: list[str]) -> int:
    """Check the unresolvable shapes reach the report, not just the accessor."""
    text = attr_reads.render("pkg.mod.selftest", (), 1, ("dynamic-import: a/one.py:3 …",))
    if "CANNOT resolve" not in text or "dynamic-import" not in text:
        out.append(f"selftest: the render omits what it could not see:\n{text}")
        return 1
    return 0


def the_operand_parses_into_its_three_forms(out: list[str]) -> int:
    """Check `leaf`, `Recv.*` and `Recv.leaf` each parse to the query they denote.

    ⚑ THE THREE FORMS ARE ONE PREDICATE, and keeping them as three branches is how the dotted one
    went missing for as long as it did.
    """
    want = (
        ("selftest", attr_reads.Query(recv=None, leaf="selftest")),
        ("mod.*", attr_reads.Query(recv="mod", leaf=None)),
        ("pkg.mod.selftest", attr_reads.Query(recv="pkg.mod", leaf="selftest")),
    )
    bad = [(o, attr_reads.parse(o)) for o, w in want if attr_reads.parse(o) != w]
    if bad:
        out.append(f"selftest: an operand parsed to the wrong query: {bad!r}")
        return 1
    return 0


_ARMS = (
    every_documented_binding_form_resolves,
    the_star_form_still_reports_every_attribute,
    the_leaf_form_stays_receiver_blind,
    an_unrelated_receiver_is_not_matched,
    a_leaf_binding_import_yields_no_receiver,
    a_non_name_receiver_is_not_resolved,
    a_bare_receiver_that_names_no_module_still_matches,
    a_re_export_chain_is_reported_as_unresolvable,
    a_dynamic_import_is_reported_as_unresolvable,
    a_relative_import_under_a_dotted_query_is_reported,
    the_leaf_form_reports_no_blindness,
    every_reading_file_is_reported,
    an_unparseable_file_yields_nothing,
    the_render_prints_its_denominator_on_zero,
    the_render_names_what_it_could_not_see,
    the_operand_parses_into_its_three_forms,
)

_CASE_COUNT = 16


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"attr-reads selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"attr-reads selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
