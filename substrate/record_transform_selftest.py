#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.record_transform` — every handler is asserted to fire on ITS OWN node.

⚑⚑⚑ A BARE POSITIVE CONTROL IS A TRANSPORT-200, AND THAT IS WHY EACH ARM PLANTS ITS OWN NODE.
cassian-observability, asked whether read-your-write was over-engineering for an in-process
visitor: *"a positive control ('a visitor DID fire on some input') proves dispatch happened, not
that the RIGHT dispatch happened on the node you care about."* The failure one level in — a
transform that binds the `Call` handler correctly and the `ClassDef` handler wrong fires on the
Call, a coarse control goes green, and the conversion silently visits nothing.

⚑⚑ SO THE POPULATION EACH ARM ASSERTS OVER IS {one planted node per claimed handler}, NOT {did
anything happen}. The value controlled is the planted node plus the mutation only that handler
produces; the read-back is the assertion that THAT node changed THAT way. Enumerate the bindings
you CLAIM — a finite whitelist — rather than trust a proxy that quantifies over nothing.

⚑⚑⚑ AND THE RESIDUAL THESE CASES EXIST FOR IS SILENT BY CONSTRUCTION. libcst validates a decorated
handler's SIGNATURE at instantiation (`MatcherDecoratableTransformer.__init__` → `_check_types`),
so a malformed one raises loudly. It cannot see a WRONG MATCHER: `@m.visit(m.FunctionDef())` where
`m.ClassDef()` was meant binds correctly and fires on the wrong node. Nothing in libcst reports
that, so it is reported here or not at all.

⚑ THE FLAG ARMS ASSERT THE FLAG'S CONTENT, NOT ITS COUNT. A handler that fired but produced the
wrong message is indistinguishable from the right one by count alone, and the message is what a
reader acts on — it names the site and the remedy.
"""

from __future__ import annotations

import sys

import libcst as cst
from libcst.codemod import CodemodContext

from substrate import record_transform

# A record, so the ClassDef and ImportFrom handlers have something to convert.
_RECORD = '''"""Doc."""

from __future__ import annotations

from typing import NamedTuple


class Planted(NamedTuple):
    """A record planted for the ClassDef handler."""

    name: str
'''

# A record whose `typing` import carries a second name, so removal must keep it.
_RECORD_SHARED_IMPORT = '''"""Doc."""

from typing import NamedTuple, TYPE_CHECKING


class Planted(NamedTuple):
    """A record."""

    name: str


USES = TYPE_CHECKING
'''

# ⚑⚑⚑ THE IMPORT SHAPES A REAL MODULE HAS, PLANTED BECAUSE 20/20 COEXISTED WITH 13 BROKEN FILES.
# The fixtures above have one simple import block — the shape the handler's author thought of —
# so `the_module_handler_adds_the_import` was green while `_add_import` silently placed nothing on
# every file with a `TYPE_CHECKING` block. A per-BINDING control is not a per-INPUT-SHAPE control,
# and only the second catches a handler that works on the case you imagined.
_WITH_TYPE_CHECKING = '''"""Doc."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path


class Planted(NamedTuple):
    """A record beneath a TYPE_CHECKING block."""

    name: str


USES = (ast, corpus, Path)
'''

# ⚑⚑⚑ THE SHAPE THAT DISCRIMINATES THE 13 FROM THE 50, and which `_WITH_TYPE_CHECKING` does not
# have. Here the `if TYPE_CHECKING:` block is the LAST import-ish statement before the record, so
# an anchor computed with `m.findall` — which matches the import NESTED INSIDE the block — lands
# on the `if` and places the new import AFTER it, outside the import run. `ruff --fix` then reads
# that as dead code and deletes it, and the decorator the ClassDef handler added is undefined.
# MEASURED on `substrate/edge_census.py`: import after transform True, after fix False.
_BLOCK_IS_LAST = '''"""Doc."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path


class Planted(NamedTuple):
    """A record whose module ends its imports with a TYPE_CHECKING block."""

    name: str


USES = (sys, corpus, Path)
'''

# A module whose only import is `__future__` — the shape left once `typing` is removed.
_FUTURE_ONLY = '''"""Doc."""

from __future__ import annotations


class Planted(NamedTuple):
    """A record whose module imports nothing else."""

    name: str
'''

# A keyless comparison and an integer subscript, planted for the flag handlers.
_KEYLESS = "rows = sorted(items)\n"
_SUBSCRIPT = "first = pair[0]\n"

# A comparison that already names its key — the negative case for the ordering flag.
_KEYED = "rows = sorted(items, key=Row.rank)\n"

# How many records the multi-record fixture declares.
_TWO = 2


def _run(source: str) -> tuple[str, record_transform.SlottedRecords]:
    """Return the transformed source and the command that produced it."""
    command = record_transform.SlottedRecords(CodemodContext())
    updated = cst.parse_module(source).visit(command)
    return updated.code, command


def the_classdef_handler_fires_on_a_planted_record(out: list[str]) -> int:
    """Check the ClassDef handler converted the node it was given — THE BINDING ARM.

    ⚑⚑ THE MUTATION ONLY THIS HANDLER PRODUCES is the decorator plus the dropped base. Asserting
    "the source changed" would pass if any OTHER handler had fired, which is exactly the
    transport-200 this arm exists not to be.
    """
    code, command = _run(_RECORD)
    if "Planted" not in command.converted:
        out.append(f"selftest: the ClassDef handler did not fire — converted {command.converted!r}")
        return 1
    if record_transform.DECORATOR not in code:
        out.append("selftest: the decorator this handler alone adds is absent")
        return 1
    if "class Planted(NamedTuple)" in code:
        out.append("selftest: the NamedTuple base survived the conversion")
        return 1
    return 0


def the_import_handler_removes_a_sole_namedtuple(out: list[str]) -> int:
    """Check the ImportFrom handler removed the whole statement — ITS OWN mutation.

    ⚑ THE WHOLE LINE GOES when `NamedTuple` was the only name: `from typing import` with nothing
    after it is a syntax error, so remove-the-name and remove-the-line are different repairs and
    the handler must pick by what remains.
    """
    code, _command = _run(_RECORD)
    if "NamedTuple" in code:
        out.append("selftest: NamedTuple survived in the converted source")
        return 1
    if "from typing import" in code:
        out.append("selftest: an empty `from typing import` was left behind")
        return 1
    return 0


def the_import_handler_keeps_the_other_names(out: list[str]) -> int:
    """Check a shared `typing` import loses only `NamedTuple`."""
    code, _command = _run(_RECORD_SHARED_IMPORT)
    if "NamedTuple" in code:
        out.append("selftest: NamedTuple was not removed from the shared import")
        return 1
    if "TYPE_CHECKING" not in code:
        out.append("selftest: a sibling name was removed with it")
        return 1
    return 0


def the_call_handler_fires_on_a_planted_keyless_sort(out: list[str]) -> int:
    """Check the Call handler flagged the planted comparison — ITS OWN marker.

    ⚑ THE MESSAGE IS ASSERTED, NOT THE COUNT. A handler that fired and produced the wrong text is
    indistinguishable from the right one by count, and the text is what a reader acts on.
    """
    _code, command = _run(_RECORD + _KEYLESS)
    keyless = [flag for flag in command.flags if "keyless sorted()" in flag]
    if not keyless:
        out.append(f"selftest: the Call handler did not fire — flags {command.flags!r}")
        return 1
    if "FIELD POSITION" not in keyless[0]:
        out.append(f"selftest: the flag does not name the cause: {keyless[0]!r}")
        return 1
    return 0


def a_keyed_comparison_is_not_flagged(out: list[str]) -> int:
    """Check the ordering flag discriminates — the F arm for the Call handler.

    ⚑⚑ WITHOUT THIS, A HANDLER THAT FLAGGED EVERYTHING WOULD PASS the arm above. A control that
    only ever asserts the positive cannot tell a working predicate from a constant one.
    """
    _code, command = _run(_RECORD + _KEYED)
    if any("keyless" in flag for flag in command.flags):
        out.append(f"selftest: a keyed sort was flagged: {command.flags!r}")
        return 1
    return 0


def the_subscript_handler_fires_on_a_planted_index(out: list[str]) -> int:
    """Check the Subscript handler flagged the planted integer index — ITS OWN marker."""
    _code, command = _run(_RECORD + _SUBSCRIPT)
    subscripts = [flag for flag in command.flags if "pair[0]" in flag]
    if not subscripts:
        out.append(f"selftest: the Subscript handler did not fire — flags {command.flags!r}")
        return 1
    if "POSITION" not in subscripts[0]:
        out.append(f"selftest: the flag does not name the cause: {subscripts[0]!r}")
        return 1
    return 0


def a_named_subscript_is_not_flagged(out: list[str]) -> int:
    """Check the subscript flag discriminates — the F arm for the Subscript handler."""
    _code, command = _run(_RECORD + 'value = mapping["name"]\n')
    if any("POSITION identifying" in flag for flag in command.flags):
        out.append(f"selftest: a string subscript was flagged: {command.flags!r}")
        return 1
    return 0


def the_module_handler_adds_the_import(out: list[str]) -> int:
    """Check the Module handler supplied the dataclass import — ITS OWN mutation."""
    code, _command = _run(_RECORD)
    if record_transform.DATACLASS_IMPORT not in code:
        out.append("selftest: the Module handler did not add the dataclass import")
        return 1
    return 0


def the_module_handler_does_not_add_it_twice(out: list[str]) -> int:
    """Check an existing dataclass import is left alone."""
    already = _RECORD.replace(
        "from typing import NamedTuple",
        "from dataclasses import dataclass\nfrom typing import NamedTuple",
    )
    code, _command = _run(already)
    if code.count(record_transform.DATACLASS_IMPORT) != 1:
        out.append(
            f"selftest: the import appears {code.count(record_transform.DATACLASS_IMPORT)} time(s)"
        )
        return 1
    return 0


def the_import_lands_beneath_a_type_checking_block(out: list[str]) -> int:
    """Check the import is added on a module with a `TYPE_CHECKING` block — THE MISSED SHAPE.

    ⚑⚑⚑ THIS ARM EXISTS BECAUSE 20/20 COEXISTED WITH THIRTEEN BROKEN FILES. Every earlier fixture
    had one simple import block, so `_add_import` was green while placing nothing on real modules
    — `F821 Undefined name 'dataclass'` on the decorator the ClassDef handler had just added. The
    per-binding control could not see it: the binding fired, on a shape that never occurs.
    """
    code, command = _run(_WITH_TYPE_CHECKING)
    if not command.converted:
        out.append("selftest: the record was not converted at all")
        return 1
    if record_transform.DATACLASS_IMPORT not in code:
        out.append(
            "selftest: no dataclass import beneath a TYPE_CHECKING block — "
            "the decorator would be undefined"
        )
        return 1
    return 0


def the_import_lands_inside_the_run_not_after_the_block(out: list[str]) -> int:
    """Check the import goes INSIDE the import run when a `TYPE_CHECKING` block ends it.

    ⚑⚑⚑ THE ARM THAT DISCRIMINATES THE THIRTEEN. An anchor computed with `m.findall` matches the
    import NESTED INSIDE an `if TYPE_CHECKING:` block, so it lands on the `if` and places the new
    import AFTER the whole block — outside the run, where `ruff --fix` deletes it as unused and
    the decorator is left undefined. MEASURED on `substrate/edge_census.py`.

    ⚑⚑ ASSERTING POSITION, NOT PRESENCE. `the_import_lands_beneath_a_type_checking_block` already
    asserts the import EXISTS and passes on the broken handler, because presence is not the
    property that fails — placement is. An arm that checks only presence cannot see this.
    """
    code, _command = _run(_BLOCK_IS_LAST)
    lines = code.splitlines()
    if record_transform.DATACLASS_IMPORT not in code:
        out.append("selftest: the import is absent entirely")
        return 1
    at = next(
        n for n, line in enumerate(lines) if line.strip() == record_transform.DATACLASS_IMPORT
    )
    block = next(n for n, line in enumerate(lines) if line.startswith("if TYPE_CHECKING"))
    if at > block:
        out.append(
            f"selftest: the import landed at line {at} — AFTER the TYPE_CHECKING block "
            f"at {block}, outside the import run, where `ruff --fix` deletes it"
        )
        return 1
    return 0


def the_import_lands_when_future_is_the_only_one(out: list[str]) -> int:
    """Check the import is added when removing `typing` leaves only `__future__`.

    ⚑ THE SHAPE THE TRANSFORM ITSELF CREATES. A module importing only `typing` and `__future__`
    becomes a `__future__`-only module mid-transform, so this is the state the handler must
    handle and the one no hand-written fixture naturally has.
    """
    code, _command = _run(_FUTURE_ONLY)
    if record_transform.DATACLASS_IMPORT not in code:
        out.append("selftest: no dataclass import when __future__ is the only import")
        return 1
    return 0


def a_file_with_no_record_is_untouched(out: list[str]) -> int:
    """Check a module declaring no record is returned byte-identical.

    ⚑⚑ THE STRONGEST ARM AGAINST AN OVER-EAGER HANDLER. A transform that added its import
    unconditionally would still pass every arm above, and would dirty 200 files that need nothing.
    """
    plain = '"""Doc."""\n\nVALUE = 1\n'
    code, command = _run(plain)
    if code != plain:
        out.append(f"selftest: a recordless module was rewritten to {code!r}")
        return 1
    if command.converted:
        out.append(f"selftest: it reported converting {command.converted!r}")
        return 1
    return 0


def every_record_in_a_file_is_converted(out: list[str]) -> int:
    """Check the handler fires per record, not once per file."""
    two = _RECORD + '\n\nclass Second(NamedTuple):\n    """Another."""\n\n    other: int\n'
    code, command = _run(two)
    if len(command.converted) != _TWO:
        out.append(f"selftest: converted {command.converted!r}")
        return 1
    if code.count(record_transform.DECORATOR) != _TWO:
        out.append(f"selftest: {code.count(record_transform.DECORATOR)} decorator(s) added")
        return 1
    return 0


def the_transform_is_instantiable(out: list[str]) -> int:
    """Check construction succeeds — libcst validates every decorated handler here.

    ⚑ THIS IS THE ARM libcst GIVES US FOR FREE. `MatcherDecoratableTransformer.__init__` runs
    `_check_types` over each `@m.visit`/`@m.leave` handler and raises `MatchDecoratorMismatch` on a
    malformed signature. It cannot see a WRONG MATCHER — that is what the planted-node arms are
    for — but it does mean a mis-typed handler fails here rather than silently never firing.
    """
    try:
        record_transform.SlottedRecords(CodemodContext())
    except Exception as exc:  # noqa: BLE001 — reported as red, not swallowed
        out.append(f"selftest: the transform would not construct: {type(exc).__name__}: {exc}")
        return 1
    return 0


_ARMS = (
    the_classdef_handler_fires_on_a_planted_record,
    the_import_handler_removes_a_sole_namedtuple,
    the_import_handler_keeps_the_other_names,
    the_call_handler_fires_on_a_planted_keyless_sort,
    a_keyed_comparison_is_not_flagged,
    the_subscript_handler_fires_on_a_planted_index,
    a_named_subscript_is_not_flagged,
    the_module_handler_adds_the_import,
    the_module_handler_does_not_add_it_twice,
    the_import_lands_beneath_a_type_checking_block,
    the_import_lands_inside_the_run_not_after_the_block,
    the_import_lands_when_future_is_the_only_one,
    a_file_with_no_record_is_untouched,
    every_record_in_a_file_is_converted,
    the_transform_is_instantiable,
)

_CASE_COUNT = 3 + 2 + 2 + 2 + 1 + 2 + 1 + 1 + 1 + 2 + 2 + 1 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"record-transform selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"record-transform selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
