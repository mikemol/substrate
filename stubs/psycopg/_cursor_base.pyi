# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`BaseCursor`, at the private module psycopg actually defines it in.

⚑⚑ A PRIVATE MODULE IS STUBBED HERE ONLY BECAUSE THE PUBLIC SURFACE NAMES IT. `rows.RowFactory`
takes a `BaseCursor`, so the protocol cannot be spelled without this type — and psycopg puts it
in `_cursor_base`, not at the package root. Declaring it at the root instead is a name the
library does not have there, which `stubtest` reports as *"not present at runtime"*. The
underscore records that a caller should not reach for it, not that a stub may relocate it.

⚑ IT IS NOT A CONSTRUCTIBLE SURFACE FOR THIS REPO. A caller receives a `Cursor`; this class
exists so the row-factory protocol has the parameters the library gives it, and only the
members a caller reads through that path are declared.
"""

class BaseCursor[ConnectionType, Row]:
    """What both cursor kinds share — the type a row factory is handed."""

    def __init__(self, connection: ConnectionType) -> None: ...
    @property
    def connection(self) -> ConnectionType: ...
    @property
    def closed(self) -> bool: ...
    @property
    def rowcount(self) -> int:
        """How many records the last operation affected, or -1 when that is unknown.

        ⚑ `-1` IS "NOT APPLICABLE", NOT "ZERO ROWS", and the two are different answers. A
        statement that returns no rowcount and one that affected none both look like a falsy
        number to a caller that does not check the sign.
        """
        ...
