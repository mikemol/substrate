"""`wg_engine` - the worklist gate's engine, narrowed to the one name a figure reads.

DECLARED FOR ONE CONSUMER, the `catalog/library/figures.py` shim (W4 file 5 cut 6, tick 63),
which repoints the origin's dead `worklist_gate.scratch_size` (gate-G440: the name moved here
when worklist_gate was drained) to `wg_engine.scratch_size`. UNANNOTATED AT SOURCE; a READING
of the body (`:112`): the bytes under a scratch tree, 0 when it does not exist, `path` defaulting
to the engine's own `SCRATCH`.

⟡declines: everything else - the sandbox, the ordering, `SCRATCH` itself.
"""

def scratch_size(path: str | None = ...) -> int: ...
