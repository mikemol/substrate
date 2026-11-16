"""`split_unblock` - the blocker-chase layer, narrowed to the five names the driver re-exports.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12, tick 53),
which re-exports `verify`, `diagnose`, `leaves_ready`, `_under` and `unblock` so its
dispatch and any consumer reaching through it resolve exactly what they did before. The
module stays in `scratch/` and keeps its deliberate import CYCLE with the driver (`_driver`
imports `split_pipeline` LATE because `unblock` repairs a link by calling `rewire_only`, a
write stage); stubtest imports it directly, which the late import permits.

EVERY FUNCTION IS UNANNOTATED AT SOURCE, so these types are READINGS of the bodies, each
named here: `verify` (`:63`) maps `(path,) + blame(...)` over its paths, so each row is
`(path, verdict, cited)`; `diagnose` (`:127`) returns `_classify`'s `(kind, detail, remedy)`;
`leaves_ready` (`:151`) returns `(all clean?, rows)` with rows shaped as `verify`'s; `_under`
(`:192`) returns sorted module names; `unblock` (`:287`) returns `(status, chain)` where
status is one of its literal outcome strings and chain the modules repaired so far.
`jobs`, `max_rounds` and `trace` default to None as the source does.

⚑ THE ROW SHAPE IS SPELLED OUT THREE TIMES RATHER THAN ALIASED, because stubtest reported a
stub-only alias as `Row is not present at runtime` - a name declared here and absent there is
the defined-in/exported-from error this stub set keeps catching, one layer down.

⟡declines: the four driver thunks (`isolate_check`, `blame`, `rewire_only`, `_classify`),
`_driver`, the two repair callers (`_repair_notinscope`, `_repair_noparse`), and the
constants. The shim reaches five names; the rest are the module's own business.
"""

def verify(paths: list[str], jobs: int | None = None) -> list[tuple[str, str, str | None]]: ...
def diagnose(path: str, trace: list[str] | None = None) -> tuple[str, str, str | None]: ...
def leaves_ready(modname: str) -> tuple[bool, list[tuple[str, str, str | None]]]: ...
def _under(modname: str) -> list[str]: ...
def unblock(path: str, max_rounds: int | None = None,
            apply: bool = False) -> tuple[str, list[str]]: ...
