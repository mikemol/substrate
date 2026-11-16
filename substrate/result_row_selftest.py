#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.result_row`: a name resolves, a shift is CAUGHT, and keys are SHARED.

⚑⚑⚑ THE SHIFT ARM IS THE MEASURED DEFECT, PINNED. `core_fp` gained a column and an existing
positional read against it then returned a DIFFERENT field with no error — the failure mode with
no symptom. The arm builds the same values under two column tuples differing by an inserted
column and asserts the NAMED read returns the same field in both while the POSITIONAL read does
not. An arm checking only that a name resolves would pass against a row type with no such
property, because resolving a name is not the same claim as surviving a schema change.

⚑⚑ THE SHARING ARM ASSERTS OBJECT IDENTITY, NOT EQUALITY, AND THE DIFFERENCE IS THE ENTIRE
POINT. Two rows built from the same interned column tuple must hold the SAME object: a builder
that copied its columns would be equal-but-distinct, satisfy any `==` check, and allocate one
tuple per row across result sets running to millions. Equality cannot see that; identity can.

⚑⚑ THE ARITY ARM CHECKS A REFUSAL RATHER THAN A RESULT. A short row answers every column up to
the short point and fails for the rest, so the error surfaces at whichever column a caller read
first — naming that column instead of the mismatch. An arm that only built well-formed rows
would never reach this, and the tolerance would ship.

⚑ AND `get` IS CHECKED TO DISTINGUISH AN ABSENT COLUMN FROM A STORED `None`, which is the same
absent-versus-empty collapse this tree refuses elsewhere. A row holding `None` under a real
column must return that `None`, not the caller's default — otherwise a genuine null reads as a
missing column and the caller substitutes a value the store never held.

⚑ EVERY CASE RUNS OFFLINE. A row is assembled from a key tuple and a value sequence, so nothing
here needs a store, a driver or a cursor — which is what makes the row type checkable at all.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import result_row, suite_emit

# A column tuple and its row, as a reader would intern them once per result set.
_COLUMNS = ("core_id", "local_id", "node_id")
_VALUES: tuple[object, ...] = (11, 22, 33)

# The SAME values under a column tuple that gained a column ahead of the last one. ⚑ THIS IS THE
# MEASURED SHIFT: a positional read of the last field now lands on a different column, while a
# named read of `node_id` must still find `node_id`.
_WIDENED = ("core_id", "local_id", "producer", "node_id")
_WIDENED_VALUES: tuple[object, ...] = (11, 22, "ingest", 33)

# ⚑ SPELLED OUT RATHER THAN SLICED. A slice of the tuple above infers a type the gate refuses,
# and writing the short row by hand also states plainly WHAT is short about it.
_SHORT_VALUES: tuple[object, ...] = (11, 22)

# The column a shift moves, and the position it used to sit at.
_SHIFTED_NAME = "node_id"
_SHIFTED_INDEX = 2

# A column no row here declares, used to drive the absent-name paths.
_ABSENT = "not_a_column"

# A column carrying a stored NULL. ⚑ IT MUST NOT READ AS ABSENT.
_NULL_COLUMNS = ("core_id", "mtime")
_NULL_VALUES: tuple[object, ...] = (11, None)

# A sentinel no stored value could equal, so a returned default is unambiguous.
_SENTINEL = "default-not-a-stored-value"


def a_name_resolves_to_its_own_field(out: list[str]) -> int:
    """Check that every column name returns the value declared at its position.

    ⚑ EVERY COLUMN IS CHECKED, NOT ONE. A row type resolving only its first name would satisfy a
    single-column arm while being wrong for the rest, and the columns most likely to be wrong are
    the ones a sampled check does not reach.
    """
    bad = 0
    row = result_row.build(_COLUMNS, _VALUES)
    for name, want in zip(_COLUMNS, _VALUES, strict=True):
        got = row[name]
        if got != want:
            out.append(f"selftest: row[{name!r}] returned {got!r}, want {want!r}")
            bad += 1
    return bad


def a_named_read_survives_a_shift_a_positional_one_does_not(out: list[str]) -> int:
    """Check that inserting a column moves the positional field but not the named one.

    ⚑⚑ THIS IS THE REGRESSION AND IT NEEDS BOTH HALVES. Asserting the named read is stable does
    not establish that the positional read is the fragile one; asserting the positional read
    moved does not establish the named read held. Only the pair shows the property that motivates
    reading by name at all.
    """
    bad = 0
    narrow = result_row.build(_COLUMNS, _VALUES)
    wide = result_row.build(_WIDENED, _WIDENED_VALUES)
    if narrow[_SHIFTED_NAME] != wide[_SHIFTED_NAME]:
        out.append(
            f"selftest: {_SHIFTED_NAME!r} read differently across a schema change "
            f"({narrow[_SHIFTED_NAME]!r} then {wide[_SHIFTED_NAME]!r}) — the named read shifted"
        )
        bad += 1
    if narrow[_SHIFTED_INDEX] == wide[_SHIFTED_INDEX]:
        out.append(
            f"selftest: position {_SHIFTED_INDEX} read the same value across an inserted column — "
            f"the fixture does not reproduce the shift it claims to"
        )
        bad += 1
    return bad


def the_column_tuple_is_shared_not_copied(out: list[str]) -> int:
    """Check that rows built from one interned column tuple hold the SAME object.

    ⚑⚑ IDENTITY, NOT EQUALITY. A builder copying its columns is equal-but-distinct, passes any
    `==` check, and allocates one tuple per row across millions of rows. Equality is blind to
    exactly the property that makes the interning worth doing.
    """
    bad = 0
    first = result_row.build(_COLUMNS, _VALUES)
    second = result_row.build(_COLUMNS, _VALUES)
    if first.keys() is not _COLUMNS:
        out.append("selftest: a row COPIED its column tuple instead of sharing the interned one")
        bad += 1
    if first.keys() is not second.keys():
        out.append("selftest: two rows of one result set hold DIFFERENT column tuple objects")
        bad += 1
    return bad


def an_absent_name_raises_and_names_the_columns(out: list[str]) -> int:
    """Check that an unknown column raises `KeyError` reporting the columns that are present.

    ⚑ THE MESSAGE IS PART OF THE CLAIM. A bare `KeyError` sends a reader chasing a renamed column
    to the SELECT to find out what it should have asked for; naming the columns answers that
    where the failure happened.
    """
    bad = 0
    row = result_row.build(_COLUMNS, _VALUES)
    try:
        row[_ABSENT]
    except KeyError as exc:
        if _COLUMNS[0] not in str(exc):
            out.append(f"selftest: the absent-column error {exc!s} does not name the columns")
            bad += 1
    else:
        out.append(f"selftest: reading the absent column {_ABSENT!r} did not raise")
        bad += 1
    return bad


def a_stored_null_is_not_an_absent_column(out: list[str]) -> int:
    """Check that `get` returns a stored `None` rather than the caller's default.

    ⚑⚑ THE ABSENT-VERSUS-EMPTY COLLAPSE, AT ROW SCALE. A `get` that returned its default for a
    real column holding NULL would make a genuine null indistinguishable from a missing column,
    and the caller would substitute a value the store never held. The sentinel makes the two
    outcomes tell each other apart.
    """
    bad = 0
    row = result_row.build(_NULL_COLUMNS, _NULL_VALUES)
    if row.get(_NULL_COLUMNS[1], _SENTINEL) is not None:
        out.append("selftest: a column holding NULL returned the DEFAULT — null reads as absent")
        bad += 1
    if row.get(_ABSENT, _SENTINEL) != _SENTINEL:
        out.append("selftest: an absent column did not return the caller's default")
        bad += 1
    return bad


def an_arity_mismatch_refuses_rather_than_truncating(out: list[str]) -> int:
    """Check that fewer values than columns raises instead of building a short row.

    ⚑ A SHORT ROW ANSWERS THE NAMES THAT HAPPEN TO LINE UP and fails for the rest, so the error
    surfaces at whichever column a caller reads first — naming that column instead of the
    mismatch. Refusing at construction names the arity that was wrong.
    """
    try:
        built = result_row.build(_COLUMNS, _SHORT_VALUES)
    except ValueError:
        return 0
    out.append(f"selftest: a short row was BUILT ({built!r}) instead of refusing")
    return 1


def unpacking_and_length_work_as_they_did(out: list[str]) -> int:
    """Check that a row still iterates and measures like the tuple it replaces.

    ⚑ THE RAMP DEPENDS ON THIS. Existing readers unpack rows and take their length; a row type
    that resolved names but broke iteration would force the atomic rewrite the incremental
    migration exists to avoid.
    """
    bad = 0
    row = result_row.build(_COLUMNS, _VALUES)
    if tuple(row) != _VALUES:
        out.append(f"selftest: iterating a row gave {tuple(row)!r}, want {_VALUES!r}")
        bad += 1
    if len(row) != len(_VALUES):
        out.append(f"selftest: a row of {len(_VALUES)} values reported length {len(row)}")
        bad += 1
    if row.as_dict() != dict(zip(_COLUMNS, _VALUES, strict=True)):
        out.append(f"selftest: as_dict() gave {row.as_dict()!r}")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="result_row",
    apex="a result row answers by column name across a schema change that moves its positions, "
    "shares one interned column tuple across the result set, distinguishes a stored null "
    "from an absent column, and refuses an arity it cannot honour",
    subject="the rows `substrate.result_row` assembles from columns and values, offline",
    members=(
        witness_family.Member(
            name="a_name_resolves_to_its_own_field",
            claim="every column name returns the value declared at its position",
            cases=3,
        ),
        witness_family.Member(
            name="a_named_read_survives_a_shift_a_positional_one_does_not",
            claim="an inserted column moves the positional field and leaves the named one",
            cases=2,
            premises=("a_name_resolves_to_its_own_field",),
        ),
        witness_family.Member(
            name="the_column_tuple_is_shared_not_copied",
            claim="rows of one result set hold the same interned column tuple object",
            cases=2,
        ),
        witness_family.Member(
            name="an_absent_name_raises_and_names_the_columns",
            claim="an unknown column raises and reports the columns that are present",
            cases=2,
        ),
        witness_family.Member(
            name="a_stored_null_is_not_an_absent_column",
            claim="get returns a stored None rather than the caller's default",
            cases=2,
            premises=("an_absent_name_raises_and_names_the_columns",),
        ),
        witness_family.Member(
            name="an_arity_mismatch_refuses_rather_than_truncating",
            claim="fewer values than columns raises instead of building a short row",
        ),
        witness_family.Member(
            name="unpacking_and_length_work_as_they_did",
            claim="a row still iterates, measures and flattens like the tuple it replaces",
            cases=3,
        ),
    ),
)

_ARMS = (
    a_name_resolves_to_its_own_field,
    a_named_read_survives_a_shift_a_positional_one_does_not,
    the_column_tuple_is_shared_not_copied,
    an_absent_name_raises_and_names_the_columns,
    a_stored_null_is_not_an_absent_column,
    an_arity_mismatch_refuses_rather_than_truncating,
    unpacking_and_length_work_as_they_did,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/result_row_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
