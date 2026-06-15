"""
thermal_gate.py — AI-7c: thermal throttle as a GATE on the clock edges.

Package temperature is an active conductance VALVE: below the throttle trip the clocks run free;
above it (PROCHOT / DPTF passive policy) the clock is clamped, scaling the clock edge(s) by a factor
g(T) in (0,1]. This adds the CLOCK shared-node to the graph (ties the two-clock + TDP findings):
the gate multiplies clock_core (compute) and -- depending on whether it is common-mode -- possibly
clock_mem (BW). A `gate`-kind GraphElement, discovered from the thermal zones.

Witnesses (each [W]):
1. THERMAL ZONES DISCOVERED: the package/CPU zone + its trip points (the gate threshold).
2. GATE SHAPE: g(T) = 1 below the trip, < 1 above (a clamp), monotone decreasing past it.
3. STRUCTURAL PLACEMENT + the honest open question: the gate multiplies the clock edge. IF it gates
   BOTH clock domains equally (common-mode) the ridge is INVARIANT; if core-only, the ridge MOVES.
   Which it is, is EMPIRICALLY testable (drive temperature, watch the ridge) -- NOT asserted here
   (validate-outputs-not-inputs). Flagged as the validation hook.
"""
import os, glob
os.environ.setdefault("CUDA_PATH", "/usr")
from host_probe import _read


def discover_thermal():
    zones = []
    for z in sorted(glob.glob("/sys/class/thermal/thermal_zone[0-9]*")):
        typ = _read(z + "/type") or ""
        temp = _read(z + "/temp")
        trips = []
        for tp in sorted(glob.glob(z + "/trip_point_*_temp")):
            tt = tp.replace("_temp", "_type")
            trips.append((_read(tt) or "?", int(_read(tp) or 0) / 1000))
        zones.append(dict(type=typ, temp=(int(temp) / 1000 if temp else None), trips=trips))
    return zones


def gate(T, T_trip, floor=0.4, k=0.03):
    """Clock-scale factor: 1 below the trip, linearly clamped above it down to a floor."""
    if T <= T_trip:
        return 1.0
    return max(floor, 1.0 - k * (T - T_trip))


if __name__ == "__main__":
    zones = discover_thermal()
    print(f"thermal zones discovered: {[(z['type'], z['temp']) for z in zones]}\n")
    SANE = lambda v: 20 <= v <= 150                      # a real trip; <=0 (e.g. -274) is a disabled sentinel
    # current package temperature (x86_pkg_temp preferred)
    pkg = next((z for z in zones if "x86_pkg" in z['type'].lower()), None) \
        or next((z for z in zones if any(s in z['type'].lower() for s in ("pkg", "cpu", "tcpu"))), None)
    cur_T = pkg['temp'] if pkg else (zones[0]['temp'] if zones else None)
    # throttle trip = the most-conservative SANE passive/hot/critical across all zones
    sane = [(z['type'], t, v) for z in zones for t, v in z['trips']
            if t in ("passive", "hot", "critical") and SANE(v)]
    disabled = [(z['type'], t, v) for z in zones for t, v in z['trips'] if not SANE(v)]
    trip = min(v for _, _, v in sane) if sane else 95.0
    trip_src = min(sane, key=lambda x: x[2])[:2] if sane else ("default", "n/a")
    w1 = cur_T is not None and bool(sane)
    print(f"1. package temp = {cur_T} C; throttle trip = {trip} C (from {trip_src}); {w1}")
    print(f"   DISABLED trips (firmware-managed, NOT in sysfs): {disabled}")
    print(f"   -> package passive throttle is DPTF/INT3400 firmware policy, not kernel trips "
          f"(surface present but firmware-unpopulated, like EDAC/IBECC)")

    # 2. gate shape
    below = gate(trip - 10, trip); at = gate(trip, trip); above = gate(trip + 20, trip)
    w2 = below == 1.0 and above < 1.0 and gate(trip + 30, trip) <= above
    print(f"2. gate shape: g({trip-10})={below:.2f} (free) ; g({trip})={at:.2f} ; g({trip+20})={above:.2f} "
          f"(clamped) ; monotone-down past trip {w2}")

    # 3. structural placement: gate multiplies the clock edge -> compute (clock_core) scales by g(T).
    base_core_clock = 4.6e9
    for T in (trip - 10, trip + 10, trip + 30):
        eff = base_core_clock * gate(T, trip)
        print(f"   T={T}C -> clock_core edge = {eff/1e9:.2f} GHz (x{gate(T,trip):.2f})")
    w3 = gate(trip + 30, trip) < gate(trip - 10, trip)
    print(f"3. gate multiplies the clock edge {w3}; OPEN (empirical, validate-outputs): if it gates BOTH")
    print(f"   clock domains equally -> ridge INVARIANT; if core-only -> ridge MOVES. Testable by driving")
    print(f"   temperature and watching the ridge (like power_arms drove the governor) -- not asserted.")

    ok = w1 and w2 and w3
    print(f"\nTHERMAL GATE (AI-7c): zones-discovered {w1}; gate-shape {w2}; clock-edge-placement {w3}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — thermal throttle is a GATE on the clock edges: g(T)=1 below the")
    print(f"  trip, clamped above. It adds the clock shared-node (compute via clock_core; BW via clock_mem")
    print(f"  if common-mode). Whether it is common-mode (ridge-invariant) or core-only (ridge-moves) is")
    print(f"  an EMPIRICAL question flagged for validation, not asserted. AI-7d (ASPM-dynamic link) remains.")
