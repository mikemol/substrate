# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Split `<key> field=value …` argv into an entry key and its fields.

⚑⚑⚑ A VALUE CONTAINS SPACES, SO A PAIR IS NOT ONE ARGV WORD — and the origin's first cut took
every `x=y` token independently. MEASURED: `claim=the bib reader has…` became `claim={the}`, and a
trailing `[tag=0]` was parsed as a FIELD NAMED `[bib-kernel-unwitnessed`. A five-word claim
arrived as a one-word claim plus a garbage field, and the entry was written that way.

⚑⚑ THE RULE THAT FIXES IT IS NARROW AND EASY TO GET WRONG: a new pair STARTS only at a token whose
`=` is preceded by a bare field name; every other token CONTINUES the current value. `[tag=0]` has
an `=` and is not a field start, because `[tag` is not a bare name. Splitting on the presence of
`=` alone is what produced the garbage field.

⚑ THIS IS THE OPERAND-OWNERSHIP CLASS THE SIBLING PARSE MODULE RECORDS FOUR TIMES, arriving inside
the code written to avoid it: the origin's `--set` already joined its trailing words, and `--add`
was written afterwards without that fix. One shape, two verbs, one of them repaired.

⚑ NAME=VALUE RATHER THAN POSITIONALS, deliberately. An entry carries five to seven fields, and a
positional order would be a roster nobody can read at the call site — which is the frozen-roster
defect one layer out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A token that STARTS a new pair: a bare field name, then `=`. ⚑ THE BARE NAME IS THE WHOLE POINT
# — `[tag=0]` matches a naive `=` test and must not start a field.
FIELD_START = re.compile(r"^[\w-]+=")


@dataclass(frozen=True, slots=True)
class Fields:
    """An entry key and the fields parsed from `name=value` operands."""

    key: str | None
    fields: dict[str, str]

    @property
    def usable(self) -> bool:
        """Whether this parse names both an entry and at least one field."""
        return bool(self.key) and bool(self.fields)


def pairs(operands: list[str], key: str | None) -> list[str]:
    """Return the `name=value` strings, each with its multi-word value rejoined.

    ⚑ THE KEY IS SKIPPED ONCE, AND ONLY BEFORE ANY FIELD HAS STARTED. A bare token appearing
    after a field has begun is part of that field's VALUE — an entry key that happens to repeat a
    word from a claim must not silently truncate it.
    """
    out: list[str] = []
    current: str | None = None
    for token in operands:
        if token == key and current is None:
            continue
        if FIELD_START.match(token):
            if current is not None:
                out.append(current)
            current = token
        elif current is not None:
            current += " " + token
    if current is not None:
        out.append(current)
    return out


def split(operands: list[str]) -> Fields:
    """Return the entry key and its fields, parsed from argv operands.

    ⚑ THE KEY IS THE FIRST `=`-FREE TOKEN, which is what makes a trailing bib path dangerous
    enough that the sibling parse module refuses it outright: without that refusal, the path is
    not a key (a key was already taken) and not a field start, so it CONTINUES the last value.
    """
    key = next((token for token in operands if "=" not in token), None)
    fields: dict[str, str] = {}
    for pair in pairs(operands, key):
        name, _eq, value = pair.partition("=")
        fields[name.strip()] = value.strip()
    return Fields(key=key, fields=fields)


USAGE = """\
usage: bibstruct.py --add <key> <field>=<value> ... --apply
  creates a NEW entry. Editing an existing field is --set.
  `claim` and `check` are required; every edge target and the
  item: witness must already exist, or this refuses.
"""
