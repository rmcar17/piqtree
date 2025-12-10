#!/usr/bin/env python3
"""
Simple benchmark that runs the piqtree workload in a fresh Python process
and IQ-TREE as an external process, measuring peak RSS (resident set size)
via GNU time (MAX RSS in KiB -> bytes).

Usage: place next to bd.0.fasta and iqtree3 (or adjust paths). Run: python3 bench_simple.py
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

TRIALS = 5
FASTA = "bd.0.fasta"
IQEXEC = Path.cwd() / "iqtree3"  # adjust if needed


def find_time_bin() -> Optional[str]:
    """Find a standalone time binary (not the shell builtin). Prefer /usr/bin/time."""
    candidates = ["/usr/bin/time"]
    which = shutil.which("time")
    if which and which not in candidates:
        candidates.append(which)
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return None


def run_with_time(
    cmd: list[str],
    time_bin: str,
    time_fmt: str = "MAXRSS:%M\nELAPSED:%e\n",
    cwd: Optional[Path | str] = None,
) -> Tuple[int, int, float]:
    """
    Run cmd under GNU time (time_bin) with -f=time_fmt.
    Returns (returncode, peak_rss_bytes, elapsed_seconds).
    peak_rss_bytes will be parsed from time's stderr (%M -> KiB).
    """
    full = [time_bin, "-f", time_fmt] + cmd
    # time writes its summary to stderr; capture both
    proc = subprocess.run(
        full,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=(str(cwd) if cwd else None),
    )
    peak_kib = 0
    elapsed = 0.0
    # parse stderr lines for MAXRSS and ELAPSED
    for line in proc.stderr.splitlines():
        if line.startswith("MAXRSS:"):
            try:
                peak_kib = int(line.split(":", 1)[1].strip())
            except Exception:
                peak_kib = 0
        if line.startswith("ELAPSED:"):
            try:
                elapsed = float(line.split(":", 1)[1].strip())
            except Exception:
                elapsed = 0.0
    return proc.returncode, peak_kib * 1024, elapsed


def fallback_run_python_child(script_text: str, fasta: str) -> Tuple[int, int, float]:
    """
    Fallback if `time` is unavailable. Runs a Python child and uses resource.getrusage
    to read RUSAGE_CHILDREN.ru_maxrss after child exits. Note: ru_maxrss units are OS-dependent
    (on Linux it's KiB).
    """
    import resource

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(script_text)
        child_path = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, child_path, fasta],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # ru_maxrss is in kilobytes on Linux
        r = resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_kib = int(getattr(r, "ru_maxrss", 0) or 0)
        elapsed = 0.0  # we could time with perf_counter if desired
        return proc.returncode, peak_kib * 1024, elapsed
    finally:
        Path(child_path).unlink(missing_ok=True)


# wrapper python body to execute the piqtree workload in a fresh process
PIQTREE_WRAPPER = r"""
import sys
from cogent3 import load_aligned_seqs
from piqtree import build_tree
aln = load_aligned_seqs(sys.argv[1], moltype="dna")
# run the heavy operation
build_tree(aln, "GTR+G", rand_seed=42)
"""


def bench_piqtree(trials: int, fasta: str, time_bin: Optional[str]):
    rows = []
    for t in range(1, trials + 1):
        print(f"PIQTREE trial {t}/{trials} ...", flush=True)
        if time_bin:
            # write wrapper to temp file and call "python wrapper.py fasta" under time
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
                fh.write(PIQTREE_WRAPPER)
                wrapper = fh.name
            try:
                code, peak_bytes, elapsed = run_with_time(
                    [sys.executable, wrapper, fasta], time_bin
                )
            finally:
                Path(wrapper).unlink(missing_ok=True)
        else:
            code, peak_bytes, elapsed = fallback_run_python_child(
                PIQTREE_WRAPPER, fasta
            )
        if code != 0:
            raise RuntimeError(f"piqtree trial {t} failed (exit {code})")
        rows.append({"trial": t, "time_s": elapsed, "peak_rss_bytes": peak_bytes})
        print(f" last: {elapsed:.2f}s, peak {peak_bytes / (1024**2):.2f} MiB")
    return rows


def bench_iqtree(trials: int, fasta: str, iqexe: Path, time_bin: Optional[str]):
    if not iqexe.exists():
        raise FileNotFoundError(f"IQ-TREE executable not found at {iqexe}")
    rows = []
    for t in range(1, trials + 1):
        print(f"IQTREE trial {t}/{trials} ...", flush=True)
        # create an isolated temp directory for this trial and copy the alignment there
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            dest = tmpdir_path / Path(fasta).name
            shutil.copy(fasta, dest)
            cmd = [
                str(iqexe),
                "-s",
                dest.name,
                "-m",
                "GTR+G",
                "-seed",
                "42",
                "-nt",
                "1",
            ]
            if time_bin:
                code, peak_bytes, elapsed = run_with_time(
                    cmd, time_bin, cwd=tmpdir_path
                )
            else:
                # fallback: run directly and rely on resource.getrusage of children (less precise)
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=tmpdir_path,
                )
                import resource

                r = resource.getrusage(resource.RUSAGE_CHILDREN)
                peak_kib = int(getattr(r, "ru_maxrss", 0) or 0)
                code = proc.returncode
                peak_bytes = peak_kib * 1024
                elapsed = 0.0
            if code != 0:
                # include stderr for debugging if available (but time may have captured it)
                raise RuntimeError(
                    f"IQ-TREE trial {t} failed (exit {code}); check files in {tmpdir}"
                )
        rows.append({"trial": t, "time_s": elapsed, "peak_rss_bytes": peak_bytes})
        print(f" last: {elapsed:.2f}s, peak {peak_bytes / (1024**2):.2f} MiB")
    return rows


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["trial", "time_s", "peak_rss_bytes", "peak_rss_mib"])
        for r in rows:
            w.writerow(
                [
                    r["trial"],
                    f"{r['time_s']:.6f}",
                    r["peak_rss_bytes"],
                    f"{r['peak_rss_bytes'] / (1024**2):.6f}",
                ]
            )


def main():
    time_bin = find_time_bin()
    if not time_bin:
        print(
            "Warning: could not find an external 'time' binary; falling back to resource.getrusage (less precise).",
            file=sys.stderr,
        )
    iq = bench_iqtree(TRIALS, FASTA, IQEXEC, time_bin)
    write_csv(Path("bench_iq_results.csv"), iq)
    piq = bench_piqtree(TRIALS, FASTA, time_bin)
    write_csv(Path("bench_piq_results.csv"), piq)

    def summarise(rows):
        times = [r["time_s"] for r in rows]
        peaks = [r["peak_rss_bytes"] for r in rows]
        print(
            f"trials: {len(rows)}, time mean {sum(times) / len(times):.3f}s, time min {min(times):.3f}s, time max {max(times):.3f}s"
        )
        print(
            f"peak mean {sum(peaks) / len(peaks) / (1024**2):.3f} MiB, peak min {min(peaks) / (1024**2):.3f} MiB, peak max {max(peaks) / (1024**2):.3f} MiB"
        )

    print("\nPIQTREE summary:")
    summarise(piq)
    print("\nIQTREE summary:")
    summarise(iq)


if __name__ == "__main__":
    main()
