// sched-batch.rs — ⟡sched-batch: set SCHED_BATCH + nice + a long EEVDF slice on self, then exec.
//
// WHY: agda builds should be "best effort" — nice 19 (~1.5% weight) yields the CPU to interactive work
// (the IDE), so they run on SPARE CPU; and the EEVDF per-task `sched_runtime` SLICE lets a scheduled agda
// run a LONG uninterrupted stretch, so one agda is NOT preempted merely because a peer agda is runnable.
// membudget's memory lease stays the concurrency roofline — this only changes HOW each admitted agda is
// scheduled, not how many run. Per-task, UNPRIVILEGED (SCHED_BATCH + nice-down need no CAP_SYS_NICE).
//
// No CLI sets the fair-class slice (chrt's -T is DEADLINE-only; SCHED_IDLE *ignores* the slice — pins the
// base slice), hence this tiny sched_setattr wrapper. Compiled single-file (no Cargo, no crates):
//   rustc -O -o scripts/sched-batch scripts/sched-batch.rs
// ~1-2MB RSS, ~1ms startup — leaner than a python interpreter in the per-agda hot path.
//
// Env (all optional): MEMBUDGET_NICE (default 19) · MEMBUDGET_SLICE_MS (default 100, kernel-clamped) ·
//                     MEMBUDGET_NOBATCH (set → skip tuning, just exec).
// Best-effort: any sched_setattr failure (old kernel / container / non-x86_64) is IGNORED — we still exec.

use std::env;
use std::os::raw::c_long;
use std::os::unix::process::CommandExt;
use std::process::Command;

#[repr(C)]
struct SchedAttr {
    size: u32,
    policy: u32,
    flags: u64,
    nice: i32,
    priority: u32,
    runtime: u64, // EEVDF: requested per-task slice (ns) for fair-class tasks
    deadline: u64,
    period: u64,
}

extern "C" {
    fn syscall(num: c_long, ...) -> c_long;
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("sched-batch: usage: sched-batch <cmd> [args...]");
        std::process::exit(2);
    }

    if env::var_os("MEMBUDGET_NOBATCH").is_none() {
        let nice: i32 = env::var("MEMBUDGET_NICE").ok().and_then(|s| s.parse().ok()).unwrap_or(19);
        let slice_ms: u64 = env::var("MEMBUDGET_SLICE_MS").ok().and_then(|s| s.parse().ok()).unwrap_or(100);
        let a = SchedAttr {
            size: std::mem::size_of::<SchedAttr>() as u32,
            policy: 3, // SCHED_BATCH
            flags: 0,
            nice,
            priority: 0,
            runtime: slice_ms.saturating_mul(1_000_000),
            deadline: 0,
            period: 0,
        };
        const SYS_SCHED_SETATTR: c_long = 314; // x86_64
        // sched_setattr(pid=0 self, &attr, flags=0) — ignore the return (best-effort tuning)
        unsafe {
            syscall(SYS_SCHED_SETATTR, 0 as c_long, &a as *const SchedAttr, 0 as c_long);
        }
    }

    let err = Command::new(&args[1]).args(&args[2..]).exec();
    eprintln!("sched-batch: exec {}: {}", args[1], err);
    std::process::exit(127);
}
