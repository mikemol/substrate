"""`sql_census` - the generated sql-relalg census, narrowed to what `sql_lift`'s CLI dispatches.

DECLARED FOR ONE CONSUMER, the `jea/metalanguage/sql_lift.py` shim (W4 file 3 swap, tick 36):
`--sync-census` and `--check-census` are MODES of `sql_lift` that delegate here, and the drift
gate pre-commit runs is `sql_lift.py --check-census`. Read from `jea/metalanguage/sql_census.py`:
`BlockError(Exception)` at `:40` (the marker pair is missing, duplicated or inverted - a fact
about the tree, exit 1 not a traceback); `cmd_sync(files=None) -> int` at `:260`;
`cmd_check(files=None) -> int` at `:274`. `files` is an optional list of paths the census builds
over, `None` meaning the default corpus.

⟡declines: `lift_census`, `builder_census`, `store_census`, `readers_census`, `render_block`,
`splice`, `current_body`, `selftest`, the marker constants and every private member. The shim
dispatches two modes; it does not render the census.
"""

class BlockError(Exception): ...

def cmd_sync(files: list[str] | None = None) -> int: ...
def cmd_check(files: list[str] | None = None) -> int: ...
