"""`agda_defs` - the definition/import index, narrowed to the one name the driver reaches.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
whose retire stage reads `reexport_index()` to find the `public` conduits a barrel still forwards.
The function is UNANNOTATED AT SOURCE; this is a READING of its body (`:1649`): one `(module,
line, target, tail, kind)` row per surviving `public` re-export under `agda/Substrate`, sorted by
module, where `tail` is the raw statement text after the target (continuation lines joined) and
`kind` is `import` for an `open import M ... public` or `apply` for an `open M args ... public`
module application - the distinction the docstring records as having been computed and then
discarded, which made the census unrankable.

⟡declines: `import_index`, `def_index`, `_local_defs`, the unused-imports census and every
other mode. The shim reaches one name.
"""

def reexport_index() -> list[tuple[str, int, str, str, str]]: ...
