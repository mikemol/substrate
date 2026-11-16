#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.edge_split` — the re-split, and the silence it prevents.

⚑⚑⚑ THE MULTI-TARGET CASE IS THE WHOLE SUBJECT. `enables = {A, B}` reaches a consumer as the
STRING `'A, B'`, so a reader that does not re-split sees ONE target named `"A, B"` — a key
matching no entry. It does not raise. A multi-target edge silently becomes a single dangling one,
and the dangling-edge report then names a key nobody ever wrote.

⚑⚑ AND BOTH ARRIVAL SHAPES NEED A CASE, because the engine hands built-in `_LIST` fields as
lists and declared consumer fields as strings. A splitter correct on one and wrong on the other
is correct on exactly the fields nobody had trouble with.

⚑ THE BLANK CASES ARE NOT PADDING. `str.split` on an empty string returns `['']`, so the naive
implementation yields one target with an empty name — an unnameable key entering every
downstream edge set, reported as dangling forever.
"""

from __future__ import annotations

import sys

from substrate import edge_split

# The two-target string an entry's declared consumer field actually arrives as.
_PAIR = "A, B"

# Both spellings of the separator seen in real entries: with and without the space.
_TIGHT = "A,B"

_EXPECTED = ("A", "B")


def a_declared_field_string_splits_into_targets(out: list[str]) -> int:
    """Check the string form yields every target.

    ⚑⚑ THE DEFECT THIS MODULE EXISTS FOR. Without the split this value is one target named
    `'A, B'` — plausible-looking, matching nothing, and raising nothing.
    """
    got = edge_split.targets(_PAIR)
    if got != _EXPECTED:
        out.append(f"selftest: {_PAIR!r} split to {got!r}")
        return 1
    return 0


def the_separator_needs_no_space(out: list[str]) -> int:
    """Check a comma with no following space splits identically.

    ⚑ AN AUTHOR WRITES EITHER, and a splitter that required the space would leave `'A,B'` as one
    dangling target — the same defect, reachable by typing one fewer character.
    """
    got = edge_split.targets(_TIGHT)
    if got != _EXPECTED:
        out.append(f"selftest: {_TIGHT!r} split to {got!r}")
        return 1
    return 0


def a_builtin_list_field_passes_through(out: list[str]) -> int:
    """Check the list form is accepted and normalized, not re-split as text.

    ⚑ THE OTHER ARRIVAL SHAPE. `rests-on` reaches a consumer as `['A', 'B']`; a splitter that
    only handled strings would stringify the list and produce targets like `"['A'" `.
    """
    got = edge_split.targets(["A", " B "])
    if got != _EXPECTED:
        out.append(f"selftest: a list field split to {got!r}")
        return 1
    return 0


def a_single_target_is_a_one_tuple(out: list[str]) -> int:
    """Check the common single-target case is unharmed."""
    got = edge_split.targets("A")
    if got != ("A",):
        out.append(f"selftest: a single target split to {got!r}")
        return 1
    return 0


def an_empty_value_yields_no_targets(out: list[str]) -> int:
    """Check a blank value yields nothing rather than one nameless target.

    ⚑⚑ `"".split(",")` IS `['']`, NOT `[]`. The naive form puts an empty key into every edge set
    that consumes it, and an empty key is dangling by construction — a permanent false finding.
    """
    bad = 0
    for blank in ("", "   ", ",", " , "):
        got = edge_split.targets(blank)
        if got != ():
            out.append(f"selftest: {blank!r} yielded {got!r}")
            bad += 1
    return bad


def only_the_named_fields_are_read(out: list[str]) -> int:
    """Check `edges` reports the named edge fields and ignores the rest.

    ⚑ AN ENTRY CARRIES CLAIM AND SECTION TOO, and treating every field as an edge would turn a
    claim's prose into a target list.
    """
    fields = {"claim": "some prose, with a comma", "enables": _PAIR, "section": "s"}
    got = edge_split.edges(fields, ("enables",))
    if got != {"enables": _EXPECTED}:
        out.append(f"selftest: edges read {got!r}")
        return 1
    return 0


def a_named_field_the_entry_lacks_is_absent(out: list[str]) -> int:
    """Check a field the entry does not carry yields no key at all.

    ⚑ NOT AN EMPTY TUPLE. *"this entry declares no enablement"* and *"this entry has no such
    field"* are different facts; a key mapped to `()` asserts the first about the second.
    """
    got = edge_split.edges({"claim": "c"}, ("enables", "rests-on"))
    if got != {}:
        out.append(f"selftest: a missing field produced {got!r}")
        return 1
    return 0


def an_entry_with_no_edges_renders_as_such(out: list[str]) -> int:
    """Check the renderer says so rather than printing an empty block."""
    if "no edges" not in edge_split.render("ALPHA", {}):
        out.append("selftest: an edgeless entry rendered no explanation")
        return 1
    return 0


def the_rendered_edge_names_its_field(out: list[str]) -> int:
    """Check each target line says which field carried it.

    ⚑ THE FIELD IS THE RELATION. `enables` and `rests-on` mean different things — one is about
    when work becomes available, the other about grounding — so a target list that drops the
    field name loses the distinction the two fields exist to draw.
    """
    text = edge_split.render("ALPHA", {"enables": _EXPECTED})
    bad = 0
    if "enables" not in text:
        out.append("selftest: the rendered edge does not name its field")
        bad += 1
    if "A, B" not in text:
        out.append(f"selftest: the rendered edge does not list its targets:\n{text}")
        bad += 1
    return bad


_ARMS = (
    a_declared_field_string_splits_into_targets,
    the_separator_needs_no_space,
    a_builtin_list_field_passes_through,
    a_single_target_is_a_one_tuple,
    an_empty_value_yields_no_targets,
    only_the_named_fields_are_read,
    a_named_field_the_entry_lacks_is_absent,
    an_entry_with_no_edges_renders_as_such,
    the_rendered_edge_names_its_field,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 4 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"edge-split selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"edge-split selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
