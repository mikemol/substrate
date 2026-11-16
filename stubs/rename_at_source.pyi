"""`rename_at_source` - the collision cure, narrowed to the one name the driver reaches.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
whose collision stage calls `rename(home, name, new, apply=True)` as a LIBRARY - which is why the
source reads `apply` as a parameter rather than from argv, and why this stub keeps it positional.
The function is UNANNOTATED AT SOURCE; this is a READING of its body (`:159`): `(renamed,
ambiguous)`, two lists of file paths - the files rewritten (or that would be) and the files left
alone because they import more than one provider, for the build to arbitrate. `site` narrows the
sweep to one file and defaults to None as the source does.

⟡declines: `def_index`, `spellings`, `apply_spellings`, `any_spelling`, `qualified_spellings`,
`classify_file`, `imports_of`, `word`. The shim reaches one name.
"""

def rename(home: str, old: str, new: str, apply: bool = False,
           site: str | None = None) -> tuple[list[str], list[str]]: ...
