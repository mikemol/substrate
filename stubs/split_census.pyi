"""`split_census` - the read-side shim, declared so the driver can import it bare under the gate.

THE MODULE IS ALREADY TYPED (W4 tick 49, gate-G432): every signature here is a COPY of the one
in `scratch/split_census.py`, not a reading of an untyped body. The stub exists because the
per-file gate lints an edit in a TEMP COPY outside `scratch/`, where a bare sibling import has no
directory to resolve against - `pycheck_show` on the real path passed while the hook's copy of the
same edit reported `import-not-found` (W4 file 4 step 13, tick 56). `check_stub_authority` holds
this file to the module, so a signature that moves there is refused here.

⟡declines: `_import_dag`, `_dag`, `_log_index`, `_tree`, `DagTuple`, `_DAG`, `_LOG_INDEX`,
`_TOP_CAP`, `ROOT`, `AG`, `__all__` - the memo and its plumbing; the driver reaches none of
them. `Leverage` is declared as the tuple subclass it is, with the three attributes `of` hangs on.
"""

from collections.abc import Iterable, Sequence
from typing import Self

from substrate import agda_build_census, agda_error_class, import_cone, log_freshness
from substrate.agda_error_class import CLASS_REMEDY as CLASS_REMEDY
from substrate.agda_error_class import is_other as is_other
from substrate.agda_error_class import other_kind as other_kind

def _blast_radius(failed_srcs: Iterable[str], root: str = ...) -> set[str]: ...

class Leverage(tuple[int, int, list[tuple[int, str]]]):
    exclusive: int | None
    members: list[str] | None
    exclusive_members: list[str] | None
    def __new__(cls, n_cone: int, n_seeds: int, top: list[tuple[int, str]]) -> Self: ...
    @classmethod
    def of(cls, lv: import_cone.Leverage) -> Leverage: ...

def leverage(srcs: Iterable[str], root: str = ...,
             against: Iterable[Iterable[str]] = ...) -> Leverage: ...
def log_is_fresh(src_rel: str, root: str = ...) -> log_freshness.Verdict: ...
def _classify(path: str, txt: str,
              trace: list[str] | None = ...) -> agda_error_class.Verdict: ...
def census_from_build(root: str = ...) -> list[agda_build_census.Row]: ...
def stale_why(root: str = ...) -> list[agda_build_census.Why]: ...
def run_census(root: str = ..., jobs: int | None = ...) -> str | int: ...
def agda_build_cmd_jobs() -> Sequence[str]: ...
def tree_stamp(root: str = ...) -> str: ...
def leaves(root: str = ...) -> list[str]: ...
