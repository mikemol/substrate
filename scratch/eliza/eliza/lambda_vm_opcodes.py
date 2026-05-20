"""Eliza.LambdaVMOpcodes — R-arc: the codec's existing machinery NAMED as
a lambda-calculus VM.

Per the user's recognition (R-arc framing):
  * S_VAR / parameterised body → already the stack (StackTensor M6)
  * S_APPLY → already what NT references do
  * S_REDUCE → Sequitur growth IS abstraction; INLINE is the inverse
                (removed per substrate discipline; reintroduced here as
                an *encoder choice* via speculation)
  * α-conversion (de Bruijn) → already implicit (opcode indices are
                                de Bruijn slots)

This module adds the explicit OPCODE LABELS for these existing
operations + the small set of new opcodes needed to fully expose the
latent lambda-VM:

  Sequitur-control:
    S_GROW         — explicit "grow opcode now from last digram"
    S_DEFER_GROW   — explicit "do not grow even though digram repeats"
    S_INLINE(rid)  — β-reduce: replace NT(rid) with its body in-place

  Stack-manipulation (Forth-style):
    S_PUSH(value)  — push entry onto stack
    S_POP          — discard top
    S_DUP          — duplicate top
    S_SWAP         — swap top two
    S_ROT          — rotate top three
    S_VAR(d)       — read entry at depth d (de Bruijn-style)

  Introspection:
    S_INSPECT(opc) — emit the structural category of opcode opc

These are CONTROL OPCODES occupying alphabet slots above the data
opcodes (terminals + grown rules). The encoder emits them when
speculation says they win.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class OpcodeCategory(IntEnum):
    """Substrate-honest classification of opcode kinds.

    The integer values are used as `S_INSPECT` return values.
    """
    CHAIN_TERMINAL = 0       # raw chain symbol (data)
    SUBSTRATE_NATIVE = 1     # V₄ / Sylow-3 / cross-Sylow patterns
    EXPLODING_BITMAP = 2     # high-redundancy patterns
    GROWN_COMPOSITE = 3      # adaptive grammar rule
    SEQUITUR_CONTROL = 4     # S_GROW / S_DEFER_GROW / S_INLINE
    STACK_CONTROL = 5        # S_PUSH / S_POP / S_DUP / S_SWAP / S_ROT
    LAMBDA_VAR = 6           # S_VAR(d) — stack-relative variable
    INTROSPECTION = 7        # S_INSPECT


# --- Control opcode IDs (relative to the control-section base) -------
# Control opcodes occupy alphabet slots:
#   [24 ..               24 + n_data_opcodes - 1] — data opcodes
#   [24 + n_data ..                            ] — control opcodes

class ControlOpcode(IntEnum):
    """Relative IDs for control opcodes within the control section."""
    S_GROW = 0
    S_DEFER_GROW = 1
    S_INLINE_LAST = 2        # inline the last-referenced NT
    S_PUSH_REWRITE = 3       # push (rewrite=1, observe=top.observe)
    S_PUSH_NO_REWRITE = 4    # push (rewrite=0, observe=top.observe)
    S_POP = 5
    S_DUP = 6
    S_SWAP = 7
    S_ROT = 8
    S_VAR_0 = 9              # read top of stack (depth 0)
    S_VAR_1 = 10             # depth 1
    S_VAR_2 = 11             # depth 2
    S_VAR_3 = 12             # depth 3
    S_INSPECT_LAST = 13      # emit category of last-emitted opcode


N_CONTROL_OPCODES = len(ControlOpcode)


def control_opcode_name(op: int) -> str:
    """Human-readable name for a control opcode index."""
    try:
        return ControlOpcode(op).name
    except ValueError:
        return f"unknown_control_{op}"


# --- Opcode category classification function -------------------------


def categorise_opcode_idx(
    idx: int, n_data_opcodes: int, n_initial_opcodes: int,
    n_exploding_bitmaps: int = 10,
) -> OpcodeCategory:
    """Classify an emit_idx into its OpcodeCategory.

    Layout in joint alphabet:
      [0 ..23]                                  — chain terminals
      [24 .. 24 + n_initial_substrate - 1]      — substrate-native generators
      [24 + n_substrate .. 24 + n_substrate + n_exp - 1]  — exploding bitmaps
      [24 + n_initial .. 24 + n_data - 1]       — grown composites
      [24 + n_data .. 24 + n_data + N_CONTROL]  — control opcodes
    """
    if idx < 24:
        return OpcodeCategory.CHAIN_TERMINAL
    op_idx = idx - 24
    if op_idx >= n_data_opcodes:
        return OpcodeCategory.SEQUITUR_CONTROL    # or other control category
    if op_idx < n_initial_opcodes - n_exploding_bitmaps:
        return OpcodeCategory.SUBSTRATE_NATIVE
    if op_idx < n_initial_opcodes:
        return OpcodeCategory.EXPLODING_BITMAP
    return OpcodeCategory.GROWN_COMPOSITE


# --- StackEntry: now a single int instead of (rewrite, observe) tuple
# --- (extension: arbitrary value as stack entry, for VAR access) -----


def stack_apply_op(stack: list, op_idx: int, top_value: Optional[int] = None) -> list:
    """Apply a control opcode to the stack; return new stack.

    `top_value` is used by S_PUSH variants if they take a value.
    Other ops don't need it.
    """
    s = list(stack)
    op = ControlOpcode(op_idx)
    if op == ControlOpcode.S_POP:
        if s:
            s.pop()
    elif op == ControlOpcode.S_DUP:
        if s:
            s.append(s[-1])
    elif op == ControlOpcode.S_SWAP:
        if len(s) >= 2:
            s[-1], s[-2] = s[-2], s[-1]
    elif op == ControlOpcode.S_ROT:
        if len(s) >= 3:
            s[-3], s[-2], s[-1] = s[-2], s[-1], s[-3]
    elif op == ControlOpcode.S_PUSH_REWRITE:
        s.append(1)    # 1 = rewrite-on
    elif op == ControlOpcode.S_PUSH_NO_REWRITE:
        s.append(0)    # 0 = rewrite-off
    # S_VAR_n / S_GROW / S_DEFER_GROW / S_INLINE_LAST / S_INSPECT_LAST
    # don't modify the stack; they're consumed by encoder logic.
    return s


def stack_top_rewrite_mode(stack: list, default: int = 1) -> int:
    """Read the rewrite mode from the top of the stack."""
    if not stack:
        return default
    return stack[-1]


def stack_var(stack: list, depth: int, default: int = 1) -> int:
    """Read entry at depth (0 = top, 1 = below top, ...)."""
    if depth >= len(stack):
        return default
    return stack[-1 - depth]


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    # Test stack manipulation semantics.
    s: list = []
    s = stack_apply_op(s, ControlOpcode.S_PUSH_REWRITE.value)
    assert s == [1]
    s = stack_apply_op(s, ControlOpcode.S_PUSH_NO_REWRITE.value)
    assert s == [1, 0]
    s = stack_apply_op(s, ControlOpcode.S_DUP.value)
    assert s == [1, 0, 0]
    s = stack_apply_op(s, ControlOpcode.S_SWAP.value)
    assert s == [1, 0, 0]    # swap top two; 0,0 stays 0,0
    s2 = stack_apply_op([1, 2, 3], ControlOpcode.S_SWAP.value)
    assert s2 == [1, 3, 2]
    s3 = stack_apply_op([1, 2, 3], ControlOpcode.S_ROT.value)
    assert s3 == [2, 3, 1]
    s4 = stack_apply_op([5], ControlOpcode.S_POP.value)
    assert s4 == []

    # S_VAR access.
    assert stack_var([10, 20, 30], 0) == 30
    assert stack_var([10, 20, 30], 1) == 20
    assert stack_var([10, 20, 30], 2) == 10
    assert stack_var([], 0, default=42) == 42

    # Categorisation.
    cat = categorise_opcode_idx(
        idx=24, n_data_opcodes=21, n_initial_opcodes=21, n_exploding_bitmaps=10
    )
    assert cat == OpcodeCategory.SUBSTRATE_NATIVE
    cat = categorise_opcode_idx(
        idx=24 + 15, n_data_opcodes=21, n_initial_opcodes=21,
        n_exploding_bitmaps=10,
    )
    assert cat == OpcodeCategory.EXPLODING_BITMAP    # 11..20 is exploding
    cat = categorise_opcode_idx(
        idx=24 + 30, n_data_opcodes=100, n_initial_opcodes=21,
    )
    assert cat == OpcodeCategory.GROWN_COMPOSITE
    cat = categorise_opcode_idx(0, n_data_opcodes=21, n_initial_opcodes=21)
    assert cat == OpcodeCategory.CHAIN_TERMINAL

    if verbose:
        print("=== LambdaVMOpcodes (R-arc) self-check ===")
        print(f"  control opcodes:        {N_CONTROL_OPCODES}")
        for op in ControlOpcode:
            print(f"    {op.value:>2}  {op.name}")
        print(f"  stack push/pop/dup/swap/rot: OK")
        print(f"  S_VAR depth-0/1/2 access:    OK")
        print(f"  opcode categorisation:       OK")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
