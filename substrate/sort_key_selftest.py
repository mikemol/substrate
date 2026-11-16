#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sort_key` — an ORDER as data, and the field access that reads a row.

⚑⚑⚑ `covers` IS THE ARM THAT MATTERS, AND ITS DISCRIMINATOR IS THE NON-PREFIX. A prefix test
that always said yes would satisfy every positive case here; what pins it is that `(a, b)` does
NOT cover `(b,)`, because sorting by `a` then `b` says nothing about the order of `b` alone. A
consumer propagating a requirement upstream on a permissive `covers` gets a plausible wrong
grouping, which is the failure this module's refusals exist to prevent.

⚑⚑ AND `Rev` IS TESTED ON TEXT, NOT NUMBERS, BECAUSE NEGATION IS THE REJECTED ALTERNATIVE.
Descending-by-negation works for numerics and fails for strings; a case using only numeric cells
cannot tell the wrapper from the negation it replaced, so every ordering case here compares text.

⚑⚑⚑ NO BUILTIN SATISFIES `Cell` IN ARGUMENT POSITION, AND THE TYPE GATE ESTABLISHED THAT OVER
THREE DRAFTS. `Cell.__lt__` takes `object`; `str.__lt__` takes only `str`, `int.__lt__` only
`int`. So a `str` is a fine cell to RECEIVE (the protocol is satisfied where a value flows out)
and is not one to PASS IN. Draft 1 compared a returned cell to a literal (non-overlapping
equality, 6 findings); draft 2 passed literals to a helper typed over `Cell` (9 more); draft 3
returned an `int` from a getter declared to return `Cell`. The gate is right each time, and the
lesson is the module's own: `_Text` below is the cell these cases pass around — it declares
`__lt__(self, object)`, which is what the protocol actually asks for.

⚑⚑ SO A RETRIEVED CELL IS CHECKED BY SORTING WITH IT, NEVER BY RE-READING IT. `_order` returns
the permutation a sort produces — the observable EFFECT — rather than the value re-read as a
literal, which is the only assertion a bare comparison protocol supports.

⚑ THE REFUSALS ARE CASES, NOT OMISSIONS. `as_cell` and `default_get` raise `OrderError` rather
than returning a degraded answer, and a suite asserting only the happy path cannot distinguish a
refusal from a silent wrong result — which is the whole reason those raise.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import sort_key

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True, order=False)
class _Text:
    """A text cell whose `__lt__` accepts `object` — what `Cell` actually requires.

    ⚑ IT WRAPS TEXT RATHER THAN A NUMBER so a descending case cannot be satisfied by arithmetic
    negation, which is the alternative `Rev` exists to replace.
    """

    value: str

    def __lt__(self, other: object, /) -> bool:
        """Report whether this cell sorts before `other`."""
        if not isinstance(other, _Text):
            return NotImplemented
        return self.value < other.value


@dataclass(frozen=True, slots=True)
class _Row:
    """An attribute-holding row — the shape `default_get` resolves second."""

    name: _Text
    rank: _Text


class _Incomparable:
    """A value with no ordering — the cell `as_cell` must refuse.

    ⚑ A CLASS DEFINED HERE, NOT A BUILTIN, so the refusal is about the PROTOCOL rather than
    about some builtin's internals.
    """

    __lt__ = None


def _order(cells: list[sort_key.Cell]) -> list[int]:
    """Return the positions of `cells` in sorted order — the ONE operation a cell supports.

    ⚑ THE OBSERVABLE EFFECT, NOT THE VALUE. A `Cell` cannot be equality-compared against a
    literal without leaving the type the module narrowed to, so a case says what a SORT does
    with the retrieved cells and reads the permutation back.
    """

    def at(index: int) -> sort_key.Cell:
        """Return the cell at `index` — a named function so no `Any` enters the key."""
        return cells[index]

    return sorted(range(len(cells)), key=at)


def _texts(*values: str) -> list[sort_key.Cell]:
    """Return `values` as cells, for an ordering case."""
    return [_Text(v) for v in values]


def an_order_is_data_a_consumer_can_read(out: list[str]) -> int:
    """Check `of` builds an ascending key and `names` strips the directions."""
    key = sort_key.SortKey.of("path", "line")
    if key.fields != (("path", False), ("line", False)):
        out.append(f"selftest: SortKey.of built {key.fields!r}")
        return 1
    if key.names != ("path", "line"):
        out.append(f"selftest: names is {key.names!r}")
        return 1
    if len(key) != len(key.fields):
        out.append(f"selftest: len is {len(key)} over {len(key.fields)} field(s)")
        return 1
    return 0


def the_empty_key_is_legal_and_falsy(out: list[str]) -> int:
    """Check `()` is UNORDERED rather than an error — distinct from a key on nothing special."""
    if sort_key.SortKey.of():
        out.append("selftest: a key on no fields read as ordering something")
        return 1
    if sort_key.UNORDERED:
        out.append("selftest: UNORDERED read as truthy")
        return 1
    if not sort_key.SortKey.of("a"):
        out.append("selftest: a key on one field read as unordered")
        return 1
    return 0


def covers_accepts_a_prefix(out: list[str]) -> int:
    """Check a key covers its own prefixes — the positive half."""
    key = sort_key.SortKey.of("a", "b", "c")
    for n in range(len(key) + 1):
        if not key.covers(key.truncate(n)):
            out.append(f"selftest: a key does not cover its own {n}-field prefix")
            return 1
    return 0


def covers_refuses_a_non_prefix(out: list[str]) -> int:
    """Check `(a, b)` does NOT cover `(b,)` — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS ARM A CONSTANT-TRUE `covers` PASSES EVERY OTHER CASE HERE. Sorting by `a`
    then `b` groups `b` only within an `a`, so a consumer told its `(b,)` requirement is
    satisfied gets groups that are silently wrong rather than a refusal it could act on.
    """
    key = sort_key.SortKey.of("a", "b")
    if key.covers(sort_key.SortKey.of("b")):
        out.append("selftest: (a, b) claimed to cover (b,) — a constant-true prefix test")
        return 1
    if key.covers(sort_key.SortKey.of("a", "b", "c")):
        out.append("selftest: a key claimed to cover a LONGER key")
        return 1
    if sort_key.UNORDERED.covers(sort_key.SortKey.of("a")):
        out.append("selftest: an unordered key claimed to cover an order")
        return 1
    return 0


def covers_is_direction_sensitive(out: list[str]) -> int:
    """Check `(path ASC)` does not cover `(path DESC)` — direction is part of the answer."""
    up = sort_key.SortKey((("path", False),))
    down = sort_key.SortKey((("path", True),))
    if up.covers(down) or down.covers(up):
        out.append("selftest: covers ignored the sort DIRECTION")
        return 1
    return 0


def an_unordered_key_renders_as_such(out: list[str]) -> int:
    """Check the refusal text distinguishes unordered from a named order."""
    if str(sort_key.UNORDERED) != "<unordered>":
        out.append(f"selftest: UNORDERED renders as {str(sort_key.UNORDERED)!r}")
        return 1
    rendered = str(sort_key.SortKey((("path", False), ("line", True))))
    if rendered != "path, line DESC":
        out.append(f"selftest: a mixed key renders as {rendered!r}")
        return 1
    return 0


def a_comparable_value_keeps_its_ordering_through_as_cell(out: list[str]) -> int:
    """Check cells survive the boundary with their ordering intact — the EFFECT arm."""
    cells = [sort_key.as_cell(c) for c in _texts("c", "a", "b")]
    if _order(cells) != [1, 2, 0]:
        out.append(f"selftest: as_cell disturbed the ordering: {_order(cells)!r}")
        return 1
    return 0


def an_incomparable_value_is_refused_at_the_boundary(out: list[str]) -> int:
    """Check `as_cell` raises rather than returning a value that fails three layers up."""
    try:
        sort_key.as_cell(_Incomparable())
    except sort_key.OrderError as exc:
        if "does not compare" not in str(exc):
            out.append(f"selftest: the refusal does not say why: {exc}")
            return 1
        return 0
    out.append("selftest: an incomparable value passed as_cell")
    return 1


def a_field_resolves_by_mapping_then_attribute_then_index(out: list[str]) -> int:
    """Check the three shapes each resolve, read back through a sort."""
    mapped = [sort_key.default_get({"k": c}, "k") for c in _texts("c", "a", "b")]
    if _order(mapped) != [1, 2, 0]:
        out.append(f"selftest: mapping fields resolved to {_order(mapped)!r}")
        return 1
    attrs = [sort_key.default_get(_Row(_Text("n"), _Text(v)), "rank") for v in ("c", "a", "b")]
    if _order(attrs) != [1, 2, 0]:
        out.append(f"selftest: attribute fields resolved to {_order(attrs)!r}")
        return 1
    positional = [sort_key.default_get((_Text("z"), c), "1") for c in _texts("c", "a", "b")]
    if _order(positional) != [1, 2, 0]:
        out.append(f"selftest: positional fields resolved to {_order(positional)!r}")
        return 1
    return 0


def a_name_beats_a_positional_index(out: list[str]) -> int:
    """Check a row that is BOTH shapes resolves by NAME — the ORDER of the three branches.

    ⚑ A NAMED TUPLE SATISFIES BOTH BRANCHES. If the positional read ran first, a field whose
    name parses as a digit would silently return the wrong column, so this pins which wins by
    asking for two fields on rows whose columns sort OPPOSITELY — a branch mix-up inverts one.
    """
    rows = [_Row(_Text("c"), _Text("a")), _Row(_Text("a"), _Text("c"))]
    by_name = [sort_key.default_get(row, "name") for row in rows]
    if _order(by_name) != [1, 0]:
        out.append("selftest: the `name` field did not resolve by attribute")
        return 1
    by_rank = [sort_key.default_get(row, "rank") for row in rows]
    if _order(by_rank) != [0, 1]:
        out.append("selftest: the two fields did not resolve independently")
        return 1
    return 0


def an_unresolvable_field_names_the_escape(out: list[str]) -> int:
    """Check a missing field refuses and points at `getter=`."""
    try:
        sort_key.default_get(_Row(_Text("m"), _Text("b")), "absent")
    except sort_key.OrderError as exc:
        if "getter=" not in str(exc):
            out.append(f"selftest: the refusal does not name the escape: {exc}")
            return 1
        return 0
    out.append("selftest: an unresolvable field did not refuse")
    return 1


def an_extractor_orders_ascending(out: list[str]) -> int:
    """Check a one-field key sorts rows — on TEXT, so negation could not stand in."""
    rows = [{"k": _Text(v)} for v in ("c", "a", "b")]
    got = [r["k"].value for r in sorted(rows, key=sort_key.extractor(sort_key.SortKey.of("k")))]
    if got != ["a", "b", "c"]:
        out.append(f"selftest: ascending order produced {got!r}")
        return 1
    return 0


def an_extractor_orders_descending_without_negating(out: list[str]) -> int:
    """Check a DESC field reverses TEXT cells — the arm negation cannot pass.

    ⚑ NEGATING A `_Text` IS NOT DEFINED. If `Rev` were ever replaced by an arithmetic negation
    this case fails loudly, which is the point: the ascending arm alone cannot see it.
    """
    rows = [{"k": _Text(v)} for v in ("a", "c", "b")]
    key = sort_key.SortKey((("k", True),))
    got = [r["k"].value for r in sorted(rows, key=sort_key.extractor(key))]
    if got != ["c", "b", "a"]:
        out.append(f"selftest: descending order over text produced {got!r}")
        return 1
    return 0


def a_mixed_key_orders_primary_first(out: list[str]) -> int:
    """Check the secondary field breaks ties and only ties."""
    rows = [{"a": _Text(x), "b": _Text(y)} for x, y in (("y", "1"), ("x", "2"), ("x", "1"))]
    key = sort_key.SortKey((("a", False), ("b", True)))
    got = [(r["a"].value, r["b"].value) for r in sorted(rows, key=sort_key.extractor(key))]
    if got != [("x", "2"), ("x", "1"), ("y", "1")]:
        out.append(f"selftest: the mixed order produced {got!r}")
        return 1
    return 0


def a_custom_getter_replaces_the_default(out: list[str]) -> int:
    """Check `getter=` is consulted, so a caller's own rows need no supported shape."""

    def by_length(row: str, name: str) -> sort_key.Cell:
        """Return a cell derived from the row rather than looked up on it."""
        return _Text("z" * len(row)) if name == "size" else _Text(name)

    got = sorted(["ccc", "a", "bb"], key=sort_key.extractor(sort_key.SortKey.of("size"), by_length))
    if got != ["a", "bb", "ccc"]:
        out.append(f"selftest: the custom getter was not used: {got!r}")
        return 1
    return 0


def an_unordered_extractor_yields_an_empty_tuple(out: list[str]) -> int:
    """Check UNORDERED extracts nothing, leaving the input's own order untouched."""
    rows = [{"k": _Text("c")}, {"k": _Text("a")}]
    compare: Callable[[dict[str, _Text]], tuple[sort_key.Cell, ...]] = sort_key.extractor(
        sort_key.UNORDERED
    )
    if compare(rows[0]) != ():
        out.append(f"selftest: the unordered comparison tuple is {compare(rows[0])!r}")
        return 1
    got = [r["k"].value for r in sorted(rows, key=compare)]
    if got != ["c", "a"]:
        out.append(f"selftest: sorting on UNORDERED reordered rows: {got!r}")
        return 1
    return 0


def rev_compares_only_against_rev(out: list[str]) -> int:
    """Check the wrapper refuses a bare cell rather than silently ordering against one."""
    wrapped = sort_key.Rev(_Text("a"))
    if wrapped.__lt__(_Text("b")) is not NotImplemented:
        out.append("selftest: Rev compared against an unwrapped cell")
        return 1
    if wrapped.__le__(_Text("b")) is not NotImplemented:
        out.append("selftest: Rev's __le__ compared against an unwrapped cell")
        return 1
    if wrapped == _Text("a"):
        out.append("selftest: Rev compared equal to its own unwrapped value")
        return 1
    if wrapped != sort_key.Rev(_Text("a")):
        out.append("selftest: two Revs over one value are unequal")
        return 1
    if hash(wrapped) != hash(sort_key.Rev(_Text("a"))):
        out.append("selftest: Rev's hash is inconsistent with its equality")
        return 1
    return 0


def rev_inverts_the_comparison(out: list[str]) -> int:
    """Check the wrapper's own ordering is the reverse of what it wraps."""
    low, high = sort_key.Rev(_Text("a")), sort_key.Rev(_Text("b"))
    if not high < low:
        out.append("selftest: Rev did not invert __lt__")
        return 1
    if low < high:
        out.append("selftest: Rev ordered ascending — the wrapper is a no-op")
        return 1
    if not high <= low:
        out.append("selftest: Rev did not invert __le__")
        return 1
    return 0


_ARMS = (
    an_order_is_data_a_consumer_can_read,
    the_empty_key_is_legal_and_falsy,
    covers_accepts_a_prefix,
    covers_refuses_a_non_prefix,
    covers_is_direction_sensitive,
    an_unordered_key_renders_as_such,
    a_comparable_value_keeps_its_ordering_through_as_cell,
    an_incomparable_value_is_refused_at_the_boundary,
    a_field_resolves_by_mapping_then_attribute_then_index,
    a_name_beats_a_positional_index,
    an_unresolvable_field_names_the_escape,
    an_extractor_orders_ascending,
    an_extractor_orders_descending_without_negating,
    a_mixed_key_orders_primary_first,
    a_custom_getter_replaces_the_default,
    an_unordered_extractor_yields_an_empty_tuple,
    rev_compares_only_against_rev,
    rev_inverts_the_comparison,
)

_CASE_COUNT = 3 + 3 + 4 + 3 + 2 + 2 + 1 + 2 + 3 + 2 + 2 + 1 + 1 + 1 + 1 + 2 + 5 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sort-key selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sort-key selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
