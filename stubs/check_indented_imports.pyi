"""`check_indented_imports` - the surviving-reference sweep the pipeline trusts as its VERIFIER.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
whose retire stage feeds `sweep(parent)`'s rows to `barrel_retire.verdict` as its `hits`. The
function is UNANNOTATED AT SOURCE; this is a READING of its body (`:30`): one `(path, line, kind,
text)` per import of `parent` anywhere under `agda/Substrate`, with `kind` either `indented` or
`top-level` and `text` the line with its trailing newline stripped. The row shape is the same
`Hit` alias `substrate/barrel_retire.py` declares, spelled out here rather than imported because a
stub-only name is one stubtest reports as absent at runtime.

⟡declines: the module's `main` and its constants.
"""

def sweep(parent: str) -> list[tuple[str, int, str, str]]: ...
