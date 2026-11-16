#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""sorted_stream.py — DRAINED. The sorted-stream carrier now lives under `substrate/`.

⚑⚑⚑ THIS FILE IS A FORWARDING SHIM, AND ITS EMPTINESS IS THE RESULT. Every concern it held has a
typed home: the order-as-data and the field reader in `substrate/sort_key.py`, the single-pass
carrier in `substrate/sorted_carrier.py`, the producers in `substrate/sorted_source.py`, the
order-requiring combinators in `substrate/sorted_combinator.py`, and the transparent nodes in
`substrate/sorted_transparent.py`. Each of those is clean under the per-file type gate; this one
could not be, and the difference is WHERE the code lives rather than what it does.

⚑⚑⚑ THE PRIOR READING — that no `jea/metalanguage/` file can reach zero because splitting would
leave two clean-shaped files both importing the untyped hub — REASONED ABOUT REPAIRING IN PLACE.
It was correct about that and wrong as a closure boundary. A drain does not repair: the concern
MOVES to a package where it can be annotated, and it takes no `jea/` import with it. The five
modules above import nothing from `jea/`, which is what makes them clean.

⚑⚑ THE CASES MOVED WITH THE CONCERN RATHER THAN BEING DELETED. The inline suite this file used to
carry is distributed across `substrate/sort_key_selftest.py`, `sorted_carrier_selftest.py`,
`sorted_source_selftest.py`, `sorted_combinator_selftest.py` and `sorted_transparent_selftest.py`
— each pinning the module whose behaviour it describes, and each ADDING the arms the inline suite
never had (a producer's declared key, `already` staying silent on a liar, `project` dropping a
getter bound to a replaced row shape).

⚑⚑ THE NAMES ARE RE-EXPORTED RATHER THAN THE FILE DELETED, because this reader's importer census
reports zero static import sites AND names seven dynamic-import shapes it cannot resolve — a zero
that bounds itself is not an absence. The shim costs one indirection and removes the guessing.
"""

from __future__ import annotations

from substrate.sort_key import (
    UNORDERED,
    Cell,
    OrderError,
    Rev,
    SortKey,
    as_cell,
    default_get,
    extractor,
)
from substrate.sorted_carrier import Sorted
from substrate.sorted_combinator import dedup, group, join, merge
from substrate.sorted_source import already, checked, from_dict, from_set
from substrate.sorted_transparent import limit, project, where

__all__ = [
    "UNORDERED",
    "Cell",
    "OrderError",
    "Rev",
    "SortKey",
    "Sorted",
    "already",
    "as_cell",
    "checked",
    "dedup",
    "default_get",
    "extractor",
    "from_dict",
    "from_set",
    "group",
    "join",
    "limit",
    "merge",
    "project",
    "where",
]
