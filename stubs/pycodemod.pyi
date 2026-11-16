"""`pycodemod` - the Python structural-query tool, narrowed to the one name a figure reads.

DECLARED FOR ONE CONSUMER, the `catalog/library/figures.py` shim (W4 file 5 cut 6, tick 63),
whose rostered reach-the-store predicates read `source_of`. The name is RE-EXPORTED from
`_pycodemod_query` (`:2654`), UNANNOTATED there; this is a READING of the body: one
`(path, line, endline, text)` per def or class named `name` across `paths` (the whole corpus
when None), sorted, empty when libcst is absent.

⚑ THE RETURN IS A LIST OF ROWS, NOT A STRING - AND THE ORIGIN FIGURE READ IT AS TEXT.
`figures.dag_rederivations` tested `"module_edges" not in src` against this list, which is a
membership test over rows and never a substring test, so every existing site reported UNPAID
whatever its source said. Declaring the true shape is what surfaced that (gate-G446).

⟡declines: every other mode and reader - `rivals`, `py_files`, the CST walkers, the CLI.
"""

def source_of(name: str, paths: list[str] | None = ...) -> list[tuple[str, int, int, str]]: ...
