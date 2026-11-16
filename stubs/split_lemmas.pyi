"""`split_lemmas` - the definition-per-file splitter, narrowed to the two names the driver reaches.

DECLARED FOR ONE CONSUMER, the `scratch/split_pipeline.py` shim (W4 file 4 step 12b, tick 54),
whose split stage calls `split(path, apply=...)` and whose diagnose stage asks `blockers(path)`
before it. Both are UNANNOTATED AT SOURCE, so these types are READINGS of the bodies, named here:
`split` (`:787`) returns `(files, named)` - `files` maps each leaf path to its emitted text, and
`named` is the `(sanitized, original, block-lines)` triple per unit; `blockers` (`:760`) returns
`[]` for a splittable file, else one `(kind, detail)` per refusal where the `applied-open` kind
carries the offending names as a list and the `other` kind carries the first message line.

⚑ THE `detail` UNION IS THE SOURCE'S SHAPE, NOT A HEDGE. The two kinds genuinely carry different
payloads, and a stub that flattened both to `str` would type the names list wrongly for the one
caller that reads it.

⟡declines: `parse`, `capture_demand`, `strip_using`, `sanitize`, `defined_names`, `field_names`,
`write_residue`, the regexes and the conservation guard. The shim reaches two names.
"""

def split(path: str, outdir: str | None = None,
          apply: bool = False) -> tuple[dict[str, str], list[tuple[str, str, list[str]]]]: ...
def blockers(path: str) -> list[tuple[str, list[str] | str]]: ...
