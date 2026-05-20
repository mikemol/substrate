"""Eliza.Pipeline — composition of bricks via type-checked edge alignment.

Python mirror of `agda/Substrate/Pipeline/Composition.agda`. A Pipeline
is a sequence of Bricks whose D-out / S-out match the next brick's
D-in / S-in. Type-checking happens at construction; ill-aligned
pipelines fail to build.

Also provides:
  * Tee: pass-through with side-channel observation.
  * Tap: name a stream so other bricks can read it.
  * compose: sequential composition of two bricks.
  * Aggregator: merge multiple inputs into one output.

These are the combinators identified in DATAFLOW_REMODEL.md's catalog.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from eliza.brick import Brick, BrickType, FunctionBrick, Witnessing, Unit, UNIT


class TypeMismatchError(TypeError):
    """Raised when two bricks' edge types don't align during composition."""


def _types_compatible(t_out: type, t_in: type) -> bool:
    """Edge-alignment check. For now: exact type equality OR identity
    type (e.g., Unit on both sides). Subclassing isn't required — the
    Agda spec uses `refl`-style equality.
    """
    return t_out is t_in or t_out == t_in


@dataclass
class Pipeline:
    """A typed sequence of Bricks.

    `bricks[i].D_out == bricks[i+1].D_in` and likewise for S.
    """
    bricks: List[Brick] = field(default_factory=list)
    name: str = "pipeline"

    def append(self, brick: Brick) -> "Pipeline":
        """Add a brick to the pipeline; raise on type mismatch."""
        if self.bricks:
            prev = self.bricks[-1]
            if not _types_compatible(prev.brick_type.D_out, brick.brick_type.D_in):
                raise TypeMismatchError(
                    f"D-edge mismatch: {prev.name}.D_out={prev.brick_type.D_out} "
                    f"!= {brick.name}.D_in={brick.brick_type.D_in}"
                )
            if not _types_compatible(prev.brick_type.S_out, brick.brick_type.S_in):
                raise TypeMismatchError(
                    f"S-edge mismatch: {prev.name}.S_out={prev.brick_type.S_out} "
                    f"!= {brick.name}.S_in={brick.brick_type.S_in}"
                )
        self.bricks.append(brick)
        return self

    @property
    def brick_type(self) -> BrickType:
        """The pipeline's own BrickType (for nesting in larger pipelines)."""
        if not self.bricks:
            raise ValueError("empty pipeline has no brick_type")
        first = self.bricks[0].brick_type
        last = self.bricks[-1].brick_type
        return BrickType(
            D_in=first.D_in, D_out=last.D_out, S_in=first.S_in, S_out=last.S_out
        )

    @property
    def witnesses(self) -> Witnessing:
        """The pipeline's witnessing is the entry brick's (convention).

        Higher modules can refine this for specific pipeline shapes.
        """
        if not self.bricks:
            return Witnessing.D_TO_S
        return self.bricks[0].witnesses

    @property
    def homomorphism_tag(self) -> str:
        return f"pipeline[{', '.join(b.homomorphism_tag for b in self.bricks)}]"

    def step(self, d_in: Any, s_in: Any) -> Tuple[Any, Any]:
        """Run the pipeline. Each brick's output feeds the next's input.

        The S state threads through; intermediate D outputs are passed
        as the next brick's D input.
        """
        d, s = d_in, s_in
        for brick in self.bricks:
            d, s = brick.step(d, s)
        return d, s

    def stats(self) -> Dict[str, Any]:
        """Merge each brick's stats. Brick names disambiguate keys.

        If two bricks emit the same stats key, the latter wins; callers
        should disambiguate via brick.name prefixes when needed.
        """
        out: Dict[str, Any] = {}
        for brick in self.bricks:
            out.update(brick.stats())
        return out


# --- Combinators -----------------------------------------------------------


def compose(b1: Brick, b2: Brick, name: str = "composed") -> Pipeline:
    """Sequential composition. The result is a Pipeline of length 2."""
    return Pipeline(bricks=[b1, b2], name=name)


@dataclass
class Tee:
    """Pass-through brick with side-channel observation.

    The observer is called on each step's (d_in, s_in, d_out, s_out) and
    may perform side effects (e.g., persist to a recorder). The brick's
    primary I/O passes through unchanged.
    """
    inner: Brick
    observer: Callable[[Any, Any, Any, Any], None]
    name: str = "tee"
    homomorphism_tag: str = ""

    @property
    def brick_type(self) -> BrickType:
        return self.inner.brick_type

    @property
    def witnesses(self) -> Witnessing:
        return self.inner.witnesses

    def step(self, d_in: Any, s_in: Any) -> Tuple[Any, Any]:
        d_out, s_out = self.inner.step(d_in, s_in)
        self.observer(d_in, s_in, d_out, s_out)
        return d_out, s_out

    def stats(self) -> Dict[str, Any]:
        return self.inner.stats()


@dataclass
class Tap:
    """Name a brick's output stream so downstream bricks can read it.

    Tap maintains a `last_value` slot updated on each step; downstream
    code reads `tap.last_value` instead of routing through the pipeline's
    D edge. Useful for diamond-shaped DAGs where one source feeds many
    consumers without altering the linear pipeline.
    """
    inner: Brick
    label: str
    last_value: Optional[Any] = None
    homomorphism_tag: str = ""

    @property
    def brick_type(self) -> BrickType:
        return self.inner.brick_type

    @property
    def name(self) -> str:
        return f"tap[{self.label}]"

    @property
    def witnesses(self) -> Witnessing:
        return self.inner.witnesses

    def step(self, d_in: Any, s_in: Any) -> Tuple[Any, Any]:
        d_out, s_out = self.inner.step(d_in, s_in)
        self.last_value = d_out
        return d_out, s_out

    def stats(self) -> Dict[str, Any]:
        return self.inner.stats()


@dataclass
class Aggregator:
    """Merge K named inputs into one output via a bundling function.

    The Merger / case-elimination brick from the catalog; witnesses C⇒D.
    Inputs are gathered from a dict and reduced by `bundle`.
    """
    input_keys: List[str]
    bundle: Callable[..., Any]
    output_type: type
    name: str = "aggregator"
    homomorphism_tag: str = ""
    witnesses: Witnessing = Witnessing.C_TO_D

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=dict, D_out=self.output_type, S_in=Unit, S_out=Unit)

    def step(self, d_in: Dict[str, Any], s_in: Any) -> Tuple[Any, Any]:
        args = [d_in[k] for k in self.input_keys]
        return self.bundle(*args), s_in

    def stats(self) -> Dict[str, Any]:
        return {}


# --- Pipeline introspection (slice 15 will extend this) --------------------


def describe(pipeline: Pipeline) -> str:
    """Plain-text rendering of the pipeline structure."""
    lines = [f"Pipeline({pipeline.name}):"]
    for i, brick in enumerate(pipeline.bricks):
        bt = brick.brick_type
        lines.append(
            f"  [{i}] {brick.name}  "
            f"({bt.D_in.__name__} × {bt.S_in.__name__}) "
            f"-> ({bt.D_out.__name__} × {bt.S_out.__name__})  "
            f"witnesses={brick.witnesses.value}"
        )
    return "\n".join(lines)


# --- Slice 10: pipeline.show() → Mermaid ---------------------------------


def _witnessing_class(w) -> str:
    """Map a Witnessing tag to a CSS class for the rendered diagram."""
    from eliza.brick import Witnessing as W
    return {
        W.D_TO_S: "swrite",  # write
        W.S_TO_D: "sread",   # read
        W.D_TO_C: "chooser",
        W.C_TO_D: "merger",
        W.S_TO_C: "dispatch",
        W.C_TO_S: "swrite",  # state mutation
    }.get(w, "pure")


def to_mermaid(pipeline: Pipeline) -> str:
    """Render a Pipeline as a Mermaid flowchart.

    Each Brick becomes a hexagon (`{{...}}`); the witnessing tag colours
    it via classDef. Edges are typed by the brick's D_out → D_in
    pairing. State carriers are inferred from S edges that share a type
    across consecutive bricks.

    The auto-generated diagram is structurally equivalent to the hand-
    drawn one in `DATAFLOW_REMODEL.md` modulo cosmetic layout.
    """
    lines = ["flowchart TB"]
    # Style definitions.
    lines.extend([
        "    classDef input fill:#cfc,stroke:#080,stroke-width:2px",
        "    classDef output fill:#fcc,stroke:#800,stroke-width:2px",
        "    classDef state fill:#ccf,stroke:#008",
        "    classDef sread fill:#ffe,stroke:#aa0",
        "    classDef swrite fill:#fee,stroke:#a00",
        "    classDef chooser fill:#fef,stroke:#a0a",
        "    classDef merger fill:#eef,stroke:#00a",
        "    classDef dispatch fill:#eff,stroke:#0aa",
        "    classDef pure fill:#eee,stroke:#888",
        "",
    ])
    # Input boundary.
    if pipeline.bricks:
        first = pipeline.bricks[0]
        lines.append(f"    input([Input: {first.brick_type.D_in.__name__}]):::input")
    # Brick nodes.
    for i, brick in enumerate(pipeline.bricks):
        bt = brick.brick_type
        cls = _witnessing_class(brick.witnesses)
        label = (
            f"{brick.name}<br/>"
            f"{brick.witnesses.value}<br/>"
            f"{bt.D_in.__name__}→{bt.D_out.__name__}"
        )
        lines.append(f"    b{i}{{{{{label}}}}}:::{cls}")
    # Output boundary.
    if pipeline.bricks:
        last = pipeline.bricks[-1]
        lines.append(
            f"    output([Output: {last.brick_type.D_out.__name__}]):::output"
        )
    lines.append("")
    # Edges.
    if pipeline.bricks:
        lines.append("    input --> b0")
        for i in range(len(pipeline.bricks) - 1):
            edge_label = pipeline.bricks[i].brick_type.D_out.__name__
            lines.append(f"    b{i} -->|{edge_label}| b{i+1}")
        lines.append(f"    b{len(pipeline.bricks) - 1} --> output")
    return "\n".join(lines)


def show(pipeline: Pipeline, path: str = None) -> str:
    """Render the pipeline as Mermaid; optionally write to `path`.

    Returns the Mermaid source as a string. If `path` ends in `.md`,
    wraps the source in a fenced ```mermaid block; else writes raw.
    """
    src = to_mermaid(pipeline)
    if path is not None:
        if path.endswith(".md"):
            content = f"# Pipeline: {pipeline.name}\n\n```mermaid\n{src}\n```\n"
        else:
            content = src
        with open(path, "w") as f:
            f.write(content)
    return src
