"""`gate_status` - the pre-commit hook parsed as the gate roster, narrowed to the one name a figure reads.

DECLARED FOR ONE CONSUMER, the `catalog/library/figures.py` shim (W4 file 5 cut 6, tick 63),
whose `wired_gates` is `gate_status.gates()`. The function is UNANNOTATED AT SOURCE; this is a
READING of its body (`:48`): one `(name, argv, conditional)` per `run` line in the hook, where
`conditional` is True for an indented line (a gate nested inside an `if`). It RAISES
`SyntaxError` when the hook does not parse as shell, refusing a silently truncated roster.

⟡declines: `HOOK`, `RUN`, the RED/GREEN rendering and the CLI.
"""

def gates(hook: str = ...) -> list[tuple[str, str, bool]]: ...
