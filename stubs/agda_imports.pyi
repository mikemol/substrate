"""`agda_imports` - the import editor, narrowed to THE shared self-import predicate.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
which calls `importable(path, mod)` before emitting any `open import` line - the predicate its
own docstring names as the sharable unit, because twelve tools rewrite imports in place and cannot
route through `add_import`. The function is UNANNOTATED AT SOURCE; this is a READING of its body
(`:64`): True unless `mod` is the module `path` itself defines, so a rewire never produces the
`[CyclicModuleDependency] X importing X` error that reads like a structural cycle.

⟡declines: `add_import`, `order`, `stage_warning`, `_module_of` and the CLI. The shim reaches
one name.
"""

def importable(path: str, mod: str) -> bool: ...
