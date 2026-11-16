"""`collapse_carrier_nesting` - the occupied-slot classifier, narrowed to the one name the driver reaches.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
whose retire stage hands `classify_occupied(leaf_mod, parent_mod)`'s answer to
`barrel_retire.verdict` as its `occupied` input. The function is UNANNOTATED AT SOURCE; this is a
READING of its body (`:296`): `(kind, uncovered)` where `kind` is `barrel` when every name the
parent defines is covered by some leaf in its directory, else `real-module`, and `uncovered` is
the sorted list of names no leaf provides (empty exactly when the kind is `barrel`).

⟡declines: `_defines`, the collapse writer and its own main. The shim reaches one name.
"""

def classify_occupied(mod: str, parent_mod: str) -> tuple[str, list[str]]: ...
