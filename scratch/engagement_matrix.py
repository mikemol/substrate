"""
engagement_matrix.py — build the operation × axis-role matrix, then
mechanically derive which V₄-rotated operations exist, which are
constructible, and which are structurally barred.

Roles per (operation, axis):
  ·  none
  I  input — operation receives this axis as parameter
  O  output — operation returns a value of this axis
  R  read — consults this axis without changing it
  M  mutate — modifies existing content of this axis
  C  create — extends this axis with new content

A cell can hold multiple roles (e.g., "IC" = input and create).

Axis capabilities (what each axis can support):
  D = {I, O, R, C}      (immutable hash-consed; no M)
  C = {I, O, R, M, C}   (memo is mutable)
  S = {I, O, R, C}      (append-only log; no M)
  W = {I, O, R, M, C}   (mutable tagged array; everything)

V₄ swaps act on the matrix by permuting columns:
  α (DC)(SW): swap D↔C, S↔W
  β (DS)(CW): swap D↔S, C↔W
  γ (DW)(CS): swap D↔W, C↔S

A V₄-twin pair: op_A's rotated profile == op_B's profile (column-wise equal).
A V₄-rotation that requires a role outside the target axis's capabilities
is STRUCTURALLY BARRED. Otherwise it's CONSTRUCTIBLE (could be built).
"""

from itertools import product


AXES = ['D', 'C', 'S', 'W']
ROLES = ['I', 'O', 'R', 'M', 'C']  # input, output, read, mutate, create

# Axis capabilities — what roles each axis supports
CAPS = {
    'D': frozenset({'I', 'O', 'R', 'C'}),         # immutable, no M
    'C': frozenset({'I', 'O', 'R', 'M', 'C'}),    # mutable memo
    'S': frozenset({'I', 'O', 'R', 'C'}),         # append-only, no M
    'W': frozenset({'I', 'O', 'R', 'M', 'C'}),    # fully mutable
}

V4_SWAPS = {
    'α': {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β': {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ': {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}


# ============================================================
# The engagement matrix — what each implemented op actually does
# ============================================================
# Profile: {axis: frozenset of roles}. Empty axis = not engaged.

def profile(D='', C='', S='', W=''):
    """Compact constructor for engagement profiles."""
    return {
        'D': frozenset(D),
        'C': frozenset(C),
        'S': frozenset(S),
        'W': frozenset(W),
    }


# Build profiles by careful inspection of each op's actual behavior
OPERATIONS = {
    # Founding micro-ops (S1-S7)
    'S1_nil':        profile(D='I'),                    # NIL is a constant data value
    'S2_cons':       profile(D='IC', S='C'),            # cons takes two D, creates D, logs S
    'S3_left':       profile(D='IO'),                   # left: D in, D out
    'S3_right':      profile(D='IO'),                   # right: D in, D out
    'S4_eq':         profile(D='IR'),                   # eq: D in, returns bool
    'S5_apply':      profile(D='IO', C='C', S='C'),     # apply: D in, D out, memo grows, log
    'S6_parse':      profile(D='C', S='C'),             # parse: creates D, logs S
    'S7_transform':  profile(D='IO', S='C'),            # transform: D in, D out, logs
    'interp':        profile(D='IO', C='C', S='C'),     # like apply, with explicit rules

    # M32 implemented V₄-twin operations
    'workspace_alloc':     profile(W='C', S='C'),       # creates W slot, logs
    'workspace_free':      profile(W='IM'),             # mutates W (frees slot)
    'store':               profile(D='I', W='IM', S='C'),  # D in, W in+mutated, log
    'load':                profile(D='O', W='IR'),      # W in+read, D out
    'workspace_kind':      profile(W='IR'),             # pure W read
    'compute_identity':    profile(D='IO'),             # nothing happens — pass through
    'state_identity':      profile(S='C'),              # only logs to history
    'compute_marker':      profile(C='I', W='IM', S='C'),   # C in, W mutated, log
    'workspace_marker':    profile(C='I', W='IM', S='C'),   # SAME profile as compute_marker!
    'is_workspace_marker': profile(W='IR'),             # pure W read
    'workspace_witness':   profile(D='IO', C='C', W='IR', S='C'),  # D out, C mut via normalize, W read, log
    'workspace_driven_state': profile(D='C', C='C', W='IR', S='C'),  # calls apply internally
}


# ============================================================
# V₄ rotation on profiles
# ============================================================

def rotate_profile(prof, swap):
    """Apply a V₄ swap to a profile by permuting axis labels."""
    swap_dict = V4_SWAPS[swap]
    rotated = {ax: frozenset() for ax in AXES}
    for ax in AXES:
        target_ax = swap_dict[ax]
        rotated[target_ax] = prof[ax]
    return rotated


def profile_equal(p1, p2):
    """Two profiles are equal iff every axis has the same role set."""
    return all(p1[ax] == p2[ax] for ax in AXES)


def profile_realizable(prof):
    """A profile is realizable iff every axis only uses roles within its capabilities."""
    return all(prof[ax] <= CAPS[ax] for ax in AXES)


def profile_violations(prof):
    """Return the (axis, role) pairs that violate capability constraints."""
    violations = []
    for ax in AXES:
        for role in prof[ax]:
            if role not in CAPS[ax]:
                violations.append((ax, role))
    return violations


# ============================================================
# Display utilities
# ============================================================

def fmt_role_set(s):
    """Render role set in canonical order (I, O, R, M, C)."""
    if not s:
        return '·'
    return ''.join(r for r in ROLES if r in s)


def fmt_profile(prof, width=4):
    return ' '.join(fmt_role_set(prof[ax]).ljust(width) for ax in AXES)


# ============================================================
# Matrix printout
# ============================================================

def print_matrix():
    print("=" * 76)
    print("  ENGAGEMENT MATRIX — implemented operations × axis roles")
    print("=" * 76)
    print()
    print(f"  Roles: I=input  O=output  R=read  M=mutate  C=create  ·=none")
    print(f"  Axis capabilities (missing role = structurally barred):")
    for ax in AXES:
        missing = set(ROLES) - CAPS[ax]
        miss_str = f"  (lacks {','.join(sorted(missing))})" if missing else ""
        print(f"    {ax}: {{{','.join(sorted(CAPS[ax]))}}}{miss_str}")
    print()
    print(f"  {'operation':<25} {'D':<5} {'C':<5} {'S':<5} {'W':<5}")
    print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for name, prof in OPERATIONS.items():
        print(f"  {name:<25} {fmt_role_set(prof['D']):<5} {fmt_role_set(prof['C']):<5} "
              f"{fmt_role_set(prof['S']):<5} {fmt_role_set(prof['W']):<5}")


# ============================================================
# V₄-rotation analysis
# ============================================================

def analyze_rotations():
    print("\n" + "=" * 76)
    print("  V₄-ROTATION ANALYSIS")
    print("=" * 76)
    print()
    print("  For each operation, compute its V₄-rotated profiles and check:")
    print("    [TWIN]    — rotated profile == another op's profile (genuine V₄-twin)")
    print("    [BUILD]   — rotated profile realizable but no op has it (constructible)")
    print("    [BARRED]  — rotated profile violates axis capabilities (unrealizable)")
    print()

    # Index profiles for lookup
    profile_to_name = {}
    for name, prof in OPERATIONS.items():
        key = tuple(prof[ax] for ax in AXES)
        profile_to_name.setdefault(key, []).append(name)

    stats = {'TWIN': 0, 'BUILD': 0, 'BARRED': 0, 'SELF': 0}

    for name, prof in OPERATIONS.items():
        print(f"\n  ── {name} : {fmt_profile(prof)} ──")
        for swap in ['α', 'β', 'γ']:
            rotated = rotate_profile(prof, swap)
            key = tuple(rotated[ax] for ax in AXES)
            if key == tuple(prof[ax] for ax in AXES):
                # Profile is V₄-invariant under this swap
                tag = 'SELF'
                detail = "(V₄-invariant: rotation gives back the same profile)"
            elif key in profile_to_name:
                tag = 'TWIN'
                twins = [n for n in profile_to_name[key] if n != name]
                detail = f"matches: {', '.join(twins)}"
            elif profile_realizable(rotated):
                tag = 'BUILD'
                detail = "rotated profile is realizable but unimplemented"
            else:
                tag = 'BARRED'
                viols = profile_violations(rotated)
                detail = f"barred by: {', '.join(f'{ax} cannot {role}' for ax, role in viols)}"
            stats[tag] += 1
            print(f"      {swap}: {fmt_profile(rotated)}  [{tag}] {detail}")

    return stats


def summarize(stats):
    print("\n" + "=" * 76)
    print("  SUMMARY")
    print("=" * 76)
    print()
    total = sum(stats.values())
    for tag in ['TWIN', 'BUILD', 'BARRED', 'SELF']:
        pct = 100 * stats[tag] / total if total else 0
        print(f"    {tag:<8} {stats[tag]:>3}/{total}  ({pct:.0f}%)")
    print()
    print("  Interpretations:")
    print("    TWIN   = V₄ symmetry holds at the engagement-profile level for this rotation.")
    print("    BUILD  = V₄ symmetry could be made to hold if we add the missing operation.")
    print("    BARRED = V₄ symmetry cannot be made to hold without axis-capability refactor.")
    print("    SELF   = operation is V₄-invariant under this swap (carries the symmetry trivially).")


# ============================================================
# Specific complement operation derivation
# ============================================================

def list_constructible_complements():
    """For each [BUILD] case, generate the spec of the missing operation."""
    print("\n" + "=" * 76)
    print("  CONSTRUCTIBLE COMPLEMENTS — operations we could build to close V₄ symmetry")
    print("=" * 76)
    print()

    profile_to_name = {}
    for name, prof in OPERATIONS.items():
        key = tuple(prof[ax] for ax in AXES)
        profile_to_name.setdefault(key, []).append(name)

    seen = set()  # avoid duplicates (same target profile from different sources)
    suggestions = []

    for name, prof in OPERATIONS.items():
        for swap in ['α', 'β', 'γ']:
            rotated = rotate_profile(prof, swap)
            key = tuple(rotated[ax] for ax in AXES)
            if key in profile_to_name or key in seen:
                continue
            if not profile_realizable(rotated):
                continue
            seen.add(key)
            suggestions.append((name, swap, rotated, prof))

    print(f"  Found {len(suggestions)} constructible complement operations.\n")
    for source, swap, rotated, source_prof in suggestions:
        print(f"  • V₄-twin of '{source}' under {swap}:")
        print(f"      source profile:  {fmt_profile(source_prof)}")
        print(f"      rotated profile: {fmt_profile(rotated)}")
        # Describe what the new operation would do
        held_axis = next((ax for ax in AXES if 'I' in rotated[ax]), None)
        creating_axis = next((ax for ax in AXES if 'C' in rotated[ax]), None)
        mutating_axis = next((ax for ax in AXES if 'M' in rotated[ax]), None)
        outputting_axis = next((ax for ax in AXES if 'O' in rotated[ax]), None)
        parts = []
        if held_axis: parts.append(f"takes {held_axis}-axis input")
        if creating_axis: parts.append(f"creates new {creating_axis}-axis entity")
        if mutating_axis: parts.append(f"mutates {mutating_axis}-axis")
        if outputting_axis: parts.append(f"returns {outputting_axis}-axis value")
        if parts:
            print(f"      semantics: {'; '.join(parts)}")
        print()


def list_structurally_barred():
    """List V₄-rotations that hit axis-capability walls."""
    print("\n" + "=" * 76)
    print("  STRUCTURALLY BARRED ROTATIONS — V₄ symmetry the architecture forbids")
    print("=" * 76)
    print()

    barred = []
    for name, prof in OPERATIONS.items():
        for swap in ['α', 'β', 'γ']:
            rotated = rotate_profile(prof, swap)
            if not profile_realizable(rotated):
                viols = profile_violations(rotated)
                barred.append((name, swap, viols))

    print(f"  Found {len(barred)} barred rotations.\n")
    by_violation = {}
    for name, swap, viols in barred:
        for ax, role in viols:
            by_violation.setdefault((ax, role), []).append(f"{name}/{swap}")

    print("  Aggregated by capability violation:\n")
    for (ax, role), ops in sorted(by_violation.items()):
        print(f"    {ax} cannot {role}: blocks {len(ops)} rotation(s)")
        for op in ops[:5]:
            print(f"      - {op}")
        if len(ops) > 5:
            print(f"      ... and {len(ops) - 5} more")
        print()

    print("  Root cause: axis-capability asymmetry.")
    print("    D and S lack M (mutate). C and W have M.")
    print("    Without M on D and S, V₄-rotations that map M onto them are barred.")


if __name__ == "__main__":
    print_matrix()
    stats = analyze_rotations()
    summarize(stats)
    list_constructible_complements()
    list_structurally_barred()
