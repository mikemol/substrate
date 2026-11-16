"""`fix_noparse` - the NoParseForApplication diagnoser, narrowed to its diagnosis half.

DECLARED FOR ONE CONSUMER, the `catalog/library/figures.py` shim (W4 file 5 cut 6, tick 63),
whose refiner reads `classify(log)` for the verdict that splits `other:NoParseForApplication`.
UNANNOTATED AT SOURCE; a READING of the body (`:72`): one `(path, line, col, culprit, verdict)`
per `[NoParseForApplication]` block, `verdict` `fixity` (a displaced prefix operator, repairable)
or `other`; a directory operand is walked for every `*.agdai.log`; an unreadable log yields [].

⟡declines: `repair`, the regexes and the CLI.
"""

def classify(log: str) -> list[tuple[str, int, int, str, str]]: ...
