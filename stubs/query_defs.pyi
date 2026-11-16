"""`query_defs` - the query compiler, narrowed to the ONE name the `sql_lift` shim reaches.

DECLARED FOR ONE CONSUMER, the `jea/metalanguage/sql_lift.py` shim (W4 file 3 swap, tick 35):
`build` interns every compiled SQL builder's Rel lowering, and the builders live in
`INTERN_BUILDERS` - the `name -> zero-argument builder` mapping bound at module scope
(`query_defs.py:~150-190`, a dict literal over the `q_*` / `v_*` functions of `query_decl`).
The shim calls each thunk and hands the `Select` to `substrate.rel_bridges.rel_of_select`.

THE VALUE TYPE IS A READING, NOT A TRANSCRIPTION - AND THE FIRST READING WAS WRONG. Upstream
binds bare function objects with no annotation; a draft declared `Callable[[], Select]`, and the
shim's first run raised `'Insert' object has no attribute 'get_final_froms'`: the roster holds
WRITE builders too, which the origin hid under the same `except Exception` that skips
parameterised builders. So the value is `Callable[[], object]`, and a consumer NARROWS with
`isinstance(stmt, Select)` - a write builder has no Rel lowering, and saying so is the honest
form of what the origin swallowed.

⟡declines: everything else - the five statement readers (`written_table`, `returned_columns`,
`_table_occurrences`, `_tables_of`, `_columns_of`, drained into `substrate.sql_statement`),
`REFERENCE_ARMS`, the `do_*` modes, `verify`, `drops`, `touching`, the compile/check gate
(drained into `substrate.sql_cache`), `_reg`, `main`, and every private member. This is a
consumer stub for one attribute, not a description of the compiler.
"""

from collections.abc import Callable

INTERN_BUILDERS: dict[str, Callable[[], object]]
