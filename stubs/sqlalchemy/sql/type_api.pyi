"""`TypeEngine` — the root of sqlalchemy's type hierarchy, in the module that really exports it.

⚑⚑ IT IS DECLARED HERE AND NOT IN `sqlalchemy/__init__.pyi` BECAUSE `from sqlalchemy import
TypeEngine` FAILS AT RUNTIME. The commissioning brief specified it for the top-level stub;
`sqlalchemy/__init__.py` re-exports many names `from .types` and this is not among them. Placing
it in the top-level stub would have type-checked green and raised `ImportError` — the failure
mode that brief records happening twice, and the reason `stubtest` is non-negotiable here.

⚑ THE PARAMETER IS INVARIANT, as upstream declares it (`_T = TypeVar("_T", bound=Any)`). The
bound is dropped rather than restated: an unbounded `_T` admits everything the bounded one did,
and spelling `Any` to reproduce a bound would put back the annotation this stub set removes.
"""

from typing import Generic, TypeVar

_T = TypeVar("_T")

class TypeEngine(Generic[_T]): ...
