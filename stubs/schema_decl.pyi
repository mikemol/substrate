"""`schema_decl` - THE schema declaration, narrowed to what its two consumers read.

CONSUMER 1, the `jea/metalanguage/sql_lift.py` shim (W4 file 3 swap, tick 36):
`substrate.recursion_class.classify` takes the DECLARED relation names as a parameter, and the
shim supplies them from `MD.tables` - the same `MetaData` `upsert` reads its column arity from,
so a new table is classifiable with no edit anywhere. Read from `jea/metalanguage/schema_decl.py:82`:
`MD = MetaData()`; `.tables` is declared on the `sqlalchemy` stub's `MetaData`.

CONSUMER 2 (W63, the `schema.py` decomposition arc): `schema_establish.py`'s `--establish`
dispatch reads `_TIERS` to validate the tier names an invocation names and to enumerate each
tier's relations for its plan/report output. Read from `jea/metalanguage/schema_decl.py:1744`:
`_TIERS = {"sourced": SOURCED_TABLES, ...}` - a `dict[str, set[str]]`, each value a set of
relation names (`SOURCED_TABLES = {"core_decoded"}`, etc).

⟡declines: every table object (`_t`, `INDEXES`, `SHADOWS`, the DDL helpers) and every other
private member. The two consumers together read one object apiece.
"""

from sqlalchemy import MetaData

MD: MetaData
_TIERS: dict[str, set[str]]
