"""`fix_notinscope` - the NotInScope diagnoser/repairer, narrowed to its diagnosis half.

DECLARED FOR ONE CONSUMER, the `catalog/library/figures.py` shim (W4 file 5 cut 6, tick 63),
whose refiner reads `classify(log)` for the verdict that splits `other:NotInScope`. UNANNOTATED
AT SOURCE; a READING of the body (`:1089`): one `(path, name, verdict, homes)` per not-in-scope
name in the log, `verdict` one of `resolvable` / `ambiguous` / `no-definer`, `homes` the defining
modules (empty for no-definer). No repair happens in it.

⟡declines: `parse`, `narrow_by_provenance`, the repair path, `--apply`, `--unresolved`.
"""

def classify(log: str) -> list[tuple[str, str, str, list[str]]]: ...
