# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The connection- and query-parameter aliases, at the module psycopg declares them in.

⚑⚑ THIS FILE EXISTS BECAUSE `stubtest` MEASURES A NAME AT ITS PATH, NOT BY ITS SPELLING. A
first draft declared `ConnParam`, `Query` and `Params` at the package root, where they read
correctly and are not: psycopg defines them in `abc.py`, so the root declarations were reported
as *"not present at runtime"* — a stub asserting a name the library does not have there. That
is the same class of defect as an invented signature, and it type-checks just as happily, which
is why the gate is the thing that catches it.

⚑ THE ALIASES ARE PSYCOPG'S OWN, NARROWED ONLY WHERE THE LIBRARY IS GENUINELY DYNAMIC. See the
package docstring for the one substitution (`Any` → `object` in a value position) and for what
`Query` deliberately omits.
"""

from collections.abc import Mapping, Sequence

#: A value a connection keyword may carry. Concrete in psycopg's own `abc.py`.
type ConnParam = str | int | None

#: A mapping of connection keywords, as `conninfo_to_dict` renders one.
type ConnDict = dict[str, ConnParam]

#: A query, as the forms this stub covers: a literal string or its encoded bytes.
#:
#: ⚑ NARROWER THAN THE LIBRARY'S `Query`, WHICH ALSO ADMITS `sql.SQL` AND `sql.Composed`, and
#: this is an omission of NAMES rather than a dropped parameter: the `sql` composition module is
#: not declared by this stub at all, so there is no type here for those alternatives to be
#: spelled as. A caller composing SQL needs that module typed, which is work, not a narrowing.
type QueryNoTemplate = str | bytes

#: What a caller may send as a statement.
type Query = QueryNoTemplate

#: Query parameters, positional or named.
#:
#: ⚑ THE VALUES ARE `object`: what a parameter may be is exactly what the adapter registry
#: accepts, which is open by design. `object` admits the same values and refuses the unchecked
#: USES that `Any` waves through.
type Params = Sequence[object] | Mapping[str, object]
