"""EMPTY BUT LOAD-BEARING — the bridge to `sqlalchemy.sql.base`, `.elements` and `.type_api`.

⚑ THE SAME CONTIGUITY REQUIREMENT AS `dialects/__init__.pyi`, AND THE SAME SILENT FAILURE. A
stub package must be walkable end to end: without this file mypy cannot reach the three
submodule stubs beneath it, falls back to the installed package, and the `Any`s this stub set
exists to remove reappear as errors reported against OUR source.

⚑ IT DECLARES NOTHING BECAUSE NOTHING IS IMPORTED FROM `sqlalchemy.sql` ITSELF. Every consumer
here names a submodule (`sqlalchemy.sql.base`, `sqlalchemy.sql.elements`,
`sqlalchemy.sql.type_api`) or the top-level package. Declaring a surface would be inventing one.
"""
