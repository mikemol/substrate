"""`fix_stale_using` - the stale-`using` repairer, narrowed to the two names the driver reaches.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54):
its last stage calls `sites(log)` to REPORT the ModuleDoesntExport blocks and then dies with the
repair command, and its standing guard calls `check_cycles()`. Both are UNANNOTATED AT SOURCE, so
these are READINGS of the bodies: `sites` (`:48`) takes one log file or a directory of per-module
`*.agdai.log` and returns `(file, line, module, names)` rows, deduplicated; `check_cycles` (`:370`)
prints every import that transitively imports its importer and returns 1 when any exists, else 0 -
an exit code, which is why it is `int` and not `bool`.

⟡declines: `_index`, `_would_cycle`, `_dedupe`, `stmt_span`, the writer path and its
stale-coordinate guard. The shim reaches two names.
"""

def sites(log: str) -> list[tuple[str, int, str, list[str]]]: ...
def check_cycles() -> int: ...
